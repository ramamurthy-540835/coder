import { BigQuery } from '@google-cloud/bigquery';
import { NextRequest, NextResponse } from 'next/server';

export const dynamic = 'force-dynamic';

export async function GET() {
  try {
    const bq = new BigQuery();
    const query = `
      SELECT DISTINCT prompt_id
      FROM \`ctoteam.prism_requirement_intelligence.requirement_candidates\`
      WHERE prompt_id IS NOT NULL AND TRIM(prompt_id) != ''
      ORDER BY prompt_id DESC
      LIMIT 100
    `;
    const [rows] = await bq.query({ query });
    const promptIds = rows.map((r: any) => r.prompt_id);
    return NextResponse.json({ status: 'success', promptIds });
  } catch (err: any) {
    console.error('Failed to query BQ prompts:', err);
    return NextResponse.json({ status: 'error', message: err.message }, { status: 500 });
  }
}
