import re
from app.parsers.config import WATERMARKS

# Dynamically build the watermark regex
WATERMARK_REGEX = r"(?i)(" + "|".join(WATERMARKS) + r")"

def normalize_text(text: str) -> list[str]:
    """
    Cleans up raw PDF text before any parsing begins.
    - Scrubs out known watermarks and isolated page numbers.
    - Normalizes multiple spaces inside the line.
    """
    clean_lines = []
    lines = text.split('\n')
    
    for line in lines:
        line = line.strip()
        # Skip empty lines
        if not line:
            continue
            
        # Scrub out known watermarks and isolated page numbers
        if re.search(WATERMARK_REGEX, line):
            continue
            
        # Normalize multiple spaces inside the line
        line = re.sub(r'\s+', ' ', line)
        clean_lines.append(line)
        
    return clean_lines

def extract_field(field_name: str, lines: list[str], missing_fields: list[str], patterns_dict: dict) -> str | int | None:
    """
    Extracts a specific metadata field (e.g., Course Code) from the cleaned lines using a configuration dict.
    Supports multi-line values (flattened tables).
    """
    patterns = patterns_dict.get(field_name, [])
    
    for i, line in enumerate(lines):
        # Specific rule to avoid grabbing "End Semester Examination" when looking for a Semester.
        if "examination" in line.lower() and field_name == "semester":
            continue
            
        for pattern in patterns:
            match = re.search(pattern, line)
            if match:
                # Capture group value. Sometimes group(1) might be None if the regex allowed empty match.
                val = match.group(1).strip() if match.group(1) else ""
                
                # Support multi-line fields (e.g. "Course Code" on line 1, "CST202" on line 2)
                if not val:
                    for j in range(i + 1, len(lines)):
                        next_line = lines[j]
                        if next_line:
                            val = next_line
                            break
                            
                if val:
                    if field_name == "credits":
                        try:
                            return int(val)
                        except ValueError:
                            return val
                    return val
                    
    # Track missing fields for the final output
    missing_fields.append(field_name)
    return None
