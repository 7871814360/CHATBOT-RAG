import json

# Load JSON data
def load_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

# Function to retrieve paragraphs by matching section title or subsection title
def get_paragraphs_by_title(data, search_title):
    result = ""
    
    for section in data.get("sections", []):
        # Check if the section title matches the search title
        if section["section_title"].lower() == search_title.lower():
            result += f"**{section['section_title']}**\n\n"
            # Add paragraphs in the main section
            for i, paragraph in enumerate(section.get("paragraphs", []), start=1):
                result += f"{paragraph}\n\n"
            
            # Check for subsections and add their paragraphs
            if "subsections" in section:
                for subsection in section["subsections"]:
                    result += f"**{subsection['subsection_title']}**\n\n"
                    for j, sub_paragraph in enumerate(subsection.get("paragraphs", []), start=1):
                        result += f"{sub_paragraph}\n\n"
        
        # Check for subsections matching the search title
        if "subsections" in section:
            for subsection in section["subsections"]:
                if subsection["subsection_title"].lower() == search_title.lower():
                    result += f"**{subsection['subsection_title']}**\n\n"
                    for j, sub_paragraph in enumerate(subsection.get("paragraphs", []), start=1):
                        result += f"{sub_paragraph}\n\n"
    
    # If result is empty, no match was found
    return result if result else None

# Function to fetch content by title
def get_paragraphs(title):
    data = load_json('./book.json')
    return get_paragraphs_by_title(data, title)