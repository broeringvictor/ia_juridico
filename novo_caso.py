import os
from tinydb import TinyDB
import json

# Função para inserir um novo caso no banco de dados
def inserir_novo_caso():
    # Criar conexão com o banco de dados
    db = TinyDB('banco_juridico.json')
    casos = db.table('casos')

    # Exemplo de dados para o novo caso
    novo_caso = {
        "acao": "Ação de Alimentos",
        "dos_fatos": {
            "relacionamento": (
                "As partes mantiveram uma união estável por mais de sete anos, entre dezembro de 2013 e junho de 2021, "
                "em convivência pública, contínua e exclusiva, com o objetivo de constituir uma família. Dessa relação nasceu a filha, "
                "em 16 de novembro de 2016, conforme certidão de nascimento anexada."
            ),
            "bens": (
                "Em janeiro de 2021, as partes adquiriram um imóvel localizado na Guarda do Cubatão. O financiamento de R$ 153.000,00 "
                "foi feito pelo Requerido na condição de solteiro, com uma entrada de R$ 46.854,00. A Requerente, embora não tenha contribuído "
                "significativamente no pagamento das parcelas, figura como fiadora no contrato de financiamento. Por essa razão, renuncia "
                "expressamente à sua meação no referido bem."
            ),
            "periodo_apos_termino": (
                "Após o término do relacionamento em março de 2021, para facilitar o contato entre pai e filha, a Requerente alugou uma residência "
                "próxima ao imóvel do Requerido. No entanto, foi obrigada a utilizar seu limite de crédito para mobiliar a nova casa, uma vez que "
                "não lhe foi permitido levar qualquer eletrodoméstico adquirido durante a união."
            ),
            "filha": (
                "A Requerente pretende a guarda compartilhada, com regulamentação das visitas para finais de semana e feriados alternados, estabelecendo "
                "a entrega da filha aos sábados, às 10 horas, e a devolução no domingo, às 18 horas, na residência fixa da criança."
            ),
            "desequilibrio_financeiro": (
                "A Requerente, desde o término do relacionamento, tem arcado sozinha com a maior parte das despesas da filha e de seu novo lar, utilizando "
                "seu limite de crédito para mobiliar a casa e fornecer um ambiente adequado à criança."
            ),
            "impacto_psicologico": (
                "A instabilidade na prestação de cuidados por parte do Requerido e o abandono de suas responsabilidades parentais têm afetado o desenvolvimento "
                "emocional da criança."
            ),
            "responsabilidade_parental": (
                "Embora as partes tenham tentado informalmente organizar uma guarda alternada, o Requerido não se mostrou comprometido com a divisão equitativa "
                "dos cuidados da filha."
            ),
            "necessidade_fixacao_alimentos": (
                "Considerando a capacidade financeira do Requerido, é imperioso que os alimentos sejam fixados no percentual de 25% de seus rendimentos líquidos."
            ),
            "previsibilidade_visitas": (
                "A Requerente propõe que o regime de visitas seja estabelecido de forma fixa, com datas e horários previamente acordados, a fim de garantir "
                "estabilidade para a filha e segurança no cumprimento dos deveres parentais."
            ),
            "renda_do_pai": (
                "O Requerido, além de seu trabalho formal como vigilante, já realizou atividades como motorista de aplicativo, o que aumentava sua renda significativamente. "
                "Após ser notificado sobre a intenção da Requerente de regularizar a situação de alimentos, interrompeu essa atividade na tentativa de reduzir sua base de cálculo. "
                "Contudo, a Teoria da Aparência deve ser aplicada aqui, considerando o padrão de vida exibido pelo Requerido, que indica uma situação financeira mais robusta."
            ),
            "teoria_da_aparencia": (
                "A Teoria da Aparência, amplamente aceita pela jurisprudência, deve ser utilizada para avaliar a capacidade contributiva do Requerido, considerando os sinais exteriores "
                "de riqueza. Mesmo que o Requerido alegue dificuldades financeiras, a sua exibição de bens de luxo e estilo de vida nas redes sociais sugere uma renda substancial."
            ),
            "bionomio_possibilidade_necessidade": (
                "A fixação dos alimentos deve respeitar o binômio possibilidade-necessidade, levando em conta tanto as necessidades da filha, como saúde, educação e lazer, quanto a "
                "capacidade financeira do Requerido, que possui emprego formal e historicamente complementou sua renda com atividades extras. A fixação de 25% dos rendimentos líquidos "
                "é justa e proporcionada."
            )
        },
        "provas_renda_genitor": "Comprovantes de rendimentos anexados.",
        "tipo_guarda": "Guarda compartilhada",    
    }

    # Inserir o novo caso no banco de dados
    casos.insert(novo_caso)
    
    # Salvar JSON formatado corretamente com acentuação
    with open('caso_formatado.json', 'w', encoding='utf-8') as f:
        json.dump(novo_caso, f, ensure_ascii=False, indent=4)
    
    db.close()

    print("Novo caso de ação de alimentos inserido com sucesso!")

if __name__ == "__main__":
    inserir_novo_caso()
