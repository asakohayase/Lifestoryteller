import { NextRequest, NextResponse } from 'next/server';
import fetch from 'node-fetch';
import { writeFile, unlink } from 'fs/promises';
import { join } from 'path';
import FormData from 'form-data';
import { createReadStream } from 'fs';

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData();
    const theme = formData.get('theme') as string | null;
    const imageFile = formData.get('image') as File | null;

    if (!theme && !imageFile) {
      return NextResponse.json(
        { error: 'Please provide either a theme or an image' },
        { status: 400 }
      );
    }

    // Prepare form data for FastAPI server
    const apiFormData = new FormData();

    if (imageFile) {
      // Save the file temporarily
      const buffer = Buffer.from(await imageFile.arrayBuffer());
      const filepath = join('/tmp', `${Date.now()}-${imageFile.name}`);
      await writeFile(filepath, buffer);

      // Add to form data
      apiFormData.append('image', createReadStream(filepath), {
        filename: imageFile.name,
        contentType: imageFile.type || 'image/jpeg',
      });

      try {
        const response = await fetch('http://127.0.0.1:8000/generate-album', {
          method: 'POST',
          body: apiFormData,
          headers: apiFormData.getHeaders(),
        });

        const data = await response.json();

        // Clean up temporary file
        await unlink(filepath);

        return NextResponse.json(data, { status: response.status });
      } catch (error) {
        // Clean up temporary file in case of error
        await unlink(filepath).catch(console.error);
        throw error;
      }
    } else if (theme) {
      apiFormData.append('theme', theme);

      const response = await fetch('http://127.0.0.1:8000/generate-album', {
        method: 'POST',
        body: apiFormData,
        headers: apiFormData.getHeaders(),
      });

      const data = await response.json();
      return NextResponse.json(data, { status: response.status });
    }

  } catch (error) {
    console.error('Error in generate album:', error);
    return NextResponse.json(
      { 
        error: 'Error generating album', 
        details: error instanceof Error ? error.message : 'Unknown error' 
      }, 
      { status: 500 }
    );
  }
}