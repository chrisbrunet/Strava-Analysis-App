from flask import Flask, render_template, jsonify
import requests
import urllib3
import pandas as pd
import numpy as np

app = Flask(__name__)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def calculate_activity_stats(data_frame, activity_type):
    filtered_activities = data_frame[data_frame['sport_type'] == activity_type]
    total_count = len(filtered_activities)
    total_distance = filtered_activities['distance'].sum() / 1000
    total_elevation = filtered_activities['total_elevation_gain'].sum()
    avg_speed = filtered_activities['average_speed'].mean() * 3.6
    avg_power = filtered_activities['average_watts'].mean()
    avg_distance = filtered_activities['distance'].mean() / 1000
    avg_elevation = filtered_activities['total_elevation_gain'].mean()

    total_count = np.nan_to_num(total_count)
    total_distance = np.nan_to_num(total_distance)
    total_elevation = np.nan_to_num(total_elevation)
    avg_speed = np.nan_to_num(avg_speed)
    avg_power = np.nan_to_num(avg_power)
    avg_distance = np.nan_to_num(avg_distance)
    avg_elevation = np.nan_to_num(avg_elevation)

    return(
        total_count, 
        round(total_distance, 1), 
        round(total_elevation, 1), 
        round(avg_speed, 1), 
        round(avg_power, 1), 
        round(avg_distance, 1), 
        round(avg_elevation, 1)
    )

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

# Getting activity data
print("\nGetting Activity Data...")
activities_url = "https://www.strava.com/api/v3/athlete/activities"
header = {'Authorization': 'Bearer ' + access_token}
request_page_num = 1
all_activities = []
while True:
    param = {'per_page': 200, 'page': request_page_num}
    get_activities = requests.get(activities_url, headers=header,params=param).json()
    if len(get_activities) == 0:
        break
    all_activities.extend(get_activities)
    request_page_num += 1
all_activities_df = pd.DataFrame(all_activities)

# Getting segment data
print("\nGetting Segment Data...")
bounds = [51.036047, -114.150184, 51.054738, -114.111313]
segments_url = "https://www.strava.com/api/v3/segments/explore"
header = {'Authorization': 'Bearer ' + access_token}
param = {'bounds': ','.join(str(coord) for coord in bounds)}
get_segments = requests.get(segments_url, headers=header, params=param).json()
all_segments = pd.DataFrame(get_segments)
normalized_data = pd.json_normalize(all_segments['segments'])
all_segments_df = pd.concat([all_segments, normalized_data], axis=1)
all_segments_df.drop(columns=['segments'], inplace=True)

# Bike Ride Activities
all_rides = all_activities_df[all_activities_df['type'] == 'Ride']
all_bike_commutes = all_rides[all_rides['commute'] == True]
all_rides_exc_commutes = all_rides[(all_rides['commute'] == False) & (all_rides['sport_type'] == 'Ride')]
all_virtual_rides = all_activities_df[all_activities_df['type'] == 'VirtualRide']
all_mtb_rides = all_activities_df[(all_activities_df['type'] == 'Ride') & (all_activities_df['sport_type'] == 'MountainBikeRide')]

# Run Activities
all_outdoor_runs = all_activities_df[all_activities_df['type'] == 'Run']
all_virtual_runs = all_activities_df[all_activities_df['type'] == 'VirtualRun']

@app.route('/')
def index():
    # Most recent activity stats
    date = all_activities[0]['start_date']
    name = all_activities[0]['name']
    type = all_activities[0]['type']
    distance = all_activities[0]['distance']

    # Ride stats
    r1, r2, r3, r4, r5, r6, r7 = calculate_activity_stats(all_rides_exc_commutes, 'Ride')
    c1, c2, c3, c4, c5, c6, c7 = calculate_activity_stats(all_bike_commutes, 'Ride')
    m1, m2, m3, m4, m5, m6, m7 = calculate_activity_stats(all_mtb_rides, 'MountainBikeRide')
    v1, v2, v3, v4, v5, v6, v7 = calculate_activity_stats(all_virtual_rides, 'VirtualRide')

    # Run stats
    or1, or2, or3, or4, or5, or6, or7 = calculate_activity_stats(all_outdoor_runs, 'Run')
    vr1, vr2, vr3, vr4, vr5, vr6, vr7 = calculate_activity_stats(all_virtual_runs, 'VirtualRun')

    # Other Stats
    
    return render_template('index.html',date=date, name=name, type=type, distance=distance, total_rides=r1, total_ride_distance=r2, 
                           total_ride_elevation=r3, avg_ride_speed=r4, avg_ride_power=r5, avg_ride_distance=r6, avg_ride_elevation=r7, 
                           total_commutes=c1, total_commute_distance=c2,total_commute_elevation=c3, avg_commute_speed=c4, 
                           avg_commute_power=c5, avg_commute_distance=c6, avg_commute_elevation=c7, total_mtb=m1, total_mtb_distance=m2, 
                           total_mtb_elevation=m3, avg_mtb_speed=m4, avg_mtb_power=m5, avg_mtb_distance=m6, avg_mtb_elevation=m7, 
                           total_virtual_rides=v1, total_virtual_ride_distance=v2, total_virtual_ride_elevation=v3, avg_virtual_ride_speed=v4, 
                           avg_virtual_ride_power=v5, avg_virtual_ride_distance=v6, avg_virtual_ride_elevation=v7, total_outdoor_runs=or1, 
                           total_outdoor_run_distance=or2, total_outdoor_run_elevation=or3, avg_outdoor_run_speed=or4, avg_outdoor_run_power=or5, 
                           avg_outdoor_distance=or6, avg_outdoor_run_elevation=or7, total_virtual_runs=vr1, total_virtual_run_distance=vr2, 
                           total_virtual_run_elevation=vr3, avg_virtual_run_speed=vr4, avg_virtual_run_power=vr5, avg_virtual_run_distance=vr6, 
                           avg_virtual_run_elevation=vr7)

@app.route('/api/all_activities')
def get_all_activities():
    return jsonify(all_activities)

if __name__ == '__main__':
    app.run()
