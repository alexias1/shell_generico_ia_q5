# Shell Genérico de IA — Questão 5

Implementa a arquitetura solicitada: base de conhecimento (fatos e regras), editor, Forward Chaining, Backward Chaining, Mixed Chaining, explicação POR QUÊ?/COMO? e interface.

## Executar
1. `python -m venv .venv`
2. Windows: `.venv\\Scripts\\activate`
3. `pip install -r requirements.txt`
4. `python app.py`
5. Acesse `http://127.0.0.1:5000`

A base é genérica e pode ser substituída por qualquer domínio. A base inicial é apenas uma demonstração de crédito.

## Mixed Chaining
A estratégia implementada primeiro fecha as consequências alcançáveis por Forward Chaining; se o objetivo não for encontrado, executa Backward Chaining direcionado ao objetivo.