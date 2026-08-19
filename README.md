# Lembrete de Água 💧

Aplicativo pessoal e open source para Ubuntu/Linux que cria um plano local de hidratação, envia lembretes confirmáveis e acompanha o histórico.

> Projeto independente de Gustavo Martins. Não possui vínculo com a Chinalink nem com qualquer empresa.

## Ideia

O usuário escolhe:

- quantos mililitros deseja beber;
- em quanto tempo deseja cumprir essa meta;
- se o aplicativo deve iniciar junto com a sessão;
- se deseja pausar ou retomar as notificações.

O aplicativo estima 25 mL por gole, limita cada lembrete a 5 goles e distribui automaticamente os lembretes pelo prazo. O histórico registra se a pessoa confirmou ou não cada ocorrência.

## Status

✅ MVP implementado. Melhorias e relatos de problemas são acompanhados nas [issues do projeto](../../issues).

## Recursos

- Plano automático a partir de volume em mL e prazo em minutos ou horas.
- Notificações clicáveis que abrem diretamente a confirmação do lembrete.
- Respostas “bebi” e “não bebi”, com ocorrências pendentes recuperáveis.
- Dashboard com timer circular, histórico recente e desempenho de 7 e 30 dias.
- Ícone próprio no menu, na janela e nas notificações.
- Controles para iniciar, pausar, retomar e substituir o plano.
- Preferências locais em `~/.config/lembrete-agua/config.json`.
- Histórico local em `~/.config/lembrete-agua/history.json`.
- Inicialização opcional com a sessão por um arquivo `.desktop` do usuário.
- Operação offline, sem conta, servidor, telemetria ou coleta de dados.

Veja os requisitos detalhados em [docs/REQUISITOS.md](docs/REQUISITOS.md).

## Requisitos

O ambiente prioritário é o Ubuntu 24.04 LTS ou mais recente, com Python 3.12+, GTK 4 e libnotify. Em uma instalação do Ubuntu, instale os pacotes necessários:

```bash
sudo apt update
sudo apt install python3 python3-venv python3-gi gir1.2-gtk-4.0 libnotify-bin
```

## Instalação

Clone o repositório, entre na pasta e crie um ambiente virtual que enxergue o PyGObject instalado pelo Ubuntu:

```bash
git clone https://github.com/gustavomartins-dev/lembrete-agua.git
cd lembrete-agua
python3 -m venv --system-site-packages .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
```

O modo editável é adequado ao projeto open source e cria o comando `lembrete-agua` dentro do ambiente virtual.

## Execução e uso

Com o ambiente ativado, abra o aplicativo:

```bash
lembrete-agua
```

Na aba **Plano**, defina o volume e o prazo. A recomendação calculada aparece antes do início. Selecione **Iniciar plano** para abrir o dashboard e iniciar o timer. **Pausar** preserva o tempo restante e **Retomar** continua a contagem.

Ao receber um aviso, clique na notificação ou em **Confirmar agora** para abrir a aba **Confirmação**. Responda **Sim, eu bebi** ou **Não bebi**. A resposta aparece imediatamente no histórico e atualiza o desempenho semanal e mensal. Lembretes ainda não respondidos ficam disponíveis no dashboard.

Ao fechar a janela com os lembretes ativos, ela é ocultada e o aplicativo continua em segundo plano. Execute `lembrete-agua` outra vez para reabrir a mesma instância. Para encerrar o aplicativo, pause os lembretes e feche a janela.

A opção **Iniciar com a sessão** vem habilitada por padrão e cria `~/.config/autostart/lembrete-agua.desktop`. O aplicativo também instala seu ícone, um lançador e um serviço D-Bus em `~/.local/share/` para aparecer no menu e permitir a ativação ao clicar em uma notificação. O ambiente virtual deve permanecer instalado no mesmo caminho.

## Desenvolvimento e testes

Instale as ferramentas de desenvolvimento e execute as mesmas verificações da integração contínua:

```bash
source .venv/bin/activate
python -m pip install pytest ruff
ruff check .
pytest
```

O código está separado em interface, modelos/validação, configuração, autostart, notificações e agendamento. As integrações com GTK, timers, arquivos e comandos do sistema possuem limites claros para permitir testes sem emitir notificações reais.

## Desinstalação

Na pasta clonada, remova o pacote e o ambiente virtual:

```bash
source .venv/bin/activate
python -m pip uninstall lembrete-agua
deactivate
rm -rf .venv
```

Para remover também preferências e inicialização automática:

