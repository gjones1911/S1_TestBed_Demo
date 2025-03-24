import os
import pandas as pd
from glob import glob

def process_sensor_file(file_path):
    """
    Reads and processes a single sensor data file.
    """
    df = pd.read_csv(file_path, skiprows=6)
    df = df.iloc[:, :2]  # Keep only the first two relevant columns
    df.columns = ["timestamp", os.path.basename(file_path).replace(".csv", "")]  # Use filename as column name
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df.dropna(inplace=True)
    return df

def set_label_from_folder(folder_name, mapping):
    """
    Extracts the fault label from the folder name.
    """
    fault_key = folder_name.split("_")[-1].lower()
    return mapping.get(fault_key, "unknown")

def merge_sensor_data(directory):
    """
    Reads multiple sensor data files from subdirectories, merges per fault folder, averages duplicate timestamps, 
    propagates missing values forward, and concatenates them.
    """
    fault_mapping = {
        "baseline": 0,
        "bent_shaft": 1,
        "eccentricrotor": 2,
        "offset_misalignment": 3,
        "resonance_beam": 4,
        "imbalance": 5,
        "faulted_coupling": 6,
        "faulted_bearing": 7,
        "angular_misalignment": 8,
        "looseness": 9
    }
    
    all_fault_dfs = []
    
    for root, dirs, files in os.walk(directory):
        folder_name = os.path.basename(root)
        fault_label = set_label_from_folder(folder_name, fault_mapping)
        
        fault_df = None
        
        for file in files:
            if file.endswith(".csv"):
                file_path = os.path.join(root, file)
                df = process_sensor_file(file_path)
                
                if fault_df is None:
                    fault_df = df
                else:
                    fault_df = pd.merge(fault_df, df, on="timestamp", how="outer")
        
        if fault_df is not None:
            fault_df["status"] = fault_label  # Assign fault label from folder name
            fault_df = fault_df.groupby(["timestamp", "status"]).mean().reset_index()  # Average duplicate timestamps
            # fault_df.fillna(method='ffill', inplace=True)  # Forward fill missing values
            fault_df.ffill(inplace=True)
            fault_df.bfill(inplace=True)
            all_fault_dfs.append(fault_df)
    
    # Concatenate all merged fault data sets
    final_df = pd.concat(all_fault_dfs, ignore_index=True)
    
    # Convert timestamp to seconds since epoch
    final_df["Epoch_Seconds"] = (final_df["timestamp"] - pd.Timestamp("1970-01-01")) // pd.Timedelta(seconds=1)
    
    return final_df
def rename_columns(df):
    """
    Renames columns by replacing 'channel1_' with 'ch1_' and 'channel2_' with 'ch2_'.
    """
    df.columns = [col.replace("channel1_", "ch1_").replace("channel2_", "ch2_") for col in df.columns]
    return df

if __name__ == "__main__":
    input_directory = "path/to/your/csv/files"  # Change to your directory path
    input_directory = r"C:\Users\iLab\Desktop\Data_01302025" # root folder containing all data folders
    output_dir = r"C:\Users\iLab\GIT_REPOS\SAFE\S1_TestBed_Demo\S1_TestBed_Demo\data"
    tdir = r"C:\Users\iLab\GIT_REPOS\SAFE\S1_TestBed_Demo\S1_TestBed_Demo\code\data_parsing_tools"
    output_file = "../../data/merged_sensor_data.csv"
    output_file = output_dir + "/merged_sensor_data_2025_b.csv"
    
    merged_data = merge_sensor_data(input_directory)
    merged_data_renamed = rename_columns(merged_data)
    merged_data_renamed.to_csv(output_file, index=False)
    
    print(f"Merged data saved to {output_file}")
