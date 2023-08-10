from flask import Flask, render_template, jsonify
import requests
import urllib3
import pandas as pd
import numpy as np

app = Flask(__name__)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def request_access_token(client_id, client_secret, refresh_token):
    auth_url = "https://www.strava.com/oauth/token"
    payload = {
        'client_id': client_id,
        'client_secret': client_secret,
        'refresh_token': refresh_token,
        'grant_type': 'refresh_token',
        'f': 'json'
    }
    print("\nRequesting Access Token...")
    res = requests.post(auth_url, data=payload, verify=False)
    access_token = res.json()['access_token']
    print(f"\nAccess Token = {access_token}")
    return access_token

def get_activity_data(access_token):
    print("\nGetting Activity Data...")
    activities_url = "https://www.strava.com/api/v3/athlete/activities"
    header = {'Authorization': 'Bearer ' + access_token}
    request_page_num = 1
    all_activities_list = []
    while True:
        param = {'per_page': 200, 'page': request_page_num}
        get_activities = requests.get(activities_url, headers=header,params=param).json()
        if len(get_activities) == 0:
            break
        all_activities_list.extend(get_activities)
        request_page_num += 1
        all_activities_df = pd.DataFrame(all_activities_list)
    return all_activities_df, all_activities_list

def get_segments_list(bounds, access_token):
    print("\nGetting Segment Data...")
    segments_url = "https://www.strava.com/api/v3/segments/explore"
    header = {'Authorization': 'Bearer ' + access_token}
    param = {'bounds': ','.join(str(coord) for coord in bounds)}
    get_segments = requests.get(segments_url, headers=header, params=param).json()
    all_segments = pd.DataFrame(get_segments)
    normalized_data = pd.json_normalize(all_segments['segments'])
    all_segments_df = pd.concat([all_segments, normalized_data], axis=1)
    all_segments_df.drop(columns=['segments'], inplace=True)
    return all_segments_df

def calculate_recent_activity_stats(data_frame):
    date = data_frame.loc[0, 'start_date']
    name = data_frame.loc[0, 'name']
    type = data_frame.loc[0, 'type']
    distance = round(data_frame.loc[0, 'distance'] / 1000, 1)

    return(
        date,
        name,
        type,
        distance,
    )

def calculate_lifetime_stats(data_frame):
    kudos_received = data_frame['kudos_count'].sum()
    data_frame['heart_beats'] = data_frame['average_heartrate'] * data_frame['moving_time']
    heart_beats = data_frame['heart_beats'].sum()
    distance_travelled = data_frame['distance'].sum() / 1000
    elevation_gained = data_frame['total_elevation_gain'].sum()

    times_around_earth = distance_travelled / 40075 # circumference of earth
    blood_pumped = heart_beats * 0.07 # average volume of blood pumped per beat
    times_up_everest = elevation_gained / 8848 # height of Mt Everest

    return(
        kudos_received,
        '{:,}'.format(round(heart_beats)),
        '{:,}'.format(round(distance_travelled)),
        '{:,}'.format(round(elevation_gained)),
        '{:,}'.format(round(blood_pumped)),
        round(times_around_earth, 2),
        round(times_up_everest, 1)
    )

def calculate_bike_run_stats(data_frame, sport_type, commute):
    filtered_activities = data_frame[(data_frame['sport_type'] == sport_type) & (data_frame['commute'] == commute)]
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

def calculate_hike_stats(data_frame, sport_type):
    filtered_activities = data_frame[data_frame['sport_type'] == sport_type]
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

def calculate_swim_stats(data_frame, sport_type):
    filtered_activities = data_frame[data_frame['sport_type'] == sport_type]
    total_count = len(filtered_activities)
    total_kudos_count = filtered_activities['kudos_count'].sum()
    total_distance = filtered_activities['distance'].sum() / 1000
    avg_speed = filtered_activities['average_speed'].mean() * 3.6
    avg_distance = filtered_activities['distance'].mean() / 1000
    avg_heartrate = filtered_activities['average_heartrate']

    total_count = np.nan_to_num(total_count)
    total_kudos_count = np.nan_to_num(total_kudos_count)
    total_distance = np.nan_to_num(total_distance)
    avg_speed = np.nan_to_num(avg_speed)
    avg_distance = np.nan_to_num(avg_distance)
    avg_heartrate = np.nan_to_num(avg_heartrate)

    return(
        total_count,
        total_kudos_count,
        round(total_distance, 1), 
        round(avg_speed, 1), 
        round(avg_distance, 1), 
        round(avg_heartrate, 1)
    )

