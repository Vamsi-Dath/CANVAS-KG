import logging
from collections import Counter
from importlib import reload
from canvas.extract import Extractor
from canvas.nlp_processor import nlp_process_entities

reload(logging)
logger = logging.getLogger(__name__)
class CanvasKG:
    def __init__(self, **kwargs) -> None:
        logging.basicConfig(level=logging.INFO)
        logger.info("Intializing CanvasKG")

        self.input_text_file_path = kwargs.get("input_text_file_path", "./data/input/example.txt")
        self.output_dir = kwargs.get("output_dir", "./data/output/")
        self.output_file_name = kwargs.get("output_file_name", "output.csv")
        self.entity_bank_json_path = kwargs.get("entity_bank_json_path", "./data/Entity_Bank.json")
        self.system_prompt_template_path = kwargs.get("system_prompt_template_path", "./prompts/system_prompt_template.txt")
        self.relationship_extraction_template_path = kwargs.get("relationship_extraction_template_path", "./prompts/relationship_extraction_template.txt")
        self.openai_model = kwargs.get("openai_model", None)
        self.local_model = kwargs.get("local_model", "llama3.1:8b")
        logger.info(f"Input text file path set to: {self.input_text_file_path}")
        logger.info(f"Output directory set to: {self.output_dir}")
        logger.info(f"Entity bank JSON path set to: {self.entity_bank_json_path}")
        logger.info(f"System prompt template path set to: {self.system_prompt_template_path}")
        logger.info(f"OpenAI model set to: {self.openai_model}")
        if not self.openai_model:
            logger.warning(f'No OpenAI model specified. Local on-device model ({self.local_model}) will be used.')
    def run(self) -> None:
        logger.info("\n\tCanvasKG run starts...\n")
        extractor = Extractor(input_text_file_path=self.input_text_file_path,
                              output_dir=self.output_dir,
                              output_file_name=self.output_file_name,
                              entity_bank_json_path=self.entity_bank_json_path,
                              system_prompt_template_path=self.system_prompt_template_path,
                              relationship_extraction_template_path=self.relationship_extraction_template_path,
                              openai_model=self.openai_model,
                              local_model=self.local_model)
        
        # extracted_entities = extractor.extract_entities_by_line()
        extracted_entities = extractor.extract_entities_by_file()

        logger.debug(f"Extracted Entities: {[Counter(e.type) for e in extracted_entities]}")
        proper_entities = nlp_process_entities(extracted_entities, self.input_text_file_path, self.openai_model)
        logger.debug(f"Processed Entities: {[Counter(e.type) for e in proper_entities]}")

        extracted_realtions = extractor.extract_realtions_by_file()
        logger.debug(f"Extracted Relations: {[Counter(r.type) for r in extracted_realtions]}")
        # proper_relations = nlp_process_relations(extracted_realtions, self.input_text_file_path, self.openai_model)
        # logger.debug(f"Processed Relations: {[Counter(r.type) for r in proper_relations]}")

        logger.info("\n\tCanvasKG run ends.\n")
        return None