import type { NextApiRequest, NextApiResponse } from 'next';
import { IncomingForm, Fields, Files } from 'formidable';
import fetch, { Response } from 'node-fetch';
import fs from 'fs';
import FormData from 'form-data';

export const config = {
  api: {
    bodyParser: false,
  },
};

const parseForm = (req: NextApiRequest): Promise<{ fields: Fields; files: Files }> => {
  const form = new IncomingForm();
  return new Promise((resolve, reject) => {
    form.parse(req, (err, fields, files) => {
      if (err) return reject(err);
      resolve({ fields, files });
    });
  });
};

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method === 'POST') {
    try {
      console.log('Received POST request to /api/generate-album');
      const { fields, files } = await parseForm(req);
      console.log('Parsed form data:', { fields, files: Object.keys(files) });

      const theme = fields.theme?.[0];
      const imageFile = files.image?.[0];

      console.log('Extracted data:', { 
        theme, 
        imageFile: imageFile ? {
          filepath: imageFile.filepath,
          originalFilename: imageFile.originalFilename,
          mimetype: imageFile.mimetype
        } : 'Not present' 
      });

      if (!theme && !imageFile) {
        console.log('Error: Neither theme nor image provided');
        return res.status(400).json({ error: 'Please provide either a theme or an image' });
      }

      let response: Response;
      const formData = new FormData();

      if (imageFile) {
        console.log('Sending image-based request');
        const fileStream = fs.createReadStream(imageFile.filepath);
        formData.append('image', fileStream, {
          filename: imageFile.originalFilename || 'image.jpg',
          contentType: imageFile.mimetype || 'image/jpeg',
        });
        console.log('Sending form-data with image');
      } else if (theme) {
        console.log('Sending theme-based request');
        formData.append('theme', theme);
        console.log('Sending form-data with theme');
      }

      console.log('FormData headers:', formData.getHeaders());

      response = await fetch('http://127.0.0.1:8000/generate-album', {
        method: 'POST',
        body: formData,
        headers: formData.getHeaders(),
      });

      console.log('Response status:', response.status);
      console.log('Response headers:', Object.fromEntries(response.headers.entries()));

      const responseText = await response.text();
      console.log('Raw response text:', responseText);

      let data;
      try {
        data = JSON.parse(responseText);
      } catch (error) {
        console.error('Failed to parse response as JSON:', error);
        data = { error: 'Invalid JSON response from server' };
      }

      console.log('Parsed response data:', data);
      res.status(response.status).json(data);

      if (imageFile) {
        fs.unlink(imageFile.filepath, (err) => {
          if (err) console.error('Error deleting temp file:', err);
        });
      }
    } catch (error) {
      console.error('Error generating album:', error);
      res.status(500).json({ error: 'Error generating album', details: error instanceof Error ? error.message : String(error) });
    }
  } else {
    res.setHeader('Allow', ['POST']);
    res.status(405).end(`Method ${req.method} Not Allowed`);
  }
}