```bash
rm -f ~/.config/autostart/lembrete-agua.desktop
rm -f ~/.local/share/applications/io.github.gustavomartinsdev.LembreteAgua.desktop
rm -f ~/.local/share/dbus-1/services/io.github.gustavomartinsdev.LembreteAgua.service
rm -f ~/.local/share/icons/hicolor/scalable/apps/io.github.gustavomartinsdev.LembreteAgua.svg
rm -rf ~/.config/lembrete-agua
```

Os últimos comandos apagam permanentemente apenas os dados locais criados pelo aplicativo.

## Limitações do MVP

- O MVP não possui ícone na bandeja; reabra a janela executando o comando novamente.
- A estimativa de 25 mL por gole é operacional, não uma medição exata.
- O aplicativo registra confirmações, mas não oferece orientação médica.
- A integração visual depende do serviço de notificações da sessão Linux.

## Como contribuir

Consulte [CONTRIBUTING.md](CONTRIBUTING.md), escolha uma issue e envie um pull request. Ao contribuir, você concorda que sua contribuição será publicada sob a licença MIT.

<details>
<summary>Prompt original para implementar o projeto com IA no VS Code</summary>

## Prompt para usar na IA do VS Code

Copie todo o texto abaixo e cole no chat da IA com este repositório aberto:

```text
Você é um engenheiro de software responsável por implementar este repositório. Leia integralmente README.md, docs/REQUISITOS.md, CONTRIBUTING.md e as configurações existentes antes de alterar qualquer arquivo.

Crie o MVP do “Lembrete de Água”, um aplicativo desktop pessoal e open source para Ubuntu/Linux. O usuário deve configurar um intervalo de tempo e uma quantidade de goles. Enquanto estiver ativo, o aplicativo deve exibir uma notificação nativa dizendo para beber a quantidade configurada de goles.

Requisitos obrigatórios:
1. Use Python 3.12+ e uma interface GTK 4 com PyGObject, salvo se o ambiente revelar uma incompatibilidade real; nesse caso, explique e use a alternativa Linux nativa mais simples.
2. Crie uma interface pequena e acessível com campos para intervalo (valor e unidade: minutos/horas), quantidade de goles, iniciar, pausar/retomar e indicação clara do estado atual.
3. Não permita intervalo ou quantidade de goles iguais a zero, negativos ou inválidos. Mostre mensagens de erro amigáveis em português brasileiro.
4. Envie notificações nativas no Ubuntu com título “Hora de beber água 💧” e mensagem com singular/plural correto, por exemplo “Beba 1 gole de água” ou “Beba 5 goles de água”.
5. Mantenha o agendamento sem travar a interface e evite notificações duplicadas.
6. Salve preferências em ~/.config/lembrete-agua/config.json usando escrita segura. Se o arquivo estiver ausente ou inválido, use padrões sensatos sem encerrar o programa.
7. Adicione opção de iniciar automaticamente com a sessão do usuário, usando um mecanismo adequado ao desktop Linux, e permita desativá-la.
8. Organize o código em módulos pequenos, com separação entre interface, configuração, notificações e agendamento. Use nomes claros e type hints.
9. Não colete telemetria, dados pessoais ou informações de uso. Não dependa de servidor, conta ou internet.
10. Adicione testes unitários para validação, persistência, pluralização e lógica do agendador. Isole integrações do sistema para que possam ser simuladas.
11. Configure Ruff e Pytest em pyproject.toml e um workflow do GitHub Actions para lint e testes.
12. Escreva instruções exatas de instalação, execução, testes e desinstalação no README. Inclua dependências apt necessárias para Ubuntu suportado.
13. Inclua um ícone simples somente se puder ser criado no próprio repositório sem copiar material protegido.
14. Preserve a licença MIT, o aviso de projeto independente e os templates do GitHub.

Modo de trabalho:
- Primeiro, examine o repositório e apresente um plano curto relacionando a implementação às issues existentes.
- Depois, implemente uma issue por vez em commits pequenos e descritivos, sem apagar documentação útil.
- Execute lint e testes após cada etapa relevante.
- Não afirme que algo funciona sem executar a verificação possível no ambiente.
- Ao final, faça uma revisão completa, corrija falhas encontradas e informe arquivos alterados, comandos executados, resultados dos testes e limitações restantes.

Critérios de conclusão:
- É possível abrir o app, configurar tempo e goles, iniciar e pausar lembretes.
- As notificações aparecem no Ubuntu no intervalo correto.
- As configurações sobrevivem ao fechamento do app.
- O app não congela e não dispara lembretes duplicados.
- Testes e lint passam.
- Uma pessoa seguindo apenas o README consegue instalar, executar e remover o app.

Comece lendo os arquivos e planejando. Em seguida, implemente o MVP completo, tomando decisões razoáveis sem interromper o trabalho por detalhes pequenos.
```

</details>

## Licença

Distribuído sob a [Licença MIT](LICENSE).
