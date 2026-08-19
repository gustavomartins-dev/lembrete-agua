# Lembrete de Água 💧

Aplicativo pessoal e open source para Ubuntu/Linux que exibe notificações em intervalos configuráveis, lembrando quantos goles de água a pessoa deve tomar.

> Projeto independente de Gustavo Martins. Não possui vínculo com a Chinalink nem com qualquer empresa.

## Ideia

O usuário escolhe:

- o intervalo entre os lembretes;
- a quantidade de goles por lembrete;
- se o aplicativo deve iniciar junto com a sessão;
- se deseja pausar ou retomar as notificações.

O aplicativo roda em segundo plano e mostra notificações nativas no desktop do Ubuntu.

## Status

🚧 Em planejamento. As tarefas iniciais estão nas [issues do projeto](../../issues).

## Escopo do MVP

- Interface simples para configurar intervalo e quantidade de goles.
- Notificações nativas no Ubuntu.
- Botões para iniciar, pausar e retomar os lembretes.
- Persistência das preferências entre execuções.
- Opção para iniciar automaticamente com a sessão do usuário.
- Validação dos valores informados.
- Instalação e execução documentadas.

Veja os requisitos detalhados em [docs/REQUISITOS.md](docs/REQUISITOS.md).

## Stack sugerida

- Python 3.12+
- PyGObject/GTK 4 para a interface
- `notify-send`/libnotify para notificações nativas
- JSON em `~/.config/lembrete-agua/` para configurações
- `systemd --user` ou arquivo `.desktop` para inicialização automática
- Pytest, Ruff e GitHub Actions para qualidade

A implementação pode ajustar essas escolhas se houver uma solução mais simples e bem mantida para Ubuntu.

## Como contribuir

Consulte [CONTRIBUTING.md](CONTRIBUTING.md), escolha uma issue e envie um pull request. Ao contribuir, você concorda que sua contribuição será publicada sob a licença MIT.

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

## Licença

Distribuído sob a [Licença MIT](LICENSE).
