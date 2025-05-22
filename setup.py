from setuptools import setup, find_packages

setup(
    name="trae",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi==0.109.0",
        "uvicorn==0.27.0",
        "pydantic[email]==2.5.3",
        "passlib==1.7.4",
        "python-jose==3.3.0",
        "jinja2==3.1.2",
        "passlib[bcrypt]==1.7.4",
        "python-dotenv==0.19.0",
        "httpx==0.26.0",
        "python-multipart==0.0.5",
        "PyJWT==2.8.0",
        "supabase==2.15.1",
        "python-jose[cryptography]==3.3.0",
        "pytest==7.4.3"
    ],
    python_requires=">=3.11"
)
