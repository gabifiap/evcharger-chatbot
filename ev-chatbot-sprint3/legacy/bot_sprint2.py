import os
import re
from google import genai
from google.genai import types
from dotenv import load_dotenv


# 1. CARREGAMENTO DE AMBIENTE E CONFIGURAÇÃO SECRETA

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")


# 2. DATASETS E BASES DE CONHECIMENTO 

# Dataset 1: Gestão de Energia e Operação Comercial
data_comercial = {
    "contexto": "Operação e Inteligência Comercial",
    "pergunta": [
        "Como o sistema evita que o posto comercial ultrapasse a demanda de energia contratada?",
        "O que é o recurso de Peak Shaving em um ambiente comercial?",
        "Como funciona a tarifa dinâmica para os clientes do posto?",
        "Qual a principal diferença da instalação comercial para a residencial?",
        "Como a Inteligência Artificial (IA) auxilia na distribuição de energia?",
        "Como o sistema lida com veículos que permanecem na vaga após o fim da recarga?",
        "Quais os modos de carregamento inteligentes disponíveis para o comércio?",
        "Como os funcionários podem monitorar o status de todos os carregadores?",
        "O sistema permite limitar a potência máxima de um carregador específico?",
        "Como é calculado o tempo estimado de recarga para informar ao cliente?"
    ],
    "resposta": [
        "O sistema utiliza o Controle Dinâmico de Carga (Dynamic Load Control), que ajusta ou pausa a velocidade de carregamento com base no consumo total da edificação para evitar o disparo do fusível principal [1, 2].",
        "O Peak Shaving reduz o consumo da rede elétrica nos horários de pico, priorizando o uso de energia solar armazenada ou gerada instantaneamente [3].",
        "O valor do kWh pode variar em tempo real: o custo diminui quando há 100% de energia solar disponível e sobe durante o horário de ponta da rede convencional [4].",
        "A solução comercial utiliza equipamentos de alta potência (11kW/22kW) com conexão trifásica e softwares de bilhetagem para múltiplos usuários [5, 6].",
        "A IA analisa previsões climáticas e padrões históricos de recarga para prever a geração solar e distribuir a potência disponível com base na urgência [7, 8].",
        "O sistema pode ser configurado para emitir uma cobrança extra proporcional ao atraso após 15 minutos do fim da recarga, garantindo a rotatividade [9, 10].",
        "Estão disponíveis os modos 'Prioridade para Solar' (usa excedente fotovoltaico), 'FV + BAT' (usa solar e baterias) e o modo 'Rápido' [11-13].",
        "Através da plataforma em nuvem SEMS Portal ou do aplicativo SolarGo, que permitem monitorar telemetria e gerenciar frotas [14-16].",
        "Sim, através das Configurações de Energia (Limit Output Power) no aplicativo, é possível definir um limite inferior à potência nominal [17].",
        "O sistema estima o tempo baseando-se na carga necessária, considering uma média de aproximadamente 1 minuto para cada 2% de recarga [18]."
    ]
}

