import os
import pandas as pd
from datetime import datetime
from pathlib import Path

def clean_and_merge_trials(base_dirs, output_dir, debounce_threshold=1.0):
    """
    Clean and merge trial 3 and trial 4 data for each participant.

    Args:
        base_dirs (list): List of directories for different participant groups (e.g., text, voice).
        output_dir (str): Path to save cleaned and merged CSVs.
        debounce_threshold (float): Minimum seconds between valid button presses to count as separate.

    Returns:
        list of str: List of saved cleaned file paths.
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    saved_files = []

    for base_dir in base_dirs:
        group_label = os.path.basename(base_dir.rstrip("/\\"))
        group_output_dir = os.path.join(output_dir, group_label)
        Path(group_output_dir).mkdir(parents=True, exist_ok=True)

        for participant_folder in os.listdir(base_dir):
            participant_path = os.path.join(base_dir, participant_folder)
            if not os.path.isdir(participant_path):
                continue

            # Identify trial 3 and 4 files
            trial_files = [f for f in os.listdir(participant_path) if f.endswith('.csv')]
            trial3_file = next((f for f in trial_files if 'Trial3' in f), None)
            trial4_file = next((f for f in trial_files if 'Trial4' in f), None)

            if not trial3_file or not trial4_file:
                continue

            # Load and concatenate
            df3 = pd.read_csv(os.path.join(participant_path, trial3_file), header=0, sep=';')
            df4 = pd.read_csv(os.path.join(participant_path, trial4_file), header=0, sep=';')
            df = pd.concat([df3, df4], ignore_index=True)
            # Step 1: Clean column names
            # Step 1: Clean column names
            df.columns = [col.strip() for col in df.columns]

            # Step 2: Detect button press columns dynamically
            inform_col = [col for col in df.columns if col.lower().endswith('inform')][0]
            intervene_col = [col for col in df.columns if col.lower().endswith('intervene')][0]
            # Step 3: Convert to bools
            df[inform_col] = df[inform_col].astype(str).str.strip().str.lower().map(
                {'true': True, 'false': False}).fillna(False)
            df[intervene_col] = df[intervene_col].astype(str).str.strip().str.lower().map(
                {'true': True, 'false': False}).fillna(False)

            # Step 4: Drop rows with timestamp 0
            df = df[df['Carla Interface.time'] != 0]

            # Step 5: Time columns
            df['time'] = pd.to_datetime(df['Carla Interface.time'].astype('int64'))
            df['rel_time'] = (df['time'] - df['time'].iloc[0]).dt.total_seconds()

            # Step 6: Apply cleaning
            df['inform_clean'] = collapse_consecutive_true(df[inform_col])
            df['intervene_clean'] = collapse_consecutive_true(df[intervene_col])
            print(f"Inform presses kept: {df['inform_clean'].sum()}")
            print(f"Intervene presses kept: {df['intervene_clean'].sum()}")
            # Save cleaned version
            participant_id = participant_folder.split('-')[0].strip()
            save_path = os.path.join(group_output_dir, f"{participant_id}.csv")
            df.to_csv(save_path, index=False)
            saved_files.append(save_path)

    return saved_files

def collapse_consecutive_true(series):
    """
    Collapse consecutive True values into a single True, rest False.
    """
    cleaned = []
    prev = False
    for val in series:
        if val and not prev:
            cleaned.append(True)
            prev = True
        else:
            cleaned.append(False)
            if not val:
                prev = False
    return cleaned

def summarize_cleaned_data(cleaned_dir, group_label):
    """
    Summarizes inform/intervene counts per participant.

    Args:
        cleaned_dir (str): Folder with cleaned CSVs.
        group_label (str): 'text' or 'voice', used to tag participant group.

    Returns:
        DataFrame with participant_id, group, n_inform, n_intervene, total_presses
    """
    summary_rows = []

    for file in os.listdir(cleaned_dir):
        if not file.endswith(".csv"):
            continue
        participant_id = Path(file).stem  # gets "R_xxxxx" from "R_xxxxx.csv"
        df = pd.read_csv(os.path.join(cleaned_dir, file))

        n_inform = df['inform_clean'].sum()
        n_intervene = df['intervene_clean'].sum()
        total = n_inform + n_intervene

        summary_rows.append({
            'participant_id': participant_id,
            'group': group_label,
            'n_inform': int(n_inform),
            'n_intervene': int(n_intervene),
            'total_presses': int(total)
        })

    return pd.DataFrame(summary_rows)



if __name__ == "__main__":
    # Set your paths here
    base_dirs = ["DataGroup1", "DataGroup2"]  # Adjust if needed
    output_dir = "CleanedData"

    cleaned_files = clean_and_merge_trials(base_dirs, output_dir)
    print(f"✅ Cleaned {len(cleaned_files)} files and saved them to {output_dir}")

    df_text = summarize_cleaned_data("CleanedData/DataGroup1", group_label="text")
    df_voice = summarize_cleaned_data("CleanedData/DataGroup2", group_label="voice")

    df_all = pd.concat([df_text, df_voice], ignore_index=True)
    df_all.to_csv("participant_press_summary.csv", index=False)
    print("✅ Summary saved to participant_press_summary.csv")


