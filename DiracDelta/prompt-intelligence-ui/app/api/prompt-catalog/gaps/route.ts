import { NextResponse } from 'next/server';
import { bigqueryClient, projectId } from '../_lib';

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const limit = Math.max(1, Math.min(200, Number(searchParams.get('limit') || 50)));
  const pid = projectId();
  const bq = bigqueryClient();

  const sql = `
    WITH current_versions AS (
      SELECT * FROM \`${pid}.prism_prompt_catalog.prompt_versions\` WHERE is_current = TRUE
    ), chunk_counts AS (
      SELECT prompt_uid, run_id, version_number, COUNT(*) AS actual_chunks
      FROM \`${pid}.prism_prompt_catalog.prompt_chunks\`
      GROUP BY prompt_uid, run_id, version_number
    ), event_counts AS (
      SELECT prompt_uid, run_id, version_number, COUNTIF(event_type = 'completed') AS completed_events
      FROM \`${pid}.prism_prompt_catalog.prompt_events\`
      GROUP BY prompt_uid, run_id, version_number
    )
    SELECT
      v.prompt_uid,
      v.source_prompt_id,
      v.version_number,
      v.run_id,
      v.status,
      v.chunk_count,
      COALESCE(c.actual_chunks, 0) AS actual_chunks,
      v.extracted_chars,
      COALESCE(e.completed_events, 0) AS completed_events,
      ARRAY_CONCAT(
        IF(v.status != 'success', ['non_success_status'], []),
        IF(v.extracted_chars = 0, ['empty_extraction'], []),
        IF(v.chunk_count != COALESCE(c.actual_chunks, 0), ['chunk_count_mismatch'], []),
        IF(COALESCE(e.completed_events, 0) = 0, ['missing_completed_event'], [])
      ) AS gap_codes
    FROM current_versions v
    LEFT JOIN chunk_counts c USING (prompt_uid, run_id, version_number)
    LEFT JOIN event_counts e USING (prompt_uid, run_id, version_number)
    WHERE v.status != 'success'
      OR v.extracted_chars = 0
      OR v.chunk_count != COALESCE(c.actual_chunks, 0)
      OR COALESCE(e.completed_events, 0) = 0
    ORDER BY ARRAY_LENGTH(gap_codes) DESC, v.valid_from DESC
    LIMIT @limit;
  `;

  try {
    const [rows] = await bq.query({ query: sql, params: { limit } });
    return NextResponse.json({ success: true, projectId: pid, rows });
  } catch (error: any) {
    return NextResponse.json({ success: false, error: error.message }, { status: 500 });
  }
}
