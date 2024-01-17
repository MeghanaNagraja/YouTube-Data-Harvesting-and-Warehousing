import pymongo
import isodate
import mysql.connector
import streamlit as st
import pandas as pd
from matplotlib import pyplot
from streamlit_option_menu import option_menu
from googleapiclient.discovery import build

# Youtube API creation 
api_key = 'APIKEY'
youtube = build('youtube', 'v3', developerKey=api_key)

# Connecting to MySQL
connection = mysql.connector.connect(host = 'localhost', password = 'password', user = 'root', database = 'youtube')
ytcursor = connection.cursor()

# Connecting to MongoDB
ytclient = pymongo.MongoClient("url")
ytdb = ytclient['youtube']
ytcollection = ytdb['channels']

#To retrieve channel's information:
def retrieve_channel_info(channel_id):
    res = youtube.channels().list(
        part="snippet,contentDetails,statistics",
        id=channel_id
    ).execute()
    channel_info = {
        'Channel_Name' : res['items'][0]['snippet'].get('title'),
        'Channel_Id' : res['items'][0].get('id'),
        'Subscription_Count' : res['items'][0]['statistics'].get('subscriberCount'),
        'Channel_Views' : res['items'][0]['statistics'].get('viewCount'),
        'Channel_Description' : res['items'][0]['snippet'].get('description'),
        'Playlist_Id' : res['items'][0]['contentDetails']['relatedPlaylists'].get('uploads')
    }
    return channel_info

#To retrieve playlists of the channel:
def retrieve_playlists(channel_id):
    playlists = {}
    next_page_token = None
    while True:
        res = youtube.playlists().list(
            part ='snippet,contentDetails',
            channelId=channel_id,
            maxResults = 50,
            pageToken = next_page_token
        ).execute()
        for i in (res['items']):
            per_playlist_info = {
                'Channel_Id':i['snippet'].get('channelId'),
                'Playlist_Id':i.get('id'),
                'Playlist_Name':i['snippet'].get('title'),
                'Video_Count':i['contentDetails'].get('itemCount')
            }
            playlists[per_playlist_info['Playlist_Id']] = per_playlist_info
        next_page_token = res.get('nextPageToken')
        if next_page_token is None:
            break
    return playlists

#To retrieve video IDs of the channel:
def retrieve_video_ids(playlist_id):
    video_ids_list = []
    next_page_token = None
    while True:
        res = youtube.playlistItems().list(
            part ='snippet',
            playlistId = playlist_id,
            maxResults = 50,
            pageToken = next_page_token
        ).execute()
        for i in range(len(res['items'])):
            video_ids_list.append(res['items'][i]['snippet']['resourceId']['videoId'])
        next_page_token = res.get('nextPageToken')
        if next_page_token is None:
            break
    return video_ids_list

#To retrieve information of channels's all videos:
def retrieve_video_info(video_ids):
    video_info ={}
    for video in video_ids:
        res = youtube.videos().list(
            part = 'snippet,contentDetails,statistics',
            id = video
        ).execute()
        per_video_info = {
            'Channel_Id' : res['items'][0]['snippet'].get('channelId'),
            'Channel_Name' : res['items'][0]['snippet'].get('channelTitle'),
            'Video_Id': res['items'][0].get('id'),
            'Video_Name' : res['items'][0]['snippet'].get('title'),
            'Video_Description' : res['items'][0]['snippet'].get('description'),
            'Published_At' : res['items'][0]['snippet'].get('publishedAt').replace("T"," ").replace("Z",""),
            'View_Count' : res['items'][0]['statistics'].get('viewCount'),
            'Like_Count' : res['items'][0]['statistics'].get('likeCount'),
            'Dislike_Count' : res['items'][0]['statistics'].get('dislikeCount'),
            'Favorite_Count' : res['items'][0]['statistics'].get('favoriteCount'),
            'Comment_Count' : res['items'][0]['statistics'].get('commentCount'),
            'Duration' : isodate.parse_duration(res['items'][0]['contentDetails'].get('duration')).total_seconds(),
            'Thumbnail' : res['items'][0]['snippet']['thumbnails']['default'].get('url'),
            'Caption_Status' : res['items'][0]['contentDetails'].get('caption'),
        }
        video_info[per_video_info['Video_Id']] = per_video_info
    return video_info

