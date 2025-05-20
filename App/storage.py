import os
import json
from typing import List, Dict, Any

BASE_DIR = os.path.join(os.path.dirname(__file__), "..", "tests_data")

def get_test_dir(test_name: str) -> str:
    return os.path.join(BASE_DIR, test_name)

def load_questions(test_name: str) -> List[Dict[str, Any]]:
    test_dir = get_test_dir(test_name)
    questions_path = os.path.join(test_dir, "questions.json")
    if not os.path.exists(questions_path):
        raise FileNotFoundError(f"Вопросы для теста '{test_name}' не найдены.")
    with open(questions_path, encoding="utf-8") as f:
        return json.load(f)

def save_questions(test_name: str, questions: List[Dict[str, Any]]):
    test_dir = get_test_dir(test_name)
    os.makedirs(test_dir, exist_ok=True)
    questions_path = os.path.join(test_dir, "questions.json")
    with open(questions_path, "w", encoding="utf-8") as f:
        json.dump(questions, f, ensure_ascii=False, indent=2)

def load_results(test_name: str) -> List[Dict[str, Any]]:
    test_dir = get_test_dir(test_name)
    results_path = os.path.join(test_dir, "results.json")
    if not os.path.exists(results_path):
        return []
    with open(results_path, encoding="utf-8") as f:
        return json.load(f)

def save_result(test_name: str, result: Dict[str, Any]):
    test_dir = get_test_dir(test_name)
    os.makedirs(test_dir, exist_ok=True)
    results_path = os.path.join(test_dir, "results.json")
    results = load_results(test_name)
    results.append(result)
    with open(results_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)