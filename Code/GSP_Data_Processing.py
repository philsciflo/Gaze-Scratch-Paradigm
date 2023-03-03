# !/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This code processes the raw data from the eye-tracker into five dictionaries:

trial_phase_data: contains gaze data separated into trials and PHASES
fixation_data: contains fixation data for trials and PHASES

The following three dictionaries are required for the analysis of areas of interest (AOI):

trial_phase_aoi_data: contains only gaze data for both AOIs separated into trials and PHASES
fixation_data_drop: contains only fixation data for AOI drop
fixation_data_rise: contains only fixation data for AOI rise

Author:  Florian Bednarski
Contact: fteichmann[at]cbs.mpg.de
Years:   2021-2023
"""

# %% Import
from copy import deepcopy
import pandas as pd
import os
import numpy as np
import math

# %% Set global vars & paths  >><< o >><< o >><< o >><< o >><< o >><< o >><< o >><< o >><< o >><< o >><< o

# Globals vars
PHASES = ["baseline", "contingent", "disruption"]
ID = "ID_52b"  # ID to ensure proper storage of csv exports
CONDITION = "Rise"  # condition for Rise/Drop Trials

# Pass the file path
DATA_PATH = ""  # INSERT PATH TO DATA FILES


# %% Functions  >><< o >><< o >><< o >><< o >><< o >><< o >><< o >><< o >><< o >><< o >><< o >><< o >><< o

def fixation_detection(x, y, time, missing=0.0, maxdist=25, mindur=0.25):
    """
    Get fixations.

    This is from the PyTrack project (https://github.com/titoghose/PyTrack).

    :param x:
    :param y:
    :param time:
    :param missing:
    :param maxdist:
    :param mindur:
    :return:
    """
    # Empty list to contain data
    s_fix = []
    e_fix = []

    # Loop through all coordinates
    si = 0
    fixstart = False
    for i in range(1, len(x)):
        # calculate Euclidean distance from the current fixation coordinate
        # to the next coordinate
        dist = ((x[si] - x[i]) ** 2 + (y[si] - y[i]) ** 2) ** 0.5
        # check if the next coordinate is below maximal distance
        if dist <= maxdist and not fixstart:
            # start a new fixation
            si = 0 + i
            fixstart = True
            s_fix.append([time[i]])
        elif dist > maxdist and fixstart:
            # end the current fixation
            fixstart = False
            # only store the fixation if the duration is ok
            if abs(time[i - 1] - s_fix[-1][0]) >= mindur:
                e_fix.append([s_fix[-1][0], time[i - 1], time[i - 1] - s_fix[-1][0], x[si], y[si]])
            # delete the last fixation start if it was too short
            else:
                s_fix.pop(-1)
            si = 0 + i
        elif not fixstart:
            si += 1

    return s_fix, e_fix


# %% __main__ o >><< o >><< o >><< o >><< o >><< o >><< o >><< o >><< o >><< o >><< o >><< o >><< o >><< o

if __name__ == "__main__":

    # Load csv files for one participant and define names for trials and PHASES.
    # So far you can only process one participant in one condition of the gaze scratch paradigm at a time
    files_GSP = os.listdir(DATA_PATH)
    trial_names = [trial_fn.split("_")[0] for trial_fn in files_GSP]
    trial_names = np.array(sorted(trial_names, key=lambda x: [0]))
    trial_names = trial_names.tolist()
    print(trial_names)

    # Split Raw Data into trials and PHASES and write in nested dictionary
    trial_phase_data = {}
    for trial_fn in files_GSP:
        # Extract trial name
        trial_name = trial_fn.split("_")[0]  # .split("_")[0] #in trial_names
        # trial_fn.split(".")[0].split("screen_")[-1]

        # Read whole trial data
        trial_data = pd.read_csv(os.path.join(DATA_PATH, trial_fn))

        # Divide data into the three PHASES (baseline/contingent/disruption) of the experiment
        # make sure the timing is correct and matches you trial design
        trial_data_baseline = trial_data.loc[(trial_data['time'] > 4) & (
                trial_data['time'] < 9)].reset_index(drop=True)
        trial_data_disruption = trial_data.loc[(
                trial_data['time'] > trial_data['time'].iloc[-1] - 5)].reset_index(drop=True)
        trial_data_contingent = trial_data.loc[
            (trial_data['time'] > trial_data_baseline['time'].iloc[-1]) & (
                    trial_data['time'] < trial_data_disruption['time'].iloc[0])].reset_index(drop=True)

        # Fill in data dict per trial
        trial_dict = {trial_name: {}}
        trial_phase_data.update(trial_dict)  # nested dict
        trial_phase_data[trial_name].update(dict(baseline=trial_data_baseline))
        trial_phase_data[trial_name].update(dict(disruption=trial_data_disruption))
        trial_phase_data[trial_name].update(dict(contingent=trial_data_contingent))

    # Clean Data per Trial and Phase (drop 'nan' values)
    for trial_name in trial_names:  # ~ trial_phase_data.keys():
        for phase in PHASES:
            trial_phase_data[trial_name][phase].dropna(inplace=True)
            trial_phase_data[trial_name][phase].reset_index(inplace=True, drop=True)

    # Sampling rate 120hz / sampling length 8.3333ms
    # We pre-registered inclusion criteria for each trial

    # Check Inclusion Criteria Baseline (LT > 1s)
    for trial_name in trial_names:
        for phase in PHASES[:1]:
            df = trial_phase_data[trial_name][phase]
            if len(df['time']) * ((1000 / 120) * 1000) < 1:
                print('Inclusion Criteria not matched.')
                print(f"Trial name: '{trial_name}' | Phase: '{phase}':\n | Deleted")
                del df
            else:
                print('Inclusion Criteria matched.')
                print(f"Trial name: '{trial_name}' | Phase: '{phase}':\n")

    # Check Inclusion Criteria Contingent (LT > 10s)
    for trial_name in trial_names:
        for phase in PHASES[1:2]:
            df = trial_phase_data[trial_name][phase]
            if len(df['time']) * ((1000 / 120) * 1000) < 10:
                print('Inclusion Criteria not matched.')
                print(f"Trial name: '{trial_name}' | Phase: '{phase}':\n | Deleted")
                del df
            else:
                print('Inclusion Criteria matched.')
                print(f"Trial name: '{trial_name}' | Phase: '{phase}':\n")

    # Check Inclusion Criteria Disruption (LT > 0.5s)
    for trial_name in trial_names:
        for phase in PHASES[2:3]:
            df = trial_phase_data[trial_name][phase]
            if len(df['time']) * ((1000 / 120) * 1000) < 0.5:
                print('Inclusion Criteria not matched.')
                print(f"Trial name: '{trial_name}' | Phase: '{phase}':\n | Deleted")
                del df
            else:
                print('Inclusion Criteria matched.')
                print(f"Trial name: '{trial_name}' | Phase: '{phase}':\n")

    # Calculate Fixations per Trial and Phase and Store in new nested dictionary -fixation_data-
    fixation_data = deepcopy(trial_phase_data)  # deepcopy (!important for dict!  structure)

    for trial_name in trial_names:  # ~ trial_phase_data.keys():
        for phase in PHASES:
            df_temp = trial_phase_data[trial_name][phase]
            x = df_temp.iloc[:, 1].tolist()
            y = df_temp.iloc[:, 2].tolist()
            time = df_temp.iloc[:, 0].tolist()
            y = [1024 - a for a in y]
            sfix, efix = fixation_detection(x, y, time, missing=0.0, maxdist=25, mindur=0.25)

            # Write fixations in pandas dataframe with labels for columns
            df_efix = pd.DataFrame(columns=['Start', 'End', 'Duration', 'X', 'Y'])

            for ef in efix:
                ef_series = pd.Series(ef, index=df_efix.columns)
                df_efix = pd.concat([df_efix, ef_series.to_frame().T], ignore_index=True)
            # Append fixation dictionary
            fixation_data[trial_name][phase] = df_efix
            # efix has the format ['Start','End','Duration', 'X', 'Y']

    # Description Dataset Fixations
    for trial_name in trial_names:  # ~ trial_phase_data.keys():
        for phase in PHASES:
            print(f"Trial name: '{trial_name}' | Phase: '{phase}':\n")
            print(len(fixation_data[trial_name][phase]))

    # Split Data from -trial_phase_data- into AOIs 'drop' and 'rise' for each trial and each phase
    # and write in new nested dictionary -trial_phase_aoi_data-

    # Two possible frames for the area of interest:
    #   Full Screen divided in four quadrants:
    #   (tp_df['gaze_point_x'] < 640) & (tp_df['gaze_point_y'] < 512)
    #   |  (tp_df['gaze_point_x'] > 640) & (tp_df['gaze_point_y'] > 512)
    #
    #   Quadrants focused on objects in corners of the screen:
    #   (tp_df['gaze_point_x'] < 478) & (tp_df['gaze_point_y'] < 382)
    #   | (tp_df['gaze_point_x'] > 802) & (tp_df['gaze_point_y'] > 642)

    trial_phase_aoi_data = deepcopy(trial_phase_data)
    for trial_name in trial_names:
        for phase in PHASES:
            tp_df = trial_phase_aoi_data[trial_name][phase]  # use short naming for code below

            # Alternative AOI tl_br_df // DROP_edge
            tl_br_df = tp_df[
                (
                        (tp_df['gaze_point_x'] < 478) & (tp_df['gaze_point_y'] < 382)
                        | (tp_df['gaze_point_x'] > 802) & (tp_df['gaze_point_y'] > 642)
                )
            ].copy()

            # Alternative AOI tr_bl_df // RISE_edge
            tr_bl_df = tp_df[
                (
                        (tp_df['gaze_point_x'] > 802) & (tp_df['gaze_point_y'] < 382)
                        | (tp_df['gaze_point_x'] < 478) & (tp_df['gaze_point_y'] > 642)
                )
            ].copy()

            # Overwrite initial df of phase in trial with dict that contains data split into two areas of interest (AOI)
            trial_phase_aoi_data[trial_name][phase] = {
                "drop": tl_br_df, "rise": tr_bl_df}  # == dict(tl_br=tl_br_df, tr_bl=tr_bl_df)

    # Calculate Fixations per Trial and Phase and AOI_Drop_edge and Store in new nested
    # dictionary -fixation_data_drop-
    fixation_data_drop = deepcopy(trial_phase_aoi_data)  # deepcopy (!important for dict!  structure)

    for trial_name in trial_names:  # ~ trial_phase_data.keys():
        for phase in PHASES:
            df_temp = trial_phase_aoi_data[trial_name][phase]["drop"]
            x = df_temp.iloc[:, 1].tolist()
            y = df_temp.iloc[:, 2].tolist()
            time = df_temp.iloc[:, 0].tolist()
            y = [1024 - a for a in y]

            sfix, efix = fixation_detection(x, y, time, missing=0.0, maxdist=25, mindur=0.25)

            # write fixations in pandas dataframe with labels for columns
            df_efix = pd.DataFrame(columns=['Start', 'End', 'Duration', 'X', 'Y'])

            for ef in efix:
                ef_series = pd.Series(ef, index=df_efix.columns)
                df_efix = pd.concat([df_efix, ef_series.to_frame().T], ignore_index=True)

            # append fixation dictionary
            fixation_data_drop[trial_name][phase]["drop"] = df_efix
            # efix has the format ['Start','End','Duration', 'X', 'Y']

    # Calculate Fixations per Trial and Phase and AOI_Rise_edge and Store in new nested
    # dictionary -fixation_data_rise-
    fixation_data_rise = deepcopy(trial_phase_aoi_data)  # deepcopy (!important for dict!  structure)

    for trial_name in trial_names:  # ~ trial_phase_data.keys():
        for phase in PHASES:
            df_temp = trial_phase_aoi_data[trial_name][phase]["rise"]
            x = df_temp.iloc[:, 1].tolist()
            y = df_temp.iloc[:, 2].tolist()
            time = df_temp.iloc[:, 0].tolist()
            y = [1024 - a for a in y]

            sfix, efix = fixation_detection(x, y, time, missing=0.0, maxdist=25, mindur=0.25)

            # write fixations in pandas dataframe with labels for columns
            df_efix = pd.DataFrame(columns=['Start', 'End', 'Duration', 'X', 'Y'])
            for ef in efix:
                ef_series = pd.Series(ef, index=df_efix.columns)
                df_efix = pd.concat([df_efix, ef_series.to_frame().T], ignore_index=True)
            # Append fixation dictionary
            fixation_data_rise[trial_name][phase]["rise"] = df_efix
            # efix has the format ['Start','End','Duration', 'X', 'Y']

    # This can be used to test dictionaries
    # *Note: You can iterate through trials and PHASES*

    for trial_name in trial_names:
        # ~ trial_phase_data.keys():  (Note: python list's are ordered, keys, hence dicts aren't)\n",
        for phase in PHASES[1:2]:  # ~ trial_phase_data[trial_name].keys():
            print(f"Trial name: '{trial_name}' | Phase: '{phase}':\n")
            print(fixation_data_rise[trial_name][phase]['rise'].head())
            print("\t\t...  ")
            print(fixation_data_rise[trial_name][phase]['rise'].tail(), "\n\n\n")
            break
        break

    # At this point all five dictionaries are build. Variables can now be extracted for further analysis.
    # trial_phase_data: contains gaze data separated into trials and PHASES
    # fixation_data: contains fixation data for trials and PHASES
    # trial_phase_aoi_data: contains only gaze data for both AOIs separated into trials and PHASES
    # fixation_data_drop: contains only fixation data for AOI drop
    # fixation_data_rise: contains only fixation data for AOI rise

    ###
    # Calculate Parameters DLS, sum, mean and std for duration for baseline phase
    ###

    # Dataframe with Sum of Duration in AOI-rise per Trial
    duration_rise = []
    list_rise = []
    for trial_name in trial_names:  # ~ trial_phase_data.keys():
        for phase in PHASES[0:1]:
            df_duration_temp = fixation_data_rise[trial_name][phase]["rise"].copy()
            duration = df_duration_temp['Duration'].sum()
            trial = trial_name
            n = [trial, duration]
            print(n)
            list_rise.append(n)
            duration_rise.append(duration)

    print(duration_rise)
    print(list_rise)
    df_rise = pd.DataFrame(list_rise, columns=['Trial', 'Duration_Rise'])
    print(df_rise)

    parameters_rise = np.array(duration_rise)
    print(f"Baseline Sum Duration AOI Rise:", np.sum(parameters_rise))
    print(f"Baseline Mean Duration AOI Rise:", np.mean(parameters_rise))
    print(f"Baseline Std Duration AOI Rise:", np.std(parameters_rise))

    # Dataframe with Sum of Duration in AOI-drop per Trial
    duration_drop = []
    list_drop = []
    for trial_name in trial_names:  # ~ trial_phase_data.keys():
        for phase in PHASES[0:1]:
            df_duration_temp = fixation_data_drop[trial_name][phase]["drop"].copy()
            duration = df_duration_temp['Duration'].sum()
            trial = trial_name
            n = [trial, duration]
            print(n)
            list_drop.append(n)
            duration_drop.append(duration)

    print(duration_drop)
    print(list_drop)
    df_drop = pd.DataFrame(list_drop, columns=['Trial', 'Duration_Drop'])
    print(df_drop)

    parameters_drop = np.array(duration_drop)
    print(f"Baseline Sum Duration per Trial AOI Drop:", duration_drop)
    print(f"Baseline Mean Duration AOI Drop:", np.mean(parameters_drop))
    print(f"Baseline Std Duration AOI Drop:", np.std(parameters_drop))

    ###
    # Dataframe with Sum of Duration in AOI-rise + AOI-drop + total Duration + DLS per Trial
    ###

    df_rise['Duration_Drop'] = df_drop['Duration_Drop']
    df_rise['Duration_Sum'] = df_rise['Duration_Rise'] + df_rise['Duration_Drop']
    df_rise['DLS'] = (df_rise['Duration_Rise'] - df_rise['Duration_Drop']) / df_rise['Duration_Sum']
    df_rise['Condition'] = CONDITION
    print(df_rise)

    # Save to csv
    path = ""  # INSERT PATH
    df_rise.to_csv(os.path.join(path, f"DUR_{ID}_{CONDITION}_Baseline.csv"), sep=",")

    # Export Fixation Data to csv files per child, trial and phase

    path_fixation_overall = ""  # INSERT PATH

    trial = []

    n = str(1)
    for n in trial_names:
        for trial_name in trial_names:  # ~ trial_phase_data.keys():
            for phase in PHASES[0:1]:
                df_fix = pd.DataFrame(columns=['Start', 'End', 'Duration', 'X', 'Y', 'Trial'])
                df_fix_temp = fixation_data[trial_name][phase].copy()
                df_fix = pd.concat([df_fix, df_fix_temp], ignore_index=True)
                df_fix['Trial'] = trial_name
                df_fix.to_csv(
                    os.path.join(path_fixation_overall,
                                 f"baseline_fixation_{ID}_{CONDITION}_{trial_name}.csv"),
                    sep=",")
                n += str(1)

    ###
    # Calculate Parameters DLS, sum, mean and std for duration for contingent phase
    ###

    # Dataframe with Sum of Duration in AOI-rise per Trial
    duration_rise = []
    list_rise = []
    for trial_name in trial_names:  # ~ trial_phase_data.keys():
        for phase in PHASES[1:2]:
            df_duration_temp = fixation_data_rise[trial_name][phase]["rise"].copy()
            duration = df_duration_temp['Duration'].sum()
            trial = trial_name
            n = [trial, duration]
            print(n)
            list_rise.append(n)
            duration_rise.append(duration)

    print(duration_rise)
    print(list_rise)
    df_rise = pd.DataFrame(list_rise, columns=['Trial', 'Duration_Rise'])
    print(df_rise)

    parameters_rise = np.array(duration_rise)
    print(f"Contingent Sum Duration AOI Rise:", np.sum(parameters_rise))
    print(f"Contingent Mean Duration AOI Rise:", np.mean(parameters_rise))
    print(f"Contingent Std Duration AOI Rise:", np.std(parameters_rise))

    # Dataframe with Sum of Duration in AOI-drop per Trial
    duration_drop = []
    list_drop = []
    for trial_name in trial_names:  # ~ trial_phase_data.keys():
        for phase in PHASES[1:2]:
            df_duration_temp = fixation_data_drop[trial_name][phase]["drop"].copy()
            duration = df_duration_temp['Duration'].sum()
            trial = trial_name
            n = [trial, duration]
            print(n)
            list_drop.append(n)
            duration_drop.append(duration)

    print(duration_drop)
    print(list_drop)
    df_drop = pd.DataFrame(list_drop, columns=['Trial', 'Duration_Drop'])
    print(df_drop)

    parameters_drop = np.array(duration_drop)
    print(f"Contingent Sum Duration per Trial AOI Drop:", duration_drop)
    print(f"Contingent Sum Duration AOI Drop:", np.sum(parameters_drop))
    print(f"Contingent Mean Duration AOI Drop:", np.mean(parameters_drop))
    print(f"Contingent Std Duration AOI Drop:", np.std(parameters_drop))

    ###
    # Dataframe with Sum of Duration in AOI-rise + AOI-drop + total Duration + DLS per Trial
    ###

    df_rise['Duration_Drop'] = df_drop['Duration_Drop']
    df_rise['Duration_Sum'] = df_rise['Duration_Rise'] + df_rise['Duration_Drop']
    df_rise['DLS'] = (df_rise['Duration_Rise'] - df_rise['Duration_Drop']) / df_rise['Duration_Sum']
    df_rise['Condition'] = CONDITION
    print(df_rise)

    path = ""  # INSERT PATH
    df_rise.to_csv(os.path.join(path, f"DUR_{ID}_{CONDITION}_Contingent.csv"), sep=",")

    # Export Fixation Data to csv files per child, trial and phase

    path_fixation_overall = ""  # INSERT PATH

    trial = []

    n = str(1)
    for n in trial_names:
        for trial_name in trial_names:  # ~ trial_phase_data.keys():
            for phase in PHASES[1:2]:
                df_fix = pd.DataFrame(columns=['Start', 'End', 'Duration', 'X', 'Y', 'Trial'])
                df_fix_temp = fixation_data[trial_name][phase].copy()
                df_fix = pd.concat([df_fix, df_fix_temp], ignore_index=True)
                df_fix['Trial'] = trial_name
                df_fix.to_csv(os.path.join(
                    path_fixation_overall, f"contingent_fixation_{ID}_{CONDITION}_{trial_name}.csv"),
                    sep=",")
                n += str(1)

    ###
    # Calculate Parameters DLS, sum, mean and std for duration for disruption phase
    ###

    # Dataframe with Sum of Duration in AOI-rise per Trial
    duration_rise = []
    list_rise = []
    for trial_name in trial_names:  # ~ trial_phase_data.keys():
        for phase in PHASES[2:3]:
            df_duration_temp = fixation_data_rise[trial_name][phase]["rise"].copy()
            duration = df_duration_temp['Duration'].sum()
            trial = trial_name
            n = [trial, duration]
            print(n)
            list_rise.append(n)
            duration_rise.append(duration)

    print(duration_rise)
    print(list_rise)
    df_rise = pd.DataFrame(list_rise, columns=['Trial', 'Duration_Rise'])
    print(df_rise)

    parameters_rise = np.array(duration_rise)
    print(f"Disruption Sum Duration AOI Rise:", np.sum(parameters_rise))
    print(f"Disruption Mean Duration AOI Rise:", np.mean(parameters_rise))
    print(f"Disruption Std Duration AOI Rise:", np.std(parameters_rise))

    # Dataframe with Sum of Duration in AOI-drop per Trial
    duration_drop = []
    list_drop = []
    for trial_name in trial_names:  # ~ trial_phase_data.keys():
        for phase in PHASES[2:3]:
            df_duration_temp = fixation_data_drop[trial_name][phase]["drop"].copy()
            duration = df_duration_temp['Duration'].sum()
            trial = trial_name
            n = [trial, duration]
            print(n)
            list_drop.append(n)
            duration_drop.append(duration)

    print(duration_drop)
    print(list_drop)
    df_drop = pd.DataFrame(list_drop, columns=['Trial', 'Duration_Drop'])
    print(df_drop)

    parameters_drop = np.array(duration_drop)
    print(f"Disruption Sum Duration per Trial AOI Drop:", duration_drop)
    print(f"Disruption Mean Duration AOI Drop:", np.mean(parameters_drop))
    print(f"Disruption Std Duration AOI Drop:", np.std(parameters_drop))

    ###
    # Dataframe with Sum of Duration in AOI-rise + AOI-drop + total Duration + DLS per Trial
    ###

    df_rise['Duration_Drop'] = df_drop['Duration_Drop']
    df_rise['Duration_Sum'] = df_rise['Duration_Rise'] + df_rise['Duration_Drop']
    df_rise['DLS'] = (df_rise['Duration_Rise'] - df_rise['Duration_Drop']) / df_rise['Duration_Sum']
    df_rise['Condition'] = CONDITION
    print(df_rise)

    path = ""  # INSERT PATH
    df_rise.to_csv(os.path.join(path, f"DUR_{ID}_{CONDITION}_Disruption.csv"), sep=",")

    # Export Fixation Data to csv files per child, trial and phase
    path_fixation_overall = ""  # INSERT PATH

    trial = []

    n = str(1)
    for n in trial_names:
        for trial_name in trial_names:  # ~ trial_phase_data.keys():
            for phase in PHASES[2:3]:
                df_fix = pd.DataFrame(columns=['Start', 'End', 'Duration', 'X', 'Y', 'Trial'])
                df_fix_temp = fixation_data_rise[trial_name][phase]["rise"].copy()
                df_fix = pd.concat([df_fix, df_fix_temp], ignore_index=True)
                df_fix['Trial'] = trial_name
                if len(df_fix) != 0:
                    df_fix.to_csv(os.path.join(
                        path_fixation_overall, f"disruption_fixation_{ID}_{CONDITION}_{trial_name}.csv"),
                        sep=",")
                n += str(1)

#  o >><< o >><< o >><< o >><< o >><< o >><< o >><< o >><< o >><< o >><< o >><< o >><< o >><< o >><< o END
