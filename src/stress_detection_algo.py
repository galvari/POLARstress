# stress_detection.py
# Author: Gianpaolo Alvari
# Description: This script processes Polar Verity Sense session data to detect stress levels by calculating HRV metrics and flagging stress episodes based on RMSSD values.

import pandas as pd
import numpy as np
from datetime import datetime
import os
import argparse
import warnings
warnings.filterwarnings("ignore")
import matplotlib.pyplot as plt
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()
import seaborn as sns
import psutil
import time

# ---------------------------------------------
# Performance Monitoring
# ---------------------------------------------
start_time = time.time()
cpu_before = psutil.cpu_percent()
mem_before = psutil.virtual_memory().used

# ---------------------------------------------
# Function to Process Session Data
# ---------------------------------------------
def enrich_session_data_with_summary_and_timestamp_fixed(file_path):
    """
    Processes a Polar session file, separating and combining summary and session data,
    and adds a 'timestamp' column based on 'Date', 'Start time', and 'Time'.
    
    Parameters:
    - file_path: str, the path to the CSV file.
    
    Returns:
    - DataFrame containing the session data enriched with summary information and a 'timestamp' column.
    """
    summary = pd.read_csv(file_path, nrows=1)
    session_data = pd.read_csv(file_path, skiprows=2)
    columns_from_summary = [col for col in summary.columns if col not in session_data.columns]
    summary_info_repeated = pd.DataFrame([summary.iloc[0]] * session_data.shape[0])
    session_data_enriched = pd.concat([session_data, summary_info_repeated], axis=1).reset_index(drop=True)
    session_data_enriched['timestamp'] = pd.to_datetime(session_data_enriched['Date'] + ' ' + session_data_enriched['Start time']) + pd.to_timedelta(session_data_enriched['Time'])
    return session_data_enriched

# ---------------------------------------------
# Function to Remove Outliers and Interpolate
# ---------------------------------------------
def remove_outliers_and_interpolate(rr_intervals, low_rri=300, high_rri=2000):
    """
    Remove outliers from RR intervals and interpolate the missing values.

    Parameters:
    rr_intervals (pd.Series): Series of RR intervals.
    low_rri (int): Lower threshold for RR interval (in milliseconds).
    high_rri (int): Upper threshold for RR interval (in milliseconds).

    Returns:
    pd.Series: RR intervals with outliers removed and interpolated.
    """
    outliers = (rr_intervals < low_rri) | (rr_intervals > high_rri)
    rr_intervals[outliers] = np.nan
    rr_intervals.interpolate(method='linear', inplace=True)
    return rr_intervals

# ---------------------------------------------
# Function to Calculate RMSSD
# ---------------------------------------------
def calculate_rmssd(rr_intervals):
    """
    Calculate the RMSSD (Root Mean Square of Successive Differences) for a series of RR intervals.

    Parameters:
    rr_intervals (pd.Series): Series of RR intervals.

    Returns:
    float: RMSSD value.
    """
    diff = np.diff(rr_intervals)
    squared_diff = np.square(diff)
    mean_squared_diff = np.mean(squared_diff)
    rmssd = np.sqrt(mean_squared_diff)
    return rmssd

