import requests
import json
import polars as pl
from ignore.key import KEY
from youtube_transcript_api import YouTubeTranscriptApi

def getVideoRecords(response):
    v_record_list = []
    data = json.loads(response.text)
    print(data.keys())
    # print(json.dumps(data['items'], indent=4))
    for yt_vid_data in data["items"]:
        if yt_vid_data['id']['kind'] != "youtube#video":
            continue
        record = {}
        record['video_id'] = yt_vid_data['id']['videoId']
        record['datetime'] = yt_vid_data['snippet']['publishedAt']
        record['title'] = yt_vid_data['snippet']['title']
        
        v_record_list.append(record)
    
    return v_record_list

url = 'https://www.googleapis.com/youtube/v3/search'
channel_id = "UC8SSI65dAwfWMox5tiJOzaQ"
page_token = None


# store video data here
video_record_list = []

while page_token != 0:
    params = {"key": KEY, 'channelId': channel_id, 
              'maxResult':50, 'part': ['snippet', 'id'], 'order': 'date',
              'pageToken': page_token }
    response =  requests.get(url, params=params)
    print(response.text)
    video_record_list += getVideoRecords(response)
    try:
        page_token = json.loads(response.text)["nextPageToken"]
    except:
        page_token = 0



df = pl.DataFrame(video_record_list)
print(df.head())
# df =  pd.read_csv("2024_eia_power_data.csv")

# # Ensure the Date column is parsed as datetime
# df['period'] = pd.to_datetime(df['period'])

# # Filter rows for months July (7) to December (12)
# df = df[df['period'].dt.month.isin(range(7, 13))]

# # Optionally, save the filtered data to a new CSV file
# df.to_csv("filtered_data.csv", index=False)
# to grab transcript, need video id
# df.dropna(axis = 1)

for vid in df:
    try:
        transcript = YouTubeTranscriptApi.get_transcript(vid["video_id"])
        print(transcript)
        vid["transcript"] = " ".join(entry["text"]for entry in transcript)
    except Exception as e:
        vid["transcript"] = e

df = pl.DataFrame(video_record_list)

df.write_csv("yt_transcripts.csv")