#To retrieve comments of each video:
def retrieve_comment_info(video_info):
    comment_info = {}
    for i in video_info:  
        if video_info[i]['Comment_Count'] == None:
            pass
        elif video_info[i]['Comment_Count'] == '0':
            pass
        else:
            response = youtube.commentThreads().list(
                part = "snippet",
                videoId = video_info[i]['Video_Id'],
                maxResults = 50
            ).execute()
            for comment in response['items']:
                per_comment_info = {
                    'Video_Id' : comment['snippet']['videoId'],
                    'Comment_Id' : comment['snippet']['topLevelComment'].get('id'),
                    'Comment_Text' : comment['snippet']['topLevelComment']['snippet'].get('textOriginal'),
                    'Comment_Author' : comment['snippet']['topLevelComment']['snippet'].get('authorDisplayName'),
                    'Comment_PublishedAt' : comment['snippet']['topLevelComment']['snippet'].get('publishedAt').replace("T"," ").replace("Z","")
                }
                comment_info[per_comment_info['Comment_Id']] = per_comment_info
    return comment_info

#To retreive all information:
def retrieve_complete_channel_info(channel_id):
    channel_info = retrieve_channel_info(channel_id)
    playlist_id = channel_info['Playlist_Id']
    playlists = retrieve_playlists(channel_id)
    video_ids = retrieve_video_ids(playlist_id)
    video_info = retrieve_video_info(video_ids)
    video_info = retrieve_video_info(video_ids)
    comment_info = retrieve_comment_info(video_info)
    complete_channel_info = {'Channel_Info':channel_info, 'Playlist_Info':playlists, 'Video_Info':video_info, 'Comment_Info':comment_info}
    return complete_channel_info

#To create SQL tables:
def create_tables():
    ytcursor.execute('''CREATE TABLE IF NOT EXISTS channels(
        channel_name VARCHAR(255),
        channel_id VARCHAR(255) NOT NULL UNIQUE,
        subscription_count INT,
        channel_views INT,
        channel_description TEXT,
        playlist_id VARCHAR(255)          
    )''')
    ytcursor.execute('''CREATE TABLE IF NOT EXISTS playlists(
        channel_id VARCHAR(255),
        playlist_id VARCHAR(255) NOT NULL UNIQUE,
        playlist_name VARCHAR(255),
        video_count INT            
    )''')
    ytcursor.execute('''CREATE TABLE IF NOT EXISTS videos(
        channel_id VARCHAR(255),
        channel_name VARCHAR(255),                                
        video_id VARCHAR(255) NOT NULL UNIQUE,
        video_name VARCHAR(255),
        video_description TEXT,
        published_date TIMESTAMP,
        view_count INT,
        like_count INT,
        dislike_count INT,
        favourite_count INT,
        comment_count INT,
        duration INT,
        thumbnail VARCHAR(255),
        caption_status VARCHAR(255)               
    )''')
    ytcursor.execute('''CREATE TABLE IF NOT EXISTS comments(
        video_id VARCHAR(255),
        comment_id VARCHAR(255) NOT NULL UNIQUE,
        comment_text TEXT,
        comment_author VARCHAR(255),
        comment_published_date TIMESTAMP              
    )''')
    connection.commit()

#To create channels list
def create_channels_list():
    channels_list = []
    for doc in ytcollection.find({},{'_id':0,'Channel_Info':1}):
        channels_list.append(doc['Channel_Info']['Channel_Name'])
    return channels_list

