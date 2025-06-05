import uuid

def generate_config():
    with open('student_id.txt', encoding='utf-8') as f:
        student = f.read().strip()
    student_id = f"{student}_{uuid.uuid4().hex[:8]}"
    with open('config.py', 'w', encoding='utf-8') as cfg:
        cfg.write(f'STUDENT_ID = "{student_id}"\nSOURCES = []\n')

if __name__ == '__main__':
    generate_config()
 