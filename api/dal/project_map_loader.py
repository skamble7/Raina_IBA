from pymongo import MongoClient
from api.config import get_settings
from typing import Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)
settings = get_settings()

client = MongoClient(settings.mongodb_uri)
db = client["Raina"]

# project_map key → (collection, id field)
PROJECTMAP_COLLECTIONS = {
    "feature_ids": ("features", "feature_id"),
    "flow_ids": ("flows", "flow_id"),
    "entity_ids": ("entities", "entity_id"),
    "persona_ids": ("personas", "persona_id"),
    "role_ids": ("roles", "role_id"),
    "story_ids": ("stories", "story_id"),
    "requirement_ids": ("requirements", "requirement_id"),
    "dag_task_ids": ("dag_tasks", "task_id"),
    "dag_definition_ids": ("dags", "dag_id"),
    "job_definition_ids": ("job_definitions", "job_id"),
    "partitioning_strategy_ids": ("partitioning_strategies", "strategy_id"),
    "checkpointing_config_ids": ("checkpointing", "checkpoint_id"),
    "trigger_mechanism_ids": ("triggers", "trigger_id"),
    "source_system_ids": ("source_systems", "source_id"),
    "raw_data_schema_ids": ("raw_data_schemas", "schema_id"),
    "target_data_model_ids": ("target_data_models", "model_id"),
    "lineage_definition_ids": ("lineage_definitions", "lineage_id"),
    "data_dictionary_ids": ("data_dictionaries", "dictionary_id"),
    "data_quality_rule_ids": ("data_quality_rules", "rule_id"),
    "transformation_rule_ids": ("transformation_rules", "rule_id"),
}

def load_project_artifacts(project_id: str) -> Tuple[str, Dict[str, List[Dict]], Dict]:
    logger.info(f"[IBA] Loading artifacts for project: {project_id}")

    project_map = db["project_map"].find_one({"project_id": project_id})
    if not project_map:
        raise ValueError(f"No project map found for project_id: {project_id}")

    artifacts: Dict[str, List[Dict]] = {}

    for key, (collection, id_field) in PROJECTMAP_COLLECTIONS.items():
        ids = project_map.get(key, [])
        if ids:
            results = list(db[collection].find({id_field: {"$in": ids}}))
            artifacts[collection] = results
        else:
            artifacts[collection] = []

    paradigm = project_map.get("paradigm", "application")
    return paradigm, artifacts, project_map
