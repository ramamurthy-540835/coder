import { BigQuery } from '@google-cloud/bigquery';

export function projectId() {
  return process.env.GCP_PROJECT_ID || process.env.GOOGLE_CLOUD_PROJECT || 'ctoteam';
}

export function bigqueryClient() {
  return new BigQuery({ projectId: projectId() });
}

export function classifyRequirementText(text: string) {
  const normalized = text.toLowerCase();
  const categories: Record<string, string[]> = {
    business_requirement: ['business', 'stakeholder', 'workflow', 'process', 'customer', 'user story', 'acceptance'],
    technical_requirement: ['api', 'service', 'database', 'schema', 'architecture', 'integration', 'code', 'backend', 'frontend'],
    data_requirement: ['bigquery', 'table', 'dataset', 'pipeline', 'etl', 'gcs', 'csv', 'json', 'data'],
    security_compliance: ['security', 'iam', 'secret', 'token', 'credential', 'compliance', 'audit', 'permission'],
    deployment_operational: ['deploy', 'cloud run', 'gcp', 'terraform', 'release', 'environment', 'monitoring', 'logging'],
    testing_acceptance: ['test', 'qa', 'validation', 'verify', 'acceptance criteria', 'unit test', 'integration test'],
  };
  const gaps: Record<string, string[]> = {
    missing_acceptance_criteria: ['acceptance', 'done when', 'success criteria'],
    missing_security_requirements: ['security', 'iam', 'permission', 'secret', 'compliance'],
    missing_test_requirements: ['test', 'validation', 'verify', 'qa'],
    missing_deployment_requirements: ['deploy', 'release', 'environment', 'cloud run', 'gcp'],
  };

  const matchedCategories: string[] = [];
  const evidence: string[] = [];
  Object.entries(categories).forEach(([category, keywords]) => {
    const hits = keywords.filter((keyword) => normalized.includes(keyword));
    if (hits.length) {
      matchedCategories.push(category);
      evidence.push(`${category}: ${hits.slice(0, 4).join(', ')}`);
    }
  });

  const missingRequirementSignals = Object.entries(gaps)
    .filter(([, keywords]) => !keywords.some((keyword) => normalized.includes(keyword)))
    .map(([gap]) => gap);

  if (!matchedCategories.length) {
    return {
      categories: ['unknown_or_needs_triage'],
      confidence: 0.35,
      missingRequirementSignals,
      evidence: ['No strong deterministic category keywords found.'],
    };
  }

  return {
    categories: matchedCategories,
    confidence: Math.min(0.9, 0.45 + matchedCategories.length * 0.1),
    missingRequirementSignals,
    evidence,
  };
}

export function detectGaps(version: any, chunks: any[], events: any[], attachments: any[] = []) {
  const gaps = [];
  if (!version) {
    return [{ code: 'missing_current_version', severity: 'high', message: 'No current prompt_versions row found.' }];
  }
  const expectedChunks = Number(version.chunk_count || 0);
  const actualChunks = chunks.length;
  if (expectedChunks !== actualChunks) {
    gaps.push({
      code: 'chunk_count_mismatch',
      severity: expectedChunks > actualChunks ? 'high' : 'medium',
      message: `Expected ${expectedChunks} chunks, found ${actualChunks} registered chunk rows.`,
    });
  }
  if (Number(version.extracted_chars || 0) === 0) {
    gaps.push({ code: 'empty_extraction', severity: 'high', message: 'Current version has zero extracted characters.' });
  }
  if (version.status !== 'success') {
    gaps.push({ code: 'non_success_status', severity: 'high', message: `Current version status is ${version.status}.` });
  }
  if (!version.gold_gcs_uri) {
    gaps.push({ code: 'missing_gold_uri', severity: 'medium', message: 'No gold artifact URI is registered.' });
  }
  if (!events.some((event) => event.event_type === 'completed')) {
    gaps.push({ code: 'missing_completed_event', severity: 'medium', message: 'No completed lifecycle event found.' });
  }
  const expectedAttachments = Number(version.text_attachment_count || 0) + Number(version.binary_attachment_count || 0);
  if (expectedAttachments !== attachments.length) {
    gaps.push({
      code: 'attachment_count_mismatch',
      severity: 'medium',
      message: `Expected ${expectedAttachments} attachments, found ${attachments.length} registered attachment rows.`,
    });
  }
  return gaps;
}
