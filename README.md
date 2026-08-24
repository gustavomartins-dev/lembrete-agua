# Lembrete de Água 💧

Aplicativo pessoal e open source para Ubuntu/Linux e Windows que cria um plano local de hidratação, envia lembretes confirmáveis e acompanha o histórico.

> Projeto desenvolvido com auxílio integral de inteligência artificial, sob direção, decisões e validação de Gustavo Martins.

> Projeto independente de Gustavo Martins. Não possui vínculo com a Chinalink nem com qualquer empresa.

## Ideia

No modo principal, o usuário escolhe:

- quantos goles deseja tomar por lembrete;
- o intervalo entre os lembretes;
- se o aplicativo deve iniciar junto com a sessão;
- se deseja pausar ou retomar as notificações.

Opcionalmente, um painel recolhido calcula três planos a partir de uma meta em mL e um prazo. O histórico registra se a pessoa confirmou ou não cada ocorrência.

## Status

✅ MVP implementado. Melhorias e relatos de problemas são acompanhados nas [issues do projeto](../../issues).

## Recursos

- Plano manual contínuo com goles e intervalo definidos livremente.
- Calculadora opcional recolhida com recomendações Leve, Equilibrada e Intensiva.
- Recomendação Equilibrada destacada como escolha principal.
- Notificações clicáveis que abrem diretamente a confirmação do lembrete.
- Respostas “bebi” e “não bebi”, com ocorrências pendentes recuperáveis.
- Dashboard com timer circular, histórico recente e desempenho de 7 e 30 dias.
- Ícone próprio no menu, na janela e nas notificações.
- Controles para iniciar, pausar, retomar e substituir o plano.
- Preferências, histórico e timer ativo em um banco SQLite local.
- Inicialização opcional com a sessão por um arquivo `.desktop` do usuário.
- Operação offline, sem conta, servidor, telemetria ou coleta de dados.

Veja os requisitos detalhados em [docs/REQUISITOS.md](docs/REQUISITOS.md).

## Ubuntu/Linux

### Requisitos

O ambiente prioritário é o Ubuntu 24.04 LTS ou mais recente, com Python 3.12+, GTK 4 e libnotify. Em uma instalação do Ubuntu, instale os pacotes necessários:

```bash
sudo apt update
sudo apt install python3 python3-venv python3-gi python3-gi-cairo gir1.2-gtk-4.0 libnotify-bin
```

### Instalação

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

### Execução

Com o ambiente ativado, abra o aplicativo:

```bash
lembrete-agua
```

## Windows 10/11

O GTK 4 com PyGObject é suportado no Windows por meio do ambiente MSYS2 UCRT64. Instale o [MSYS2](https://www.msys2.org/), abra o terminal **MSYS2 UCRT64** e execute:

```bash
pacman -Syu
pacman -S --needed git mingw-w64-ucrt-x86_64-gtk4 \
  mingw-w64-ucrt-x86_64-python \
  mingw-w64-ucrt-x86_64-python-gobject \
  mingw-w64-ucrt-x86_64-python-pip
```

Feche e abra novamente o terminal UCRT64 se a atualização solicitar. Depois instale o projeto:

```bash
git clone https://github.com/gustavomartins-dev/lembrete-agua.git
cd lembrete-agua
python -m pip install --user -e .
python -m lembrete_agua
```

A dependência `windows-toasts` é instalada automaticamente apenas no Windows. As preferências e o histórico ficam em `%APPDATA%\Lembrete de Agua`. O interruptor **Iniciar com a sessão** usa a chave `HKCU\Software\Microsoft\Windows\CurrentVersion\Run`, sem exigir privilégios de administrador.

As notificações usam os toasts do Windows. Enquanto o aplicativo estiver executando o plano, clicar no toast traz a janela para frente e abre a confirmação correspondente.

## Uso

Na aba **Plano**, defina diretamente quantos goles deseja tomar e de quanto em quanto tempo. Selecione **Iniciar plano** para abrir o dashboard e iniciar um plano contínuo. **Pausar** preserva o tempo restante e **Retomar** continua a contagem.

No dashboard, os botões abaixo do cronômetro permitem pausar/retomar ou reiniciar somente a contagem do próximo lembrete. Também é possível informar um novo intervalo e selecionar **Aplicar** durante um plano ativo. Essas ações não apagam o histórico nem o progresso.

O banco `lembrete-agua.sqlite3` fica em `~/.config/lembrete-agua/` no Linux e em `%APPDATA%\Lembrete de Agua` no Windows. Ao reabrir o aplicativo, o plano, a pausa e o prazo exato do próximo aviso são restaurados. Arquivos JSON de versões anteriores são migrados automaticamente.

Para receber ajuda no cálculo, abra **Cálculo automático (opcional)**, informe os mL e o prazo e escolha uma opção:

- **Leve:** até 3 goles por aviso, com lembretes mais frequentes.
- **Equilibrado ★:** até 5 goles por aviso; é a recomendação principal.
- **Intensivo:** até 8 goles por aviso, com lembretes menos frequentes.

Cada opção mostra previamente o número de avisos e o intervalo calculado. Editar novamente qualquer campo manual muda a seleção de volta para o modo manual.

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

No Windows, execute no terminal UCRT64:

```bash
python -m pip uninstall lembrete-agua windows-toasts
rm -rf "$APPDATA/Lembrete de Agua"
reg delete 'HKCU\Software\Microsoft\Windows\CurrentVersion\Run' \
  /v 'Lembrete de Água' /f
```

## Limitações do MVP

- O MVP não possui ícone na bandeja; reabra a janela executando o comando novamente.
- A estimativa de 25 mL por gole é operacional, não uma medição exata.
- O aplicativo registra confirmações, mas não oferece orientação médica.
- A integração visual depende do serviço de notificações da sessão Linux.
- A integração Windows foi coberta por testes automatizados, mas precisa de validação visual final em uma máquina Windows 10/11.

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
