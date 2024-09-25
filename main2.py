import os
from tokenizers import ByteLevelBPETokenizer

# Definir o caminho do diretório onde está o arquivo .txt convertido
path = './'
txt_file = os.path.join(path, 'acao_alimentos_convertido.txt')


# Inicializar o ByteLevelBPETokenizer
tokenizer = ByteLevelBPETokenizer()

# Definir tags estruturais como tokens especiais
special_tokens = [
    "<s>", "<pad>", "</s>", "<unk>", "<mask>",
    "<h1>", "<h2>", "<h3>", "<h4>", "<h5>", "<h6>",  # Tags de títulos
    "<ul>", "<li>", "<ol>",  # Tags de lista
    "<b>", "<i>", "<a>",  # Tags de formatação
]

# Treinar o tokenizer no arquivo .txt com tags estruturais
tokenizer.train(
    files=[txt_file],  # arquivo .txt encontrado
    vocab_size=52_000,
    min_frequency=2,
    special_tokens=special_tokens
)

# Salvar o tokenizer treinado (opcional, se quiser salvar para uso futuro)
output_dir = './tokenizer_output'
tokenizer.save_model(output_dir)
print(f'Tokenizer treinado e salvo no diretório: {output_dir}')
