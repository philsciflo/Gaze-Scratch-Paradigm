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
import argparse
from copy import deepcopy
import os

import pandas as pd
import numpy as np

# %% Set global vars & paths  >><< o >><< o >><< o >><< o >><< o >><< o >><< o >><< o >><< o >><< o >><< o

# Vars to set manually (these are default values for arg-parser below)
ID: str = "ID_52b"  # subject ID
CONDITION: str = "Rise"  # condition for Rise/Drop Trials

# Pass the file path
DATA_PATH: str = ""  # INSERT PATH TO DATA FILES IF REQUIRED
SAVE_PATH_DF_RISE: str = ""  # INSERT PATH TO SAVE DF
SAVE_PATH_FIXATION_OVERALL: str = ""  # INSERT PATH TO SAVE FIXATION OVERALL

# Globals vars
PHASES = ["baseline", "contingent", "disruption"]
FILES_GSP = os.listdir(DATA_PATH)
TRIAL_NAMES = sorted([trial_fn.split("_")[0] for trial_fn in FILES_GSP])


# %% Functions  >><< o >><< o >><< o >><< o >><< o >><< o >><< o >><< o >><< o >><< o >><< o >><< o >><< o

def download_study_data(stimuli_only: bool, verbose: bool = False) -> None:
    """Download study data from OSF."""
    import shutil
    from urllib.request import urlretrieve
    import zipfile

    # Download data
    if verbose:
        print("Downloading data from OSF ...")
    fname, headers = urlretrieve(
        url="https://files.de-1.osf.io/v1/resources/xrbzg/providers/osfstorage/"
            "?view_only=13cf79f5e8eb47afab6982fb1731cd12&zip=",
        # TODO update when OSF is public
        filename="osfstorage-archive.zip")
    if verbose:
        print(f"Data downloaded to '{fname}'.")

    # Unzip data
    with zipfile.ZipFile(fname, 'r') as zip_ref:
        zip_ref.extractall()

    # Remove zip file
    os.remove(fname)
    data_dir: str = "Data"
    if stimuli_only:
        # Remove data files
        shutil.rmtree(data_dir)
        if verbose:
            print(f"{data_dir} directory and it files removed.")
    else:
        # Unpack Data
        path_to_data_zip = os.path.join(data_dir, data_dir+".zip")
        with zipfile.ZipFile(path_to_data_zip, 'r') as zip_ref:
            zip_ref.extractall()
        # Remove zip file
        os.remove(path_to_data_zip)

    # Remove __MACOSX folder
    shutil.rmtree("__MACOSX", ignore_errors=True)

    # Print files in data directory
    if verbose:
        if not stimuli_only:
            print(f"List dir: 'Data':")
            print(os.listdir("Data"))
        print(f"\nList dir: 'Stimuli':")
        print(os.listdir("Stimuli"))


def fixation_detection(x, y, time, max_dist: int = 25, min_dur: float = 0.25):
    """
    Get fixations.

    This is from the PyTrack project (https://github.com/titoghose/PyTrack).

    :param x:
    :param y:
    :param time:
    :param max_dist:
    :param min_dur:
    :return:
    """
    # Empty list to contain data
    s_fix = []
    e_fix = []

    # Loop through all coordinates
    si = 0
    fix_start = False
    for i in range(1, len(x)):
        # calculate Euclidean distance from the current fixation coordinate
        # to the next coordinate
        dist = ((x[si] - x[i]) ** 2 + (y[si] - y[i]) ** 2) ** 0.5
        # check if the next coordinate is below maximal distance
        if dist <= max_dist and not fix_start:
            # start a new fixation
            si = 0 + i
            fix_start = True
            s_fix.append([time[i]])
        elif dist > max_dist and fix_start:
            # end the current fixation
            fix_start = False
            # only store the fixation if the duration is ok
            if abs(time[i - 1] - s_fix[-1][0]) >= min_dur:
                e_fix.append([s_fix[-1][0], time[i - 1], time[i - 1] - s_fix[-1][0], x[si], y[si]])
            # delete the last fixation start if it was too short
            else:
                s_fix.pop(-1)
            si = 0 + i
        elif not fix_start:
            si += 1

    return s_fix, e_fix


