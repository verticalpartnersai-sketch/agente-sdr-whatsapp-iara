# Toda a estrutura do Agente será da seguinte forma:

1. Agente estará integrado com o SUPABASE como banco de dados para:

    - TABELA (leads_wpp) para Armazenar dados do lead com as colunas:
        - Nome
        - Número de telefone
        - ultima_interacao_lead (horário que o lead enviou a última mensagem)
        - ultima_interacao_agente (horário que o agente enviou a última mensagem)
        - agendar_conversa (horário para agendar a próxima conversa). Exemplo: lead não está disponível no momento e pediu para chamar as 10h30, então o agente agendará a chamada para as 10h30. (Isso é um follow-up personalizado de acordo com a necessidade do lead)
        - fup_enviado (nesta coluna tem uma contagem de quantas vezes o agente enviou um follow-up para este lead). Máximo até 3 vezes (3 follow-ups dentro de uma janela de 72 horas)
        - tags (serve para o Agente de follow-up fazer uma analise da conversa (ler o histórico de mensagens da conversa da tabela "memoria" e identificar se o lead ainda está interessado em continuar a conversa, se o lead demonstrar algum desinteresse, inserimos a tag "BREAK" e paramos o follow-up.) Por padrão a coluna "tags" vem com o valor "IA" isso quer dizer que por enquanto está permitido fazer follow-up. No caso o Agente deve sempre antes de fazer o follow-up, identificar nesta coluna se tem a tag "IA", se tiver progresse para o follow-up, se tiver "BREAK" interrompe o follow-up para aquele lead.)

        - TABELA (knowledege) para Armazenar o conhecimento do Agente com as colunas:
            - id (chave primária)
            - assunto (assunto do conhecimento)
            - conteudo (conteúdo do conhecimento)
            - Perguntas (pergunta relacionada ao conhecimento)
            - Respostas (respostas relacionadas à pergunta)
            - tags (tags relacionadas ao conhecimento)
            - embedding (embedding do conteúdo do conhecimento)
            - metadata (metadados do conhecimento)

OBS: O RAG do Agente deve ser feito de forma HIBRIDA com RAG semântico e RAG híbrido, acima eu dei uma sugestão de colunas, mas você pode utilizar o padrão que for mais adequado para o Agente e mais inteligente.

==================================================

2. O Agente será integrado com o REDIS para armazenar as mensagens trocadas com os leads (histórico de mensagens) com as colunas:

    - TABELA (memoria_wpp) para Armazenar as mensagens trocadas com os leads (histórico de mensagens) com as colunas:
    - id (chave primária)
    - numero_telefone (número de telefone do lead)
    - mensagem (conteúdo da mensagem)
    - tipo (se é uma mensagem do lead ou do agente)
    - timestamp (horário da mensagem)

Ou siga o formato ideal de tabelas e colunas ideias que o REDIS suporta para memoria do Agente. TODA memória do Agente deve ser armazenada no REDIS.

    - O Agente também será integrado com o REDIS para buffer de mensagens.
    - O Buffer deve ter uma duração de até no máximo 30 segundos aguardando o lead enviar uma mensagem, depois concatena todas as mensagens em um único buffer e responde ao lead de acordo com as mensagens do buffer.

===================================================

3. O Agente precisará ser integrado com o RabbitMQ para fila de mensagens.

    - No máximo até 10 requisições na fila do RabbitMQ, envia para o Agente processar.

==================================================

4. O Agente deve interpretar:

- Imagens
- Vídeos
- Áudios
- Documentos

==================================================

5. O Agente deve ter um sistema de follow-up da seguinte forma:

    - Follow-up de 30 minutos após a última mensagem do Agente.
    - Se o lead não respondeu, aguarda mais 4 horas e envia outra mensagem.
    - Se o lead ainda assim não respondeu, envia mais uma mensagem após 12 horas.
    - Se o lead ainda assim não respondeu, envia mais uma mensagem após 24 horas.

Observações:

    - TODOS os follow-ups devem ser feitos na janela de horário das 07h até as 21h.
    - Se o lead responder, o Agente deve resetar o contador de follow-ups para 0.
    - Este Follow-up deve ser trabalhado de acordo com a tabela (leads_wpp) nas colunas: (fup_enviado) e (ultima_interacao_agente) e (tags).
    - Se o lead disser que deseja conversar em outro momento, o Agente deve perguntar o horário em que pode conversar, registrar na tabela (leads_wpp) na coluna (agendar_conversa) e depois fazer o follow-up para aquele horário.
    - O Agente não deve fazer follow-up para leads que estão com a tag "reuniao_agendada", "reuniao_cancelada" ou "reuniao_reagendada" na tabela (leads_wpp) na coluna (tags).
    - O Agente não deve fazer follow-up para leads que estão com a tag "não_interessado" na tabela (leads_wpp) na coluna (tags).
    - O Agente não deve fazer follow-up para leads que estão com a tag "atendimento_humano" na tabela (leads_wpp) na coluna (tags).

Lembre-se: TODOS os follow-ups não devem ultrapassar a janela de 72 horas, faça um cálculo e veja se os horários que eu inseri acima encaixam em 72 horas.

==================================================

6. O Agente deve ter uma integração com o Google Calendar:

