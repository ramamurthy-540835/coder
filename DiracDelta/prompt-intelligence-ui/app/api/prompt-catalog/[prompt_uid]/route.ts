import { NextResponse } from 'next/server';
import { bigqueryClient, classifyRequirementText, detectGaps, projectId } from '../_lib';

export async function GET(_request: Request, context: { params: Promise<{ prompt_uid: string }> }) {
  const params = await context.params;
  const promptUid = decodeURIComponent(params.prompt_uid);
  const pid = projectId();
  const bq = bigqueryClient();
  const queryParams = { prompt_uid: promptUid };

  try {
    const [versionRows] = await bq.query({
      query: `
        SELECT *
        FROM \`${pid}.prism_prompt_catalog.prompt_versions\`
        WHERE prompt_uid = @prompt_uid AND is_current = TRUE
        LIMIT 1;
      `,
      params: queryParams,
    });
    const version = versionRows[0] || null;

    const [chunkRows] = await bq.query({
      query: `
        SELECT chunk_order, chunk_file, gcs_uri, char_count, estimated_tokens, role, artifact_type, created_at
        FROM \`${pid}.prism_prompt_catalog.prompt_chunks\`
        WHERE prompt_uid = @prompt_uid
        ORDER BY version_number DESC, chunk_order ASC
        LIMIT 100;
      `,
      params: queryParams,
    });

    const [eventRows] = await bq.query({
      query: `
        SELECT event_type, lifecycle_status, repeat_mode, severity, message, created_at
        FROM \`${pid}.prism_prompt_catalog.prompt_events\`
        WHERE prompt_uid = @prompt_uid
        ORDER BY created_at DESC
        LIMIT 50;
      `,
      params: queryParams,
    });

    const [attachmentRows] = await bq.query({
      query: `
        SELECT attachment_id, mime_type, attachment_type, gcs_uri, size_bytes, decoded, created_at
        FROM \`${pid}.prism_prompt_catalog.prompt_attachments\`
        WHERE prompt_uid = @prompt_uid
        ORDER BY created_at DESC
        LIMIT 50;
      `,
      params: queryParams,
    });

    const classifierText = [
      promptUid,
      version ? Object.values(version).join(' ') : '',
      chunkRows.map((row: any) => `${row.chunk_file} ${row.role} ${row.artifact_type}`).join(' '),
    ].join('\n');

    return NextResponse.json({
      success: true,
      projectId: pid,
      promptUid,
      version,
      chunks: chunkRows,
      events: eventRows,
      attachments: attachmentRows,
      gaps: detectGaps(version, chunkRows, eventRows, attachmentRows),
      classification: classifyRequirementText(classifierText),
    });
  } catch (error: any) {
    return NextResponse.json({ success: false, error: error.message }, { status: 500 });
  }
}
