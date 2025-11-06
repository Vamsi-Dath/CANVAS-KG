import logging
from importlib import reload
from utils.helper import run_ollama
from canvas.extract import Extractor

reload(logging)
logger = logging.getLogger(__name__)
class CanvasKG:
    def __init__(self, **kwargs) -> None:
        logging.basicConfig(level=logging.INFO)
        logger.info("Intializing CanvasKG")

        self.input_text_file_path = kwargs.get("input_text_file_path", "./data/input/example.txt")
        self.output_dir = kwargs.get("output_dir", "./data/output/")

        logger.info(f"Input text file path set to: {self.input_text_file_path}")
        logger.info(f"Output directory set to: {self.output_dir}")

    def run(self) -> None:
        logger.info("\n\tCanvasKG run starts...\n")
        extractor = Extractor(self.input_text_file_path,
                              self.output_dir,
                              output_file_name="output.csv")
        extracted_entities = extractor.extract_entities()
        logger.info(f"Extracted Entities: {extracted_entities}")
        logger.info("\n\tCanvasKG run ends.\n")
        return None