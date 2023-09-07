def get_channel_stats(youtube, channel_ids):
    
     """
    Retrieves a list of video IDs from a YouTube playlist using the YouTube Data API.

    Args:
        youtube (YouTube API Client): An authenticated YouTube API client.
        playlist_id (str): The ID of the YouTube playlist from which to fetch video IDs.

    Returns:
        list: A list of video IDs extracted from the specified playlist.

    Example:
        To use this function, provide a valid YouTube API client and a playlist ID.
        For example:
        youtube = build_youtube_api_client(api_key='YOUR_API_KEY')
        playlist_id = 'YOUR_PLAYLIST_ID'
        video_ids = get_video_ids(youtube, playlist_id)
    """
    
    all_data = []
    
    request = youtube.channels().list(
        part="snippet,contentDetails,statistics",
        id=','.join(channel_ids)
    )
    response = request.execute()

    # loop through items
    for item in response['items']:
        data = {'channelName': item['snippet']['title'],
                'subscribers': item['statistics']['subscriberCount'],
                'views': item['statistics']['viewCount'],
                'totalVideos': item['statistics']['videoCount'],
                'playlistId': item['contentDetails']['relatedPlaylists']['uploads']
        }
        
        all_data.append(data)
        
    return pd.DataFrame(all_data)

def get_video_ids(youtube, playlist_id):
    
    """
    Retrieves a list of video IDs from a YouTube playlist using the YouTube Data API.

    Args:
        youtube (YouTube API Client): An authenticated YouTube API client.
        playlist_id (str): The ID of the YouTube playlist from which to fetch video IDs.

    Returns:
        list: A list of video IDs extracted from the specified playlist.

    Raises:
        Any exceptions raised by the YouTube Data API calls are not caught within this function.

    Example:
        To use this function, provide a valid YouTube API client and a playlist ID.
        For example:
        youtube = build_youtube_api_client(api_key='YOUR_API_KEY')
        playlist_id = 'YOUR_PLAYLIST_ID'
        video_ids = get_video_ids(youtube, playlist_id)

    Note:
        This function handles pagination automatically and retrieves all video IDs
        from the playlist, taking into account the 'maxResults' limit of the API.

    YouTube Data API Reference:
        https://developers.google.com/youtube/v3/docs/playlistItems/list
    """
    
    video_ids = []
    
    request = youtube.playlistItems().list(
        part="snippet,contentDetails",
        playlistId=playlist_id,
        maxResults = 50
    )
    response = request.execute()
    
    for item in response['items']:
        video_ids.append(item['contentDetails']['videoId'])
        
    next_page_token = response.get('nextPageToken')
    while next_page_token is not None:
        request = youtube.playlistItems().list(
                    part='contentDetails',
                    playlistId = playlist_id,
                    maxResults = 50,
                    pageToken = next_page_token)
        response = request.execute()

        for item in response['items']:
            video_ids.append(item['contentDetails']['videoId'])

        next_page_token = response.get('nextPageToken')
        
    return video_ids
    
    
def get_video_details(youtube, video_ids):

    all_video_info = []
    
    for i in range(0, len(video_ids), 50):
        request = youtube.videos().list(
            part="snippet,contentDetails,statistics",
            id=','.join(video_ids[i:i+50])
        )
        response = request.execute() 

        for video in response['items']:
            stats_to_keep = {'snippet': ['channelTitle', 'title', 'description', 'tags', 'publishedAt'],
                             'statistics': ['viewCount', 'likeCount', 'favouriteCount', 'commentCount'],
                             'contentDetails': ['duration', 'definition', 'caption']
                            }
            video_info = {}
            video_info['video_id'] = video['id']

            for k in stats_to_keep.keys():
                for v in stats_to_keep[k]:
                    try:
                        video_info[v] = video[k][v]
                    except:
                        video_info[v] = None

            all_video_info.append(video_info)
    
    return pd.DataFrame(all_video_info)