# Introduction
print("\nWelcome to the Strava API Test App")
client_id = '111595'
client_secret = '8e8f246270159ece4b0eb3c75e494241bad86027'
refresh_token = '8285947a1614c22ebf0a7308cafb267ed4d9426f'

access_token = request_access_token(client_id, client_secret, refresh_token)
all_activities, all_activities_list = get_activity_data(access_token)

bounds = [51.036047, -114.150184, 51.054738, -114.111313]
all_segments = get_segments_list(bounds, access_token)

# print(all_activities[all_activities['type'] == 'Swim'].iloc[1])

@app.route('/')
def index():

    # Lifetime Stats
    l1, l2, l3, l4, l5, l6, l7 = calculate_lifetime_stats(all_activities)

    # Most recent activity stats
    date, name, type, distance = calculate_recent_activity_stats(all_activities)

    # Ride stats
    r1, r2, r3, r4, r5, r6, r7 = calculate_bike_run_stats(all_activities, 'Ride', False)
    c1, c2, c3, c4, c5, c6, c7 = calculate_bike_run_stats(all_activities, 'Ride', True)
    m1, m2, m3, m4, m5, m6, m7 = calculate_bike_run_stats(all_activities, 'MountainBikeRide', False)
    v1, v2, v3, v4, v5, v6, v7 = calculate_bike_run_stats(all_activities, 'VirtualRide', False)

    # Run/Hike stats
    or1, or2, or3, or4, or5, or6, or7 = calculate_bike_run_stats(all_activities, 'Run', False)
    vr1, vr2, vr3, vr4, vr5, vr6, vr7 = calculate_bike_run_stats(all_activities, 'VirtualRun', False)
    h1, h2, h3, h4, h5, h6, h7 = calculate_hike_stats(all_activities, 'Hike')

    # Other Stats
    
    return render_template('index.html',
        kudos_received=l1, heart_beats=l2, distance_travelled=l3, elevation_gained=l4, blood_pumped=l5, times_around_earth=l6, times_up_everest=l7,
        date=date, name=name, type=type, distance=distance, 
        total_rides=r1, total_ride_distance=r2, total_ride_elevation=r3, avg_ride_speed=r4, avg_ride_power=r5, avg_ride_distance=r6, avg_ride_elevation=r7, 
        total_commutes=c1, total_commute_distance=c2,total_commute_elevation=c3, avg_commute_speed=c4, avg_commute_power=c5, avg_commute_distance=c6, avg_commute_elevation=c7, 
        total_mtb=m1, total_mtb_distance=m2, total_mtb_elevation=m3, avg_mtb_speed=m4, avg_mtb_power=m5, avg_mtb_distance=m6, avg_mtb_elevation=m7, 
        total_virtual_rides=v1, total_virtual_ride_distance=v2, total_virtual_ride_elevation=v3, avg_virtual_ride_speed=v4, avg_virtual_ride_power=v5, avg_virtual_ride_distance=v6, avg_virtual_ride_elevation=v7, 
        total_outdoor_runs=or1, total_outdoor_run_distance=or2, total_outdoor_run_elevation=or3, avg_outdoor_run_speed=or4, avg_outdoor_run_power=or5, avg_outdoor_distance=or6, avg_outdoor_run_elevation=or7, 
        total_virtual_runs=vr1, total_virtual_run_distance=vr2, total_virtual_run_elevation=vr3, avg_virtual_run_speed=vr4, avg_virtual_run_power=vr5, avg_virtual_run_distance=vr6, avg_virtual_run_elevation=vr7, 
        total_hikes=h1, total_hike_distance=h2, total_hike_elevation=h3, avg_hike_speed=h4,avg_hike_power=h5, avg_hike_distance=h6, avg_hike_elevation=h7)

@app.route('/api/all_activities')
def get_all_activities():
    return jsonify(all_activities_list)

if __name__ == '__main__':
    app.run()
