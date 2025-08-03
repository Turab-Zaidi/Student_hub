import os

def save_pdf(uploaded_file, subject, doc_type):
        subject_folder = f"data/{subject}/{doc_type.replace(' ', '_').lower()}/"
        os.makedirs(subject_folder, exist_ok=True)
        file_path = os.path.join(subject_folder, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        return file_path