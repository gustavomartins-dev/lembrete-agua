# Requisitos do produto

## Objetivo

Ajudar pessoas que usam Ubuntu a criar o hábito de beber água por meio de lembretes locais, configuráveis e discretos.

## Fluxo principal

1. A pessoa abre o aplicativo.
2. Define uma quantidade em mL e um prazo.
3. Confere o plano calculado e inicia os lembretes.
4. O aplicativo permanece ativo sem bloquear a área de trabalho.
5. Ao fim de cada intervalo, uma notificação nativa é exibida.
6. Ao clicar no aviso, a pessoa confirma se bebeu ou não.
7. O dashboard atualiza timer, histórico e desempenho.
8. A pessoa pode pausar, retomar ou alterar o plano.

## Requisitos funcionais

- RF01: configurar volume positivo em mililitros e prazo em minutos ou horas.
- RF02: calcular goles e intervalo usando uma regra explícita e consistente.
- RF03: iniciar, pausar e retomar lembretes.
- RF04: exibir estado atual e configuração ativa.
- RF05: emitir notificação nativa clicável com quantidade e pluralização corretas.
- RF06: persistir preferências localmente.
- RF07: oferecer inicialização automática opcional.
- RF08: recuperar-se de configuração ausente ou inválida.
- RF09: registrar cada lembrete como pendente, confirmado ou não consumido.
- RF10: abrir a confirmação correspondente ao clicar na notificação.
- RF11: exibir timer circular, histórico e desempenho de 7 e 30 dias.

## Requisitos não funcionais

- Interface e mensagens em português brasileiro.
- Operação totalmente local e offline.
- Nenhuma telemetria ou coleta de dados.
- Baixo consumo de recursos.
- Compatibilidade prioritária com versões Ubuntu LTS ainda suportadas.
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
