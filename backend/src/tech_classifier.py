"""
tech_classifier.py

AISAF Technology Intelligence Engine

Detects:
- Programming Language
- Framework
- Database
- Frontend
- Project Type
- Application Domain
- Architecture Style
- Deployment Technology
"""


import re



# ==========================================================
# Knowledge Base
# ==========================================================


LANGUAGES = {

    "python": "Python",

    "java": "Java",

    "javascript": "JavaScript",

    "typescript": "TypeScript",

    "c#": "C#",

    "php": "PHP",

    "golang": "Go",

    "go": "Go",

    "rust": "Rust"

}



FRAMEWORKS = {

    "flask": "Flask",

    "django": "Django",

    "fastapi": "FastAPI",

    "spring boot": "Spring Boot",

    "spring": "Spring Boot",

    "express": "Express.js",

    "node.js": "Node.js",

    "node": "Node.js",

    "react": "React",

    "next.js": "Next.js",

    "next": "Next.js",

    "vue": "Vue",

    "angular": "Angular"

}



DATABASES = {

    "postgresql": "PostgreSQL",

    "postgres": "PostgreSQL",

    "mysql": "MySQL",

    "mongodb": "MongoDB",

    "mongo": "MongoDB",

    "sqlite": "SQLite",

    "oracle": "Oracle",

    "redis": "Redis"

}



PROJECT_TYPES = {

    "rest api": "REST API",

    "api": "REST API",

    "backend": "Backend Service",

    "website": "Website",

    "web application": "Web Application",

    "web app": "Web Application",

    "dashboard": "Dashboard",

    "chatbot": "AI Chatbot",

    "mobile application": "Mobile Application",

    "mobile app": "Mobile Application"

}



DOMAINS = {

    "bank": "Banking",

    "banking": "Banking",

    "finance": "FinTech",

    "financial": "FinTech",

    "payment": "FinTech",

    "fintech": "FinTech",

    "health": "Healthcare",

    "healthcare": "Healthcare",

    "medical": "Healthcare",

    "patient": "Healthcare",

    "hospital": "Healthcare",

    "ecommerce": "E-Commerce",

    "e-commerce": "E-Commerce",

    "shopping": "E-Commerce",

    "education": "Education",

    "student": "Education",

    "learning": "Education",

    "social": "Social Platform",

    "security": "Cybersecurity",

    "cybersecurity": "Cybersecurity",

    "ai": "Artificial Intelligence",

    "machine learning": "Artificial Intelligence"

}



ARCHITECTURES = {

    "microservice": "Microservices",

    "microservices": "Microservices",

    "monolith": "Monolithic",

    "serverless": "Serverless",

    "rest": "REST Architecture",

    "api": "API Based",

    "event driven": "Event Driven"

}



DEPLOYMENT = {

    "docker": "Docker",

    "container": "Containerized",

    "kubernetes": "Kubernetes",

    "k8s": "Kubernetes",

    "aws": "AWS",

    "azure": "Azure",

    "gcp": "Google Cloud",

    "google cloud": "Google Cloud"

}



# ==========================================================
# Helper Function
# ==========================================================


def _find(text, dictionary):

    """
    Detect keyword from dictionary.

    Uses substring matching so that:
    bank -> banking
    ecommerce -> e-commerce
    """

    text = text.lower()


    for keyword, value in dictionary.items():

        if keyword in text:

            return value


    return None




# ==========================================================
# Technology Classifier
# ==========================================================


def classify_technology(requirement: str):


    language = _find(
        requirement,
        LANGUAGES
    )


    framework = _find(
        requirement,
        FRAMEWORKS
    )


    database = _find(
        requirement,
        DATABASES
    )


    project_type = _find(
        requirement,
        PROJECT_TYPES
    )


    domain = _find(
        requirement,
        DOMAINS
    )


    architecture = _find(
        requirement,
        ARCHITECTURES
    )


    deployment = _find(
        requirement,
        DEPLOYMENT
    )



    frontend = None



    if framework in [

        "React",

        "Next.js",

        "Vue",

        "Angular"

    ]:

        frontend = framework




    # ==================================================
    # Infer language from framework
    # ==================================================


    if language is None:


        framework_mapping = {


            "Flask": "Python",

            "Django": "Python",

            "FastAPI": "Python",


            "Spring Boot": "Java",


            "Express.js": "JavaScript",

            "Node.js": "JavaScript",


            "React": "JavaScript",

            "Next.js": "JavaScript",

            "Vue": "JavaScript",

            "Angular": "TypeScript"

        }



        language = framework_mapping.get(
            framework
        )




    # ==================================================
    # Infer architecture
    # ==================================================


    if architecture is None:


        if project_type == "REST API":

            architecture = "REST Architecture"




    return {


        "language": language,


        "framework": framework,


        "database": database,


        "frontend": frontend,


        "project_type": project_type,


        "domain": domain,


        "architecture": architecture,


        "deployment": deployment

    }





# ==========================================================
# Test
# ==========================================================


if __name__ == "__main__":


    requirement = """

    Build a secure banking REST API
    using Java Spring Boot,
    PostgreSQL and Docker.

    Include JWT authentication
    and transaction management.

    """



    result = classify_technology(
        requirement
    )



    print("\nAISAF Technology Analysis")

    print("-" * 40)



    for key,value in result.items():

        print(
            f"{key:15}: {value}"
        )