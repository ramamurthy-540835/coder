import { NextResponse } from 'next/server';
import { BigQuery } from '@google-cloud/bigquery';

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const selectedUid = searchParams.get('promptUid') || '';
  
  const bq = new BigQuery({ projectId: 'ctoteam' });

  try {
    // 1. Fetch all distinct prompt UIDs to populate the dropdown selection list
    const listQuery = `
      SELECT DISTINCT prompt_uid 
      FROM \`ctoteam.prism_prompt_catalog.prompt_versions\`
      ORDER BY prompt_uid;
    `;
    const [listRows] = await bq.query({ query: listQuery });
    const availablePrompts = listRows.map(r => r.prompt_uid);

    // Default to a fallback standard ID if database list is empty
    const activeUid = selectedUid || availablePrompts[0] || 'vertexai:3381323161097207808';
    const sourcePromptId = activeUid.split(':').pop() || activeUid;

    // 2. Fetch the latest active version metadata (SCD Type 2)
    const versionQuery = `
      SELECT 
        prompt_uid,
        source_prompt_id as prompt_id,
        version_number, 
        run_id, 
        repeat_mode, 
        valid_from,
        chunk_count, 
        user_message_count, 
        model_message_count,
        raw_size_bytes, 
        extracted_chars, 
        status, 
        system_present
      FROM \`ctoteam.prism_prompt_catalog.prompt_versions\`
      WHERE prompt_uid = @prompt_uid AND is_current = TRUE
      LIMIT 1;
    `;
    const [versionRows] = await bq.query({ 
      query: versionQuery,
      params: { prompt_uid: activeUid }
    });
    const latestVersion = versionRows[0] || null;

    // 3. Fetch the latest AI estimation from BigQuery
    let estimation = null;
    try {
      const estimationQuery = `
        SELECT 
          estimated_tokens, actual_loc, confidence_score,
          raw_json, created_at
        FROM \`ctoteam.prism_sentinel_estimation.ai_development_estimates\`
        WHERE prompt_id = @prompt_id
        ORDER BY created_at DESC
        LIMIT 1;
      `;
      const [estRows] = await bq.query({ 
        query: estimationQuery,
        params: { prompt_id: sourcePromptId }
      });
      if (estRows.length > 0) {
        estimation = estRows[0];
      }
    } catch (e: any) {
      console.warn("Estimates table query skipped or empty:", e.message);
    }

    // 4. Fetch recent state machine audit events
    const eventsQuery = `
      SELECT event_type, lifecycle_status, repeat_mode, severity, created_at
      FROM \`ctoteam.prism_prompt_catalog.prompt_events\`
      WHERE prompt_uid = @prompt_uid
      ORDER BY created_at DESC
      LIMIT 15;
    `;
    const [eventsRows] = await bq.query({ 
      query: eventsQuery,
      params: { prompt_uid: activeUid }
    });

    return NextResponse.json({
      success: true,
      activeUid,
      availablePrompts,
      latestVersion,
      estimation,
      events: eventsRows
    });
  } catch (error: any) {
    return NextResponse.json({ success: false, error: error.message }, { status: 500 });
  }
}
