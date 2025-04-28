import pandas as pd

def merge_cleaned_data(survey_csv, presses_csv, output_path="MergedData.csv"):
    # Load both datasets
    df_survey = pd.read_csv(survey_csv)
    df_presses = pd.read_csv(presses_csv)

    # Strip IDs just in case
    df_survey['ResponseId'] = df_survey['ResponseId'].str.strip()
    df_presses['participant_id'] = df_presses['participant_id'].str.strip()

    # Merge on ID
    df_merged = pd.merge(df_survey, df_presses, left_on='ResponseId', right_on='participant_id', how='inner')

    # Drop duplicate column if needed
    df_merged = df_merged.drop(columns=['participant_id'])

    # Save merged file
    df_merged.to_csv(output_path, index=False)
    print(f"✅ Merged data saved to: {output_path}")
    return df_merged

# Usage
merged_df = merge_cleaned_data("CleanedSurvey.csv", "participant_press_summary.csv")