# Dataset completo com os 16 erros técnicos (Manual HCA G2 - Seção 9.5)
data_erros_tecnicos = {
    "codigo": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16"],
    "falha": [
        "Falha na conexão da pistola", "Parada de emergência", "Erro de aterramento", "Temperatura ambiente",
        "Sobretensão", "Subtensão", "Sobrecorrente", "Tempo limite de desvio", "Tempo limite de preparação",
        "Falha do contator soldado", "Falha no medidor", "Falha de corrente de fuga", "Erro de leitura",
        "Erro EEPROM", "Erro de flash", "Falha no detector de vazamento"
    ],
    "causa_tecnica": [
        "Carregador desconectado durante o processo de carga.",
        "O botão físico de parada de emergência foi pressionado.",
        "Cabo de aterramento da entrada CA desconectado ou com má conexão.",
        "Temperatura interna do carregador superior a 98 graus Celsius.",
        "A tensão de entrada CA está acima do limite permitido.",
        "A tensão de entrada CA está abaixo do limite permitido.",
        "Conexão de saída em curto-circuito ou com demanda de corrente excessiva.",
        "Bateria cheia, temperatura ambiente muito baixa ou conexão anormal.",
        "Falha na comunicação do sinal CP entre o carregador e o veículo.",
        "Componente interno (contator) com defeito físico.",
        "Erro de comunicação ou falha no hardware do medidor inteligente.",
        "Detecção de fuga de corrente alternada ou contínua acima dos limites.",
        "Falha no processamento de leitura de dados do sistema.",
        "Erro de gravação ou leitura na memória não volátil (EEPROM).",
        "Erro na integridade da memória Flash interna.",
        "Falha no sensor interno de detecção de corrente residual."
    ],
    "solucao_chatbot": [
        "Verifique se o plugue está bem inserido e reconecte o carregador.",
        "Gire e solte o botão de parada de emergência para destravar o sistema.",
        "Verifique a integridade e reconecte o cabo de aterramento na entrada CA.",
        "Aguarde o resfriamento; o sistema reiniciará automaticamente em níveis seguros.",
        "Aguarde a estabilização da rede; o sistema retornará ao modo espera quando a tensão normalizar.",
        "Aguarde a estabilização da rede; o sistema retornará ao modo espera quando a tensão normalizar.",
        "Aguarde a normalização da saída; o sistema reiniciará automaticamente após a falha cessar.",
        "Verifique se a carga está completa ou pré-aqueça o veículo em ambientes muito frios.",
        "Verifique se o veículo está totalmente carregado e reconecte o plugue após 15 segundos.",
        "Reinicie o carregador; se o erro persistir, entre em contato com o suporte técnico.",
        "Verifique as conexões do medidor e reinicie o carregador.",
        "Verifique se há danos no cabo de carregamento ou plugue e reinicie o sistema.",
        "Realize o reset do equipamento através do aplicativo SolarGo.",
        "Reinicie o carregador; se persistir, realize uma atualização de firmware via SolarGo.",
        "Reinicie o carregador; se persistir, realize uma atualização de firmware via SolarGo.",
        "Reinicie o carregador; caso não resolva, o hardware precisa de manutenção técnica."
    ]
}

# Dataset 2: Instalação e Configuração (Foco: Técnicos)
data_instalacao = {
    "contexto": "Instalação e Infraestrutura Técnica",
    "pergunta": [
        "Quais são as tensões nominais de entrada para os modelos comerciais de 11kW e 22kW?",
        "Qual protocolo é utilizado para a integração com sistemas de gestão externos?",
        "Como deve ser feita a comunicação física entre o carregador HCA e um inversor GoodWe?",
        "Qual o requisito obrigatório de proteção externa para a instalação?",
        "Qual o papel do medidor MID opcional em instalações comerciais?",
        "Como é feito o acesso inicial ao carregador via Bluetooth para configuração?",
        "O que acontece se o carregador perder a conexão com o sensor de monitoramento de carga?",
        "Como configurar o IP estático se o DHCP estiver desabilitado?",
        "Qual a distância máxima recomendada para o cabo de comunicação RS485?",
        "Como o técnico pode vincular novos cartões RFID para uso dos funcionários?"
    ],
    "resposta": [
        "A tensão nominal para modelos trifásicos é de 380V (esquema 3L / N / PE) [19, 20].",
        "O sistema utiliza o protocolo OCPP (Open Charge Point Protocol) baseado em JSON/WebSockets para comunicação externa segura [21].",
        "Deve ser utilizada a porta RS485 (RS485_A1/B1) do carregador conectada à porta correspondente do inversor [22-24].",
        "É obrigatório instalar um dispositivo RCD (Dispositivo de Corrente Residual) externo tipo A [25, 26].",
        "O medidor MID coleta dados de consumo certificados para fins de reembolso de faturas e transparência de custos [27, 28].",
        "Utiliza-se o app SolarGo, selecionando o número de série do dispositivo e inserindo a senha inicial 'goodwe2022' [29].",
        "Existe o risco de desarme dos disjuntores, pois o sistema perde a capacidade de modulação dinâmica de corrente em tempo real [1, 3].",
        "No app SolarGo, acesse More > Communication Setting > WLAN, desative o DHCP e insira manualmente o IP, Máscara e Gateway [30].",
        "A distância máxima para a integridade do sinal no cabo de comunicação RS485 deve ser inferior a 10 metros [31].",
        "No aplicativo, acesse 'EV Card Management' e selecione 'Binding Card' para cadastrar até 10 cartões por carregador [32, 33]."
    ]
}

