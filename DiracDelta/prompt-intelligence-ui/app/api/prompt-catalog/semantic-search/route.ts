import { NextResponse } from 'next/server';
import crypto from 'crypto';
import { bigqueryClient, projectId } from '../_lib';

const DATASET = 'prism_prompt_catalog';
const TABLE = 'prompt_semantic_memory';
const DIMENSIONS = 128;

function stableHash(text: string) {
  return crypto.createHash('sha256').update(text).digest('hex');
}

function embedding(text: string) {
  const vector = Array(DIMENSIONS).fill(0);
  const tokens = text.toLowerCase().replaceAll('_', ' ').split(/\s+/).filter(Boolean);
  for (const token of tokens) {
    const digest = crypto.createHash('sha256').update(token).digest();
    const index = digest.readUInt32BE(0) % DIMENSIONS;
    const sign = digest[4] % 2 === 0 ? 1 : -1;
    vector[index] += sign;
  }
  const norm = Math.sqrt(vector.reduce((sum, value) => sum + value * value, 0));
  return norm ? vector.map((value) => Number((value / norm).toFixed(8))) : vector;
}

function dot(left: number[], right: number[]) {
  if (!left.length || left.length !== right.length) return 0;
  return left.reduce((sum, value, index) => sum + value * Number(right[index] || 0), 0);
}

async function ensureSemanticTable() {
  const bq = bigqueryClient();
  const table = bq.dataset(DATASET).table(TABLE);
  const [exists] = await table.exists();
  if (exists) return;
  await bq.dataset(DATASET).createTable(TABLE, {
    schema: [
      { name: 'memory_id', type: 'STRING', mode: 'REQUIRED' },
      { name: 'source_type', type: 'STRING', mode: 'REQUIRED' },
      { name: 'source_id', type: 'STRING', mode: 'REQUIRED' },
      { name: 'prompt_uid', type: 'STRING', mode: 'REQUIRED' },
      { name: 'version_number', type: 'INT64' },
      { name: 'run_id', type: 'STRING' },
      { name: 'chunk_order', type: 'INT64' },
      { name: 'title', type: 'STRING' },
      { name: 'text', type: 'STRING', mode: 'REQUIRED' },
      { name: 'text_hash', type: 'STRING', mode: 'REQUIRED' },
      { name: 'embedding', type: 'FLOAT64', mode: 'REPEATED' },
      { name: 'embedding_model', type: 'STRING', mode: 'REQUIRED' },
      { name: 'categories', type: 'STRING', mode: 'REPEATED' },
      { name: 'protection_level', type: 'STRING' },
      { name: 'status', type: 'STRING' },
      { name: 'gcs_uri', type: 'STRING' },
      { name: 'created_at', type: 'TIMESTAMP', mode: 'REQUIRED' },
      { name: 'updated_at', type: 'TIMESTAMP', mode: 'REQUIRED' },
    ],
    timePartitioning: { type: 'DAY', field: 'created_at' },
    clustering: { fields: ['source_type', 'prompt_uid', 'status'] },
  });
}

async function indexSubmissions(limit = 100) {
  await ensureSemanticTable();
  const bq = bigqueryClient();
  const pid = projectId();
  const [submissionRows] = await bq.query({
    query: `
      SELECT submission_id, prompt_uid, title, prompt_text, categories, protection_level, status
      FROM \`${pid}.${DATASET}.prompt_submissions\`
      WHERE prompt_text IS NOT NULL AND prompt_text != ''
      ORDER BY created_at DESC
      LIMIT @limit;
    `,
    params: { limit: Math.max(1, Math.min(1000, limit)) },
  });
  if (!submissionRows.length) return 0;

  const [existingRows] = await bq.query({
    query: `SELECT text_hash FROM \`${pid}.${DATASET}.${TABLE}\` WHERE source_type = 'prompt_submission';`,
  });
  const existing = new Set(existingRows.map((row: any) => row.text_hash));
  const now = new Date().toISOString();
  const rows = submissionRows
    .map((row: any) => {
      const textHash = stableHash(row.prompt_text);
      if (existing.has(textHash)) return null;
      return {
        memory_id: crypto.randomUUID(),
        source_type: 'prompt_submission',
        source_id: row.submission_id,
        prompt_uid: row.prompt_uid,
        version_number: null,
        run_id: null,
        chunk_order: null,
        title: row.title,
        text: row.prompt_text,
        text_hash: textHash,
        embedding: embedding(row.prompt_text),
        embedding_model: 'local-hash-embedding-v1',
        categories: row.categories || [],
        protection_level: row.protection_level,
        status: row.status,
        gcs_uri: null,
        created_at: now,
        updated_at: now,
      };
    })
    .filter(Boolean);

  if (!rows.length) return 0;
  await bq.dataset(DATASET).table(TABLE).insert(rows);
  return rows.length;
}

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const query = typeof body.query === 'string' ? body.query.trim() : '';
    const limit = Math.max(1, Math.min(50, Number(body.limit || 8)));
    const shouldIndex = body.indexFirst !== false;
    if (!query) return NextResponse.json({ success: false, error: 'query is required.' }, { status: 400 });

    const indexedRows = shouldIndex ? await indexSubmissions(200) : 0;
    await ensureSemanticTable();
    const bq = bigqueryClient();
    const pid = projectId();
    const [rows] = await bq.query({
      query: `
        SELECT memory_id, source_type, prompt_uid, title, text, categories, protection_level, status, embedding, embedding_model, updated_at
        FROM \`${pid}.${DATASET}.${TABLE}\`
        WHERE ARRAY_LENGTH(embedding) = @dimensions
        ORDER BY updated_at DESC
        LIMIT 1000;
      `,
      params: { dimensions: DIMENSIONS },
    });
    const qv = embedding(query);
    const results = rows
      .map((row: any) => ({
        memoryId: row.memory_id,
        sourceType: row.source_type,
        promptUid: row.prompt_uid,
        title: row.title,
        textPreview: String(row.text || '').slice(0, 500),
        categories: row.categories || [],
        protectionLevel: row.protection_level,
        status: row.status,
        embeddingModel: row.embedding_model,
        similarity: Number(dot(qv, row.embedding).toFixed(6)),
      }))
      .sort((a: any, b: any) => b.similarity - a.similarity)
      .slice(0, limit);

    return NextResponse.json({ success: true, projectId: pid, indexedRows, results });
  } catch (error: any) {
    return NextResponse.json({ success: false, error: error.message, details: error.errors }, { status: 500 });
  }
}
