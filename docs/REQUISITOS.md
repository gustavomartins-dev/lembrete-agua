# Requisitos do produto

## Objetivo

Ajudar pessoas que usam Ubuntu a criar o hábito de beber água por meio de lembretes locais, configuráveis e discretos.

## Fluxo principal

1. A pessoa abre o aplicativo.
2. Define o intervalo e a quantidade de goles.
3. Inicia os lembretes.
4. O aplicativo permanece ativo sem bloquear a área de trabalho.
5. Ao fim de cada intervalo, uma notificação nativa é exibida.
6. A pessoa pode pausar, retomar ou alterar a configuração.

## Requisitos funcionais

- RF01: configurar intervalo em minutos ou horas.
- RF02: configurar uma quantidade inteira e positiva de goles.
- RF03: iniciar, pausar e retomar lembretes.
- RF04: exibir estado atual e configuração ativa.
- RF05: emitir notificação nativa com quantidade e pluralização corretas.
- RF06: persistir preferências localmente.
- RF07: oferecer inicialização automática opcional.
- RF08: recuperar-se de configuração ausente ou inválida.

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
- Histórico detalhado de consumo.

## Observação de saúde

O aplicativo é apenas um lembrete e não oferece orientação médica. A quantidade adequada de água varia conforme a pessoa e suas condições de saúde.
