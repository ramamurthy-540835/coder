import { NextResponse } from 'next/server';
import crypto from 'crypto';
import { bigqueryClient, classifyRequirementText, projectId } from '../_lib';

const DATASET = 'prism_prompt_catalog';
const TABLE = 'prompt_submissions';

function cleanText(value: unknown, maxLen = 200000) {
  return typeof value === 'string' ? value.trim().slice(0, maxLen) : '';
}

async function ensureSubmissionsTable() {
  const bq = bigqueryClient();
  const dataset = bq.dataset(DATASET);
  const table = dataset.table(TABLE);
  const [exists] = await table.exists();
  if (exists) return;

  await dataset.createTable(TABLE, {
    schema: [
      { name: 'submission_id', type: 'STRING', mode: 'REQUIRED' },
      { name: 'prompt_uid', type: 'STRING', mode: 'REQUIRED' },
      { name: 'title', type: 'STRING' },
      { name: 'description', type: 'STRING' },
      { name: 'prompt_text', type: 'STRING', mode: 'REQUIRED' },
      { name: 'classification_json', type: 'STRING' },
      { name: 'categories', type: 'STRING', mode: 'REPEATED' },
      { name: 'protection_level', type: 'STRING', mode: 'REQUIRED' },
      { name: 'status', type: 'STRING', mode: 'REQUIRED' },
      { name: 'approved', type: 'BOOLEAN', mode: 'REQUIRED' },
      { name: 'submitted_by', type: 'STRING', mode: 'REQUIRED' },
      { name: 'source_system', type: 'STRING', mode: 'REQUIRED' },
      { name: 'raw_hash', type: 'STRING', mode: 'REQUIRED' },
      { name: 'prompt_chars', type: 'INTEGER', mode: 'REQUIRED' },
      { name: 'created_at', type: 'TIMESTAMP', mode: 'REQUIRED' },
      { name: 'updated_at', type: 'TIMESTAMP', mode: 'REQUIRED' },
    ],
    timePartitioning: { type: 'DAY', field: 'created_at' },
    clustering: { fields: ['prompt_uid', 'status', 'protection_level'] },
  });
}

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const promptText = cleanText(body.promptText);
    const title = cleanText(body.title, 500);
    const description = cleanText(body.description, 4000);
    const submittedBy = cleanText(body.submittedBy, 250) || 'unknown';
    const protectionLevel = ['none', 'internal', 'production', 'critical'].includes(body.protectionLevel)
      ? body.protectionLevel
      : 'internal';
    const status = ['draft', 'submitted', 'approved', 'protected'].includes(body.status)
      ? body.status
      : 'submitted';
    const approved = body.approved === true || status === 'approved' || status === 'protected';

    if (!promptText) {
      return NextResponse.json({ success: false, error: 'promptText is required.' }, { status: 400 });
    }

    const rawHash = crypto.createHash('sha256').update(promptText).digest('hex');
    const submissionId = crypto.randomUUID();
    const promptUid = cleanText(body.promptUid, 250) || `prism:${rawHash.slice(0, 16)}`;
    const now = new Date().toISOString();
    const classification = classifyRequirementText(`${title}\n${description}\n${promptText}`);

    await ensureSubmissionsTable();
    const bq = bigqueryClient();
    await bq.dataset(DATASET).table(TABLE).insert([
      {
        submission_id: submissionId,
        prompt_uid: promptUid,
        title,
        description,
        prompt_text: promptText,
        classification_json: JSON.stringify(classification),
        categories: classification.categories,
        protection_level: protectionLevel,
        status,
        approved,
        submitted_by: submittedBy,
        source_system: 'prism_ui',
        raw_hash: rawHash,
        prompt_chars: promptText.length,
        created_at: now,
        updated_at: now,
      },
    ]);

    return NextResponse.json({
      success: true,
      projectId: projectId(),
      submission: {
        submissionId,
        promptUid,
        title,
        status,
        protectionLevel,
        approved,
        rawHash,
        promptChars: promptText.length,
        classification,
      },
    });
  } catch (error: any) {
    return NextResponse.json({ success: false, error: error.message, details: error.errors }, { status: 500 });
  }
}
