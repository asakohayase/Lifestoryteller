import type { NextApiRequest, NextApiResponse } from 'next'
import { IncomingForm, Fields, Files } from 'formidable'
import fs from 'fs'
import fetch from 'node-fetch'
import FormData from 'form-data'
import path from 'path'

export const config = {
  api: {
    bodyParser: false,
  },
}

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  console.log("API route /api/upload called");
  if (req.method === 'POST') {
    const form = new IncomingForm()
    form.parse(req, async (err: Error | null, fields: Fields, files: Files) => {
      console.log("Form parsed", { err, fields, files });
      if (err) {
        console.error("Error parsing form", err);
        return res.status(500).json({ error: 'Error parsing form data' })
      }

      const file = files.file && Array.isArray(files.file) ? files.file[0] : files.file;
      if (!file) {
        console.error("No file uploaded");
        return res.status(400).json({ error: 'No file uploaded' })
      }

      const formData = new FormData()
      const filename = file.originalFilename || path.basename(file.filepath);
      formData.append('file', fs.createReadStream(file.filepath), filename)

      try {
        const response = await fetch('http://127.0.0.1:8000/upload-image', {
          method: 'POST',
          body: formData,
        });
      
        console.log("Response received", { status: response.status });
      
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
      
        const result = await response.json();
        console.log("Result", result);
      
        if (!result.image_id) {
          throw new Error('No image ID received from server');
        }
      
        res.status(200).json({ 
          imageId: result.image_id,
          s3Url: result.s3_url,
          crewResult: result.crew_result
        });
      } catch (error) {
        console.error('Error uploading to FastAPI server:', error);
        res.status(500).json({ error: 'Error uploading to FastAPI server' });
      }finally {
        // Clean up the temporary file
        fs.unlink(file.filepath, (err) => {
          if (err) console.error('Error deleting temporary file:', err);
        });
      }
    })
  } else {
    res.setHeader('Allow', ['POST'])
    res.status(405).end(`Method ${req.method} Not Allowed`)
  }
}