module.exports = {
  apps: [
    {
      name: "backend",
      script: "App/main.py",
      interpreter: "python",
      args: "--host 0.0.0.0 --port 8000",
      env: {
        "SECRET_KEY": process.env.SECRET_KEY || "your-secret-key",
        "TEACHER_PASSWORD_HASH": process.env.TEACHER_PASSWORD_HASH || "$2b$12$cARwIzIh6iW3hVCCpVyexurQzGAB3Z3zB/qyAjZ.2ilQldZ1yEA5W",
        "STUDENT_PASSWORD_HASH": process.env.STUDENT_PASSWORD_HASH || "$2b$12$.V6E0NjdkHLStFf8Ngjh3.I4.13EYRF54xoXHQgoZWZa4rKsORmJm"
      }
    },
    {
      name: "frontend",
      script: "npm",
      args: "start",
      cwd: "frontend",
      interpreter: "none",
      env: {
        "PORT": "3000",
        "REACT_APP_API_URL": "http://localhost:8000"
      }
    }
  ]
};
