/**
 * Sistema de Diárias — camada protegida Google Apps Script.
 *
 * O HTML público no GitHub contém apenas a interface. Esta camada executa com
 * a conta autorizada, lê a planilha e guarda credenciais do Conta Azul nas
 * Propriedades do Script.
 */

const DIARIAS = Object.freeze({
  spreadsheetId: '133Nv2tzOZOzMSgQdF_MCE5X3J6BPb62C9YbmjTOds9Q',
  sheetName: 'Página1',
  interfaceUrl: 'https://raw.githubusercontent.com/uaimattoso/sistema-diarias-bpo/main/index.html',
  contaAzulApi: 'https://api-v2.contaazul.com',
  pageSize: 100
});

function doGet() {
  const html = UrlFetchApp.fetch(DIARIAS.interfaceUrl, { muteHttpExceptions: true });
  if (html.getResponseCode() !== 200) {
    throw new Error('Não foi possível carregar a interface do Sistema de Diárias.');
  }
  return HtmlService.createHtmlOutput(html.getContentText())
    .setTitle('Controle de Pagamentos - Diárias')
    .setXFrameOptionsMode(HtmlService.XFrameOptionsMode.DEFAULT);
}

function listarColaboradoresDaPlanilha() {
  const aba = SpreadsheetApp.openById(DIARIAS.spreadsheetId).getSheetByName(DIARIAS.sheetName);
  if (!aba) throw new Error('A aba "' + DIARIAS.sheetName + '" não foi encontrada.');

  const valores = aba.getDataRange().getDisplayValues();
  if (valores.length < 2) return [];

  const porCpf = {};
  valores.slice(1).forEach(function (linha) {
    const cpf = somenteDigitos_(linha[0]).padStart(11, '0');
    const nome = String(linha[1] || '').trim();
    const observacao = String(linha[2] || '').trim();
    if (cpf.length !== 11 || !nome || !observacao) return;
    porCpf[cpf] = { cpf: formatarCpf_(cpf), nome: nome, observacao: observacao };
  });

  return Object.keys(porCpf).sort().map(function (cpf) { return porCpf[cpf]; });
}

/**
 * Consulta fornecedores (Pessoas) no Conta Azul e devolve um resumo por CPF.
 * Configure CA_ACCESS_TOKEN nas Propriedades do Script antes do primeiro uso.
 * A renovação OAuth será adicionada quando as credenciais do app forem ligadas.
 */
function listarFornecedoresContaAzul() {
  const token = propriedadeObrigatoria_('CA_ACCESS_TOKEN');
  let pagina = 1;
  let resultado = [];

  while (true) {
    const url = DIARIAS.contaAzulApi + '/v1/pessoas?' + montarQuery_({
      pagina: pagina,
      tamanho_pagina: DIARIAS.pageSize,
      tipo_perfil: 'Fornecedor',
      tipo_ordenacao: 'NOME',
      ordem_ordenacao: 'ASC'
    });
    const resposta = UrlFetchApp.fetch(url, {
      method: 'get',
      headers: { Authorization: 'Bearer ' + token },
      muteHttpExceptions: true
    });
    const corpo = JSON.parse(resposta.getContentText() || '{}');
    if (resposta.getResponseCode() < 200 || resposta.getResponseCode() >= 300) {
      throw new Error('Conta Azul respondeu ' + resposta.getResponseCode() + ': ' + resposta.getContentText());
    }

    const itens = corpo.items || [];
    resultado = resultado.concat(itens);
    if (!itens.length || resultado.length >= Number(corpo.totalItems || corpo.total_itens || 0)) break;
    pagina++;
  }
  return resultado;
}

function propriedadeObrigatoria_(nome) {
  const valor = PropertiesService.getScriptProperties().getProperty(nome);
  if (!valor) throw new Error('Configure a propriedade segura ' + nome + '.');
  return valor;
}

function somenteDigitos_(valor) {
  return String(valor || '').replace(/\D/g, '');
}

function formatarCpf_(cpf) {
  return cpf.slice(0, 3) + '.' + cpf.slice(3, 6) + '.' + cpf.slice(6, 9) + '-' + cpf.slice(9);
}

function montarQuery_(objeto) {
  return Object.keys(objeto).map(function (chave) {
    return encodeURIComponent(chave) + '=' + encodeURIComponent(objeto[chave]);
  }).join('&');
}
