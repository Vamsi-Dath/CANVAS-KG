from utils.helper import run_ollama, validate_entity, save_e_to_csv, remove_duplicates_from_e_csv, openai_chat_completion
from schema.entity import Entity
import logging
from pathlib import Path
import json

logger = logging.getLogger(__name__)
class Extractor:
    def __init__(self, input_text_file_path: str, output_dir: str, output_file_name: str, entity_bank_json_path: str, system_prompt_template_path: str, openai_model: str) -> None:
        self.input_text_file_path = input_text_file_path
        self.output_dir = output_dir
        self.output_file_name = output_file_name
        self.entity_bank_json_path = entity_bank_json_path
        self.system_prompt_template_path = system_prompt_template_path
        self.openai_model = openai_model

    def extract_json_objects(self, text: str) -> list[str]:
        json_objects = []
        start = None
        count = 0
        for i, ch in enumerate(text):
            if ch == '{':
                if not count:
                    start = i
                count += 1
            elif ch == '}':
                count -= 1
                if not count and start is not None:
                        json_objects.append(text[start:i+1])
                        start = None
        return json_objects
    
    """
    def extract_entities_by_line(self) -> list[Entity]:
        raw_entities = []
        for idx, line in enumerate(open(self.input_text_file_path, 'r', encoding='utf-8')):
            if not line.strip():
                logger.info(f"Line {idx} skipped: Empty line.")
                continue
            
            entity_bank_json = json.load(open(self.entity_bank_json_path, 'r', encoding='utf-8'))

            system_prompt_template = open(self.system_prompt_template_path, 'r', encoding='utf-8').read()

            system_prompt = system_prompt_template.format_map({
                "entity_bank_json": json.dumps(entity_bank_json)
            })

            user_prompt = f"Input Text:\n{line.strip()}"

            response = run_ollama("llama3.1:8b", system_prompt, user_prompt)
            logger.info(f"Line {idx} run status: Completed")
            raw_jsons = self.extract_json_objects(response)
            logging.info(f"\tLine {idx} extracted entities count: {len(raw_jsons)}")
            raw_entities = raw_entities + raw_jsons

        entities = []
        for e in raw_entities:
            try:
                entities.append(validate_entity(e))
            except Exception as ve:
                logging.warning(f"Skipping Entity: {e}, due to failed pydantic validation")
                continue
        logging.info(f"Total validated entities count: {len(entities)}\n")

        if self.output_dir and self.output_file_name and self.output_file_name.endswith('.csv'):
            save_e_to_csv(self.output_dir, self.output_file_name, entities)
        
        remove_duplicates_from_e_csv(
            input_file_path=Path(self.output_dir)/self.output_file_name,
            output_file_path=Path(self.output_dir)/f"unq_{self.output_file_name}"
        )

        return entities
    """

    def extract_entities_by_file(self) -> list[Entity]:
        raw_entities = []
        text = open(self.input_text_file_path, 'r', encoding='utf-8').read()
        
        entity_bank_json = json.load(open(self.entity_bank_json_path, 'r', encoding='utf-8'))

        system_prompt_template = open(self.system_prompt_template_path, 'r', encoding='utf-8').read()

        system_prompt = system_prompt_template.format_map({
            "entity_bank_json": json.dumps(entity_bank_json)
        })

        user_prompt = f"Input Text:\n{text}"

        if self.openai_model:
            response = openai_chat_completion(
                model=self.openai_model,
                system_prompt=system_prompt,
                user_prompt=[{"role": "user", "content": user_prompt}],
                temperature=0.7,
                max_tokens=4000
            )
        else:
            response = run_ollama("llama3.1:8b", system_prompt, user_prompt)

        logger.info(f"File run status: Completed")
        raw_jsons = self.extract_json_objects(response)
        logging.info(f"\tExtracted entities count: {len(raw_jsons)}")
        raw_entities = raw_entities + raw_jsons

        entities = []
        for e in raw_entities:
            try:
                entities.append(validate_entity(e))
            except Exception as ve:
                logging.warning(f"Skipping Entity: {e}, due to failed pydantic validation")
                continue
        logging.info(f"Total validated entities count: {len(entities)}\n")

        dir = Path(self.output_dir)/Path(self.input_text_file_path).stem
        
        if self.openai_model:
            dir = dir / self.openai_model
        else:
            dir = dir / "llama3.1_8b"
            
        dir.mkdir(parents=True, exist_ok=True)
        if self.output_dir and self.output_file_name and self.output_file_name.endswith('.csv'):
            save_e_to_csv(dir, self.output_file_name, entities)
        
        remove_duplicates_from_e_csv(
            input_file_path=dir / self.output_file_name,
            output_file_path=dir / f"unq_{self.output_file_name}"
        )

        return entities
    