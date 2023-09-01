import spacy
print("spacy imported")
# Load pre-trained English language model
nlp = spacy.load('en_core_web_sm')
print("loaded")
# Example complete resume text
resume_text = """
John Doe
Software Engineer

Projects:
1. E-commerce Website - Developed a responsive e-commerce website using Django.
2. Sentiment Analysis App - Created a sentiment analysis app using Flask and NLTK.

Education:
Bachelor of Science in Computer Science - XYZ University
"""

# Process the complete resume text
doc = nlp(resume_text)

# Initialize variables to store project information
projects = []
current_project = ""

print([x for x in doc.sents])

# Identify project-related sentences
for sent in doc.sents:
	print(current_project)
    if "projects" in sent.text.lower():
        current_project = sent.text
    elif current_project:
        current_project += " " + sent.text
    if current_project and sent.is_last:
        projects.append(current_project)
        current_project = ""

# Print extracted project information
for idx, project in enumerate(projects):
    print(f"Project {idx + 1}: {project}")