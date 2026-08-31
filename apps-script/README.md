# Web App protegido — Sistema de Diárias

Esta pasta contém a camada privada do sistema. Ela lê a planilha no servidor e mantém tokens do Conta Azul fora do HTML e do GitHub.

## Implantação inicial

1. Abra `script.google.com` com a conta proprietária da planilha.
2. Crie um projeto chamado **Sistema de Diárias BPO**.
3. Substitua o conteúdo de `Code.gs` pelo arquivo desta pasta.
4. Em **Configurações do projeto**, marque a opção para exibir o arquivo de manifesto e substitua `appsscript.json` pelo manifesto desta pasta.
5. Clique em **Implantar → Nova implantação → Aplicativo da Web**.
6. Execute como **você** e permita acesso somente a **você** na primeira versão.
7. Autorize leitura da planilha e acesso externo.

O endereço `/exec` gerado será o novo acesso remoto protegido.

## Conta Azul

As credenciais e tokens devem ser salvos em **Configurações do projeto → Propriedades do script**. Nunca coloque `client_secret`, `access_token` ou `refresh_token` no HTML ou no GitHub.

A função `listarFornecedoresContaAzul` usa a API de Pessoas (`/v1/pessoas`) filtrada pelo perfil `Fornecedor`. A etapa seguinte é ligar o fluxo OAuth e definir a regra de conciliação por CPF antes de permitir qualquer atualização no CRM.