1. Agendamento de Reuniões da seguinte forma:
    - O Agente deve agendar reuniões com o lead no Google Calendar.
    - O Agente irá fornecer o lead horários disponiveis no Google Calendar.
    - O Agente deve aguardar a confirmação do lead ou se o lead sugerir outro horário, o Agente deve verificar no Google Calendar se o horário está disponivel.
    - Se o horário estiver disponível, o Agente deve agendar a reunião no Google Calendar.
    - Se o horário não estiver disponível, o Agente deve fornecer outro horário ao lead.

2. Cancelamento de Reuniões da seguinte forma:
    - Se o lead solicitar o cancelamento da reunião, o Agente deve identifiar a reunião agendada e cancelar.

3. Reagendamento de reuniões:
    - Se o lead solicitar o reagendamento da reunião, o Agente deve identificar a reunião agendada e fornecer ao lead os novos horários disponíveis.
    - O Agente deve aguardar a confirmação do lead ou se o lead sugerir outro horário, o Agente deve verificar no Google Calendar se o horário está disponivel.
    - Se o horário estiver disponível, o Agente deve reagendar a reunião no Google Calendar.
    - Se o horário não estiver disponível, o Agente deve fornecer outro horário ao lead.

4. Atualização de Reuniões

    - Caso o lead queira adicionar um novo participante na reunião ou alterar algum e-mail de convite dentro do agendamento da reunião no Google calendar;
    - O Agente deve solicitar quais alterações o lead quer fazer, se for remover um e-mail ou adicionar um novo e-mail ou atualizar algum e-mail, o Agente deve prosseguir e fazer conforme necessário.

5. O Agente deve fazer um lembrete dos Agendamentos:

    - Enviar uma mensagem para o lead com uma mensagem personalizada que estará dentro do PROMPT do Agente para lembrar o lead da reunião 24horas antes da reunião e 2horas antes da reunião, tentando ao máximo confirmar a presença do lead.
    - Se o lead quiser reagendar, o Agente deve usar a tool "reagenda_reunioes" e fazer o reagendamento com o lead.
    - Se o lead quiser cancelar, o Agente deve entender o motivo, tentar contornar o máximo de objeções possiveis e se mesmo assim o lead não quiser, deve cancelar a reunião utilizando a tool "cancela_reunioes".

5. TOOLs do Google Calendar que o Agente deve ter acesso:

    - consulta_horários
    - agenda_reunioes
    - cancela_reunioes
    - reagenda_reunioes
    - atualiza_informacoes
    - consulta_reunioes

Observações: 

    - O Agente deve SEMPRE consultar todas as TOOls.
    - As TOOls devem estar no PROMPT do Agente.
    - SEMPRE que uma reunião for agendada, cancelada, etc... O Agente deve inserir na tabela (leads_wpp) na coluna (tags) a tag "reuniao_agendada" ou "reuniao_cancelada" ou "reuniao_reagendada".
    
"Me diga quais credenciais você precisa do Google Calendar para fazer a integração com o Agente."

==================================================

7. O Agente deve estar integrado com a ElevenLabs para poder enviar áudios SEMPRE que necessário ou quando o lead pedir para o Agente enviar um áudio.

    - Aqui está a APIKey da ElevenLabs:

==================================================

8. SEMPRE que uma reunião for agendada com o lead:

    - O Agente deve enviar um vídeo para o lead, este video será um vídeo do nosso sócio Gessyan Lion se apresentando e dando um breve resumo de como será a reunião.
    - Eu irei disponibilizar para você uma URL do supabase com o LINK do vídeo, e você irá inserir no sistema do Agente para ele enviar este vídeo.

==================================================

9. Iremos usar a API OFICIAL DO WHATSAPP para poder fazer a integração com o Agente e ele irá se comunicar com os leads através do WhatsApp.

"Me diga quais credenciais você precisa do WhatsApp API Oficial para fazer a integração com o Agente."

==================================================

10. Particularidades do Agente:

    - Se em algum momento da conversa o Agente identificar que o lead não tem interesse, não quer mais receber mensagens ou qualquer outro tipo de mensagem negativa, o Agente deve inserir na tabela (leads_wpp) na coluna (tags) a tag "não_interessado".
    - SEMPRE que o Agente identificar que o lead quer ser atendido por um humano/atendimento humano, deve respeitar, dizer que irá transferir para um atendente humano e inserir na tabela (leads_wpp) na coluna (tags) a tag "atendimento_humano".
    - Os fluxos da pasta "Agentes em JSON do N8N" são apenas fluxos do N8N que eu extrai para você ter uma noção de como fizemos os Agentes no N8N.
    - O Agente deve seguir 100% Python com LangChain.
    - O Agente deve ter acesso a todas as TOOls que foram mencionadas anteriormente e também outras tools que voce precisar criar.
    - O Agente deve seguir 100% do PROMPT que deve estar em um arquivo .md.
    - O Agente deve ter acesso ao arquivo .md com o PROMPT.
    - O prompt do Agente deve ser EXTREMAMENTE HUMANIZADO.
    - O Agente deve enviar mensagens concatenadas, picotadas e com no máximo de 20 à 30 palavras por mensagem.
    - O Agente precisa ser humanizado, então não precisa concatenar/quebrar mensagens somente nas pontuações, o Agente deve ser inteligente suficiente para entender o final da frase e quebrar a mensagem, enviar e depois em outra mensagem enviar o restante da mensagem e assim sucessivamente.

==================================================