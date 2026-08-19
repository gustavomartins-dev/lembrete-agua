# Como contribuir

1. Verifique as issues abertas e avise em qual deseja trabalhar.
2. Crie uma branch de trabalho a partir de `local`.
3. Faça alterações pequenas, documentadas e acompanhadas de testes.
4. Execute lint e testes localmente.
5. Abra um pull request explicando o problema, a solução e como verificou o resultado.

Use português ou inglês em discussões. No código, prefira nomes técnicos claros e consistentes. Nunca inclua segredos, tokens, dados pessoais ou artefatos do ambiente local.

## Fluxo de branches

- `local`: recebe o desenvolvimento e os primeiros testes.
- `dev`: recebe alterações de `local` por pull request para integração.
- `prod`: recebe versões validadas de `dev` por pull request.
- `main`: espelha a versão estável publicada em `prod`.

Não envie alterações diretamente para `dev` ou `prod`. Cada promoção deve manter lint, testes e revisão do diff aprovados.

## Ambiente local

No Ubuntu 24.04 LTS, prepare o projeto e execute as verificações com:

```bash
sudo apt install python3-venv python3-gi python3-gi-cairo gir1.2-gtk-4.0 libnotify-bin
python3 -m venv --system-site-packages .venv
source .venv/bin/activate
python -m pip install -e . pytest ruff
ruff check .
pytest
```
