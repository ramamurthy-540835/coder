import { Storage } from '@google-cloud/storage';
import { NextRequest, NextResponse } from 'next/server';

export const dynamic = 'force-dynamic';

export async function GET(req: NextRequest) {
  const { searchParams } = new URL(req.url);
  const promptId = searchParams.get('promptId');
  const downloadPath = searchParams.get('downloadPath');

  try {
    const storage = new Storage();
    const bucketName = 'agentproject';
    const bucket = storage.bucket(bucketName);

    // Case 1: Secure Download/View Proxy
    if (downloadPath) {
      // Validate requested path is restricted to prompts/ folder for security
      if (!downloadPath.startsWith('prompts/')) {
        return NextResponse.json({ error: 'Access Denied: Path restricted.' }, { status: 403 });
      }

      const file = bucket.file(downloadPath);
      const [exists] = await file.exists();
      if (!exists) {
        return NextResponse.json({ error: 'File not found' }, { status: 404 });
      }

      const [metadata] = await file.getMetadata();
      const stream = file.createReadStream();

      // Convert stream to ReadableStream for Next.js response streaming
      const readableStream = new ReadableStream({
        start(controller) {
          stream.on('data', (chunk) => controller.enqueue(chunk));
          stream.on('end', () => controller.close());
          stream.on('error', (err) => controller.error(err));
        },
      });

      const isZip = downloadPath.endsWith('.zip');
      return new Response(readableStream, {
        headers: {
          'Content-Type': isZip ? 'application/zip' : 'text/plain; charset=utf-8',
          'Content-Disposition': `attachment; filename="${pathBaseline(downloadPath)}"`,
        },
      });
    }

    // Case 2: List GCS Files for the Prompt
    if (!promptId) {
      return NextResponse.json({ error: 'Missing promptId parameter' }, { status: 400 });
    }

    const prefix = `prompts/${promptId}/`;
    const [files] = await bucket.getFiles({ prefix });

    const fileList = files.map((file) => ({
      name: file.name,
      size: file.metadata.size,
      updated: file.metadata.updated,
      contentType: file.metadata.contentType,
    }));

    return NextResponse.json({
      status: 'success',
      promptId,
      files: fileList,
    });
  } catch (err: any) {
    console.error('Failed to interface with GCS Store:', err);
    return NextResponse.json({ status: 'error', message: err.message }, { status: 500 });
  }
}

function pathBaseline(filePath: string) {
  const parts = filePath.split('/');
  return parts[parts.length - 1];
}
