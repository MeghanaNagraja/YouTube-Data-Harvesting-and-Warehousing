# Problem Statement:

to create a Streamlit application that allows users to access and analyze data from multiple YouTube channels.

    - Ability to input a YouTube channel ID and retrieve all the relevant data (Channel name, subscribers, total video count, playlist ID, video ID, likes, dislikes, comments of each video) using Google API.
    - Option to store the data in a MongoDB database as a data lake.
    - Ability to collect data for up to 10 different YouTube channels and store them in the data lake by clicking a button.
    - Option to select a channel name and migrate its data from the data lake to a SQL database as tables.
    - Ability to search and retrieve data from the SQL database using different search options, including joining tables to get channel details.


# Approach:

    - Connecting to youtube API
    - Creating streamlit dashboard
    - Collecting data
    - Uploading to MongoDB
    - Migrate to SQL
    - Getting insights from data

# Requirements:
    - Pandas
    - Streamlit
    - Pymongo
    - MySQL connector
    - Google API Client

## Connecting to youtube API

YouTube API is used to retrieve channel and video data. Google API client library is used to make requests to the API.
![yt](https://github.com/MeghanaNagraja/YouTube-Data-Harvesting-and-Warehousing/assets/122547199/016a4251-165d-4445-ba3e-e5eae3bdddc2

## Creating streamlit dashboard

![img2](https://github.com/MeghanaNagraja/YouTube-Data-Harvesting-and-Warehousing/assets/122547199/08f5a6f7-735c-431b-90bd-66740c0f80d9)
Streamlit is to create a simple UI where users can enter a YouTube channel ID, view the channel details, and select channels to migrate to the data warehouse and to SQL,  SQL queries are used to get insights from the data.

## Collecting data and Uploading to MongoDB

Once we retrieve the data from the YouTube API (using youtube API reference), we can store it in a MongoDB data lake. MongoDB is a great choice for a data lake because it can handle unstructured and semi-structured data easily.

## Migrate to SQL

![img1](https://github.com/MeghanaNagraja/YouTube-Data-Harvesting-and-Warehousing/assets/122547199/7023aaef-f773-4468-9d89-b081b8b5bcb9)
After we've collected data for multiple channels, we can migrate it to a SQL data warehouse. SQL database MySQL is used for this.

## Getting insights from data

![img3](https://github.com/MeghanaNagraja/YouTube-Data-Harvesting-and-Warehousing/assets/122547199/bb8b1362-15a1-4e34-b22b-b97c90f55df2)
We can use SQL queries to join the tables in the SQL data warehouse and retrieve data for specific channels based on user input.
