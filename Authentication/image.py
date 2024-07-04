import base64

def convert_image_to_base64(image_path, output_path):
    with open(image_path, 'rb') as image_file:
        base64_string = base64.b64encode(image_file.read()).decode('utf-8')
    with open(output_path, 'w') as output_file:
        output_file.write(base64_string)

# Example usage
image_path = 'images/logo.png'
output_path = 'images/logo_base64.txt'
convert_image_to_base64(image_path, output_path)
