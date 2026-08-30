# Sistema de Diárias

Aplicação para cadastrar colaboradores e lançar pagamentos de diárias, com filtro semanal, resumo dos valores e exportação compatível com o Conta Azul. O projeto também inclui um dashboard financeiro opcional feito com Streamlit.

## Funcionalidades

- cadastro e edição de colaboradores;
- validação de CPF e chave PIX;
- lançamentos de diárias por data e setor;
- fechamento e consulta por período semanal;
- exportação de planilhas;
- armazenamento local no navegador;
- dashboard financeiro com KPIs, gráficos e chat opcional via Google Gemini.

## Usar o controle de diárias

Abra o arquivo `index.html` em um navegador moderno. Não é necessário instalar nada.

Os cadastros e lançamentos ficam no `localStorage` do navegador. Portanto, eles permanecem somente naquele navegador e dispositivo e podem ser apagados ao limpar os dados do site. Faça exportações periódicas como cópia de segurança.

Para publicar a interface pelo GitHub Pages, use a raiz da branch principal como origem. O arquivo `index.html` será aberto como página inicial.

## Executar o dashboard financeiro

Requer Python 3.10 ou superior.

```bash
pip install -r requirements.txt
streamlit run dashboard_financeiro.py
```

O dashboard abre em `http://localhost:8501`. Na ausência de uma planilha, ele exibe dados fictícios para demonstração.

### Integração opcional com Gemini

Informe a chave na barra lateral ou configure a variável de ambiente `GEMINI_API_KEY`. Nunca salve uma chave real no código, no `.env` versionado ou no GitHub.

### Estrutura da planilha financeira

| Data | Categoria | Valor | Status |
| --- | --- | ---: | --- |
| 01/01/2026 | Faturamento de Serviços | 85000.00 | Pago |
| 01/01/2026 | Folha de Pagamento | -32000.00 | Pago |

Valores positivos representam entradas; valores negativos representam saídas.

## Privacidade

CPF, chave PIX e informações financeiras são dados sensíveis. Os documentos e exportações locais (`.csv`, `.xls`, `.xlsx` e `.pdf`) são ignorados pelo Git e não devem ser publicados. Antes de compartilhar uma exportação, confirme que ela não contém dados pessoais ou bancários.

## Arquivos principais

- `index.html`: aplicação de controle de diárias, executada no navegador;
- `dashboard_financeiro.py`: dashboard financeiro opcional;
- `requirements.txt`: dependências do dashboard.