#To upload to SQL database:
def upload_to_SQL(cha_info, play_info, vid_info, com_info):
    try:
        cha_list = []
        cha_list.append(cha_info)
        cha_df = pd.DataFrame(cha_list)
        for index,row in cha_df.iterrows():
            cha_query = '''INSERT INTO channels(
                channel_name,
                channel_id,
                subscription_count,
                channel_views,
                channel_description,
                playlist_id   
            ) 
            VALUES(%s,%s,%s,%s,%s,%s)'''
            cha_val = (
                row['Channel_Name'],
                row['Channel_Id'],
                row['Subscription_Count'],
                row['Channel_Views'],
                row['Channel_Description'],
                row['Playlist_Id']
            )
            ytcursor.execute(cha_query, cha_val)
            connection.commit()

        play_df = pd.DataFrame(play_info)
        for index,row in play_df.iterrows():
            play_query = '''INSERT INTO playlists(
                channel_id,
                playlist_id,
                playlist_name,
                video_count
            )
            VALUES(%s,%s,%s,%s)'''
            play_val = (
                row['Channel_Id'],
                row['Playlist_Id'],
                row['Playlist_Name'],
                row['Video_Count']
            )
            ytcursor.execute(play_query, play_val)
            connection.commit()

        vid_df = pd.DataFrame(vid_info)
        for index,row in vid_df.iterrows():
            vid_query = '''INSERT INTO videos(
                channel_id,
                channel_name,
                video_id,
                video_name,
                video_description,
                published_date,
                view_count,
                like_count,
                dislike_count,
                favourite_count,
                comment_count,
                duration,
                thumbnail,
                caption_status
            )
            VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'''
            vid_val = (
                row['Channel_Id'],
                row['Channel_Name'],
                row['Video_Id'],
                row['Video_Name'],
                row['Video_Description'],
                row['Published_At'],
                row['View_Count'],
                row['Like_Count'],
                row['Dislike_Count'],
                row['Favorite_Count'],
                row['Comment_Count'],
                row['Duration'],
                row['Thumbnail'],
                row['Caption_Status']
            )
            ytcursor.execute(vid_query, vid_val)
            connection.commit()

        com_df = pd.DataFrame(com_info)
        for index,row in com_df.iterrows():
            com_query = '''INSERT INTO comments(
                video_id,
                comment_id,
                comment_text,
                comment_author,
                comment_published_date
            )
            VALUES(%s,%s,%s,%s,%s)'''
            com_val = (
                row['Video_Id'],
                row['Comment_Id'],
                row['Comment_Text'],
                row['Comment_Author'],
                row['Comment_PublishedAt']
            )
            ytcursor.execute(com_query, com_val)
            connection.commit()
    except:
        st.error('values already existing')

#Building streamlit dashboard
with st.sidebar:
    st.title('YOUTUBE DATA HARVESTING AND WAREHOUSING')
    st.image('image.jpg', width = 450)
    select = option_menu(
        menu_title = "Home",
        options = ['Collect & store data to MongoDB','Migrate data to SQL warehouse','Data Insights & Visualisation'],
        default_index = 0
    )
    st.subheader('Technologies used:')
    st.caption('Python')
    st.caption('MongoDB & MySQL')
    st.caption('Streamlit')

#Uploading data to MongoDB
if select == 'Collect & store data to MongoDB':
    channel_id = st.text_input('Enter channel ID')
    if channel_id:
        output = retrieve_complete_channel_info(channel_id)
        st.dataframe(output['Channel_Info'])
        if st.button('Store Data in MongoDB'):
            ytcollection.insert_one(output)
            st.success("Data is stored")

#Uploading data to SQL
create_tables()
if select == 'Migrate data to SQL warehouse':
    selected_channel = st.selectbox('Select a channel',(create_channels_list()))
    if selected_channel:
        for doc in ytcollection.find({},{'_id':0, 'Channel_Info':1, 'Playlist_Info':1, 'Video_Info':1, 'Comment_Info':1}):
            if selected_channel == doc['Channel_Info']['Channel_Name']:
                if st.button('show tables'):
                    st.header('Channel_Info')
                    st.dataframe(doc['Channel_Info'])
                    st.header('Playlist_Info')
                    st.dataframe(list(doc['Playlist_Info'].values()))
                    st.header('Video_Info')
                    st.dataframe(list(doc['Video_Info'].values()))
                    st.header('Comment_Info')
                    st.dataframe(list(doc['Comment_Info'].values()))
                if st.button('migrate to SQL'):
                    upload_to_SQL(
                        cha_info = doc['Channel_Info'], 
                        play_info = list(doc['Playlist_Info'].values()), 
                        vid_info = list(doc['Video_Info'].values()), 
                        com_info = list(doc['Comment_Info'].values())
                    )
                    st.success("Data is migrated to SQL")