def compute_df_e_fix(current_df: pd.DataFrame) -> pd.DataFrame:
    x_i = current_df.iloc[:, 1].tolist()
    y_j = current_df.iloc[:, 2].tolist()
    time_t = current_df.iloc[:, 0].tolist()
    y_j = [1024 - a for a in y_j]

    _s_fix, _e_fix = fixation_detection(x=x_i, y=y_j, time=time_t, max_dist=25, min_dur=0.25)

    # Write fixations in pandas dataframe with labels for columns
    df_e_fix = pd.DataFrame(columns=['Start', 'End', 'Duration', 'X', 'Y'])

    for ef in _e_fix:
        ef_series = pd.Series(ef, index=df_e_fix.columns)
        df_e_fix = pd.concat([df_e_fix, ef_series.to_frame().T], ignore_index=True)

    return df_e_fix


def compute_duration_rise(current_phase: str, fix_data_rise) -> pd.DataFrame:
    duration_rise = []
    list_rise = []
    for tr_name in TRIAL_NAMES:  # ~ trial_phase_data.keys():
        df_duration_temp_ = fix_data_rise[tr_name][current_phase]["rise"].copy()
        duration = df_duration_temp_['Duration'].sum()
        _n = [tr_name, duration]
        print(_n)
        list_rise.append(_n)
        duration_rise.append(duration)

    print(duration_rise)
    print(list_rise)
    _df_rise = pd.DataFrame(list_rise, columns=['Trial', 'Duration_Rise'])
    print(_df_rise)

    print(f"Baseline Sum Duration AOI Rise:", np.sum(duration_rise))
    print(f"Baseline Mean Duration AOI Rise:", np.mean(duration_rise))
    print(f"Baseline Std Duration AOI Rise:", np.std(duration_rise))

    return _df_rise


def compute_duration_drop(current_phase: str, fix_data_drop) -> pd.DataFrame:
    # Dataframe with Sum of Duration in AOI-drop per Trial
    duration_drop = []
    list_drop = []
    for tr_name in TRIAL_NAMES:  # ~ trial_phase_data.keys():
        df_duration_temp = fix_data_drop[tr_name][current_phase]["drop"].copy()
        duration = df_duration_temp['Duration'].sum()
        _n = [tr_name, duration]
        print(_n)
        list_drop.append(_n)
        duration_drop.append(duration)

    print(duration_drop)
    print(list_drop)
    _df_drop = pd.DataFrame(list_drop, columns=['Trial', 'Duration_Drop'])
    print(_df_drop)

    print(f"Baseline Sum Duration per Trial AOI Drop:", np.sum(duration_drop))
    print(f"Baseline Mean Duration AOI Drop:", np.mean(duration_drop))
    print(f"Baseline Std Duration AOI Drop:", np.std(duration_drop))

    return _df_drop


def add_drop_and_save(current_df_rise: pd.DataFrame, current_df_drop: pd.DataFrame,
                      condition: str, save_dir: str) -> None:
    current_df_rise['Duration_Drop'] = current_df_drop['Duration_Drop']
    current_df_rise['Duration_Sum'] = current_df_rise['Duration_Rise'] + current_df_rise['Duration_Drop']
    current_df_rise['DLS'] = (current_df_rise['Duration_Rise'] -
                              current_df_rise['Duration_Drop']) / current_df_rise['Duration_Sum']
    current_df_rise['Condition'] = condition
    print(current_df_rise)

    # Save to csv
    current_df_rise.to_csv(os.path.join(
        save_dir, f"DUR_{FLAGS.id}_{condition}_Baseline.csv"), sep=",")


def df_fix_to_csv(current_phase: str, fix_data):
    """Saves Fixation Data to csv files per child, trial and phase"""
    for tr_name in TRIAL_NAMES:  # ~ trial_phase_data.keys():
        _df_fix = pd.DataFrame(columns=['Start', 'End', 'Duration', 'X', 'Y', 'Trial'])
        _df_fix_temp = fix_data[tr_name][current_phase].copy()
        _df_fix = pd.concat([_df_fix, _df_fix_temp], ignore_index=True)
        _df_fix['Trial'] = tr_name
        if len(_df_fix) != 0:
            _df_fix.to_csv(os.path.join(
                SAVE_PATH_FIXATION_OVERALL,
                f"{current_phase}_fixation_{FLAGS.id}_{FLAGS.condition}_{tr_name}.csv"), sep=",")