# Dataset 3: Manutenção e Resolução de Problemas (Foco: Suporte Técnico)
data_manutencao = {
    "contexto": "Manutenção e Diagnóstico de Falhas",
    "pergunta": [
        "O que indica o LED na cor azul constante no carregador?",
        "Como proceder se o indicador LED estiver vermelho fixo?",
        "O que fazer em caso de erro de temperatura ambiente elevada (acima de 98°C)?",
        "Qual a periodicidade recomendada para a manutenção do botão de parada de emergência?",
        "Como resolver o erro 'Falha na conexão da pistola'?",
        "Qual o procedimento de segurança antes de abrir o equipamento para manutenção?",
        "O que significa o LED vermelho piscar duas vezes ao tentar carregar com cartão?",
        "Como realizar o reset de fábrica se a senha de login for perdida?",
        "Quais os limites operacionais de altitude para o carregador?",
        "Como tratar cabos de carregamento que apresentem núcleos de cobre expostos?"
    ],
    "resposta": [
        "O LED azul constante indica que o carregador está operando e o veículo está sendo carregado [34, 35].",
        "O LED vermelho indica uma falha; o técnico deve verificar o código de erro específico através do app SEMS Portal ou SolarGo [36-38].",
        "Aguarde o resfriamento; o carregador retornará ao status de espera automaticamente assim que a temperatura baixar [39].",
        "O botão de parada de emergência deve ser testado (ligar/desligar 3 vezes) uma vez a cada 6 meses [40].",
        "Verifique se há obstruções e reconecte o conector de carregamento firmemente ao veículo [41].",
        "Desconecte o RCBO e aguarde 5 minutos até que os componentes estejam completamente descarregados para evitar choque elétrico [42].",
        "Isso indica que o carregador e o cartão RFID não correspondem (cartão não vinculado) [36, 37].",
        "Através do app SolarGo, selecione 'Restaurar Configurações de Fábrica'; a senha voltará ao padrão 'goodwe2022' [43].",
        "O carregador deve ser instalado em altitudes inferiores a 2.000 metros [22, 44, 45].",
        "É proibido carregar o veículo nestas condições; o cabo deve ser imediatamente substituído por um técnico qualificado [46, 47]."
    ]
}

data_1 = [
  {
    "pergunta": "Quais são os modelos disponíveis na Linha HCA G2?",
    "resposta": "Os modelos disponíveis são o GW7K-HCA-20 (monofásico 220V), GW11K-HCA-20 (trifásico 380V) e GW22K-HCA-20 (trifásico 380V)."
  },
  {
    "pergunta": "Qual é a potência de saída do carregador monofásico?",
    "resposta": "O modelo GW7K-HCA-20 possui potência de 7 kW com corrente de 32A."
  },
  {
    "pergunta": "Quais são os métodos de autenticação suportados?",
    "resposta": "O carregador suporta autenticação via cartão RFID (acompanha 2 unidades, suporta até 10), via App SolarGo/SEMS+ ou modo automático."
  },
  {
    "pergunta": "O carregador possui proteção contra intempéries?",
    "resposta": "Sim, ele possui grau de proteção IP66, sendo resistente a poeira e jatos potentes de água, além de possuir DPS CA Tipo II integrado."
  },
  {
    "pergunta": "Quais protocolos de comunicação estão disponíveis?",
    "resposta": "O hardware possui RS-485, LAN, Wi-Fi e Bluetooth integrados. O protocolo MODBUS está disponível sob solicitação, mas o OCPP ainda não é suportado nativamente."
  },
  {
    "pergunta": "O que significa o Modo de Operação 2 (Prioridade Solar)?",
    "resposta": "Neste modo, o carregador prioriza o uso de energia fotovoltaica (solar) para a recarga antes de consumir energia da rede elétrica."
  },
  {
    "pergunta": "É possível agendar o horário de recarga?",
    "resposta": "Sim, o Modo de Operação 4 (Agendamento) permite definir janelas de horário específicas para a recarga do veículo."
  },
  {
    "pergunta": "O carregador acompanha o cabo de carregamento?",
    "resposta": "Sim, o equipamento inclui um cabo de carregamento de 6 metros com conector padrão europeu IEC 62196-2 Tipo II."
  },
  {
    "pergunta": "Quais aplicativos são usados para configurar o equipamento?",
    "resposta": "O aplicativo SolarGo é utilizado para o comissionamento técnico e o SEMS+ para o monitoramento remoto."
  },
  {
    "pergunta": "Qual a garantia e certificação do produto?",
    "resposta": "O produto possui 2 anos de garantia e possui certificações IEC 61851-1, IEC 62955 e homologação ANATEL."
  }
]

