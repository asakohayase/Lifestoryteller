/** @type {import('next').NextConfig} */
// const nextConfig = {
//   images: {
//     remotePatterns: [
//       {
//         protocol: 'https',
//         hostname: `${process.env.S3_BUCKET_NAME}.s3.amazonaws.com`,
//         port: '',
//         pathname: '/**',
//       },
//     ],
//   },
// };

const nextConfig = {
  images: {
    domains: ['localhost', 'minio'],  
    remotePatterns: [
      {
        protocol: 'http',
        hostname: '**',  
        port: '9000',
        pathname: '/**',
      }
    ],
  },
};

export default nextConfig;
