import { NextResponse } from 'next/server';
import { classifyRequirementText } from '../_lib';

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const text = typeof body.text === 'string' ? body.text : '';
    return NextResponse.json({ success: true, classification: classifyRequirementText(text) });
  } catch (error: any) {
    return NextResponse.json({ success: false, error: error.message }, { status: 500 });
  }
}
