import json
import os
from typing import List, Optional
from models import Question, Test, Student, TestResult
import random
from datetime import datetime

class TestService:
    def __init__(self, tests_dir: str = "tests", data_dir: str = "data"):
        self.tests_dir = tests_dir
        self.data_dir = data_dir
        os.makedirs(self.tests_dir, exist_ok=True)
        os.makedirs(self.data_dir, exist_ok=True)

    def save_test(self, test: Test) -> None:
        """Сохраняет тест в JSON файл"""
        test_file = os.path.join(self.tests_dir, f"{test.id}.json")
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(test.json())

    def load_test(self, test_id: str) -> Optional[Test]:
        """Загружает тест из JSON файла"""
        test_file = os.path.join(self.tests_dir, f"{test_id}.json")
        if not os.path.exists(test_file):
            return None
        
        with open(test_file, 'r', encoding='utf-8') as f:
            return Test.parse_raw(f.read())

    def get_test_questions(self, test_id: str, difficulty: int) -> List[Question]:
        """Возвращает вопросы определенного уровня сложности"""
        test = self.load_test(test_id)
        if not test:
            return []
        
        return [q for q in test.questions if q.difficulty == difficulty]

    def create_student_session(self, full_name: str, test_id: str, initial_difficulty: int) -> Student:
        """Создает сессию для ученика"""
        student = Student(
            full_name=full_name,
            test_id=test_id,
            start_time=datetime.now(),
            current_difficulty=initial_difficulty
        )
        return student

    def save_student_result(self, student: Student) -> None:
        """Сохраняет результаты ученика"""
        result = TestResult(
            student=student,
            total_points=sum(a['points'] for a in student.answers if a['is_correct']),
            correct_answers=sum(1 for a in student.answers if a['is_correct']),
            total_questions=len(student.answers),
            completion_time=datetime.now() - student.start_time
        )
        
        result_file = os.path.join(self.data_dir, f"result_{student.test_id}_{student.full_name.replace(' ', '_')}.json")
        with open(result_file, 'w', encoding='utf-8') as f:
            f.write(result.json())

    def get_results(self, test_id: str) -> List[TestResult]:
        """Получает все результаты для теста"""
        results = []
        for file in os.listdir(self.data_dir):
            if file.startswith(f"result_{test_id}"):
                with open(os.path.join(self.data_dir, file), 'r', encoding='utf-8') as f:
                    results.append(TestResult.parse_raw(f.read()))
        return results

    def get_next_question(self, student: Student) -> Optional[Question]:
        """Получает следующий вопрос, учитывая текущую сложность"""
        questions = self.get_test_questions(student.test_id, student.current_difficulty)
        if not questions:
            return None
        
        # Выбираем случайный вопрос из доступных
        return random.choice(questions)

    def update_difficulty(self, student: Student, is_correct: bool) -> int:
        """Обновляет уровень сложности в зависимости от правильности ответа"""
        if is_correct:
            return min(3, student.current_difficulty + 1)
        return max(1, student.current_difficulty - 1)
