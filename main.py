import os
import sys
import flet as ft
from langchain.prompts import PromptTemplate
from langchain_openai.chat_models import ChatOpenAI
from langchain.callbacks.base import BaseCallbackHandler
import openai
import time
import sqlite3
import logging

# Configuração da chave da API OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

if openai.api_key is None:
    print("Chave da API OpenAI não encontrada. Verifique as variáveis de ambiente.")

# Configurar logging para saída no terminal
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

# Função para extrair exemplos com base no tipo de ação
def extrair_exemplos(conn, acao_selecionada):
    exemplos = []
    cursor = conn.cursor()

    # Obter o ID da ação selecionada
    cursor.execute('SELECT id FROM acoes WHERE acao = ?', (acao_selecionada,))
    result = cursor.fetchone()
    if result is None:
        return exemplos
    acao_id = result[0]

    # Obter os 'dos_fatos' relacionados à ação
    cursor.execute('SELECT valor FROM dos_fatos WHERE acao_id = ?', (acao_id,))
    fatos = cursor.fetchall()
    exemplos_texto = ' '.join([fato[0] for fato in fatos])
    exemplos.append(exemplos_texto)

    return exemplos

# Callback Handler personalizado para registrar informações no terminal
class MyCustomHandler(BaseCallbackHandler):
    def on_llm_start(self, serialized, prompts, **kwargs):
        logging.info("LLM iniciado.")
        logging.info(f"Prompt: {prompts}")

    def on_llm_end(self, response, **kwargs):
        logging.info("LLM finalizado.")
        logging.info(f"Respostas: {response.generations}")

    def on_llm_new_token(self, token, **kwargs):
        logging.info(f"Novo token gerado: {token}")

    def on_chain_start(self, serialized, inputs, **kwargs):
        logging.info("Cadeia iniciada.")
        logging.info(f"Entradas: {inputs}")

    def on_chain_end(self, outputs, **kwargs):
        logging.info("Cadeia finalizada.")
        logging.info(f"Saídas: {outputs}")

    def on_tool_start(self, serialized, input_str, **kwargs):
        logging.info("Ferramenta iniciada.")
        logging.info(f"Entrada da ferramenta: {input_str}")

    def on_tool_end(self, output, **kwargs):
        logging.info("Ferramenta finalizada.")
        logging.info(f"Saída da ferramenta: {output}")

    def on_text(self, text, **kwargs):
        logging.info(f"Texto: {text}")

    def on_error(self, error, **kwargs):
        logging.error(f"Erro: {error}")

# Função para criar o prompt de estilo com few-shot prompting
def criar_prompt_estilo(exemplos):
    texto_exemplos = "\n\n".join(exemplos)
    # Limita o tamanho do texto_exemplos se necessário
    max_length = 2000
    if len(texto_exemplos) > max_length:
        texto_exemplos = texto_exemplos[:max_length]
    prompt_estilo = (
        "Por favor, utilize os seguintes exemplos de estilo de escrita como referência ao redigir o texto. "
        "Mantenha o embasamento legal e o tom jurídico apropriado. Evite o uso do termo 'menor', que pode ser considerado pejorativo; "
        "em vez disso, utilize 'infante', 'criança' ou 'adolescente', conforme o caso. Substitua os nomes das partes por 'Autor' e 'Réu', conforme aplicável. "
        "Mantenha o texto claro, formal e preciso, seguindo o estilo de escrita jurídica.\n\n"
        f"{texto_exemplos}\n\n"
    )
    return prompt_estilo

def criar_agente(prompt_estilo):
    llm = ChatOpenAI(model_name='gpt-4', temperature=0.3)

    prompt = PromptTemplate(
        input_variables=['input_text'],
        template=(
            f"{prompt_estilo}"
            "Agora, com base nas informações fornecidas pelo usuário, redija a seção dos fatos seguindo o mesmo estilo e retorne em formato Markdown:\n"
            "{input_text}\n"
        )
    )
    # Utilizando o novo padrão com 'Runnable'
    chain = prompt | llm
    return chain

