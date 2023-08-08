from flask import Flask, render_template
import requests
import urllib3
import pandas as pd

app = Flask(__name__)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

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
    param = {'per page': 200, 'page': request_page_num}
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

# Ride Analysis
total_rides = len(all_rides_exc_commutes)
total_ride_distance = all_rides_exc_commutes['distance'].sum() / 1000
total_ride_elevation = all_rides_exc_commutes['total_elevation_gain'].sum()
avg_ride_speed = all_rides_exc_commutes['average_speed'].mean() * 3.6
avg_ride_power = all_rides_exc_commutes['average_watts'].mean()
avg_ride_distance = all_rides_exc_commutes['distance'].mean() / 1000
avg_ride_elevation = all_rides_exc_commutes['total_elevation_gain'].mean()

# Commute Analysis
total_commutes = len(all_bike_commutes)
total_commute_distance = all_bike_commutes['distance'].sum() / 1000
total_commute_elevation = all_bike_commutes['total_elevation_gain'].sum()
avg_commute_speed = all_bike_commutes['average_speed'].mean() * 3.6
avg_commute_power = all_bike_commutes['average_watts'].mean()
avg_commute_distance = all_bike_commutes['distance'].mean() / 1000
avg_commute_elevation = all_bike_commutes['total_elevation_gain'].mean()

# Mtb Analysis
total_mtb = len(all_mtb_rides)
total_mtb_distance = all_mtb_rides['distance'].sum() / 1000
total_mtb_elevation = all_mtb_rides['total_elevation_gain'].sum()
avg_mtb_speed = all_mtb_rides['average_speed'].mean() * 3.6
avg_mtb_power = all_mtb_rides['average_watts'].mean()
avg_mtb_distance = all_mtb_rides['distance'].mean() / 1000
avg_mtb_elevation = all_mtb_rides['total_elevation_gain'].mean()


@app.route('/')
def index():
    v1 = total_rides
    v2 = round(total_ride_distance, 1)
    v3 = round(total_ride_elevation, 1)
    v4 = round(avg_ride_speed, 1)
    v5 = round(avg_ride_power, 1)
    v6 = round(avg_ride_distance, 1)
    v7 = round(avg_ride_elevation, 1)

    c1 = total_commutes
    c2 = round(total_commute_distance, 1)
    c3 = round(total_commute_elevation, 1)
    c4 = round(avg_commute_speed, 1)
    c5 = round(avg_commute_power, 1)
    c6 = round(avg_commute_distance, 1)
    c7 = round(avg_commute_elevation, 1)

    m1 = total_mtb
    m2 = round(total_mtb_distance, 1)
    m3 = round(total_mtb_elevation, 1)
    m4 = round(avg_mtb_speed, 1)
    m5 = round(avg_mtb_power, 1)
    m6 = round(avg_mtb_distance, 1)
    m7 = round(avg_mtb_elevation, 1)
    
    return render_template('index.html', total_rides=v1, total_ride_distance=v2, total_ride_elevation=v3, avg_ride_speed=v4,
                           avg_ride_power=v5, avg_ride_distance=v6, avg_ride_elevation=v7, total_commutes=c1, total_commute_distance=c2,
                           total_commute_elevation=c3, avg_commute_speed=c4, avg_commute_power=c5, avg_commute_distance=c6, 
                           avg_commute_elevation=c7, total_mtb=m1, total_mtb_distance=m2, total_mtb_elevation=m3, avg_mtb_speed=m4, 
                           avg_mtb_power=m5, avg_mtb_distance=m6, avg_mtb_elevation=m7)

if __name__ == '__main__':
    app.run()
