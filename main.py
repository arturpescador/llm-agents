from autogen import AssistantAgent, UserProxyAgent
from dotenv import load_dotenv
import os

# Load the .env file with the api key
load_dotenv()
api_key = os.getenv("API_KEY")

MAX_USER_REPLIES=5

INPUT_START_MESSAGE = """
Plot a chart of AAPL and TESLA stock price change YTD. Save the python code. Save the result to a file named chart.png.
"""

system_message = """
Você é um assistente de IA útil que escreve códigos e o usuário executa. Resolva tarefas usando suas habilidades de programação e linguagem.

Siga os passos de forma clara para resolver a tarefa: 
1. Se necessário, escreva código Python para o usuário executar.
2. Divida a tarefa em etapas e, sempre que for usar código, destaque qual parte do código deve ser executada.

Quando fornecer código:
- Indique o tipo de script no bloco de código.
- Certifique-se de que o código está completo e o usuário não precisará modificar nada.
- Não forneça múltiplos blocos de código em uma única resposta.
- Use a função `print()` sempre que relevante para exibir o resultado.
- Não sugira que o usuário altere o código, apenas forneça o código completo e pronto para execução.
  
Após o código ser executado:
- Se o resultado indicar erro, corrija o erro e forneça novamente o código completo para ser executado.
- Se a tarefa não for resolvida, analise o problema, revise suas suposições, colete informações adicionais e proponha uma nova abordagem.
- Verifique a resposta cuidadosamente antes de confirmar o resultado.
- Inclua evidências verificáveis sempre que possível.

Importante:
- Espere que o usuário execute o código.
- Não inclua "FINISH" até que o código tenha sido executado e você tenha confirmando que o processo está concluído com sucesso.
"""

# Model
config_list_gemini = [
    {
        "model": "gemini-1.5-pro-latest",
        "api_key": api_key,
        "api_type": "google"
    }
]

# Assistant agent
assistant = AssistantAgent(
    name="assistant",
    system_message=system_message,
    llm_config={
        "cache_seed": 41,
        "config_list": config_list_gemini,
        "seed": 42
    },
)

# User proxy agent
try:
  user_proxy = UserProxyAgent(
    name="user_proxy",
    human_input_mode="NEVER",
    max_consecutive_auto_reply=MAX_USER_REPLIES,
    is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
    code_execution_config={
        "work_dir": "coding",
        "use_docker": False
    },
  )
except Exception as e:
  print(f"Error: {str(e)}")
  exit()

# Chat between the user proxy and the assistant agent
chat_response = user_proxy.initiate_chat(
    assistant,
    message=INPUT_START_MESSAGE,
    summary_method="reflection_with_llm",
)

chat_id = chat_response.chat_id
convs = chat_response.chat_history

for conv in convs:
  content = conv['content']
  active_role = conv['role']

  print(f"{active_role}: {content}")

print("COMPLETE")