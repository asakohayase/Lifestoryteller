// 'use server'

// import { revalidatePath } from 'next/cache'

// export async function uploadPhoto(formData: FormData) {
//   console.log('Attempting to upload photo...');
//   try {
//     console.log('FormData contents:');
//     formData.forEach((value, key) => {
//       if (typeof value === 'object' && value !== null && 'name' in value) {
//         console.log(key, 'File:', (value as { name: string }).name);
//       } else {
//         console.log(key, typeof value, value);
//       }
//     });

//     // Make sure the file field name matches what your server expects
//     const file = formData.get('file');
//     if (!file || (typeof file === 'object' && !('name' in file))) {
//       throw new Error('No file selected or invalid file');
//     }
  

//     const response = await fetch('http://127.0.0.1:8000/upload-image', {
//       method: 'POST',
//       body: formData,
//     });

//     console.log('Response status:', response.status);
//     console.log('Response headers:', response.headers);

//     const responseText = await response.text();
//     console.log('Response body:', responseText);

//     if (!response.ok) {
//       throw new Error(`Failed to upload image: ${response.status} ${responseText}`);
//     }

//     const result = JSON.parse(responseText);
//     revalidatePath('/');
//     return result;
//   } catch (error) {
//     console.error('Error in uploadPhoto:', error);
//     throw error;
//   }
// }

// export async function generateAlbum(theme: string) {
//   const response = await fetch('http://localhost:8000/generate-album', {
//     method: 'POST',
//     headers: {
//       'Content-Type': 'application/json',
//     },
//     body: JSON.stringify({ theme }),
//   });

//   if (!response.ok) {
//     throw new Error('Failed to generate album');
//   }

//   const result = await response.json();
//   revalidatePath('/');
//   return result;
// }