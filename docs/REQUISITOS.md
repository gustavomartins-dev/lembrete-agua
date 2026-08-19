# Requisitos do produto

## Objetivo

Ajudar pessoas que usam Ubuntu a criar o hábito de beber água por meio de lembretes locais, configuráveis e discretos.

## Fluxo principal

1. A pessoa abre o aplicativo.
2. Define uma quantidade de goles e um intervalo, ou abre a calculadora opcional.
3. Na calculadora, informa mL/prazo e escolhe entre três recomendações.
4. Inicia os lembretes.
5. O aplicativo permanece ativo sem bloquear a área de trabalho.
6. Ao fim de cada intervalo, uma notificação nativa é exibida.
7. Ao clicar no aviso, a pessoa confirma se bebeu ou não.
8. O dashboard atualiza timer, histórico e desempenho.
9. A pessoa pode pausar, retomar ou alterar o plano.

## Requisitos funcionais

- RF01: configurar manualmente goles e intervalo em minutos ou horas.
- RF02: oferecer cálculo opcional por volume e prazo em painel inicialmente recolhido.
- RF03: iniciar, pausar e retomar lembretes.
- RF04: exibir estado atual e configuração ativa.
- RF05: emitir notificação nativa clicável com quantidade e pluralização corretas.
- RF06: persistir preferências localmente.
- RF07: oferecer inicialização automática opcional.
- RF08: recuperar-se de configuração ausente ou inválida.
- RF09: registrar cada lembrete como pendente, confirmado ou não consumido.
- RF10: abrir a confirmação correspondente ao clicar na notificação.
- RF11: exibir timer circular, histórico e desempenho de 7 e 30 dias.
- RF12: oferecer recomendações Leve, Equilibrada e Intensiva, destacando a Equilibrada.

## Requisitos não funcionais

- Interface e mensagens em português brasileiro.
- Operação totalmente local e offline.
- Nenhuma telemetria ou coleta de dados.
- Baixo consumo de recursos.
- Compatibilidade com Ubuntu LTS suportado e Windows 10/11 via MSYS2 UCRT64.
- Interface responsiva e navegável por teclado.
- Código testável e documentado.

## Fora do MVP

- Aplicativo móvel.
- Sincronização em nuvem.
- Contas de usuário.
- Metas médicas ou cálculo clínico de hidratação.
- Sincronização do histórico entre dispositivos.

## Observação de saúde

O aplicativo é apenas um lembrete e não oferece orientação médica. A quantidade adequada de água varia conforme a pessoa e suas condições de saúde.