def main():
    # Load csv files for one participant and define names for trials and PHASES.
    # So far you can only process one participant in one condition of the gaze scratch paradigm at a time
    print("Trial names:\n", TRIAL_NAMES)

    # Split Raw Data into trials and PHASES and write in nested dictionary
    trial_phase_data = {}
    for trial_name in TRIAL_NAMES:
        # Read whole trial data
        trial_data = pd.read_csv(os.path.join(DATA_PATH, trial_name))

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
    for trial_name in TRIAL_NAMES:  # ~ trial_phase_data.keys():
        for phase in PHASES:
            trial_phase_data[trial_name][phase].dropna(inplace=True)
            trial_phase_data[trial_name][phase].reset_index(inplace=True, drop=True)

    # Sampling rate 120 hz / sampling length 8.3333 ms
    # We pre-registered inclusion criteria for each trial
    # Check Inclusion Criteria
    th_dict = {'baseline': 1, 'contingent': 10, 'disruption': .5}  # in seconds
    for phase in PHASES:
        for trial_name in TRIAL_NAMES:
            df = trial_phase_data[trial_name][phase]
            if len(df['time']) * ((1000 / 120) * 1000) < th_dict[phase]:
                print('Inclusion Criteria not matched.')
                print(f"Trial name: '{trial_name}' | Phase: '{phase}':\n | Deleted")
                del df
            else:
                print('Inclusion Criteria matched.')
                print(f"Trial name: '{trial_name}' | Phase: '{phase}':\n")

    # Calculate Fixations per Trial and Phase and Store in new nested dictionary -fixation_data-
    fixation_data = deepcopy(trial_phase_data)  # deepcopy (!important for dict!  structure)

    for trial_name in TRIAL_NAMES:  # ~ trial_phase_data.keys():
        for phase in PHASES:
            df_temp = trial_phase_data[trial_name][phase]
            # Append fixation dictionary
            fixation_data[trial_name][phase] = compute_df_e_fix(df_temp)
            # _e_fix has the format ['Start','End','Duration', 'X', 'Y']

    # Description Dataset Fixations
    for trial_name in TRIAL_NAMES:  # ~ trial_phase_data.keys():
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
    for trial_name in TRIAL_NAMES:
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

            # Overwrite initial df of phase in trial with dict that contains data split into two areas
            # of interest (AOI)
            trial_phase_aoi_data[trial_name][phase] = {
                "drop": tl_br_df, "rise": tr_bl_df}  # == dict(tl_br=tl_br_df, tr_bl=tr_bl_df)

    # Calculate Fixations per Trial and Phase and AOI_Drop_edge and Store in new nested
    # dictionary -fixation_data_drop-
    fixation_data_drop = deepcopy(trial_phase_aoi_data)  # deepcopy (!important for dict! structure)

    for trial_name in TRIAL_NAMES:  # ~ trial_phase_data.keys():
        for phase in PHASES:
            df_temp = trial_phase_aoi_data[trial_name][phase]["drop"]
            # append fixation dictionary
            fixation_data_drop[trial_name][phase]["drop"] = compute_df_e_fix(df_temp)
            # _e_fix has the format ['Start','End','Duration', 'X', 'Y']

    # Calculate Fixations per Trial and Phase and AOI_Rise_edge and Store in new nested
    # dictionary -fixation_data_rise-
    fixation_data_rise = deepcopy(trial_phase_aoi_data)  # deepcopy

    for trial_name in TRIAL_NAMES:  # ~ trial_phase_data.keys():
        for phase in PHASES:
            df_temp = trial_phase_aoi_data[trial_name][phase]["rise"]
            # Append fixation dictionary
            fixation_data_rise[trial_name][phase]["rise"] = compute_df_e_fix(df_temp)
            # _e_fix has the format ['Start','End','Duration', 'X', 'Y']

    # This can be used to test dictionaries
    # *Note: You can iterate through trials and PHASES*
    for trial_name in TRIAL_NAMES:
        # ~ trial_phase_data.keys():  (Note: python list's are ordered, keys, hence dicts aren't)\n",
        for phase in PHASES:  # ~ trial_phase_data[trial_name].keys():
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
    df_rise = compute_duration_rise(current_phase=PHASES[0],  # baseline phase
                                    fix_data_rise=fixation_data_rise)

    # Dataframe with Sum of Duration in AOI-drop per Trial
    df_drop = compute_duration_drop(current_phase=PHASES[0],
                                    fix_data_drop=fixation_data_drop)

    ###
    # Dataframe with Sum of Duration in AOI-rise + AOI-drop + total Duration + DLS per Trial
    ###
    add_drop_and_save(current_df_rise=df_rise, current_df_drop=df_drop, condition=FLAGS.condition,
                      save_dir=SAVE_PATH_DF_RISE)

    # Export Fixation Data to csv files per child, trial and phase
    df_fix_to_csv(current_phase=PHASES[0], fix_data=fixation_data)

    ###
    # Calculate Parameters DLS, sum, mean and std for duration for contingent phase
    ###

    # Dataframe with Sum of Duration in AOI-rise per Trial
    df_rise = compute_duration_rise(current_phase=PHASES[1],  # contingent phase
                                    fix_data_rise=fixation_data_rise)

    # Dataframe with Sum of Duration in AOI-drop per Trial
    df_drop = compute_duration_drop(current_phase=PHASES[1],
                                    fix_data_drop=fixation_data_drop)

    ###
    # Dataframe with Sum of Duration in AOI-rise + AOI-drop + total Duration + DLS per Trial
    ###
    add_drop_and_save(current_df_rise=df_rise, current_df_drop=df_drop, condition=FLAGS.condition,
                      save_dir=SAVE_PATH_DF_RISE)

    # Export Fixation Data to csv files per child, trial and phase
    df_fix_to_csv(current_phase=PHASES[1], fix_data=fixation_data)

    ###
    # Calculate Parameters DLS, sum, mean and std for duration for disruption phase
    ###

    # Dataframe with Sum of Duration in AOI-rise per Trial
    df_rise = compute_duration_rise(current_phase=PHASES[2],  # disruption phase
                                    fix_data_rise=fixation_data_rise)

    # Dataframe with Sum of Duration in AOI-drop per Trial
    df_drop = compute_duration_drop(current_phase=PHASES[2],  # disruption phase
                                    fix_data_drop=fixation_data_drop)

    ###
    # Dataframe with Sum of Duration in AOI-rise + AOI-drop + total Duration + DLS per Trial
    ###
    add_drop_and_save(current_df_rise=df_rise, current_df_drop=df_drop, condition=FLAGS.condition,
                      save_dir=SAVE_PATH_DF_RISE)

    # Export Fixation Data to csv files per child, trial and phase
    phase = PHASES[2]
    for trial_name in TRIAL_NAMES:  # ~ trial_phase_data.keys():
        df_fix = pd.DataFrame(columns=['Start', 'End', 'Duration', 'X', 'Y', 'Trial'])
        df_fix_temp = fixation_data_rise[trial_name][phase]["rise"].copy()
        df_fix = pd.concat([df_fix, df_fix_temp], ignore_index=True)
        df_fix['Trial'] = trial_name
        if len(df_fix) != 0:
            df_fix.to_csv(os.path.join(
                SAVE_PATH_FIXATION_OVERALL,
                f"{phase}_fixation_{FLAGS.id}_{FLAGS.condition}_{trial_name}.csv"), sep=",")


# %% __main__ o >><< o >><< o >><< o >><< o >><< o >><< o >><< o >><< o >><< o >><< o >><< o >><< o >><< o

if __name__ == "__main__":
    # Setup parser
    parser = argparse.ArgumentParser(description='Process subject in specific condition.')
    parser.add_argument('--id', type=str, help='Subject ID', default=ID)
    parser.add_argument('-c', '--condition', type=str, help='Condition', default=CONDITION)

    # Parse arguments
    FLAGS, unparsed = parser.parse_known_args()

    # %% Run main
    main()
#  o >><< o >><< o >><< o >><< o >><< o >><< o >><< o >><< o >><< o >><< o >><< o >><< o >><< o >><< o END