def main(page: ft.Page):
    page.theme_mode = ft.ThemeMode.LIGHT
    page.title = "Assistente Jurídico com IA"

    # Conectando ao banco de dados SQLite
    conn = sqlite3.connect('database.db')

    # Obtém a lista de tipos de ação disponíveis no banco de dados
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT DISTINCT acao FROM acoes')
        acao_list = [row[0] for row in cursor.fetchall()]
    except Exception as e:
        print(f"Erro ao obter a lista de ações: {e}")
        acao_list = []

    if not acao_list:
        print("Nenhum tipo de ação encontrado no banco de dados.")
        acao_list = ["Ação de Alimentos"]  # Adiciona uma opção padrão

    # Elementos da interface gráfica
    acao_dropdown = ft.Dropdown(
        label="Tipo de Ação",
        options=[ft.dropdown.Option(acao) for acao in acao_list],
        width=300,
        disabled=False
    )
    acao_dropdown.value = acao_list[0]

    campo_input = ft.TextField(
        label="Descreva os fatos do caso:", 
        multiline=True, 
        width=600,
        hint_text="Insira aqui uma descrição detalhada dos fatos do caso."
    )

    tipo_guarda_input = ft.TextField(
        label="Tipo de Guarda",
        width=300,
        hint_text="Especifique o tipo de guarda, se aplicável."
    )

    teorias_input = ft.TextField(
        label="Teorias Jurídicas",
        multiline=True, 
        width=600,
        hint_text="Liste as teorias jurídicas relevantes ao caso."
    )

    provas_input = ft.TextField(
        label="Provas",
        multiline=True, 
        width=600,
        hint_text="Descreva as provas disponíveis."
    )

    resultado = ft.Markdown(value="", width=600, selectable=True)

    carregando_spinner = ft.ProgressRing(visible=False)

    # Botão para copiar o resultado
    botao_copiar = ft.IconButton(
        icon=ft.icons.COPY,
        tooltip="Copiar Resultado",
        on_click=lambda e: page.set_clipboard(resultado.value),
        visible=False
    )

    # Função que será chamada ao pressionar o botão
    def processar_entrada(e):
        # Limpar mensagens de erro anteriores
        campo_input.error_text = None
        acao_dropdown.error_text = None

        acao_selecionada = acao_dropdown.value
        entrada_usuario = campo_input.value
        tipo_guarda = tipo_guarda_input.value
        teorias = teorias_input.value
        provas = provas_input.value

        if not entrada_usuario or not acao_selecionada:
            resultado.value = "Por favor, selecione um tipo de ação e insira os fatos do caso."
            if not entrada_usuario:
                campo_input.error_text = "Este campo é obrigatório."
            if not acao_selecionada:
                acao_dropdown.error_text = "Por favor, selecione um tipo de ação."
            page.update()
            return

        # Exibir o spinner de carregamento
        carregando_spinner.visible = True
        resultado.value = ""
        botao_copiar.visible = False
        page.update()

        # Extrair exemplos com base na ação selecionada
        exemplos = extrair_exemplos(conn, acao_selecionada)

        if not exemplos:
            resultado.value = "Não foram encontrados exemplos para o tipo de ação selecionado."
            carregando_spinner.visible = False
            page.update()
            return

        # Criar o prompt de estilo e o agente
        prompt_estilo = criar_prompt_estilo(exemplos)
        agente = criar_agente(prompt_estilo)

        # Construir o texto de entrada combinando as informações do usuário
        input_text = (
            f"Fatos do Caso:\n{entrada_usuario}\n\n"
            f"Tipo de Guarda:\n{tipo_guarda}\n\n"
            f"Teorias Jurídicas:\n{teorias}\n\n"
            f"Provas:\n{provas}\n"
        )

        # Calcular o tempo de resposta
        inicio = time.time()

        # Obter a resposta do agente
        try:
            # Usar o callback handler personalizado
            handler = MyCustomHandler()
            resposta = agente.invoke({"input_text": input_text}, config={"callbacks": [handler]})
        except Exception as e:
            logging.error(f"Ocorreu um erro ao gerar a resposta: {e}")
            resultado.value = "Ocorreu um erro ao gerar a resposta. Por favor, verifique o terminal para detalhes."
            carregando_spinner.visible = False
            page.update()
            return

        fim = time.time()
        tempo_total = fim - inicio

        # Atualizar o resultado com o tempo e a resposta
        resultado.value = f"**Resposta Gerada:**\n\n{resposta}\n\n*Tempo de processamento: {tempo_total:.2f} segundos.*"
        botao_copiar.visible = True

        # Esconder o spinner de carregamento
        carregando_spinner.visible = False
        page.update()

    # Botão para processar a entrada
    botao_processar = ft.ElevatedButton(text="Processar", on_click=processar_entrada)

    # Layout principal
    layout = ft.Column(
        [
            acao_dropdown,
            ft.Divider(),
            ft.Text("Informações do Caso", style=ft.TextThemeStyle.HEADLINE_SMALL),
            campo_input,
            tipo_guarda_input,
            ft.Divider(),
            ft.Text("Detalhes Adicionais", style=ft.TextThemeStyle.HEADLINE_SMALL),
            teorias_input,
            provas_input,
            ft.Divider(),
            ft.Row([botao_processar, carregando_spinner]),
            resultado,
            botao_copiar
        ],
        expand=True,
        scroll=ft.ScrollMode.AUTO
    )

    # Adicionando o layout na página
    page.add(layout)

    # Fechar a conexão quando a aplicação for fechada
    page.on_close = lambda e: conn.close()

if __name__ == "__main__":
    ft.app(target=main)
