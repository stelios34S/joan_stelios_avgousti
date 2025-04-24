import os
import pandas as pd
from pathlib import Path

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
    df_text = summarize_cleaned_data("CleanedData/DataGroup1", group_label="text")
    df_voice = summarize_cleaned_data("CleanedData/DataGroup2", group_label="voice")

    df_all = pd.concat([df_text, df_voice], ignore_index=True)
    df_all.to_csv("participant_press_summary.csv", index=False)
    print("✅ Summary saved to participant_press_summary.csv")
