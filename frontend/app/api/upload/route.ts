import { NextRequest, NextResponse } from 'next/server'
import { writeFile, unlink } from 'fs/promises'
import { join } from 'path'
import { createReadStream } from 'fs'
import FormData from 'form-data'
import fetch from 'node-fetch'
import { buildApiUrl } from '@/app/lib/config'

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData()
    const file: File | null = formData.get('file') as unknown as File


    if (!file || !file.name) {
      console.error('No file in request')
      return NextResponse.json(
        { error: 'No file uploaded' },
        { status: 400 }
      )
    }

    // Convert to Buffer
    const arrayBuffer = await file.arrayBuffer()
    const buffer = Buffer.from(arrayBuffer)

    // Create temporary file
    const filename = file.name
    const filepath = join('/tmp', `${Date.now()}-${filename}`)
    
    // Save file
    await writeFile(filepath, buffer)

    // Prepare form data for FastAPI server
    const apiFormData = new FormData()
    apiFormData.append('file', createReadStream(filepath), filename)

    const response = await fetch(buildApiUrl('/upload-image'), {
      method: 'POST',
      body: apiFormData,
    })

    if (!response.ok) {
      throw new Error(`FastAPI server responded with status: ${response.status}`)
    }

    const result = await response.json()

    if (!result.image_id) {
      throw new Error('No image ID received from server')
    }

    // Clean up temporary file
    try {
      await unlink(filepath)
    } catch (error) {
      console.error('Error deleting temporary file:', error)
    }

    return NextResponse.json({
      imageId: result.image_id,
      s3Url: result.s3_url,
      crewResult: result.crew_result
    })

  } catch (error) {
    console.error('Error in upload handler:', error)
    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'Error processing upload' },
      { status: 500 }
    )
  }
}