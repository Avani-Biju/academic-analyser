from app.parsers.question_parser import parse_question_paper
import json

with open('app/extracted/420251390-22320-Sample-question-paper-Digital-Techniques-pdf.txt', 'r') as f:
    text = f.read()

data = parse_question_paper(text)
qs = data['questions']

print(f"Total questions: {len(qs)}")
for q in qs:
    q_num = f"Q{q['question_number']}"
    if q['sub_question']:
        q_num += f"({q['sub_question']})"
    print(f"{q_num}: {q['question'][:40]}...")
