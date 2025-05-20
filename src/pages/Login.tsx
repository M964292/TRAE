import React, { useState } from "react";
import { useNavigate } from "react-router-dom";

function Login() {
  const [name, setName] = useState("");
  const [level, setLevel] = useState(2);
  const [subject, setSubject] = useState("");
  const [variant, setVariant] = useState("");
  const [teacherMode, setTeacherMode] = useState(false);
  const [teacherPassword, setTeacherPassword] = useState("");
  const navigate = useNavigate();

  const handleStudentLogin = () => {
    if (name && subject && variant) {
      // Можно сохранить данные в localStorage/sessionStorage
      sessionStorage.setItem("student", JSON.stringify({ name, level, subject, variant }));
      navigate("/student");
    }
  };

  const handleTeacherLogin = () => {
    if (teacherPassword) {
      sessionStorage.setItem("teacherPassword", teacherPassword);
      navigate("/teacher");
    }
  };

  return (
    <div style={{ maxWidth: 400, margin: "40px auto" }}>
      <h2>Вход в систему тестирования</h2>
      <div>
        <label>
          <input
            type="checkbox"
            checked={teacherMode}
            onChange={() => setTeacherMode(!teacherMode)}
          />{" "}
          Я учитель
        </label>
      </div>
      {teacherMode ? (
        <div>
          <input
            type="password"
            placeholder="Пароль учителя"
            value={teacherPassword}
            onChange={e => setTeacherPassword(e.target.value)}
            style={{ width: "100%", margin: "8px 0" }}
          />
          <button onClick={handleTeacherLogin} style={{ width: "100%" }}>
            Войти как учитель
          </button>
        </div>
      ) : (
        <div>
          <input
            type="text"
            placeholder="ФИО"
            value={name}
            onChange={e => setName(e.target.value)}
            style={{ width: "100%", margin: "8px 0" }}
          />
          <input
            type="number"
            min={1}
            max={3}
            placeholder="Начальный уровень (1-3)"
            value={level}
            onChange={e => setLevel(Number(e.target.value))}
            style={{ width: "100%", margin: "8px 0" }}
          />
          <input
            type="text"
            placeholder="Код предмета"
            value={subject}
            onChange={e => setSubject(e.target.value)}
            style={{ width: "100%", margin: "8px 0" }}
          />
          <input
            type="text"
            placeholder="Код варианта"
            value={variant}
            onChange={e => setVariant(e.target.value)}
            style={{ width: "100%", margin: "8px 0" }}
          />
          <button onClick={handleStudentLogin} style={{ width: "100%" }}>
            Войти как ученик
          </button>
        </div>
      )}
    </div>
  );
}

export default Login;