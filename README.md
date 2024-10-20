<a id="readme-top"></a>
<h1>LifeStoryteller</h1>

<div align="left">
  <p>
   LifeStoryteller is a web application designed to help users upload photos, generate albums and videos, and view all their cherished memories in one place. With the ability to create albums and videos based on themes or specific images, LifeStoryteller makes it easy to organize and revisit special moments.
</div>


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
**・Photo Upload** : xxx

<img width="1438" alt="Screenshot 2024-02-10 at 4 49 27 PM" src="https://github.com/asakohayase/Hipnode-SocialMedia/assets/76857882/51f134e8-d0b4-49e6-ba23-caca66440b1c">
<br />
<br />

**・Album Generation** : Create photo albums using themes you describe in natural language, or let the uploaded images guide the album’s story.

<img width="1430" alt="Screenshot 2024-02-10 at 5 02 11 PM" src="https://github.com/asakohayase/Hipnode-SocialMedia/assets/76857882/54038089-f2cf-42d9-b342-e9220cf844ea">
<br />
<br />

**・Video Creation** : Generate videos from the generated photo albums.

<img width="1432" alt="Screenshot 2024-02-10 at 4 50 27 PM" src="https://github.com/asakohayase/Hipnode-SocialMedia/assets/76857882/43941387-ed32-41e9-8f75-0ab7db3ac91c">
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
   git clone https://github.com/asakohayase/ai_youtube_quiz_generator
   ```
2. Install dependencies
   ```sh
   poetry install
   npm install
   ```
   
3. Enter your API key in `.env` 
   * frontend
   ```js
   MONGODB_URI=
   S3_BUCKET_NAME=
   BACKEND_URL=
   ```
   * backend
   ```js
   OPENAI_API_KEY=sk-proj-WHJrxZEe41s97p05k3XhT3BlbkFJUYTD0NyRT3PDbSwCoyTa
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
5.  


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


