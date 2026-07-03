import { BigQuery } from '@google-cloud/bigquery';
import { NextRequest, NextResponse } from 'next/server';

export const dynamic = 'force-dynamic';

export async function GET(req: NextRequest) {
  const { searchParams } = new URL(req.url);
  const promptId = searchParams.get('promptId') || '3381323161097207808';

  try {
    const bq = new BigQuery();

    // 1. Fetch Candidates
    const queryCandidates = `
      SELECT requirement_category, line_text
      FROM \`ctoteam.prism_requirement_intelligence.requirement_candidates\`
      WHERE prompt_id = @promptId AND noise_type = 'TRUE_REQUIREMENT' AND line_text IS NOT NULL AND TRIM(line_text) != ''
      LIMIT 100
    `;
    const [candidateRows] = await bq.query({
      query: queryCandidates,
      params: { promptId },
    });

    // 2. Fetch Traceability mapped rows
    const queryTrace = `
      SELECT requirement_id, requirement_text, implementation_file, status, gap_text, risk_level
      FROM \`ctoteam.prism_sentinel_audit.requirement_traceability\`
      WHERE audit_run_id = 'audit-5de9f124'
    `;
    const [traceRows] = await bq.query({ query: queryTrace });

    return NextResponse.json({
      status: 'success',
      promptId,
      candidates: candidateRows,
      traces: traceRows,
    });
  } catch (err: any) {
    console.error('BigQuery Trace Mapping query failed:', err);
    return NextResponse.json(
      { status: 'error', message: err.message },
      { status: 500 }
    );
  }
}
