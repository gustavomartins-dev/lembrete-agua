# Changelog

Todas as mudanças relevantes deste projeto serão registradas neste arquivo.

## [Não publicado]

### Adicionado

- Pausa automática quando o lembrete anterior continua sem resposta no próximo horário.
- Limpeza das notificações pertencentes ao aplicativo ao pausar automaticamente ou iniciar uma nova instância.
- Notificações urgentes e de duração ampliada para destacar a necessidade de resposta.
- Botão **Confirmar agora** registra o consumo diretamente pela notificação.

## [0.2.0] - 2026-08-19

### Adicionado

- Banco SQLite local para preferências, histórico e sessão ativa.
- Restauração do prazo, estado de pausa e progresso depois de reiniciar o app.
- Alteração do intervalo diretamente no dashboard.
- Botões para pausar, retomar e reiniciar a contagem do próximo lembrete.
- Migração automática dos arquivos JSON de versões anteriores.

### Corrigido

- Fallback visual do cronômetro quando a integração Cairo opcional não está disponível.
- Prevenção de timers duplicados ao alterar ou reiniciar o intervalo.

[Não publicado]: https://github.com/gustavomartins-dev/lembrete-agua/compare/prod...local
[0.2.0]: https://github.com/gustavomartins-dev/lembrete-agua/compare/f068bfe...aad1bba