#Insights from the data:
if select == 'Data Insights & Visualisation':
    query = st.selectbox('Select a query',
        ('Names of all the videos',
        'Channels with most number of videos',
        'Top 10 most viewed videos',
        'Comments on each video',
        'Videos with highest number of likes',
        'Total number of likes and dislikes for each video',
        'Total number of views for each channel',
        'Channels that have published videos in 2022',
        'Average duration of all videos in each channel',
        'Videos with highest number of comments')
    )

    if query == 'Names of all the videos':
        ytcursor.execute(''' SELECT video_name AS video_name, channel_name AS channel_name
            FROM videos
            ORDER BY channel_name''')
        qdf = pd.DataFrame(ytcursor.fetchall(),columns = ytcursor.column_names)
        qdf.index+=1
        st.write(qdf)
    elif query == 'Channels with most number of videos':
        ytcursor.execute('''SELECT DISTINCT channel_name AS channel_name, 
            COUNT(*) OVER(PARTITION BY channel_id) AS video_count FROM videos LIMIT 5''')
        qdf = pd.DataFrame(ytcursor.fetchall(),columns = ytcursor.column_names)
        qdf.index+=1
        st.write(qdf)
    elif query == 'Top 10 most viewed videos':
        ytcursor.execute('''SELECT video_name AS video_name,view_count AS views, channel_name AS channel_name  
            FROM videos ORDER BY view_count DESC LIMIT 10''')
        qdf = pd.DataFrame(ytcursor.fetchall(),columns = ytcursor.column_names)
        qdf.index+=1
        st.write(qdf)
        qdf = qdf.set_index('video_name')
        st.bar_chart(data = qdf, y = 'views')
    elif query == 'Comments on each video':
        ytcursor.execute('''SELECT video_name AS video_name, comment_count AS comment_count 
            FROM videos ORDER BY comment_count DESC''')
        qdf = pd.DataFrame(ytcursor.fetchall(),columns = ytcursor.column_names)
        qdf.index+=1
        st.write(qdf)
    elif query == 'Videos with highest number of likes':
        ytcursor.execute('''SELECT video_name AS video_name, like_count AS like_count, channel_name AS channel_name 
            FROM videos ORDER BY like_count DESC LIMIT 20''')
        qdf = pd.DataFrame(ytcursor.fetchall(),columns = ytcursor.column_names)
        qdf.index+=1
        st.write(qdf)
    elif query == 'Total number of likes and dislikes for each video':
        ytcursor.execute('''SELECT video_name AS video_name, like_count AS like_count, dislike_count AS dislike_count 
            FROM videos''')
        qdf = pd.DataFrame(ytcursor.fetchall(),columns = ytcursor.column_names)
        qdf.index+=1
        st.write(qdf)
    elif query == 'Total number of views for each channel':
        ytcursor.execute('''SELECT channel_name AS channel_name, channel_views AS channel_views 
        FROM channels''')
        qdf = pd.DataFrame(ytcursor.fetchall(),columns = ytcursor.column_names)
        qdf.index+=1
        st.write(qdf)
        qdf = qdf.set_index('channel_name')
        st.bar_chart(qdf) 
    elif query == 'Channels that have published videos in 2022':
        ytcursor.execute('''SELECT channel_name AS channel_name, published_date AS published_date,
            video_name AS video_name 
            FROM videos 
            WHERE published_date>="2022-01-01 00:00:00" AND published_date<= "2023-01-01 00:00:00" 
            ORDER BY channel_name''')
        qdf = pd.DataFrame(ytcursor.fetchall(),columns = ytcursor.column_names)
        qdf.index+=1
        st.write(qdf)
    elif query == 'Average duration of all videos in each channel':
        ytcursor.execute('''SELECT channel_name AS channel_name, AVG(duration) AS avg_duration_seconds   
            FROM videos GROUP BY channel_name''')
        qdf = pd.DataFrame(ytcursor.fetchall(),columns = ytcursor.column_names)
        qdf.index+=1
        st.write(qdf)
        qdf['avg_duration_seconds'] = qdf['avg_duration_seconds'].astype(float)
        qdf = qdf.set_index('channel_name')
        st.bar_chart(qdf)
    elif query == 'Videos with highest number of comments':
        ytcursor.execute('''SELECT video_name AS video_name, channel_name AS channel_name,  
            comment_count AS comment_count FROM videos ORDER BY comment_count DESC LIMIT 10''')
        qdf = pd.DataFrame(ytcursor.fetchall(),columns = ytcursor.column_names)
        qdf.index+=1
        st.write(qdf)