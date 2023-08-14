import requests
import urllib3
import pandas as pd 

# Introduction
print("\nWelcome to the Strava API Test App")
client_id = '111595'

# API access token generation
auth_url = "https://www.strava.com/oauth/token"
payload = {
    'client_id': client_id,
    'client_secret': '8e8f246270159ece4b0eb3c75e494241bad86027',
    'refresh_token': '8285947a1614c22ebf0a7308cafb267ed4d9426f',
    'grant_type': 'refresh_token',
    'f': 'json'
}
print("\nRequesting Access Token...")
res = requests.post(auth_url, data=payload, verify=False)
access_token = res.json()['access_token']
print(f"\nAccess Token = {access_token}")

# Getting segment data
print("\nGetting Segment Data...")
bounds = [51.036047, -114.150184, 51.054738, -114.111313]
segments_url = "https://www.strava.com/api/v3/segments/explore"
header = {'Authorization': 'Bearer ' + access_token}
param = {'bounds': ','.join(str(coord) for coord in bounds), 'activity_type': 'riding'}
get_segments = requests.get(segments_url, headers=header, params=param).json()
all_segments = pd.DataFrame(get_segments)
normalized_data = pd.json_normalize(all_segments['segments'])
all_segments_df = pd.concat([all_segments, normalized_data], axis=1)
all_segments_df.drop(columns=['segments'], inplace=True)

# Printing Nearby Segments
for id in all_segments_df.loc[:, 'id']:
    segment_stats_url = "https://www.strava.com/api/v3/segments/" + str(int(id))
    get_segment_stats = requests.get(segment_stats_url, headers=header).json()
    if(get_segment_stats['athlete_segment_stats']['pr_elapsed_time'] == None):
        print("Name:", get_segment_stats['name'])
        print("Avg Grade:", get_segment_stats['average_grade'])
        print("Distance:", get_segment_stats['distance'])
        print("PR: NA")
        print("Averge Speed: NA")
        print("Overall:", get_segment_stats['xoms']['overall'])
        print("")
    else:
        print("Name:", get_segment_stats['name'])
        print("Avg Grade:", get_segment_stats['average_grade'])
        print("Distance:", get_segment_stats['distance'])
        print("PR:", get_segment_stats['athlete_segment_stats']['pr_elapsed_time'])
        print("Averge Speed:", get_segment_stats['distance']/get_segment_stats['athlete_segment_stats']['pr_elapsed_time'] * 3.6)
        print("Overall:", get_segment_stats['xoms']['overall'])
        print("")