data_2 = [
  {
    "pergunta": "Como a IA auxilia no Controle Dinâmico de Carga?",
    "resposta": "A IA monitora a corrente real consumida e a compara com o limite da rede; se chegar perto do limite, ela reduz a potência ou pausa o carregamento para evitar o disparo do fusível principal."
  },
  {
    "pergunta": "O ChargeGrid resolve qual problema da GoodWe?",
    "resposta": "Ele resolve a ausência de um modelo padrão de cobrança e a falta de integração com plataformas terceiras de billing/pagamento para a linha HCA G2."
  },
  {
    "pergunta": "Como funciona a tarifação dinâmica no projeto?",
    "resposta": "A tarifação é acionada por APIs de pagamento e pode variar conforme a demanda da rede elétrica e a orquestração de potência feita pelo sistema."
  },
  {
    "pergunta": "Qual o impacto do Controle de Demanda na infraestrutura?",
    "resposta": "O principal impacto é a redução de custos de infraestrutura e a otimização da rede elétrica, evitando sobrecargas no sistema do condomínio ou comércio."
  },
  {
    "pergunta": "Para quais setores o ChargeGrid Intelligence é focado?",
    "resposta": "O foco principal é o setor comercial, varejo e condomínios, onde há necessidade de gestão de múltiplos usuários e cobrança."
  },
  {
    "pergunta": "Como a IA faz a previsão de picos de consumo?",
    "resposta": "Através da análise de sessões de recarga anteriores, permitindo a alocação inteligente de potência e precificação dinâmica baseada no uso."
  },
  {
    "pergunta": "O que acontece quando a corrente da rede volta ao normal após um pico?",
    "resposta": "O carregador reiniciará automaticamente a recarga assim que a diferença entre a corrente de conexão e a consumida atender às condições de segurança."
  },
  {
    "pergunta": "Quem são os responsáveis pelos custos de energia no modelo comercial?",
    "resposta": "Isso faz parte do desafio de implantação, onde o sistema deve definir a divisão de receita e o gateway de pagamento entre o dono do eletroposto e o usuário."
  },
  {
    "pergunta": "Como o sistema garante a interoperabilidade entre diferentes hardwares?",
    "resposta": "Através de protocolos abertos como MODBUS (atual) e a futura implementação de integração via OCPP."
  },
  {
    "pergunta": "A IA pode sugerir horários de recarga mais baratos?",
    "resposta": "Sim, com base na análise de dados e controle de demanda, a IA pode sugerir horários de menor carga na rede para otimizar o custo da tarifação dinâmica."
  }
]

