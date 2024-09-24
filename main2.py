import os
import glob
import re
import flet as ft
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import openai
import time

# Obtendo a chave da variável de ambiente
openai.api_key = os.getenv("OPENAI_API_KEY")

if openai.api_key is None:
    print("Chave da API OpenAI não encontrada. Verifique as variáveis de ambiente.")

# Função para extrair a seção "Dos Fatos" dos arquivos .txt
def extrair_dos_fatos(txt_paths):
    textos_dos_fatos = []
    
    # Lê todos os arquivos .txt na pasta
    for txt_path in txt_paths:
        try:
            with open(txt_path, 'r', encoding='utf-8') as file:
                texto_completo = file.read()

            # Adiciona o conteúdo do arquivo diretamente à lista
            textos_dos_fatos.append(texto_completo.strip())

        except Exception as e:
            print(f"Erro ao processar o arquivo {txt_path}: {e}")

    return textos_dos_fatos

# Função para criar o prompt de estilo com few-shot prompting
def criar_prompt_estilo(textos_dos_fatos):
    # Seleciona alguns exemplos para o few-shot prompting
    exemplos = textos_dos_fatos[:3]  # Pega os primeiros 3 exemplos
    texto_exemplos = "\n\n".join(exemplos)
    # Limita o tamanho do texto_exemplos se necessário
    max_length = 2000
    if len(texto_exemplos) > max_length:
        texto_exemplos = texto_exemplos[:max_length]
    prompt_estilo = (
        "Por favor, ao processar os textos dos PDFs, utilize os seguintes exemplos de estilo de redação como referência. "
        "Mantenha o embasamento legal e o tom jurídico apropriado. Evite o uso do termo 'menor', que pode ser considerado pejorativo; "
        "em vez disso, utilize 'infante', 'criança' ou 'adolescente', conforme o caso.\n\n"
        f"{texto_exemplos}\n\n"
    )
    return prompt_estilo

# Função para criar o agente utilizando LLMChain
def criar_agente(prompt_estilo):
    try:
        llm = ChatOpenAI(model_name='gpt-4', temperature=0.7)
    except Exception as e:
        print(f"Erro ao inicializar o modelo GPT-4: {e}")
        print("Tentando usar o modelo GPT-3.5-turbo.")
        llm = ChatOpenAI(model_name='gpt-3.5-turbo', temperature=0.7)
    prompt = PromptTemplate(
        input_variables=['input_text'],
        template=(
            f"{prompt_estilo}"
            "Agora, escreva uma resposta seguindo o mesmo estilo para os seguintes fatos fornecidos pelo usuário:\n"
            "{input_text}\n\n"
            "No final, indique o que precisa ser provado."
        )
    )
    llm_chain = LLMChain(llm=llm, prompt=prompt, verbose=True)
    return llm_chain

def main(page: ft.Page):
    page.theme_mode = ft.ThemeMode.LIGHT
    page.title = "Extração de Dados Jurídicos"
    
    # Extrair os textos dos arquivos .txt
    pasta_txt = r"C:\Users\Victor Broering\pycode\ia_juridico\memoria"
    txt_paths = glob.glob(os.path.join(pasta_txt, '*.txt'))
    textos_dos_fatos = extrair_dos_fatos(txt_paths)
    
    if not textos_dos_fatos:
        print("Não foi possível encontrar conteúdo nos arquivos.")
        return

    # Criar o prompt de estilo e o agente
    prompt_estilo = criar_prompt_estilo(textos_dos_fatos)
    agente = criar_agente(prompt_estilo)

    # Indicador de carregamento
    carregando_spinner = ft.ProgressRing(visible=False)

    # Função que será chamada ao pressionar o botão
    def processar_entrada(e):
        entrada_usuario = campo_input.value
        if not entrada_usuario:
            resultado.value = "Por favor, insira um texto."
            page.update()
            return

        # Exibir o spinner de carregamento
        carregando_spinner.visible = True
        resultado.value = ""
        page.update()

        # Calcular o tempo de resposta
        inicio = time.time()

        # Obter a resposta do agente
        resposta = agente.predict(input_text=entrada_usuario)

        fim = time.time()
        tempo_total = fim - inicio

        # Atualizar o resultado com o tempo e a resposta
        resultado.value = f"Resposta Gerada:\n\n{resposta}\n\nTempo de processamento: {tempo_total:.2f} segundos."
        
        # Esconder o spinner de carregamento
        carregando_spinner.visible = False
        page.update()

    # Campo de input para o usuário escrever os fatos da petição
    campo_input = ft.TextField(
        label="Escreva os fatos da petição jurídica:", 
        multiline=True, 
        width=600
    )

    # Texto para exibir o resultado
    resultado = ft.Text(value="", width=600)

    # Botão para processar a entrada
    botao_processar = ft.ElevatedButton(text="Processar", on_click=processar_entrada)

    # Layout principal com coluna e scroll habilitado
    layout = ft.Column(
        [   ft.Row([
            campo_input,
            botao_processar,
            carregando_spinner,], expand=True,),
            resultado
            
        ],
        expand=True,
        scroll=ft.ScrollMode.AUTO
    )

    # Adicionando o layout na página
    page.add(layout)

if __name__ == "__main__":
    ft.app(target=main)

