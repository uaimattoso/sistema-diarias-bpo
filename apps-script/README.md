# Web App protegido — Sistema de Diárias

Esta pasta contém a camada privada do sistema. Nesta primeira etapa, ela lê CPF, nome e PIX da planilha no servidor sem expor esses dados no HTML ou no GitHub.

## Implantação inicial

1. Abra `script.google.com` com a conta proprietária da planilha.
2. Crie um projeto chamado **Sistema de Diárias BPO**.
3. Substitua o conteúdo de `Code.gs` pelo arquivo desta pasta.
4. Em **Configurações do projeto**, marque a opção para exibir o arquivo de manifesto e substitua `appsscript.json` pelo manifesto desta pasta.
5. Clique em **Implantar → Nova implantação → Aplicativo da Web**.
6. Execute como **você** e permita acesso somente a **você** na primeira versão.
7. Autorize leitura da planilha e acesso externo.

O endereço `/exec` gerado será o novo acesso remoto protegido.

O Conta Azul não faz parte desta primeira implantação. Ele será tratado separadamente depois que a leitura da planilha estiver validada.