data_3 = [
    {
        "pergunta": "Como motorista, como sei que o carregamento começou com sucesso?",
        "resposta": "O início da carga é indicado pela luz de status do carregador, que passará a pulsar na cor verde. Além disso, o painel do seu veículo exibirá o ícone de carregamento e o tempo estimado para conclusão. ⚡"
    },
    {
        "pergunta": "O sistema está acusando sobrecarga no setor comercial. O que devo fazer como operador?",
        "resposta": "Acesse o painel do ChargeGrid Intelligence e verifique o módulo de 'Balanceamento de Carga'. O sistema deve redistribuir a potência automaticamente entre os bicos ativos para garantir a estabilidade da rede. 🛠️"
    },
    {
        "pergunta": "O cabo de um cliente ficou preso no carro após o fim da carga. Como ajudo ele?",
        "resposta": "Solicite que o motorista realize o destravamento das portas pelo controle do veículo, o que geralmente libera o bocal. Caso persista, o sistema permite o comando de liberação manual através do terminal do operador. 🚗"
    },
    {
        "pergunta": "Posso carregar meu carro se estiver chovendo ou é perigoso?",
        "resposta": "Sim, é seguro. Os carregadores GoodWe possuem certificação IP65 de isolamento contra água. O fluxo de energia só é iniciado após o sistema detectar que a conexão entre o cabo e o veículo está totalmente vedada. 🌧️"
    },
    {
        "pergunta": "Um motorista disse que o QR Code de pagamento não está funcionando. Qual o procedimento?",
        "resposta": "Verifique se há reflexo excessivo na tela ou sujeira na lente do celular do cliente. Caso o erro persista, você pode iniciar a sessão de carga manualmente via sistema ou utilizar um cartão RFID de suporte da unidade. 💳"
    },
    {
        "pergunta": "O que é essa orquestração de potência que o sistema faz sozinho?",
        "resposta": "É uma gestão inteligente que distribui a carga disponível entre os veículos conectados. Isso evita que a demanda ultrapasse o limite contratado do posto, mantendo a operação segura e contínua. 🎶"
    },
    {
        "pergunta": "O carregador está com uma luz amarela piscando. É algum erro grave?",
        "resposta": "A luz amarela indica que o equipamento está em modo de espera ou em processo de comunicação com o servidor. Não é um erro crítico; o carregador estará pronto para uso assim que a luz estabilizar ou o veículo for conectado. 🟡"
    },
    {
        "pergunta": "Tem um carro parado na vaga que já terminou de carregar há tempo. O que eu faço?",
        "resposta": "Recomenda-se orientar o motorista sobre a necessidade de liberação da vaga. O ChargeGrid permite a configuração de taxas de ociosidade para desencorajar o uso da vaga como estacionamento após o fim da recarga. 🅿️"
    },
    {
        "pergunta": "Como verifico o total de energia (kWh) consumido neste ponto hoje?",
        "resposta": "Essa informação está disponível no seu painel administrativo, na aba 'Relatórios de Ciclos'. Lá você encontrará o detalhamento do consumo em kWh por carregador e por período. 📊"
    },
    {
        "pergunta": "Como faço para resetar um carregador que travou no painel?",
        "resposta": "Tente primeiro o comando de reinicialização via software. Se não houver resposta, desligue o disjuntor do equipamento por 30 segundos e religue-o. O sistema passará por um processo de autodiagnóstico ao reiniciar. ⚡"
    }
]


# 3. PROMPT DE INSTRUÇÃO DO SISTEMA 

SYSTEM_PROMPT = """
Você é o 'Guia Técnico GoodWe', uma inteligência de missão crítica para eletropostos comerciais.

DIRETRIZES DE ATUAÇÃO:
1. PÚBLICO: Funcionários operacionais e motoristas em trânsito.
2. FOCO TÉCNICO: Exclusivo para ChargeGrid Intelligence (comercial). Ignore contextos residenciais.
3. POSTURA: Profissional, solícito e direto. Use um tom educativo sem ser excessivamente informal.

DOMÍNIOS DE CONHECIMENTO (O QUE VOCÊ DEVE SABER):
- ORQUESTRAÇÃO DE POTÊNCIA: Gerenciar a distribuição de energia entre múltiplos veículos para não exceder o limite do posto.
- REGISTRO E FATURAMENTO: Entender logs de ciclos de recarga, consumo em kWh e taxas de ociosidade.
- DIAGNÓSTICO DE HARDWARE: Interpretar luzes de status, travas de conectores e procedimentos de reset/segurança.

PROTOCOLO DE RESPOSTA (OBRIGATÓRIO E RIGOROSO):
- Sempre valide a dúvida do usuário com educação.
- NUNCA dê respostas vagas ou puramente conceituais para falhas físicas.
- Para alertas de hardware (como Luz Vermelha Piscando), você DEVE instruir o usuário de forma prática: diga explicitamente para acessar o aplicativo oficial SEMS Portal ou SolarGo no celular, localizar o carregador e identificar o código de erro exato gerado pelo sistema.
- Cruze imediatamente a pergunta do usuário ou o código relatado por ele com a sua base de 'DIAGNÓSTICO DE ERROS TÉCNICOS' para fornecer a solução exata da falha, mas não na mesma resposta, mas conduza o diálogo.
- Em situações de risco crítico (fumaça, faíscas), priorize a instrução de desligar o disjuntor imediatamente.
- Responda de forma prestativa suscinta sem tantas linhas, completa e termine a última frase com ponto final.
"""


