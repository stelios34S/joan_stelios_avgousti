import pandas as pd

def process_survey_data(survey_csv_path):
    # Step 0: Load full file
    raw_df = pd.read_csv(survey_csv_path, header=None)

    # Step 1: Set the first row as header, drop 2nd and 3rd rows
    raw_df.columns = raw_df.iloc[0]
    df = raw_df.drop([0, 1, 2]).reset_index(drop=True)

    # Step 2: Strip column names
    df.columns = df.columns.str.strip()

    # Step 3: Rename columns
    df = df.rename(columns={
        'ResponseId': 'ResponseId',
        'Q1': 'age', 'Q2': 'gender', 'Q3': 'driving_experience',
        'Q4': 'av_experience', 'Q5': 'comfort_with_automation',
        'Q6': 'q6', 'Q7': 'q7', 'Q8': 'q8', 'Q9': 'q9', 'Q10': 'q10',
        'Q11': 'q11', 'Q12': 'q12', 'Q13': 'q13', 'Q14': 'q14',
        'Q15': 'q15', 'Q16': 'q16', 'Q17': 'q17',
        'Q18_1': 'rank_1', 'Q18_2': 'rank_2', 'Q18_3': 'rank_3',
        'Q19': 'why_ranked', 'Q20': 'trust_explanation',
        'Q21': 'control_buttons', 'Q22': 'final_feedback'
    })

    # Step 4: Map Likert strings to numeric values
    likert_map = {
        'Strongly Disagree': 1,
        'Disagree': 2,
        'Slightly Disagree': 3,
        'Neutral': 4,
        'Slightly Agree': 5,
        'Agree': 6,
        'Strongly Agree': 7
    }
    trust_items = [f'q{i}' for i in range(6, 18)]
    df[trust_items] = df[trust_items].replace(likert_map)

    # Step 5: Reverse score negatively worded questions
    for col in ['q7', 'q9', 'q11', 'q12', 'q14']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
        df[col] = 8 - df[col]

    # Step 6: Compute trust score (mean of q6–q17)
    df['trust_score'] = df[trust_items].astype(float).mean(axis=1)
    # Step 7: Encode other relevant fields
    df['gender'] = df['gender'].str.strip().str.lower().map({
        'male': 0,
        'female': 1,
        'other': 2
    })

    df['driving_experience'] = df['driving_experience'].str.strip().map({
        'Not experienced': 1,
        'Slightly Experienced': 2,
        'Experienced': 3,
        'Moderately Experienced': 4,
        'Very Experienced': 5
    })

    df['av_experience'] = df['av_experience'].str.strip().str.lower().map({
        'yes': 1,
        'no': 0
    })

    df['comfort_with_automation'] = df['comfort_with_automation'].replace(likert_map)
    # Step 7: Keep relevant columns
    keep_cols = ['ResponseId', 'age', 'gender', 'driving_experience',
                 'av_experience', 'comfort_with_automation',
                 'trust_score', 'rank_1', 'rank_2', 'rank_3',
                 'why_ranked', 'trust_explanation', 'control_buttons', 'final_feedback']
    df = df[keep_cols].copy()
    df['ResponseId'] = df['ResponseId'].str.strip()

    return df


survey_path = "surveydata.csv"
df_survey = process_survey_data(survey_path)
df_survey.to_csv("CleanedSurvey.csv", index=False)