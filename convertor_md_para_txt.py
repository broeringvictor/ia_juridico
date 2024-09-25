import re

# Função para converter markdown em texto com tags
def markdown_to_tagged_text(markdown_content):
    # Converte títulos
    markdown_content = re.sub(r'###### (.*)', r'<h6>\1</h6>', markdown_content)
    markdown_content = re.sub(r'##### (.*)', r'<h5>\1</h5>', markdown_content)
    markdown_content = re.sub(r'#### (.*)', r'<h4>\1</h4>', markdown_content)
    markdown_content = re.sub(r'### (.*)', r'<h3>\1</h3>', markdown_content)
    markdown_content = re.sub(r'## (.*)', r'<h2>\1</h2>', markdown_content)
    markdown_content = re.sub(r'# (.*)', r'<h1>\1</h1>', markdown_content)
    
    # Converte listas não ordenadas
    markdown_content = re.sub(r'^\* (.*)', r'<ul><li>\1</li></ul>', markdown_content, flags=re.MULTILINE)
    markdown_content = re.sub(r'^\- (.*)', r'<ul><li>\1</li></ul>', markdown_content, flags=re.MULTILINE)
    
    # Converte listas ordenadas
    markdown_content = re.sub(r'^\d+\. (.*)', r'<ol><li>\1</li></ol>', markdown_content, flags=re.MULTILINE)
    
    # Converte negrito e itálico
    markdown_content = re.sub(r'\*\*(.*)\*\*', r'<b>\1</b>', markdown_content)
    markdown_content = re.sub(r'\*(.*)\*', r'<i>\1</i>', markdown_content)
    
    # Converte links
    markdown_content = re.sub(r'\[(.*)\]\((.*)\)', r'<a href="\2">\1</a>', markdown_content)
    
    return markdown_content

# Lendo o conteúdo do arquivo markdown fornecido
markdown_file_path = 'acao_alimentos.md'
with open(markdown_file_path, 'r', encoding='utf-8') as file:
    markdown_content = file.read()

# Convertendo para o formato com tags
tagged_text = markdown_to_tagged_text(markdown_content)

# Salvando o resultado em um arquivo .txt
output_txt_file_path = 'acao_alimentos_convertido.txt'
with open(output_txt_file_path, 'w', encoding='utf-8') as output_file:
    output_file.write(tagged_text)

print(f"Arquivo convertido salvo em: {output_txt_file_path}")
