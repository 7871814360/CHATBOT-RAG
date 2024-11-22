import json

def json_to_txt(input_file, output_file):
    # Read JSON data from the input file
    with open(input_file, 'r',encoding='utf-8') as file:
        data = json.load(file)
    
    # Open a file for writing the output
    with open(output_file, 'w') as file:
        # Write the main title
        file.write(data['title'] + '\n')
        file.write('-----------\n')
        
        # Loop through each section
        for section in data['sections']:
            # Write section title
            file.write(section['section_title'] + '\n')
            file.write('-----------\n')
            
            # Write paragraphs in the section
            for paragraph in section.get('paragraphs', []):
                file.write(paragraph + '\n')
                file.write('-----------\n')
            
            # If subsections exist, handle them as well
            if 'subsections' in section:
                for subsection in section['subsections']:
                    # Write subsection title
                    file.write(subsection['subsection_title'] + '\n')
                    file.write('-----------\n')
                    
                    # Write paragraphs in the subsection
                    for paragraph in subsection.get('paragraphs', []):
                        file.write(paragraph + '\n')
                        file.write('-----------\n')

# Call the function with the input JSON file and output text file names
input_file = './Policy.json'  # Input JSON file path
output_file = 'output.txt'  # Output TXT file path

json_to_txt(input_file, output_file)

print("Conversion complete! Check the 'output.txt' file.")
