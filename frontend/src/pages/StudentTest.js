import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

function StudentTest() {
  const [tests, setTests] = useState([]);
  const [selectedTest, setSelectedTest] = useState(null);
  const [questions, setQuestions] = useState([]);
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [answers, setAnswers] = useState({});
  const navigate = useNavigate();

  useEffect(() => {
    fetchTests();
  }, []);

  const fetchTests = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_API_URL}/tests`);
      if (response.ok) {
        const data = await response.json();
        setTests(data.tests);
      }
    } catch (error) {
      console.error('Ошибка при загрузке тестов:', error);
    }
  };

  const fetchQuestions = async (testName) => {
    try {
      const response = await fetch(`${process.env.REACT_APP_API_URL}/questions/${testName}`);
      if (response.ok) {
        const data = await response.json();
        setQuestions(data.questions);
        setSelectedTest(testName);
      }
    } catch (error) {
      console.error('Ошибка при загрузке вопросов:', error);
    }
  };

  const handleTestSelect = (testName) => {
    fetchQuestions(testName);
  };

  const handleAnswer = (questionId, answer) => {
    setAnswers(prev => ({
      ...prev,
      [questionId]: answer
    }));
  };

  const submitTest = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_API_URL}/results`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          test: selectedTest,
          answers: answers,
          timestamp: new Date().toISOString()
        }),
      });

      if (response.ok) {
        navigate('/results');
      }
    } catch (error) {
      console.error('Ошибка при отправке результатов:', error);
      alert('Произошла ошибка при отправке результатов');
    }
  };

  if (!selectedTest) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-md w-full space-y-8">
          <div>
            <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
              Выберите тест
            </h2>
          </div>
          <div className="mt-8">
            <select
              className="block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
              onChange={(e) => handleTestSelect(e.target.value)}
            >
              <option value="">Выберите тест</option>
              {tests.map(test => (
                <option key={test} value={test}>
                  {test}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Тест: {selectedTest}
          </h2>
        </div>
        <div className="mt-8">
          {questions.length > 0 && (
            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-4">
                Вопрос {currentQuestion + 1} из {questions.length}
              </h3>
              <div className="space-y-4">
                <p className="text-gray-600">{questions[currentQuestion].text}</p>
                <div>
                  {questions[currentQuestion].options.map((option, index) => (
                    <label key={index} className="flex items-center space-x-2">
                      <input
                        type="radio"
                        name={`q${currentQuestion}`}
                        value={option}
                        checked={answers[questions[currentQuestion].id] === option}
                        onChange={() => handleAnswer(questions[currentQuestion].id, option)}
                        className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300"
                      />
                      <span className="text-gray-700">{option}</span>
                    </label>
                  ))}
                </div>
              </div>
              <div className="mt-6 flex justify-between">
                <button
                  onClick={() => {
                    if (currentQuestion > 0) {
                      setCurrentQuestion(currentQuestion - 1);
                    }
                  }}
                  className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50"
                >
                  Предыдущий
                </button>
                <button
                  onClick={() => {
                    if (currentQuestion < questions.length - 1) {
                      setCurrentQuestion(currentQuestion + 1);
                    } else {
                      submitTest();
                    }
                  }}
                  className="px-4 py-2 border border-transparent rounded-md text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700"
                >
                  {currentQuestion < questions.length - 1 ? 'Следующий' : 'Завершить'}
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default StudentTest;
