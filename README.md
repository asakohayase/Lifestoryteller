<a id="readme-top"></a>
<h1>LifeStoryteller</h1>

<div align="left">
  <p>
   LifeStoryteller is a web application designed to help users upload photos, generate albums and videos, and view all their cherished memories in one place. With the ability to create albums and videos based on themes or specific images, LifeStoryteller makes it easy to organize and revisit special moments.
</div>

<img width="828" alt="Screenshot 2024-10-20 at 11 40 57 PM" src="https://github.com/user-attachments/assets/0c0180d5-182b-4fa5-8396-46e0eb547ae4">


<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li><a href="#features">Features</a> </li>
    <li><a href="#built-with">Built With</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#contact">Contact</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## Features
**・Photo Upload** : Select or drag & drop a photo from your folder to upload.

<img width="609" alt="Screenshot 2024-10-20 at 11 37 25 PM" src="https://github.com/user-attachments/assets/da689a93-0e81-4b60-9aef-2be53f98a5b8">
<br />
<br />

**・Album Generation** : Create photo albums using themes you describe in natural language, or let the uploaded images guide the album’s story.

<img width="607" alt="Screenshot 2024-10-20 at 11 37 41 PM" src="https://github.com/user-attachments/assets/76d73aaa-5730-437f-9937-bfcd7017a591">
<br />
<br />

**・Video Creation** : Generate videos from the generated photo albums.

<img width="688" alt="Screenshot 2024-10-20 at 11 38 43 PM" src="https://github.com/user-attachments/assets/f333a73a-1ded-4326-86cb-aaf482679284">
<br />
<br />




## Built With

* Frontend - Next.js, Typescript and Tailwind CSS
* Backend - Python and Fast API
* Storage - Mongo DB for storing photo and album metadata, AWS S3 for image storage and Qdrant for vector store
* Others - CrewAI for image upload and album creation tasks

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- GETTING STARTED -->
## Getting Started

### Prerequisites

- Docker and Docker Compose
- Git
- Node.js (for local development)

### Installation

1. Clone the repository and navigate to the directory:
```bash
git clone https://github.com/asakohayase/Lifestoryteller.git
cd Lifestoryteller
```

2. Create `.env.frontend`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
BACKEND_URL=http://backend:8000
```

3. Create `.env.backend`:
```env
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key

# MongoDB Configuration
MONGODB_URI=your_mongodb_uri  # Change your_mongodb_uri

# MinIO (S3) Configuration
AWS_ACCESS_KEY_ID=minio
AWS_SECRET_ACCESS_KEY=minio123
AWS_REGION=us-east-1
S3_BUCKET_NAME=your-bucket-name  # Change your-bucket-name
S3_ENDPOINT_URL=http://minio:9000

# Qdrant Configuration
QDRANT_HOST=qdrant
QDRANT_PORT=6333
QDRANT_COLLECTION_NAME=your_collection_name  # Change your_collection_name
```

### Running with Docker

1. Build and start all services:
```bash
docker compose up --build
```

2. Or build and run in detached mode (background):
```bash
docker compose up -d --build
```

3. View running containers:
```bash
docker ps
```

4. View logs:
```bash
# All containers
docker compose logs

# Specific service
docker compose logs backend
docker compose logs frontend
```

5. Stop services:
```bash
docker compose down
```

### MinIO Setup (Required after first run)

1. **Backend Configuration** (in `.env.backend`):
```env
# MinIO (S3) Configuration
S3_ENDPOINT_URL=http://minio:9000  # API endpoint for file operations
AWS_ACCESS_KEY_ID=minio
AWS_SECRET_ACCESS_KEY=minio123
S3_BUCKET_NAME=your-bucket-name
```

2. **Create Bucket using MinIO Console**:
   - Access MinIO Console at http://localhost:9001 (Web management interface)
   - Login with default credentials:
     - Username: minio
     - Password: minio123
   - Create a new bucket matching your S3_BUCKET_NAME

Note: The different ports are used for:
- Port 9000: S3 API endpoint (used by the backend)
- Port 9001: Web Console interface (used for bucket management)

### Name Constraints

When choosing names for your collections and bucket:

1. Database Name:
   - Lowercase letters, numbers, and underscores
   - Example: `photo_gallery`, `my_family_photos`

2. Bucket Name:
   - Lowercase letters, numbers, hyphens
   - Must start and end with letter or number
   - Example: `family-photos`, `my-memories-2024`

3. Qdrant Collection Name:
   - Alphanumeric characters and underscores
   - Example: `image_vectors`, `photo_embeddings`

### Troubleshooting

1. If containers aren't starting:
```bash
# Check container status
docker ps -a

# Check detailed logs
docker compose logs
```

2. To reset data and start fresh:
```bash
# Stop containers and remove volumes
docker compose down -v

# Rebuild and start
docker compose up --build
```

3. To restart a specific service:
```bash
docker compose restart backend
```

The application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- MinIO Console: http://localhost:9001
   

<!-- CONTRIBUTING -->
## Contributing

If you have an idea to improve this, kindly fork the repository and open a pull request. We also welcome enhancement suggestions filed as issues. 
Stars ⭐ from you will brighten our day! Thanks for checking out our project.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/NewFeature`)
3. Commit your Changes (`git commit -m 'Add some NewFeature'`)
4. Push to the Branch (`git push origin feature/NewFeature`)
5. Open a Pull Request





<!-- CONTACT -->
## Contact

Asako Hayase- [LinkedIn](https://www.linkedin.com/in/asako-hayase-924508ba/)


