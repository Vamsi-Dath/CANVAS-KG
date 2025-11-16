import subprocess
import time
import logging
import csv
import os
from dotenv import load_dotenv
import openai
from pathlib import Path
from schema.entity import Entity
from schema.relation import Relation

logging.basicConfig(level=logging.DEBUG)
load_dotenv()

def run_ollama(model:str, system_prompt:str, user_prompt:str, max_tries=10, timeout=300) -> str:
    if system_prompt:
        prompt = f"<|system|>\n{system_prompt}\n<|end|>\n<|user|>\n{user_prompt}\n<|end|>\n"
    else:
        prompt = f"<|user|>\n{user_prompt}\n<|end|>\n"
    response = None
    while response is None and max_tries > 0:
        max_tries -= 1
        try:
            result = subprocess.run(
                ["ollama", "run", model],
                input=f"{prompt}".encode("utf-8"),
                capture_output=True,
                check=True,
                timeout=timeout
            )
            response = result.stdout.decode("utf-8").strip()
        except subprocess.CalledProcessError as e:
            logging.warning(f"Ollama Error: {e}. Re-run in 5 seconds... Attempts left: {max_tries}")
            time.sleep(5)
        except KeyboardInterrupt:
            logging.warning("User KeyboardInterrupt.")
            raise
        except Exception as e:
            logging.error(f"Error: {e}. Re-run in 5 seconds... Attempts left: {max_tries}")
            time.sleep(5)

    if response is None:
        raise RuntimeError("Failed to get response from Ollama after max_tries.")
    
    logging.debug(f"Model: {model}\n""Prompt:\n {user_prompt}\n""Result: {response}\n")
    return response

def openai_chat_completion(model: str, system_prompt: str, user_prompt: str, temperature=0, max_tokens=512, max_tries=10) -> str:
    openai.api_key = os.getenv("OPENAI_KEY")
    response = None
    if system_prompt is not None:
        messages = [{"role": "system", "content": system_prompt}] + user_prompt
    else:
        messages = user_prompt
    while response is None and max_tries > 0:
        max_tries -= 1
        try:
            response = openai.chat.completions.create(
                model=model, messages=messages, temperature=temperature, max_tokens=max_tokens
            )
        except Exception as e:
            logging.warning(f"Ollama Error: {e}. Re-run in 5 seconds... Attempts left: {max_tries}")
            time.sleep(5)
    # logging.debug(f"Model: {model}\nPrompt:\n {messages}\n Result: {response.choices[0].message.content}")
    return response.choices[0].message.content


def validate_entity(entity_json: str) -> Entity:
    try:
        entity = Entity.model_validate_json(entity_json)
        logging.debug(f"Validated Entity: {entity}")
        return entity
    except Exception as e:
        logging.error(f"Validation error: {e}")
        raise

def validate_relation(relation_json: str) -> Relation:
    try:
        relation = Relation.model_validate_json(relation_json)
        logging.debug(f"Validated Relation: {relation}")
        return relation
    except Exception as e:
        logging.error(f"Validation error: {e}")
        raise

def save_e_to_csv(output_dir: str, output_file_name: str, entities: list[Entity]) -> None:
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    output_file_path = Path(output_dir)/output_file_name
    try:
        with open(output_file_path, mode='w+', newline='', encoding='utf-8') as f:
            fieldnames = Entity.model_fields.keys()
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for idx, entity in enumerate(entities):
                entity_dict = entity.model_dump()
                entity_dict['idx'] = idx
                writer.writerow(entity_dict)
        logging.info(f"Entities: {len(entities)} saved to {output_file_path}")
    except Exception as e:
        logging.error(f"Error saving to {output_file_path}: {e}")
        raise

def save_r_to_csv(output_dir: str, output_file_name: str, relations: list[Relation]) -> None:
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    output_file_path = Path(output_dir)/output_file_name
    try:
        with open(output_file_path, mode='w+', newline='', encoding='utf-8') as f:
            fieldnames = Relation.model_fields.keys()
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for id, relation in enumerate(relations):
                relation_dict = relation.model_dump()
                relation_dict['id'] = id
                writer.writerow(relation_dict)
        logging.info(f"Relations: {len(relations)} saved to {output_file_path}")
    except Exception as e:
        logging.error(f"Error saving to {output_file_path}: {e}")
        raise

def remove_duplicates_from_e_csv(input_file_path: Path, output_file_path: Path) -> None:
    try:
        unique_entities = {}
        with open(input_file_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                key = (row['name'].lower(), row['category'].lower(), row['type'].lower())
                if key not in unique_entities:
                    unique_entities[key] = row
            
        with open(output_file_path, mode='w+', newline='', encoding='utf-8') as f:
            fieldnames = Entity.model_fields.keys()
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for idx, entity in enumerate(unique_entities.values()):
                entity['idx'] = idx
                writer.writerow(entity)
        logging.info(f"Removed duplicates, no. of unique entities: {len(unique_entities)}")

    except Exception as e:
        logging.error(f"Error removing duplicates from {input_file_path} to {output_file_path}: {e}")
        raise

def remove_duplicates_from_r_csv(input_file_path: Path, output_file_path: Path) -> None:
    try:
        unique_relations = {}
        with open(input_file_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                key = (row['subject_entity_id'], row['object_entity_id'], row['predicate'].lower())
                if key not in unique_relations:
                    unique_relations[key] = row
            
        with open(output_file_path, mode='w+', newline='', encoding='utf-8') as f:
            fieldnames = Relation.model_fields.keys()
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for id, relation in enumerate(unique_relations.values()):
                relation['id'] = id
                writer.writerow(relation)
        logging.info(f"Removed duplicates, no. of unique relations: {len(unique_relations)}")

    except Exception as e:
        logging.error(f"Error removing duplicates from {input_file_path} to {output_file_path}: {e}")
        raise
