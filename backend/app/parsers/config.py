"""
Configuration for the syllabus parser.
This file contains all the generic patterns, headers, noise words, and watermarks
used to identify and extract data from various university syllabus PDFs.

By modifying this file, you can add support for new university formats without touching the parsing logic.
"""

# Regex patterns for extracting metadata fields.
# We use non-capturing groups (?:...) for variations of the label, and an optional capturing group (.*) for the value.
# The optional capturing group allows the parser to support multi-line fields (e.g. "Course Code\n1234").
FIELD_PATTERNS = {
    "course_code": [
        r"(?i)(?:Course|Subject|Paper)\s*Code\s*[:\-]?\s*(.*)",
        r"(?i)^Code\s*[:\-]?\s*(.*)"
    ],
    "program_code": [
        r"(?i)(?:Program(?:me)?)\s*Code\s*[:\-]?\s*(.*)"
    ],
    "course_name": [
        r"(?i)(?:Course|Subject)?\s*(?:Name|Title)\s*[:\-]?\s*(.*)"
    ],
    "semester": [
        r"(?i)\((S[1-8])\)",
        r"(?i)^(?:Semester|Sem)\s*[:\-]?\s*(.*)$"
    ],
    "scheme": [
        r"(?i)Scheme\s*[:\-]?\s*(.*)"
    ],
    "credits": [
        r"(?i)(?:Course\s*)?Credits?\s*[:\-]?\s*(.*)"
    ]
}

# Words indicating a module or unit is beginning.
MODULE_HEADERS = [
    "Module",
    "Unit",
    "Chapter"
]

# Sections that explicitly signal the parser to STOP collecting topics for a module or course outcomes.
STOP_SECTIONS = [
    "TEXT BOOKS",
    "REFERENCE BOOKS",
    "MODEL QUESTION PAPER",
    "QUESTION PAPER PATTERN",
    "QUESTION PAPER",
    "TEACHING PLAN",
    "APPROVAL SUMMARY",
    "MODES OF EVALUATION",
    "MODE OF EVALUATION",
    "END SEMESTER EXAMINATION",
    "CO-PO MAPPING",
    "CO-PSO MAPPING",
    "COURSE DESCRIPTION",
    "COURSE CONTENTS"
]

# Table headers or metadata rows that often appear inside modules (flattened tables) that we want to ignore.
MODULE_NOISE_WORDS = [
    "cos",
    "hrs.",
    "hrs",
    "module title",
    "topics",
    "hours",
    "course outcomes",
    "content",
    "syllabus"
]

# Watermarks, repetitive footers, or headers that should be scrubbed before parsing.
WATERMARKS = [
    r"KTUNOTES\.IN",
    r"Downloaded\s+from.*",
    r"^\s*Page\s+\d+\s*$",
    r"^\s*\d+\s*\|\s*Page\s*$",
    r"Scanned\s+with\s+CamScanner"
]

# ==========================================
# QUESTION PAPER SPECIFIC CONFIGURATION
# ==========================================

QUESTION_METADATA = {
    "exam": [
        r"(?i)^\s*(Sample Question Paper|End Semester Examination|Mid Semester Examination|Internal Assessment|Sample Test Paper).*"
    ],
    "month": [
        r"(?i)(?:Month)?\s*[:\-]?\s*(January|February|March|April|May|June|July|August|September|October|November|December)"
    ],
    "year": [
        r"(?i)(?:Year)?\s*[:\-]?\s*(20\d{2})"
    ],
    "duration": [
        r"(?i)(?:Time|Duration)\s*[:\-]?\s*(\d+\s*Hours?)"
    ],
    "maximum_marks": [
        r"(?i)(?:Max\.?|Maximum)?\s*Marks\s*[:\-]?\s*(\d+)",
        r"(?i)(\d+)\s*Marks"
    ]
}

QUESTION_SECTION_HEADERS = [
    "PART",
    "SECTION"
]

QUESTION_STOP_SECTIONS = [
    "Instructions",
    "Approval",
    "Evaluation Scheme",
    "Blank Page",
    "Footer Notes"
]
