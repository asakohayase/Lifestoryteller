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
* Storage - Mongo DB for storing photo and album metadata, AWS S3 for image storage and Qdrant for vector search
* Others - CrewAI for image upload and album creation tasks

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- GETTING STARTED -->
## Getting Started

To get a local copy up and running follow these simple example steps.

### Installation
   
1. Clone the repo
   ```sh
   git clone https://github.com/asakohayase/Lifestoryteller
   ```
2. Install dependencies
   ```sh
   poetry install
   npm install
   ```
   
3. Create `.env` 
   * frontend
   ```js
   MONGODB_URI=
   S3_BUCKET_NAME=
   BACKEND_URL=
   ```
   * backend
   ```js
   OPENAI_API_KEY=
   MONGODB_URI=
   AWS_ACCESS_KEY_ID=
   AWS_SECRET_ACCESS_KEY=
   AWS_REGION=
   S3_BUCKET_NAME=
   QDRANT_COLLECTION_NAME=
   ```

4. Activate the virtual environment
   ```sh
   poetry shell
   ```
5.  Set the path to the virtual environment to Python Interpreter
6.  To run the app
   
   * Activate Qdrant
   ```sh
   docker volume create qdrant_data
   docker run -p 6333:6333 -v qdrant_data:/qdrant/storage qdrant/qdrant
   docker run -p 6333:6333 qdrant/qdrant
   ```
   * Activate MongoDB
   ```sh
   docker pull mongo
   docker run -d -p 27017:27017 --name mongodb mongo
   docker start mongodb
   ```
   * Activate uvicorn
   ```sh
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

   * Activate frontend
   ```sh
   npm run dev
   ```
   

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


