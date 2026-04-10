# General Information

This coding challenge is designed to evaluate your ability to work across both the frontend and backend of a simple application. The goal is not to produce a perfect or production-ready system, but to demonstrate clear thinking, clean code organization, and familiarity with common development patterns.

The solution should be implemented using:

- **Angular** for the frontend
- **Python Flask** for the backend

The challenge is intended to take **around 2 hours**, but you may spend additional time if you want.

When submitting your solution, please include:

- A **README** with clear setup and run instructions
  - How to install dependencies
  - How to run the backend server
  - How to run the frontend application
  - Any environment variables or config required
- Any notes, assumptions, or design decisions you feel are relevant

Your submission should reflect:

- Understanding of core Angular concepts (components, services, routing, bindings)
- Ability to build and interact with a backend API
- Clean, maintainable, and well-organized code
- Basic user interface design considerations
- Separation of concerns between frontend and backend logic

## Dataset Description

You are provided with two CSV files representing movie rating catalog.
Your backend should use these files as your data source.

Below is the full schema and explanation of both CSVs.

- movies.csv

Contains movie related information.

| Column Name | Type         | Description              |
| ----------- | ------------ | ------------------------ |
| movieId     | integer (PK) | Unique ID for each movie |
| title       | string       | Movie name               |
| genres      | string       | Genre for movie          |

- ratings.csv

Contains movie ratings.

| Column Name | Type    | Description                                             |
| ----------- | ------- | ------------------------------------------------------- |
| userId      | integer | User ID                                                 |
| movieId     | integer | Movie ID                                                |
| rating      | float   | Rating for each movie per user                          |
| timestamp   | integer | Unix timestamp indicating when the user rated the movie |

- ratings_sample.csv

Similar to ratings.csv but contains only initial records. Use it only for reference purpose.

## Backend

Build a simple Flask backend service that exposes API endpoints used by the Angular frontend.
You will be provided with a **CSV file containing sample data**. Your backend should load this CSV and treat it as your data source.

### 1. Implement API Endpoints

Do preliminary data analysis and create a list of movies with the following criteria -

- More than 10,000 ratings
- Average rating > 4.0

Your backend should expose the following types of endpoints:

#### **GET Endpoint(s)**

### A. Movies With High Rating Activity

Return movies that meet BOTH conditions:

- More than 10,000 ratings
- Average rating > 4.0

A sample expected processed structure is provided in `output_sample.json`.

### B. Movie Details by Name

Given a movie name (query parameter), return:

- Genre(s)
- Release year (extract from title)
- Number of users who rated the movie
- Average rating

### Search / Filtering Endpoint

Support optional query parameters such as:

- Movie Name
- Genre
- Year
- Rating

## Frontend

Build a small Angular application that demonstrates foundational skills.

### 1. Fetch Data From an API

- Create a service that retrieves data from a backend API endpoint (using the backend portion of the task).

### 2. Display the Data

- Show the retrieved data in a list, use the movie name as the displayed value.
- Use any layout or styling that presents the list clearly and cleanly.

### 3. Search & Filter

- Provide the ability to search and/or filter the list.
- Search based on movie name.
- Filters should correspond to the attributes returned by the backend endpoints (e.g., movie name, genre, release year, average rating).

### 4. Item Details

- Allow selecting movie from the list to view additional details.
- Display the information returned by the backend for that movie (e.g., genre, release year, number of ratings, average rating).
