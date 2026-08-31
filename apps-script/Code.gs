/**
 * Sistema de Diárias — camada protegida Google Apps Script.
 *
 * O HTML público no GitHub contém apenas a interface. Esta camada executa com
 * a conta autorizada e lê a planilha sem expor CPF ou PIX no código público.
 */

const DIARIAS = Object.freeze({
  spreadsheetId: '133Nv2tzOZOzMSgQdF_MCE5X3J6BPb62C9YbmjTOds9Q',
  sheetName: 'Página1',
  interfaceUrl: 'https://raw.githubusercontent.com/uaimattoso/sistema-diarias-bpo/main/index.html'
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

function somenteDigitos_(valor) {
  return String(valor || '').replace(/\D/g, '');
}

function formatarCpf_(cpf) {
  return cpf.slice(0, 3) + '.' + cpf.slice(3, 6) + '.' + cpf.slice(6, 9) + '-' + cpf.slice(9);
}
