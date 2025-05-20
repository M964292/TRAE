import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

function TeacherPanel() {
  const [tests, setTests] = useState([]);
  const [newTestName, setNewTestName] = useState('');
  const [questions, setQuestions] = useState([]);
  const [newQuestion, setNewQuestion] = useState('');
  const [newOptions, setNewOptions] = useState(['']);
  const navigate = useNavigate();

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

  const addOption = () => {
    setNewOptions([...newOptions, '']);
  };

  const removeOption = (index) => {
    if (newOptions.length > 1) {
      const updatedOptions = [...newOptions];
      updatedOptions.splice(index, 1);
      setNewOptions(updatedOptions);
    }
  };

  const saveTest = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_API_URL}/questions/${newTestName}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          questions: [
            {
              text: newQuestion,
              options: newOptions.filter(option => option.trim() !== '')
            }
          ]
        }),
      });

      if (response.ok) {
        setNewTestName('');
        setNewQuestion('');
        setNewOptions(['']);
        fetchTests();
      }
    } catch (error) {
      console.error('Ошибка при сохранении теста:', error);
      alert('Произошла ошибка при сохранении теста');
    }
  };

  useEffect(() => {
    fetchTests();
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('token');
    navigate('/');
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex">
              <div className="flex-shrink-0 flex items-center">
                <span className="text-xl font-bold text-indigo-600">Панель Учителя</span>
              </div>
            </div>
            <div className="flex items-center">
              <button
                onClick={handleLogout}
                className="px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700"
              >
                Выйти
              </button>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <div className="border-4 border-dashed border-gray-200 rounded-lg h-96 p-6">
            <h2 className="text-2xl font-bold mb-6">Создание теста</h2>
            <div className="space-y-4">
              <div>
                <label htmlFor="testName" className="block text-sm font-medium text-gray-700">
                  Название теста
                </label>
                <input
                  type="text"
                  id="testName"
                  value={newTestName}
                  onChange={(e) => setNewTestName(e.target.value)}
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                />
              </div>
              <div>
                <label htmlFor="question" className="block text-sm font-medium text-gray-700">
                  Вопрос
                </label>
                <input
                  type="text"
                  id="question"
                  value={newQuestion}
                  onChange={(e) => setNewQuestion(e.target.value)}
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Варианты ответов
                </label>
                {newOptions.map((option, index) => (
                  <div key={index} className="flex space-x-2 mt-2">
                    <input
                      type="text"
                      value={option}
                      onChange={(e) => {
                        const updatedOptions = [...newOptions];
                        updatedOptions[index] = e.target.value;
                        setNewOptions(updatedOptions);
                      }}
                      className="flex-1 rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                    />
                    <button
                      onClick={() => removeOption(index)}
                      className="px-2 py-1 text-red-600 hover:text-red-800"
                    >
                      Удалить
                    </button>
                  </div>
                ))}
                <button
                  onClick={addOption}
                  className="mt-2 px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700"
                >
                  Добавить вариант
                </button>
              </div>
              <button
                onClick={saveTest}
                className="mt-4 px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700"
              >
                Сохранить тест
              </button>
            </div>
          </div>
        </div>

        <div className="mt-8">
          <h2 className="text-2xl font-bold mb-4">Существующие тесты</h2>
          <ul className="space-y-4">
            {tests.map(test => (
              <li key={test} className="bg-white p-4 rounded-lg shadow">
                {test}
              </li>
            ))}
          </ul>
        </div>
      </main>
    </div>
  );
}

export default TeacherPanel;
