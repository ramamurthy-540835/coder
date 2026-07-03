import { NextResponse } from 'next/server';
import { bigqueryClient, projectId } from '../_lib';

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const q = searchParams.get('q') || '';
  const status = searchParams.get('status') || '';
  const gapOnly = searchParams.get('gapOnly') === 'true';
  const limit = Math.max(1, Math.min(200, Number(searchParams.get('limit') || 50)));
  const pid = projectId();
  const bq = bigqueryClient();

  const sql = `
    WITH current_versions AS (
      SELECT *
      FROM \`${pid}.prism_prompt_catalog.prompt_versions\`
      WHERE is_current = TRUE
        AND (@status = '' OR status = @status)
        AND (@q = '' OR LOWER(prompt_uid) LIKE CONCAT('%', LOWER(@q), '%')
          OR LOWER(source_prompt_id) LIKE CONCAT('%', LOWER(@q), '%'))
    ), chunk_counts AS (
      SELECT prompt_uid, run_id, version_number, COUNT(*) AS actual_chunks
      FROM \`${pid}.prism_prompt_catalog.prompt_chunks\`
      GROUP BY prompt_uid, run_id, version_number
    ), event_counts AS (
      SELECT prompt_uid, run_id, version_number, COUNTIF(event_type = 'completed') AS completed_events, MAX(created_at) AS latest_event_at
      FROM \`${pid}.prism_prompt_catalog.prompt_events\`
      GROUP BY prompt_uid, run_id, version_number
    )
    SELECT
      v.prompt_uid,
      v.source_prompt_id,
      v.version_number,
      v.run_id,
      v.status,
      v.repeat_mode,
      v.chunk_count,
      COALESCE(c.actual_chunks, 0) AS actual_chunks,
      GREATEST(v.chunk_count - COALESCE(c.actual_chunks, 0), 0) AS missing_chunks,
      v.extracted_chars,
      v.raw_size_bytes,
      v.valid_from,
      COALESCE(e.completed_events, 0) AS completed_events,
      e.latest_event_at,
      (v.status != 'success'
        OR v.extracted_chars = 0
        OR v.chunk_count != COALESCE(c.actual_chunks, 0)
        OR COALESCE(e.completed_events, 0) = 0) AS has_gap
    FROM current_versions v
    LEFT JOIN chunk_counts c USING (prompt_uid, run_id, version_number)
    LEFT JOIN event_counts e USING (prompt_uid, run_id, version_number)
    WHERE (@gapOnly = FALSE OR (v.status != 'success'
        OR v.extracted_chars = 0
        OR v.chunk_count != COALESCE(c.actual_chunks, 0)
        OR COALESCE(e.completed_events, 0) = 0))
    ORDER BY has_gap DESC, v.valid_from DESC
    LIMIT @limit;
  `;

  try {
    const [rows] = await bq.query({ query: sql, params: { q, status, gapOnly, limit } });
    return NextResponse.json({ success: true, projectId: pid, rows });
  } catch (error: any) {
    return NextResponse.json({ success: false, error: error.message }, { status: 500 });
  }
}
