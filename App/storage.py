from .models import Student, Question, Result, AnswerRecord, TestSession
from .auth import get_current_user
from typing import List, Dict, Any, Optional, Union
from sqlalchemy import create_engine, Column, Integer, String, Float, JSON, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
import json
import os
from pathlib import Path

BASE_DIR = os.path.join(os.path.dirname(__file__), "..", "tests_data")

def load_questions(test_name: str) -> List[Question]:
    """Загрузить вопросы теста из JSON файла"""
    base = os.path.join(os.path.dirname(__file__), "..", "tests_data")
    test_dir = os.path.join(base, test_name)
    if not os.path.exists(test_dir):
        raise FileNotFoundError(f"Тест {test_name} не найден")
    
    questions = []
    for filename in os.listdir(test_dir):
        if filename.endswith(".json"):
            with open(os.path.join(test_dir, filename), 'r', encoding='utf-8') as f:
                data = json.load(f)
                questions.extend([Question(**q) for q in data])
    return questions

def save_questions(test_name: str, questions: List[Dict[str, Any]]) -> None:
    """Сохранить вопросы теста в JSON файл"""
    base = os.path.join(os.path.dirname(__file__), "..", "tests_data")
    os.makedirs(os.path.join(base, test_name), exist_ok=True)
    
    # Разделяем вопросы по темам
    topics = {}
    for q in questions:
        topic = q.get("topic", "default")
        if topic not in topics:
            topics[topic] = []
        topics[topic].append(q)
    
    # Сохраняем каждый файл с темой
    for topic, topic_questions in topics.items():
        filename = f"{topic}.json" if topic != "default" else "questions.json"
        with open(os.path.join(base, test_name, filename), 'w', encoding='utf-8') as f:
            json.dump(topic_questions, f, ensure_ascii=False, indent=2)

def load_results(test_name: str) -> List[Result]:
    """Загрузить результаты теста из JSON файла"""
    base = os.path.join(os.path.dirname(__file__), "..", "results")
    test_dir = os.path.join(base, test_name)
    if not os.path.exists(test_dir):
        return []
    
    results = []
    for filename in os.listdir(test_dir):
        if filename.endswith(".json"):
            with open(os.path.join(test_dir, filename), 'r', encoding='utf-8') as f:
                data = json.load(f)
                results.extend([Result(**r) for r in data])
    return results

def save_result(test_name: str, result: Dict[str, Any]) -> None:
    """Сохранить результат теста в JSON файл"""
    base = os.path.join(os.path.dirname(__file__), "..", "results")
    os.makedirs(os.path.join(base, test_name), exist_ok=True)
    
    # Получаем текущую дату для имени файла
    date = result.get("start_time", "results").split("T")[0]
    filename = os.path.join(base, test_name, f"{date}.json")
    
    # Загружаем существующие результаты
    existing_results = []
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            existing_results = json.load(f)
    
    # Добавляем новый результат
    existing_results.append(result)
    
    # Сохраняем обновленный список
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(existing_results, f, ensure_ascii=False, indent=2)

def create_test_session(student: Student, test_name: str) -> TestSession:
    """Создать новую сессию тестирования"""
    session_id = str(uuid.uuid4())
    questions = load_questions(test_name)
    
    # Инициализируем статистику по темам
    topic_stats = {}
    for q in questions:
        if q.topic not in topic_stats:
            topic_stats[q.topic] = {
                "correct": 0,
                "total": 0,
                "average_difficulty": 0,
                "success_rate": 0
            }
    
    return TestSession(
        session_id=session_id,
        student=student,
        start_time=datetime.now().isoformat(),
        current_level=student.initial_level,
        questions=questions,
        asked=[],
        answers=[],
        finished=False,
        current_topic="",
        current_subtopic="",
        topic_stats=topic_stats
    )

def update_topic_stats(session: TestSession, answer: AnswerRecord) -> None:
    """Обновить статистику по темам после ответа"""
    if answer.topic not in session.topic_stats:
        session.topic_stats[answer.topic] = {
            "correct": 0,
            "total": 0,
            "average_difficulty": 0,
            "success_rate": 0
        }
    
    topic_stats = session.topic_stats[answer.topic]
    topic_stats["total"] += 1
    if answer.correct:
        topic_stats["correct"] += 1
    
    # Обновляем среднюю сложность
    total_difficulty = sum(
        q.difficulty for q in session.questions 
        if q.topic == answer.topic
    )
    topic_stats["average_difficulty"] = total_difficulty / len(
        [q for q in session.questions if q.topic == answer.topic]
    )
    
    # Обновляем процент успешности
    topic_stats["success_rate"] = (
        topic_stats["correct"] / topic_stats["total"] * 100
    )

def calculate_next_level(session: TestSession, answer: AnswerRecord) -> int:
    """Рассчитать следующий уровень сложности"""
    topic_stats = session.topic_stats[answer.topic]
    
    # Если ответ правильный и процент успешности высокий - увеличиваем сложность
    if answer.correct and topic_stats["success_rate"] >= 70:
        return min(session.current_level + 1, 5)
    
    # Если ответ неправильный и процент успешности низкий - уменьшаем сложность
    if not answer.correct and topic_stats["success_rate"] <= 30:
        return max(session.current_level - 1, 1)
    
    return session.current_level

def select_next_question(session: TestSession) -> Question:
    """Выбрать следующий вопрос с учетом адаптивности"""
    if session.finished:
        return None
    
    # Находим тему с наименьшим процентом успешности
    min_success_rate = float('inf')
    target_topic = None
    
    for topic, stats in session.topic_stats.items():
        if stats["total"] > 0 and stats["success_rate"] < min_success_rate:
            min_success_rate = stats["success_rate"]
            target_topic = topic
    
    # Если нет тем с ответами, выбираем случайную тему
    if target_topic is None:
        target_topic = next(iter(session.topic_stats))
    
    # Находим вопросы подходящей сложности
    candidates = [
        q for q in session.questions 
        if q.topic == target_topic 
        and q.difficulty == session.current_level 
        and q.id not in session.asked
    ]
    
    # Если нет вопросов текущей сложности, ищем на любом уровне
    if not candidates:
        candidates = [
            q for q in session.questions 
            if q.topic == target_topic 
            and q.id not in session.asked
        ]
    
    if not candidates:
        session.finished = True
        return None
    
    # Выбираем случайный вопрос из подходящих
    import random
    question = random.choice(candidates)
    session.asked.append(question.id)
    session.current_topic = question.topic
    session.current_subtopic = question.subtopic
    return question

def calculate_final_stats(session: TestSession) -> Dict[str, Any]:
    """Рассчитать финальную статистику по тесту"""
    total_score = sum(a.score for a in session.answers)
    
    # Статистика по темам
    topic_scores = {}
    for topic, stats in session.topic_stats.items():
        topic_scores[topic] = {
            "correct": stats["correct"],
            "total": stats["total"],
            "success_rate": stats["success_rate"],
            "average_difficulty": stats["average_difficulty"]
        }
    
    # Распределение по сложности
    difficulty_distribution = {}
    for a in session.answers:
        difficulty_distribution[a.difficulty] = difficulty_distribution.get(a.difficulty, 0) + 1
    
    # Время на тест
    start_time = datetime.fromisoformat(session.start_time)
    end_time = datetime.now()
    time_spent = (end_time - start_time).total_seconds()
    
    return {
        "total_score": total_score,
        "topic_scores": topic_scores,
        "difficulty_distribution": difficulty_distribution,
        "time_spent": time_spent
    }