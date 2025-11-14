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
    parser.add_argument(
        "--output_file_name",
        default = "output.csv",
        type = str,
        help = "File to which the extracted entities are saved."
    )
    parser.add_argument(
        "--entity_bank_json_path",
        default = "./data/Entity_Bank.json",
        type = str,
        help = "Path to the entity bank JSON file."
    )
    parser.add_argument(
        "--system_prompt_template_path",
        default = "./prompts/system_prompt_template.txt",
        type = str,
        help = "Path to the system prompt template file."
    )
    parser.add_argument(
        "--relationship_extraction_template_path",
        default = "./prompts/relationship_extraction_template.txt",
        type = str,
        help = "Path to the relationship extraction prompt template file."
    )
    parser.add_argument(
        "--openai_model",
        default = None,
        type = str,
        help = "OpenAI model to use for processing."
    )
    parser.add_argument(
        "--local_model",
        default = "llama3.1:8b",
        type = str,
        help = "Local on-device model usage."
    )   
    args = parser.parse_args()
    args = vars(args)
    canvas_kg = CanvasKG(**args)
    canvas_kg.run()