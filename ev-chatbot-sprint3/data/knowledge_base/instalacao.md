# Diretrizes de instalação
Contexto: Instalação e Infraestrutura Técnica

## Quais são as tensões nominais de entrada para os modelos comerciais de 11kW e 22kW?
A tensão nominal para modelos trifásicos é de 380V (esquema 3L / N / PE) [19, 20].

## Qual protocolo é utilizado para a integração com sistemas de gestão externos?
O sistema utiliza o protocolo OCPP (Open Charge Point Protocol) baseado em JSON/WebSockets para comunicação externa segura [21].

## Como deve ser feita a comunicação física entre o carregador HCA e um inversor GoodWe?
Deve ser utilizada a porta RS485 (RS485_A1/B1) do carregador conectada à porta correspondente do inversor [22-24].

## Qual o requisito obrigatório de proteção externa para a instalação?
É obrigatório instalar um dispositivo RCD (Dispositivo de Corrente Residual) externo tipo A [25, 26].

## Qual o papel do medidor MID opcional em instalações comerciais?
O medidor MID coleta dados de consumo certificados para fins de reembolso de faturas e transparência de custos [27, 28].

## Como é feito o acesso inicial ao carregador via Bluetooth para configuração?
Utiliza-se o app SolarGo, selecionando o número de série do dispositivo e inserindo a senha inicial 'goodwe2022' [29].

## O que acontece se o carregador perder a conexão com o sensor de monitoramento de carga?
Existe o risco de desarme dos disjuntores, pois o sistema perde a capacidade de modulação dinâmica de corrente em tempo real [1, 3].

## Como configurar o IP estático se o DHCP estiver desabilitado?
No app SolarGo, acesse More > Communication Setting > WLAN, desative o DHCP e insira manualmente o IP, Máscara e Gateway [30].

## Qual a distância máxima recomendada para o cabo de comunicação RS485?
A distância máxima para a integridade do sinal no cabo de comunicação RS485 deve ser inferior a 10 metros [31].

## Como o técnico pode vincular novos cartões RFID para uso dos funcionários?
No aplicativo, acesse 'EV Card Management' e selecione 'Binding Card' para cadastrar até 10 cartões por carregador [32, 33].
