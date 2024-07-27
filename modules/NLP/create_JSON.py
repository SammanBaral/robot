import docx
import re
import json


def extract_text_from_docx(file_path):
    doc = docx.Document(file_path)
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    return '\n'.join(full_text)


def extract_museum_info(text):
    museum_info = {}

    # Extract basic information
    museum_info['name'] = re.search(r'Name: (.+)', text).group(1)
    museum_info['location'] = re.search(r'Location: (.+)', text).group(1)
    museum_info['contact'] = re.search(r'Contact: (.+)', text).group(1)
    museum_info['website'] = re.search(r'Website: (.+)', text).group(1)
    museum_info['opening_hours'] = re.search(r'Opening Hours: (.+)', text).group(1)

    # Extract ticket prices
    ticket_prices = re.findall(r'([A-Za-z ]+) \([\w\s\+]+\): \$(\d+)', text)
    museum_info['ticket_prices'] = {category: int(price) for category, price in ticket_prices}

    return museum_info


def extract_gallery_info(text):
    galleries = {}
    gallery_sections = re.findall(r'Gallery ([A-Z]): (.+?)Key Artifacts:(.*?)(?=Gallery|\Z)', text, re.DOTALL)

    for letter, name, artifacts in gallery_sections:
        galleries[f'Gallery {letter}'] = {
            'name': name.strip(),
            'artifacts': [artifact.strip() for artifact in artifacts.strip().split('\n') if artifact.strip()]
        }

    return galleries


def extract_artifact_details(text):
    artifacts = {}
    artifact_sections = re.findall(
        r'(?<=\n\n)([\w\s\'\-]+)\nLocation: (Gallery [A-Z])\nDescription: (.+?)\nSignificance: (.+?)(?=\n\n|$)',
        text, re.DOTALL
    )

    for name, location, description, significance in artifact_sections:
        artifacts[name.strip()] = {
            'location': location.strip(),
            'description': description.strip(),
            'significance': significance.strip()
        }
    return artifacts

def create_museum_json(file_path="knowledge_base/Museum.docx", output_file="knowledge_base/museum_data.json"):
  
  text = extract_text_from_docx(file_path)
  museum_info = extract_museum_info(text)
  galleries = extract_gallery_info(text)
  artifacts = extract_artifact_details(text)

  museum_data = {
      "museum_info": museum_info,
      "galleries": galleries,
      "artifacts": artifacts
  }

  with open(output_file, 'w') as f:
      json.dump(museum_data, f, indent=4)

  print(f"Museum data has been written to {output_file}")