# 4. CONSTRUÇÃO LOGICA DO COMPLEMENTO DE DADOS

# Injeta os dicionários dinamicamente na string de contexto, simulando o Modelfile
datasets_texto = "\n--- BASES DE CONHECIMENTO DO PROJETO ---\n"
datasets_mapeados = {
    'data_comercial': ' GESTÃO COMERCIAL E FLUXO',
    'data_instalacao': ' DIRETRIZES DE INSTALAÇÃO',
    'data_manutencao': ' MANUTENÇÃO E SUPORTE',
    'data_erros_tecnicos': ' DIAGNÓSTICO DE ERROS TÉCNICOS',
    'data_1': ' BASE DE DADOS COMPLEMENTAR 1',
    'data_2': ' BASE DE DADOS COMPLEMENTAR 2',
    'data_3': ' BASE DE DADOS COMPLEMENTAR 3'
}

for var_name, titulo in datasets_mapeados.items():
    if var_name in globals():
        datasets_texto += f"\n{titulo}:\n{globals()[var_name]}\n"

PROMPT_GEMINI_COMPLETO = f"{SYSTEM_PROMPT}\n{datasets_texto}"


# 5. FUNÇÃO DE INICIALIZAÇÃO E COMUNICAÇÃO (BACKEND)

client = genai.Client(api_key=api_key)

import time
from google.genai.errors import ServerError, ClientError

def responder_usuario(mensagem_usuario):
    """
    Função principal com proteção contra erros de autenticação,
    limites de requisição (429) e oscilações do servidor (503).
    """
    try:
        # Tenta criar o chat e enviar a mensagem normalmente
        chat = client.chats.create(
            model="gemini-2.5-flash",
            config=types.GenerateContentConfig(
                system_instruction=PROMPT_GEMINI_COMPLETO,
                temperature=0.2,
                max_output_tokens=2048
            )
        )
        response = chat.send_message(mensagem_usuario)
        return response.text
        
    except ServerError as e:
        # Se o servidor do Google piscar (Erro 503), aciona o plano B com tratamento seguro de erro
        try:
            time.sleep(3)  # Espera 3 segundos para o servidor respirar
            response = chat.send_message(mensagem_usuario)
            return response.text
        except:
            return "⚠️ O servidor do Gemini está muito instável agora. Por favor, aguarde um minutinho e envie sua mensagem novamente!"

    except ClientError as e:
        # Tratamento universal seguro capturando a mensagem de erro do cliente de texto puro (evita falha de status_code)
        erro_msg = str(e).lower()
        if "401" in erro_msg or "unauthenticated" in erro_msg or "api key" in erro_msg:
            return "🔑 Erro de Autenticação: Sua chave de API do Gemini (GEMINI_API_KEY) está inválida, incorreta ou não foi detectada. Verifique as configurações do seu ambiente!"
        elif "429" in erro_msg or "quota" in erro_msg:
            return "⏳ Erro 429: Limite de requisições excedido (Quota). Por favor, aguarde alguns segundos antes de tentar novamente."
        else:
            return f"🚫 Erro de Cliente da API Gemini: {e}"

    except Exception as e:
        # Evita a tela vermelha do Streamlit para qualquer outro erro desconhecido
        return f"❌ Ocorreu um erro inesperado no processamento: {e}"
