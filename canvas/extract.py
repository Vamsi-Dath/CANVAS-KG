from utils.helper import run_ollama, validate_entity, validate_relation, save_e_to_csv, save_r_to_csv, remove_duplicates_from_e_csv, remove_duplicates_from_r_csv, openai_chat_completion, read_docx_file
from schema.entity import Entity
from schema.relation import Relation
import logging
from pathlib import Path
import json
from datetime import datetime

logger = logging.getLogger(__name__)
class Extractor:
    def __init__(self, input_text_file_path: str, output_dir: str, output_file_name: str, entity_bank_json_path: str, system_prompt_template_path: str, relationship_extraction_template_path: str, openai_model: str, local_model: str, valid_start_time: datetime, valid_end_time: datetime) -> None:
        self.input_text_file_path = input_text_file_path
        self.output_dir = output_dir
        self.output_file_name = output_file_name
        self.entity_bank_json_path = entity_bank_json_path
        self.system_prompt_template_path = system_prompt_template_path
        self.relationship_extraction_template_path = relationship_extraction_template_path
        self.openai_model = openai_model
        self.local_model = local_model
        self.valid_start_time = valid_start_time
        self.valid_end_time = valid_end_time

    def extract_json_objects(self, text: str) -> list[str]:
        json_objects = []
        start = None
        count = 0
        failed = 0
        for i, ch in enumerate(text):
            if ch == '{':
                if not count:
                    start = i
                count += 1
            elif ch == '}':
                count -= 1
                if not count and start is not None:
                        json_str = text[start:i+1]
                        try:
                            json_obj = json.loads(json_str)
                            json_objects.append(json_obj)
                        except json.JSONDecodeError:
                            failed += 1
                        start = None
        if failed > 0:
            logging.warning(f"Failed to decode JSON objects: {failed}")
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

            response = run_ollama(self.local_model, system_prompt, user_prompt)
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

        if self.input_text_file_path.endswith('.docx'):
            text = read_docx_file(self.input_text_file_path)
        else:
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
            response = run_ollama(self.local_model, system_prompt, user_prompt)

        logger.info(f"File run status: Completed")
        raw_jsons = self.extract_json_objects(response)
        logging.info(f"\tExtracted entities count: {len(raw_jsons)}")
        raw_entities = raw_entities + raw_jsons

        entities = []
        for e in raw_entities:
            e["valid_start_time"] = self.valid_start_time.strftime("%Y-%m-%d %H:%M:%S")
            e["valid_end_time"] = self.valid_end_time.strftime("%Y-%m-%d %H:%M:%S")
            e_json = json.dumps(e)
            try:
                entities.append(validate_entity(e_json))
            except Exception as ve:
                logging.warning(f"Skipping Entity: {e_json}, due to failed pydantic validation")
                continue
        logging.info(f"Total validated entities count: {len(entities)}\n")

        dir = Path(self.output_dir)/Path(self.input_text_file_path).stem/"entities"
        
        if self.openai_model:
            dir = dir / self.openai_model
        elif self.local_model:
            dir = dir / self.local_model
        else:
            dir = dir / "unknown_model"

        dir.mkdir(parents=True, exist_ok=True)
        if self.output_dir and self.output_file_name and self.output_file_name.endswith('.csv'):
            save_e_to_csv(dir, self.output_file_name, entities)
        
        remove_duplicates_from_e_csv(
            input_file_path=dir / self.output_file_name,
            output_file_path=dir / f"unq_{self.output_file_name}"
        )

        return entities
    
    def extract_realtions_by_file(self) -> list[Relation]:
        extracted_relations = []

        if self.input_text_file_path.endswith('.docx'):
            text = self.read_docx_file(self.input_text_file_path)
        else:
            text = open(self.input_text_file_path, 'r', encoding='utf-8').read()

        dir = Path(self.output_dir) / Path(self.input_text_file_path).stem / "nlp_processed_entities"

        if self.openai_model:
            dir = dir / self.openai_model
        elif self.local_model:
            dir = dir / self.local_model
        else:
            dir = dir / "unknown_model"

        dedup_file = dir / "nlp_processed_entities_dedup.csv"

        with open(dedup_file, 'r', encoding='utf-8') as f:
            extracted_entities = f.read()


        realtionship_extraction_template = open(self.relationship_extraction_template_path, 'r', encoding='utf-8').read()
        system_prompt = realtionship_extraction_template.format_map({
            "extracted_entities": extracted_entities
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
            response = run_ollama(self.local_model, system_prompt, user_prompt)

        logger.info(f"File run status: Completed")
        raw_jsons = self.extract_json_objects(response)
        logging.info(f"\tExtracted relations count: {len(raw_jsons)}")
        extracted_relations = extracted_relations + raw_jsons

        relations = []
        for r in extracted_relations:
            r["valid_start_time"] = self.valid_start_time.strftime("%Y-%m-%d %H:%M:%S")
            r["valid_end_time"] = self.valid_end_time.strftime("%Y-%m-%d %H:%M:%S")
            r_json = json.dumps(r)
            try:
                relations.append(validate_relation(r_json))
            except Exception as ve:
                logging.warning(f"Skipping Relation: {r_json}, due to failed pydantic validation")
                continue
        logging.info(f"Total validated relations count: {len(relations)}\n")

        dir = Path(self.output_dir)/Path(self.input_text_file_path).stem/Path("relations")

        if self.openai_model:
            dir = dir / self.openai_model
        elif self.local_model:
            dir = dir / self.local_model
        else:
            dir = dir / "unknown_model"

        dir.mkdir(parents=True, exist_ok=True)
        if self.output_dir and self.output_file_name and self.output_file_name.endswith('.csv'):
            save_r_to_csv(dir, self.output_file_name, relations)

        remove_duplicates_from_r_csv(
            input_file_path=dir / self.output_file_name,
            output_file_path=dir / f"unq_{self.output_file_name}"
        )

        return relations
