from argparse import ArgumentParser
from canvas.canvas_framework import CanvasKG

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument(
        "--input_text_file_path",
        default = "./data/input/example.txt",
        type = str,
        help = "File from which KG is extracted, where each line is a piece of text."
    )
    parser.add_argument(
        "--output_dir",
        default = "./data/output/",
        type = str,
        help = "Directory to save the extracted KG."
    )
    args = parser.parse_args()
    args = vars(args)
    canvas_kg = CanvasKG(**args)
    canvas_kg.run()