# ---------------------------------------------
# Main Execution
# ---------------------------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process Polar session file, output flagged data, and optionally save a plot.")
    parser.add_argument("input_file", type=str, help="Input file path for the Polar session CSV.")
    parser.add_argument("output_folder", type=str, help="Output folder path for the flagged data CSV and optional plot.")
    parser.add_argument("--save_plot", action='store_true', help="Option to save plot. If set, saves plot as PNG.")
    args = parser.parse_args()

    base_name = os.path.basename(args.input_file)
    file_name_without_ext = os.path.splitext(base_name)[0]
    output_csv_path = os.path.join(args.output_folder, f"{file_name_without_ext}_flagged.csv")
    output_plot_path = os.path.join(args.output_folder, f"{file_name_without_ext}_flagged.png")

    print('1. Preparing data...')
    session_data_with_timestamp = enrich_session_data_with_summary_and_timestamp_fixed(args.input_file)

    print('2. Resampling...')
    session_data_with_timestamp.set_index('timestamp', inplace=True)
    time_from_start = session_data_with_timestamp.index.to_series() - session_data_with_timestamp.index[0]
    session_data_with_timestamp['Baseline'] = (time_from_start <= pd.Timedelta(minutes=3)).astype(int)

    resampled_session_data = session_data_with_timestamp.resample('1S').apply(lambda x: x.mean() if x.name == 'HR (bpm)' else x.max())

    print('3. Interpolating...')
    resampled_session_data['HR_spline'] = resampled_session_data['HR (bpm)'].interpolate(method='spline', order=3)
    resampled_session_data['HR_linear'] = resampled_session_data['HR (bpm)'].interpolate(method='linear')

    print('4. Computing RR intervals...')
    resampled_session_data['RR_intervals'] = 60000 / resampled_session_data['HR_spline']
    resampled_session_data['RR_intervals'] = remove_outliers_and_interpolate(resampled_session_data['RR_intervals'])

    print('5. Computing HRV Baseline...')
    five_minute_data = resampled_session_data.first('5T')
    window_size = 30
    step_size = 15
    rmssd_values = []
    timestamps = []
    for start in range(0, len(five_minute_data) - window_size + 1, step_size):
        end = start + window_size
        rr_intervals = five_minute_data['RR_intervals'].iloc[start:end]
        rmssd = calculate_rmssd(rr_intervals)
        rmssd_values.append(rmssd)
        timestamps.append(five_minute_data.index[start])
    rmssd_df = pd.DataFrame({'Timestamp': timestamps, 'RMSSD': rmssd_values})
    rmssd_df.set_index('Timestamp', inplace=True)
    resampled_session_data['RMSSD'] = rmssd_df['RMSSD']
    rolling_rmssd = rmssd_df['RMSSD'].rolling(window=5, min_periods=5).mean()
    highest_rmssd_idx = rolling_rmssd.idxmax()
    baseline_start = highest_rmssd_idx - pd.Timedelta(minutes=2)
    baseline_end = highest_rmssd_idx
    resampled_session_data['Baseline_computed'] = 0
    resampled_session_data.loc[baseline_start:baseline_end, 'Baseline_computed'] = 1
    baseline_window = resampled_session_data.loc[baseline_start:baseline_end]
    rmssd_mean_bs = baseline_window['RMSSD'].mean()
    rmssd_std_bs = baseline_window['RMSSD'].std()
    rmssd_tuple_bs = (rmssd_mean_bs, rmssd_std_bs)
    resampled_session_data['Baseline_RMSSD'] = resampled_session_data.apply(lambda x: rmssd_tuple_bs, axis=1)

    print('6. Computing HRV Overlapping Windows...')
    resampled_session_data['RMSSD'] = np.nan
    rmssd_values_full = [np.nan] * len(resampled_session_data)
    window_size = 60
    step_size = 30
    for start in range(0, len(resampled_session_data) - window_size + 1, step_size):
        end = start + window_size
        window_rr_intervals = resampled_session_data['RR_intervals'].iloc[start:end]
        rmssd_window = calculate_rmssd(window_rr_intervals)
        for i in range(start, end):
            if pd.isna(rmssd_values_full[i]):
                rmssd_values_full[i] = rmssd_window
            else:
                rmssd_values_full[i] = (rmssd_values_full[i] + rmssd_window) / 2
    resampled_session_data['RMSSD'] = rmssd_values_full

    print('7. Flagging Stress Levels...')
    mean_rmssd = np.mean(rmssd_values_full)
    std_rmssd = np.std(rmssd_values_full)
    resampled_session_data['Stress_Flag'] = resampled_session_data['RMSSD'].apply(lambda x: 'High Stress' if x <= mean_rmssd - 2 * std_rmssd else ('Moderate Stress' if x <= mean_rmssd - std_rmssd else ('Normal' if x <= mean_rmssd + std_rmssd else 'Relaxed')))

    print('8. Saving...')
    resampled_session_data.to_csv(output_csv_path)
    print(f"Data saved to {output_csv_path}")

    if args.save_plot:
        sns.set(style="darkgrid")
        plt.figure(figsize=(12, 6))
        timestamps = resampled_session_data.index
        signal = 'HR_spline'
        for i in range(len(timestamps) - 1):
            start, end = timestamps[i], timestamps[i + 1]
            color = resampled_session_data['Stress_Flag'].iloc[i]
            plt.plot([start, end], resampled_session_data[signal].iloc[i:i + 2], color=color.lower())
        baseline_fill = plt.fill_between(timestamps, resampled_session_data[signal], where=resampled_session_data['Baseline_computed'] == 1, color='lightblue', alpha=0.3)
        plt.title("Heart Rate Over Time with Stress Flags")
        plt.xlabel("Time")
        plt.ylabel("Heart Rate (bpm)")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(output_plot_path)
        print(f"Plot saved to {output_plot_path}")

end_time = time.time()
cpu_after = psutil.cpu_percent()
mem_after = psutil.virtual_memory().used
print(f"Execution time: {end_time - start_time} seconds")
print(f"CPU usage: {cpu_after - cpu_before}%")
mem_usage_mb = (mem_after - mem_before) / (2.**20)
print(f"Memory usage: {mem_usage_mb:.2f} MB")
