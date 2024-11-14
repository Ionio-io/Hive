def replace_image_tokens(report_file_path, image_directory):
    with open(report_file_path, 'r') as file:
        report_content = file.read()

    # Replace tokens with actual Markdown image syntax
    report_content = report_content.replace(
        '<IMAGE="', f'![image]({image_directory}/'
    ).replace('"/>', '})')

    # Write the modified content back to the report file
    with open(report_file_path, 'w') as file:
        file.write(report_content)

# Call the function after generating the report
replace_image_tokens('report.md', 'path/to/image/directory')

# After generating the report with O1
o1_generate_report()

# Replace image tokens in the generated report
replace_image_tokens('report.md', 'generated_images')
