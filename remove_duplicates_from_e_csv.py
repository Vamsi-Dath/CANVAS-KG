from pathlib import Path
from utils.helper import remove_duplicates_from_e_csv
if __name__ == "__main__":
    output_dir = "./data/output/"
    output_file_name = "output.csv"
    remove_duplicates_from_e_csv(
            input_file_path=Path(output_dir)/output_file_name,
            output_file_path=Path(output_dir)/f"unq_{output_file_name}"
        )