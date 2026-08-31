/**
 * Sistema de Diárias — camada protegida Google Apps Script.
 *
 * O HTML público no GitHub contém apenas a interface. Esta camada executa com
 * a conta autorizada e lê a planilha sem expor CPF ou PIX no código público.
 */

const DIARIAS = Object.freeze({
  spreadsheetId: '133Nv2tzOZOzMSgQdF_MCE5X3J6BPb62C9YbmjTOds9Q',
  sheetName: 'Página1',
  interfaceUrl: 'https://raw.githubusercontent.com/uaimattoso/sistema-diarias-bpo/85943b5/index.html',
  firebaseApiKey: 'AIzaSyBjK_9axgVosw0ksePw85uEoB-5ma1IlLs'
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

function listarColaboradoresDaPlanilha(idToken) {
  validarTokenFirebase_(idToken);
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

function validarTokenFirebase_(idToken) {
  if (!idToken) throw new Error('Acesso negado: autenticação obrigatória.');

  const resposta = UrlFetchApp.fetch(
    'https://identitytoolkit.googleapis.com/v1/accounts:lookup?key=' + encodeURIComponent(DIARIAS.firebaseApiKey),
    {
      method: 'post',
      contentType: 'application/json',
      payload: JSON.stringify({ idToken: idToken }),
      muteHttpExceptions: true
    }
  );

  if (resposta.getResponseCode() !== 200) {
    throw new Error('Acesso negado: sessão inválida ou expirada.');
  }

  const dados = JSON.parse(resposta.getContentText() || '{}');
  const usuario = dados.users && dados.users[0];
  if (!usuario || !usuario.email) {
    throw new Error('Acesso negado: usuário não identificado.');
  }
  return usuario;
}

function somenteDigitos_(valor) {
  return String(valor || '').replace(/\D/g, '');
}

function formatarCpf_(cpf) {
  return cpf.slice(0, 3) + '.' + cpf.slice(3, 6) + '.' + cpf.slice(6, 9) + '-' + cpf.slice(9);
}
