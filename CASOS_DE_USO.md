# CASOS DE USO - PLANNER FINANCEIRO WEB

**Projeto:** Sistema de Gestão Financeira Pessoal
**Versão:** 1.0
**Data:** 18 de Dezembro de 2025
**Baseado em:** Meu_Planner_Financeiro_MacOs_V3-2.xlsm

---

## ÍNDICE

1. [Visão Geral do Sistema](#visão-geral-do-sistema)
2. [Atores](#atores)
3. [Módulos Funcionais](#módulos-funcionais)
4. [Casos de Uso por Módulo](#casos-de-uso-por-módulo)
5. [Casos de Uso Detalhados](#casos-de-uso-detalhados)
6. [Requisitos Não-Funcionais](#requisitos-não-funcionais)
7. [Diagrama de Relacionamentos](#diagrama-de-relacionamentos)

---

## VISÃO GERAL DO SISTEMA

### Objetivo
Plataforma web de gestão financeira pessoal que permite controle completo de receitas, despesas, investimentos e planejamento financeiro de longo prazo, acessível localmente via rede doméstica.

### Escopo
Sistema completo de controle financeiro incluindo:
- Registro e categorização de transações
- Controle de fluxo de caixa
- Gestão de investimentos (renda fixa e variável)
- Planejamento financeiro de longo prazo
- Simuladores financeiros
- Dashboards e relatórios analíticos
- Sistema multiusuário (família)

### Tecnologias
- **Backend:** Python + Flask/FastAPI
- **Frontend:** HTML5, CSS3, JavaScript (React/Vue.js)
- **Banco de Dados:** PostgreSQL ou SQLite
- **Deploy:** Servidor local (Raspberry Pi, PC sempre ligado, ou Docker)
- **Acesso:** Rede local via IP/hostname

---

## ATORES

### 1. Usuário Principal (Administrador)
- Acesso completo a todas as funcionalidades
- Gestão de configurações do sistema
- Cadastro de outros usuários
- Controle de permissões

### 2. Usuário Secundário (Cônjuge/Familiar)
- Visualização de dashboards
- Registro de transações
- Consulta de relatórios
- Acesso limitado a configurações

### 3. Sistema
- Cálculos automáticos
- Geração de relatórios
- Consolidação de dados
- Notificações e alertas

---

## MÓDULOS FUNCIONAIS

### M1. Autenticação e Perfis
Gerenciamento de usuários, login, perfis e permissões

### M2. Fluxo de Caixa
Registro e controle de todas as transações financeiras

### M3. Controle Financeiro
Visão consolidada mensal de receitas e despesas

### M4. Investimentos
Gestão de portfólio de investimentos

### M5. Planos Financeiros
Planejamento e acompanhamento de metas de longo prazo

### M6. Planejamento de Receitas
Projeção de receitas futuras

### M7. Simuladores
Ferramentas de simulação financeira

### M8. Dashboards e Relatórios
Visualizações e análises

### M9. Cadastros Base
Gerenciamento de categorias, instituições, cartões, etc.

### M10. Importação/Exportação
Integração com extratos bancários e backup de dados

---

## CASOS DE USO POR MÓDULO

### M1. AUTENTICAÇÃO E PERFIS

#### UC-M1-001: Realizar Login
**Ator:** Usuário Principal, Usuário Secundário
**Descrição:** Autenticar no sistema com credenciais
**Prioridade:** Alta

#### UC-M1-002: Gerenciar Perfil
**Ator:** Usuário Principal, Usuário Secundário
**Descrição:** Editar informações do perfil pessoal
**Prioridade:** Média

#### UC-M1-003: Cadastrar Usuário
**Ator:** Usuário Principal
**Descrição:** Adicionar novo usuário ao sistema (família)
**Prioridade:** Alta

#### UC-M1-004: Configurar Permissões
**Ator:** Usuário Principal
**Descrição:** Definir níveis de acesso por usuário
**Prioridade:** Média

#### UC-M1-005: Configurar Preferências do Sistema
**Ator:** Usuário Principal
**Descrição:** Definir moeda, formato de data, tema, etc.
**Prioridade:** Média

---

### M2. FLUXO DE CAIXA

#### UC-M2-001: Registrar Transação
**Ator:** Usuário Principal, Usuário Secundário
**Descrição:** Adicionar nova receita ou despesa
**Prioridade:** Alta
**Campos:**
- Data do Evento
- Data de Efetivação
- Instituição Financeira
- Cartão de Crédito (opcional)
- Categoria
- Subcategoria
- Descrição
- Valor
- Status (Pendente/Concluído)

#### UC-M2-002: Editar Transação
**Ator:** Usuário Principal, Usuário Secundário
**Descrição:** Modificar transação existente
**Prioridade:** Alta

#### UC-M2-003: Excluir Transação
**Ator:** Usuário Principal
**Descrição:** Remover transação do sistema
**Prioridade:** Média

#### UC-M2-004: Consultar Transações
**Ator:** Usuário Principal, Usuário Secundário
**Descrição:** Buscar e filtrar transações
**Filtros:**
- Período (data)
- Categoria/Subcategoria
- Instituição Financeira
- Cartão de Crédito
- Status
- Valor (faixa)
**Prioridade:** Alta

#### UC-M2-005: Marcar Transação como Concluída
**Ator:** Usuário Principal, Usuário Secundário
**Descrição:** Alterar status de Pendente para Concluído
**Prioridade:** Alta

#### UC-M2-006: Visualizar Pendências
**Ator:** Usuário Principal, Usuário Secundário
**Descrição:** Listar todas as transações pendentes
**Prioridade:** Alta

#### UC-M2-007: Duplicar Transação Recorrente
**Ator:** Usuário Principal, Usuário Secundário
**Descrição:** Criar cópia de transação para meses seguintes
**Prioridade:** Média

---

### M3. CONTROLE FINANCEIRO

#### UC-M3-001: Visualizar Controle Mensal
**Ator:** Usuário Principal, Usuário Secundário
**Descrição:** Ver resumo financeiro do mês
**Exibe:**
- Saldo Mensal (Receitas - Despesas)
- Despesas por Categoria
- Receitas por Categoria
- Comparativo com meses anteriores
- Estatísticas (Mín, Méd, Máx)
**Prioridade:** Alta

#### UC-M3-002: Comparar Períodos
**Ator:** Usuário Principal, Usuário Secundário
**Descrição:** Análise comparativa entre diferentes períodos
**Prioridade:** Média

#### UC-M3-003: Analisar Percentual por Categoria
**Ator:** Usuário Principal, Usuário Secundário
**Descrição:** Ver distribuição percentual dos gastos
**Prioridade:** Alta

#### UC-M3-004: Definir Planejamento Mensal
**Ator:** Usuário Principal
**Descrição:** Estabelecer metas de gastos por categoria
**Prioridade:** Alta

#### UC-M3-005: Verificar Compliance do Planejamento
**Ator:** Usuário Principal, Usuário Secundário
**Descrição:** Comparar realizado vs planejado
**Prioridade:** Alta

---

### M4. INVESTIMENTOS

#### UC-M4-001: Cadastrar Investimento
**Ator:** Usuário Principal
**Descrição:** Registrar novo investimento no portfólio
**Campos:**
- Instituição Financeira
- Tipo de Produto (CDB, CRA, CRI, Debênture, ETF, FII, Ações, etc.)
- Classificação (Renda Fixa/Variável)
- Valor Investido
- Data de Aplicação
- Data de Vencimento (se aplicável)
- Taxa/Rentabilidade
- Observações
**Prioridade:** Alta

#### UC-M4-002: Atualizar Valor do Investimento
**Ator:** Usuário Principal
**Descrição:** Atualizar saldo atual do investimento
**Prioridade:** Alta

#### UC-M4-003: Registrar Provento/Dividendo
**Ator:** Usuário Principal
**Descrição:** Lançar recebimento de proventos
**Prioridade:** Alta

#### UC-M4-004: Visualizar Portfólio
**Ator:** Usuário Principal, Usuário Secundário
**Descrição:** Ver composição completa dos investimentos
**Exibe:**
- Valor total investido
- Valor atual (com rentabilidade)
- Rentabilidade (% e R$)
- Distribuição Renda Fixa vs Variável
- Alocação por tipo de ativo
**Prioridade:** Alta

#### UC-M4-005: Analisar Performance
**Ator:** Usuário Principal, Usuário Secundário
**Descrição:** Análise histórica de rentabilidade
**Prioridade:** Média

#### UC-M4-006: Resgatar Investimento
**Ator:** Usuário Principal
**Descrição:** Registrar resgate total ou parcial
**Prioridade:** Alta

#### UC-M4-007: Gerar Relatório de Investimentos
**Ator:** Usuário Principal
**Descrição:** Exportar relatório detalhado do portfólio
**Prioridade:** Média

---

### M5. PLANOS FINANCEIROS

#### UC-M5-001: Criar Plano Financeiro
**Ator:** Usuário Principal
**Descrição:** Estabelecer meta financeira de longo prazo
**Campos:**
- Nome do Plano (ex: Aposentadoria, Casa, Carro)
- Valor Objetivo
- Parcela Mensal
- Instituição Financeira
- Partição (Principal/Secundária)
- Prazo (meses)
**Prioridade:** Alta

#### UC-M5-002: Atualizar Saldo do Plano
**Ator:** Usuário Principal
**Descrição:** Registrar aportes mensais no plano
**Prioridade:** Alta

#### UC-M5-003: Visualizar Progresso do Plano
**Ator:** Usuário Principal, Usuário Secundário
**Descrição:** Ver evolução do plano ao longo do tempo
**Exibe:**
- Valor Acumulado
- Valor Restante
- % de Conclusão
- Previsão de Conclusão
- Gráfico de Evolução
**Prioridade:** Alta

#### UC-M5-004: Linha do Tempo dos Planos
**Ator:** Usuário Principal, Usuário Secundário
**Descrição:** Visualizar todos os planos em timeline
**Prioridade:** Média

#### UC-M5-005: Editar Plano
**Ator:** Usuário Principal
**Descrição:** Modificar parâmetros do plano (valor, parcela, prazo)
**Prioridade:** Média

#### UC-M5-006: Concluir/Quitar Plano
**Ator:** Usuário Principal
**Descrição:** Marcar plano como finalizado
**Prioridade:** Alta

---

### M6. PLANEJAMENTO DE RECEITAS

#### UC-M6-001: Definir Receita Fixa Mensal
**Ator:** Usuário Principal
**Descrição:** Estabelecer receita mensal esperada (salário)
**Prioridade:** Alta

#### UC-M6-002: Adicionar Receita Extra Futura
**Ator:** Usuário Principal
**Descrição:** Projetar receitas não recorrentes (13º, bônus, etc.)
**Prioridade:** Média

#### UC-M6-003: Visualizar Projeção de Receitas
**Ator:** Usuário Principal, Usuário Secundário
**Descrição:** Ver receitas projetadas para os próximos meses
**Prioridade:** Média

#### UC-M6-004: Calcular Sobra Mensal Planejada
**Ator:** Sistema
**Descrição:** Calcular automaticamente: Receita - Despesas Fixas
**Prioridade:** Alta

#### UC-M6-005: Adicionar Anotações de Planejamento
**Ator:** Usuário Principal
**Descrição:** Inserir observações sobre projeções
**Prioridade:** Baixa

---

### M7. SIMULADORES

#### UC-M7-001: Simular Investimento com Objetivo
**Ator:** Usuário Principal, Usuário Secundário
**Descrição:** Calcular quanto investir para atingir valor alvo
**Entradas:**
- Valor Objetivo
- Valor Inicial
- Tempo (anos)
- Rentabilidade esperada (% a.a.)
**Saídas:**
- Aplicação Mensal Necessária
- Valor Total Investido
- Valor dos Juros
**Prioridade:** Alta

#### UC-M7-002: Simular Tempo para Objetivo
**Ator:** Usuário Principal, Usuário Secundário
**Descrição:** Calcular tempo necessário dado valor e aplicação
**Entradas:**
- Valor Objetivo
- Valor Inicial
- Aplicação Mensal
- Rentabilidade esperada (% a.a.)
**Saídas:**
- Tempo Necessário (anos/meses)
- Gráfico de Evolução
**Prioridade:** Alta

#### UC-M7-003: Simular Montante Futuro
**Ator:** Usuário Principal, Usuário Secundário
**Descrição:** Calcular valor futuro de investimento
**Entradas:**
- Valor Inicial
- Aplicação Mensal
- Tempo (anos)
- Rentabilidade esperada (% a.a.)
**Saídas:**
- Montante Futuro
- Valor Investido Total
- Valor dos Juros
- Gráfico de Composição
**Prioridade:** Alta

---

### M8. DASHBOARDS E RELATÓRIOS

#### UC-M8-001: Visualizar Dashboard Principal
**Ator:** Usuário Principal, Usuário Secundário
**Descrição:** Painel com visão geral das finanças
**Exibe:**
- Saldo Total em Contas
- Saldo Total em Investimentos
- Receita do Mês
- Despesas do Mês
- Saldo do Mês
- Gráficos de Distribuição
- Alertas e Notificações
**Prioridade:** Alta

#### UC-M8-002: Visualizar Dashboard de Investimentos
**Ator:** Usuário Principal, Usuário Secundário
**Descrição:** Painel focado em investimentos
**Exibe:**
- Valor Total do Portfólio
- Rentabilidade Geral
- Distribuição por Tipo
- Renda Fixa vs Variável
- Melhores e Piores Performances
**Prioridade:** Alta

#### UC-M8-003: Visualizar Dashboard de Planos
**Ator:** Usuário Principal, Usuário Secundário
**Descrição:** Painel focado em metas financeiras
**Exibe:**
- Lista de Planos Ativos
- Progresso de cada Plano
- Total Guardado vs Total a Guardar
- Velocímetro de Progresso
**Prioridade:** Média

#### UC-M8-004: Gerar Relatório de Fluxo de Caixa
**Ator:** Usuário Principal
**Descrição:** Relatório detalhado de transações por período
**Prioridade:** Alta

#### UC-M8-005: Gerar Relatório por Categoria
**Ator:** Usuário Principal
**Descrição:** Análise de gastos agrupados por categoria
**Prioridade:** Média

#### UC-M8-006: Gerar Relatório Anual
**Ator:** Usuário Principal
**Descrição:** Consolidação anual das finanças
**Prioridade:** Média

#### UC-M8-007: Exportar Relatório (PDF/Excel)
**Ator:** Usuário Principal
**Descrição:** Baixar relatórios em diferentes formatos
**Prioridade:** Baixa

#### UC-M8-008: Filtrar Dados por Período
**Ator:** Usuário Principal, Usuário Secundário
**Descrição:** Aplicar filtros temporais nos dashboards
**Opções:**
- Últimos 3 meses
- Últimos 6 meses
- Últimos 12 meses
- Ano atual
- Período customizado
- Tudo
**Prioridade:** Alta

---

### M9. CADASTROS BASE

#### UC-M9-001: Gerenciar Categorias
**Ator:** Usuário Principal
**Descrição:** CRUD de categorias de receitas/despesas
**Operações:** Criar, Listar, Editar, Excluir
**Prioridade:** Alta

#### UC-M9-002: Gerenciar Subcategorias
**Ator:** Usuário Principal
**Descrição:** CRUD de subcategorias vinculadas a categorias
**Prioridade:** Alta

#### UC-M9-003: Gerenciar Instituições Financeiras
**Ator:** Usuário Principal
**Descrição:** CRUD de bancos e contas
**Campos:**
- Nome da Instituição
- Tipo de Conta (Corrente, Poupança, Investimento)
- Partição (Principal, Secundária)
**Prioridade:** Alta

#### UC-M9-004: Gerenciar Cartões de Crédito
**Ator:** Usuário Principal
**Descrição:** CRUD de cartões
**Campos:**
- Nome/Apelido
- Instituição Emissora
- Dia de Fechamento
- Dia de Vencimento
**Prioridade:** Média

#### UC-M9-005: Gerenciar Tipos de Investimento
**Ator:** Usuário Principal
**Descrição:** CRUD de produtos de investimento
**Exemplos:** CDB, CRA, CRI, Debênture, ETF, FII, Ações
**Prioridade:** Média

---

### M10. IMPORTAÇÃO/EXPORTAÇÃO

#### UC-M10-001: Importar Extrato Bancário (CSV)
**Ator:** Usuário Principal
**Descrição:** Upload de arquivo CSV de extrato bancário
**Processo:**
1. Upload do arquivo
2. Mapeamento de colunas
3. Validação de dados
4. Pré-visualização
5. Confirmação e importação
**Prioridade:** Média

#### UC-M10-002: Importar Extrato de Cartão (CSV)
**Ator:** Usuário Principal
**Descrição:** Upload de fatura de cartão de crédito
**Prioridade:** Média

#### UC-M10-003: Exportar Dados Completos
**Ator:** Usuário Principal
**Descrição:** Backup completo do sistema em JSON/SQL
**Prioridade:** Alta

#### UC-M10-004: Importar Dados de Backup
**Ator:** Usuário Principal
**Descrição:** Restaurar sistema a partir de backup
**Prioridade:** Alta

#### UC-M10-005: Migrar da Planilha Excel
**Ator:** Usuário Principal
**Descrição:** Importação inicial a partir da planilha atual
**Prioridade:** Alta

---

## CASOS DE USO DETALHADOS

### UC-M2-001: Registrar Transação

#### Descrição Completa
Permite ao usuário registrar uma nova transação financeira (receita ou despesa) no sistema.

#### Pré-condições
- Usuário autenticado
- Ao menos uma categoria cadastrada
- Ao menos uma instituição financeira cadastrada

#### Fluxo Principal
1. Usuário acessa a tela de "Nova Transação"
2. Sistema exibe formulário com campos obrigatórios e opcionais
3. Usuário preenche:
   - Data do Evento (quando ocorreu)
   - Data de Efetivação (quando será/foi processado)
   - Instituição Financeira (dropdown)
   - Cartão de Crédito (dropdown, opcional)
   - Categoria (dropdown)
   - Subcategoria (dropdown dependente de Categoria)
   - Descrição (texto livre)
   - Valor (numérico, positivo para receita, negativo para despesa)
   - Status (Pendente/Concluído)
4. Usuário clica em "Salvar"
5. Sistema valida os dados
6. Sistema salva a transação no banco de dados
7. Sistema exibe mensagem de sucesso
8. Sistema atualiza saldos e estatísticas automaticamente

#### Fluxos Alternativos

**FA1: Validação falha**
- 5a. Sistema identifica erro de validação
- 5b. Sistema exibe mensagem de erro indicando o campo problemático
- 5c. Retorna ao passo 3

**FA2: Usuário cancela**
- *a. A qualquer momento, usuário clica em "Cancelar"
- *b. Sistema descarta dados não salvos
- *c. Sistema retorna à tela anterior

**FA3: Categoria não existe**
- 3a. Usuário não encontra categoria desejada
- 3b. Usuário clica em "Nova Categoria"
- 3c. Sistema abre modal de criação rápida
- 3d. Usuário cria categoria
- 3e. Sistema salva e retorna ao formulário com categoria selecionada
- 3f. Continua do passo 3

#### Pós-condições
- Transação registrada no banco de dados
- Saldos atualizados
- Estatísticas recalculadas
- Transação visível nos dashboards e relatórios

#### Regras de Negócio
- RN1: Data do Evento não pode ser posterior a 1 ano no futuro
- RN2: Valor não pode ser zero
- RN3: Se Data de Efetivação não informada, assume Data do Evento
- RN4: Receitas devem ter valor positivo, despesas negativo
- RN5: Status "Concluído" só permite Data de Efetivação no passado ou presente

#### Requisitos Especiais
- RE1: Formulário deve ter validação em tempo real
- RE2: Campos devem ter autocomplete quando apropriado
- RE3: Última categoria/instituição usada devem vir pré-selecionadas
- RE4: Deve haver opção de "Salvar e Nova" para inserções múltiplas

---

### UC-M7-001: Simular Investimento com Objetivo

#### Descrição Completa
Permite ao usuário calcular quanto deve investir mensalmente para atingir um objetivo financeiro em determinado prazo.

#### Pré-condições
- Usuário autenticado
- Acesso ao módulo de simuladores

#### Fluxo Principal
1. Usuário acessa "Simuladores" > "Investimento com Objetivo"
2. Sistema exibe formulário de simulação
3. Usuário informa:
   - Valor Objetivo (ex: R$ 100.000)
   - Valor Inicial disponível (ex: R$ 5.000)
   - Prazo em anos (ex: 5 anos)
   - Rentabilidade esperada % a.a. (ex: 10%)
4. Usuário clica em "Simular"
5. Sistema calcula:
   - Aplicação Mensal Necessária
   - Montante Final
   - Total Investido pelo usuário
   - Total de Juros gerados
6. Sistema exibe resultados com:
   - Valores calculados
   - Gráfico de evolução mês a mês
   - Gráfico de composição (capital vs juros)
   - Tabela detalhada mês a mês (opcional, expandível)
7. Usuário pode:
   - Ajustar parâmetros e resimular
   - Salvar simulação
   - Exportar resultados
   - Criar plano financeiro baseado na simulação

#### Fluxos Alternativos

**FA1: Validação de entrada**
- 3a. Usuário informa valor negativo ou zero
- 3b. Sistema exibe mensagem de erro
- 3c. Retorna ao passo 3

**FA2: Objetivo impossível**
- 5a. Sistema detecta que objetivo é impossível com parâmetros informados
- 5b. Sistema exibe mensagem explicativa
- 5c. Sistema sugere ajustes (aumentar prazo, aumentar rentabilidade, reduzir objetivo)
- 5d. Retorna ao passo 3

**FA3: Criar plano a partir da simulação**
- 7a. Usuário clica em "Criar Plano Financeiro"
- 7b. Sistema abre formulário de novo plano com dados pré-preenchidos
- 7c. Usuário confirma ou ajusta
- 7d. Sistema cria o plano
- 7e. Sistema redireciona para gestão de planos

#### Pós-condições
- Simulação exibida ao usuário
- Usuário informado sobre viabilidade do objetivo
- Opcionalmente, plano financeiro criado

#### Regras de Negócio
- RN1: Cálculo usa juros compostos mensais
- RN2: Fórmula: PMT = (FV - PV*(1+i)^n) / [((1+i)^n - 1) / i]
  - PMT = Pagamento Mensal
  - FV = Valor Futuro (objetivo)
  - PV = Valor Presente (inicial)
  - i = taxa mensal (anual/12)
  - n = número de meses
- RN3: Rentabilidade deve estar entre 0% e 50% a.a.
- RN4: Prazo mínimo: 1 mês, máximo: 40 anos (480 meses)
- RN5: Todos os cálculos consideram aportes no início do mês

#### Requisitos Especiais
- RE1: Gráficos devem ser interativos (zoom, tooltip)
- RE2: Cálculos devem ser reativos (atualizar enquanto usuário digita)
- RE3: Deve haver tooltips explicativos sobre rentabilidade esperada
- RE4: Simulador deve funcionar offline (sem necessidade de backend)

---

### UC-M8-001: Visualizar Dashboard Principal

#### Descrição Completa
Exibe uma visão consolidada e em tempo real de toda a situação financeira do usuário.

#### Pré-condições
- Usuário autenticado
- Sistema com dados carregados

#### Fluxo Principal
1. Usuário faz login ou clica em "Dashboard" no menu
2. Sistema carrega dados consolidados
3. Sistema exibe dashboard com widgets:

   **Widget 1: Resumo Financeiro**
   - Saldo Total em Contas Bancárias
   - Saldo Total em Investimentos
   - Patrimônio Líquido Total

   **Widget 2: Mês Atual**
   - Receitas do Mês
   - Despesas do Mês
   - Saldo do Mês
   - % Gasto em relação à Receita
   - Barra de progresso

   **Widget 3: Distribuição de Gastos**
   - Gráfico de pizza/rosca com categorias
   - Top 5 categorias de despesa
   - Valores e percentuais

   **Widget 4: Evolução Mensal**
   - Gráfico de linha dos últimos 6 meses
   - Receitas, Despesas e Saldo

   **Widget 5: Planos Financeiros**
   - Lista resumida dos 3 principais planos
   - Progresso de cada um
   - Link para visualização completa

   **Widget 6: Investimentos**
   - Valor total do portfólio
   - Rentabilidade do período
   - Distribuição Renda Fixa vs Variável

   **Widget 7: Alertas e Notificações**
   - Contas a vencer
   - Orçamento estourado
   - Metas próximas de serem atingidas

4. Usuário pode:
   - Clicar em qualquer widget para ver detalhes
   - Aplicar filtro de período
   - Atualizar dados (refresh)
   - Customizar quais widgets exibir

#### Fluxos Alternativos

**FA1: Sem dados suficientes**
- 2a. Sistema detecta ausência de dados mínimos
- 2b. Sistema exibe mensagem de boas-vindas
- 2c. Sistema oferece tour guiado ou ação rápida (adicionar primeira transação)

**FA2: Filtro de período**
- 4a. Usuário seleciona filtro de período (último mês, últimos 3 meses, ano, etc.)
- 4b. Sistema recarrega dashboard com dados do período
- 4c. Sistema atualiza todos os widgets

**FA3: Customização de layout**
- 4a. Usuário clica em "Customizar Dashboard"
- 4b. Sistema entra em modo de edição
- 4c. Usuário arrasta/remove/adiciona widgets
- 4d. Usuário salva configuração
- 4e. Sistema persiste preferências do usuário

#### Pós-condições
- Dashboard carregado e exibido
- Usuário tem visão geral das finanças
- Preferências de visualização salvas (se alteradas)

#### Regras de Negócio
- RN1: Todos os valores em widgets são calculados em tempo real
- RN2: Saldo Total = Soma(Saldos Contas) + Soma(Saldos Investimentos)
- RN3: Receitas/Despesas consideram apenas transações com Status "Concluído"
- RN4: Gráficos devem usar cores consistentes (verde=receita, vermelho=despesa, azul=saldo)
- RN5: Percentuais são calculados com 2 casas decimais
- RN6: Alertas são gerados automaticamente pelo sistema

#### Requisitos Especiais
- RE1: Dashboard deve carregar em menos de 2 segundos
- RE2: Widgets devem ser responsivos (mobile-friendly)
- RE3: Gráficos devem ser interativos
- RE4: Deve haver opção de dark mode
- RE5: Dashboard deve atualizar automaticamente a cada 5 minutos quando aberto

---

## REQUISITOS NÃO-FUNCIONAIS

### RNF-001: Performance
- Sistema deve responder a ações do usuário em menos de 1 segundo
- Dashboards devem carregar em menos de 2 segundos
- Suporte para até 10.000 transações sem degradação

### RNF-002: Segurança
- Senhas devem ser hasheadas (bcrypt ou argon2)
- Sessões devem expirar após 24 horas de inatividade
- Comunicação via HTTPS quando exposto além da rede local
- Backup automático diário dos dados

### RNF-003: Usabilidade
- Interface intuitiva, sem necessidade de manual
- Feedback visual para todas as ações
- Tooltips e ajuda contextual
- Responsivo para desktop, tablet e mobile

### RNF-004: Compatibilidade
- Funcionar nos navegadores: Chrome, Firefox, Safari, Edge (últimas 2 versões)
- Acessível via rede local (LAN/WiFi)
- Opcionalmente acessível via VPN/Tunnel para acesso externo

### RNF-005: Disponibilidade
- Sistema deve estar disponível 24/7
- Backup automático antes de qualquer operação de exclusão em massa
- Tolerância a falhas com mensagens de erro amigáveis

### RNF-006: Manutenibilidade
- Código documentado e modular
- Testes unitários para regras de negócio críticas
- Logs de auditoria para operações importantes
- Versionamento de banco de dados (migrations)

### RNF-007: Escalabilidade
- Arquitetura deve permitir futura adição de módulos
- Banco de dados normalizado
- API RESTful para futuras integrações

### RNF-008: Acessibilidade
- Suporte a leitores de tela (ARIA labels)
- Contraste adequado para baixa visão
- Navegação por teclado

---

## DIAGRAMA DE RELACIONAMENTOS

```
┌─────────────────────────────────────────────────────────────┐
│                      USUÁRIO                                │
│  ┌─────────────┐              ┌──────────────┐            │
│  │   Login     │              │   Perfil     │            │
│  └──────┬──────┘              └──────┬───────┘            │
│         │                             │                     │
└─────────┼─────────────────────────────┼─────────────────────┘
          │                             │
          ▼                             ▼
┌─────────────────────────────────────────────────────────────┐
│                   MÓDULOS PRINCIPAIS                        │
│                                                             │
│  ┌──────────────┐  ┌───────────────┐  ┌─────────────────┐│
│  │ Fluxo Caixa  │◄─┤  Controle     │◄─┤   Categorias    ││
│  │              │  │  Financeiro   │  │                 ││
│  └──────┬───────┘  └───────┬───────┘  └─────────────────┘│
│         │                  │                               │
│         ▼                  ▼                               │
│  ┌──────────────────────────────────────────┐            │
│  │         TRANSAÇÕES (Core)                │            │
│  │  - Data Evento                           │            │
│  │  - Data Efetivação                       │            │
│  │  - Instituição Financeira ───────┐       │            │
│  │  - Cartão Crédito ────────┐      │       │            │
│  │  - Categoria ──────┐       │      │       │            │
│  │  - Subcategoria    │       │      │       │            │
│  │  - Valor           │       │      │       │            │
│  │  - Status          │       │      │       │            │
│  └────────────────────┼───────┼──────┼───────┘            │
│                       │       │      │                     │
└───────────────────────┼───────┼──────┼─────────────────────┘
                        │       │      │
        ┌───────────────┘       │      └─────────────────┐
        │                       │                        │
        ▼                       ▼                        ▼
┌──────────────┐      ┌─────────────────┐      ┌───────────────┐
│ Cadastros    │      │  Instituições   │      │   Cartões     │
│ Categoria    │      │  Financeiras    │      │   Crédito     │
│ Subcategoria │      └────────┬────────┘      └───────────────┘
└──────────────┘               │
                               │
                ┌──────────────┴───────────────┐
                │                              │
                ▼                              ▼
        ┌──────────────┐              ┌───────────────┐
        │ Investimentos│              │    Planos     │
        │              │              │  Financeiros  │
        │ - Tipo       │              │               │
        │ - Valor      │              │ - Objetivo    │
        │ - Renda      │              │ - Parcela     │
        │   Fixa/Var   │              │ - Progresso   │
        └──────┬───────┘              └───────┬───────┘
               │                              │
               └──────────┬───────────────────┘
                          │
                          ▼
                ┌─────────────────┐
                │   Dashboards    │
                │   Relatórios    │
                │   Simuladores   │
                └─────────────────┘

RELACIONAMENTOS:
─────────── : Relacionamento direto
◄────────── : Dependência/Uso
```

---

## PRIORIZAÇÃO DE DESENVOLVIMENTO (Sugestão de MVP)

### Fase 1 - MVP Básico (4-6 semanas)
**Objetivo:** Sistema funcional para controle básico

Módulos:
- M1: Autenticação (UC-001, UC-002, UC-003)
- M2: Fluxo de Caixa (UC-001, UC-002, UC-004, UC-005)
- M9: Cadastros Base (UC-001, UC-002, UC-003)
- M8: Dashboard Principal básico (UC-001)

### Fase 2 - Controle Avançado (3-4 semanas)
**Objetivo:** Análises e controle financeiro detalhado

Módulos:
- M3: Controle Financeiro (todos UCs)
- M8: Relatórios (UC-004, UC-005, UC-008)
- M2: Fluxo de Caixa completo (UCs restantes)

### Fase 3 - Planejamento (3-4 semanas)
**Objetivo:** Ferramentas de planejamento futuro

Módulos:
- M5: Planos Financeiros (todos UCs)
- M6: Planejamento de Receitas (todos UCs)
- M7: Simuladores (todos UCs)

### Fase 4 - Investimentos (2-3 semanas)
**Objetivo:** Gestão de portfólio

Módulos:
- M4: Investimentos (todos UCs)
- M8: Dashboard de Investimentos (UC-002)

### Fase 5 - Integrações (2-3 semanas)
**Objetivo:** Importação e exportação

Módulos:
- M10: Importação/Exportação (todos UCs)
- M9: Gestão de Cartões (UC-004)

### Fase 6 - Refinamentos (contínuo)
**Objetivo:** Melhorias de UX e novas features

- Notificações push
- Comparti

lhamento de relatórios
- Modo offline
- App mobile nativo
- Integração com Open Banking
- Inteligência artificial para categorização automática

---

## GLOSSÁRIO

**Categoria**: Agrupamento principal de transações (ex: Alimentação, Transporte, Saúde)

**Subcategoria**: Detalhamento dentro de uma categoria (ex: Alimentação > Supermercado)

**Instituição Financeira**: Banco ou corretora onde o dinheiro está depositado

**Partição**: Divisão lógica dentro de uma instituição (ex: Conta Principal, Conta Reserva)

**Fluxo de Caixa**: Registro cronológico de todas as entradas e saídas de dinheiro

**Controle Financeiro**: Visão consolidada mensal de receitas e despesas

**Plano Financeiro**: Meta de longo prazo com objetivo, prazo e aportes mensais

**Renda Fixa**: Investimentos com rentabilidade previsível (CDB, Tesouro, etc.)

**Renda Variável**: Investimentos com rentabilidade variável (Ações, FIIs, etc.)

**Dashboard**: Painel visual com indicadores e gráficos

**Status Concluído**: Transação já efetivada/processada

**Status Pendente**: Transação futura ou ainda não processada

**Data do Evento**: Quando a transação de fato ocorreu

**Data de Efetivação**: Quando a transação impacta o saldo da conta

---

## OBSERVAÇÕES FINAIS

### Extensões Futuras Sugeridas
1. **Integração com Open Banking**: Sincronização automática com bancos
2. **OCR de Notas Fiscais**: Upload de foto para registro automático
3. **Categorização por IA**: Machine Learning para sugerir categorias
4. **Alertas Inteligentes**: Notificações baseadas em padrões de gastos
5. **Modo Colaborativo**: Chat e comentários em transações
6. **Gamificação**: Badges e conquistas por metas atingidas
7. **Comparação com Média Nacional**: Benchmarking de gastos
8. **Previsão de Gastos**: IA para prever despesas futuras
9. **Otimização de Portfólio**: Sugestões de rebalanceamento
10. **Multi-moeda**: Suporte para múltiplas moedas e conversão automática

### Considerações Técnicas
- Utilizar framework web moderno (Flask + React ou FastAPI + Vue.js)
- Banco de dados relacional (PostgreSQL recomendado)
- ORM (SQLAlchemy ou similar) para abstração de dados
- Autenticação JWT para APIs
- Docker para facilitar deploy
- Nginx como reverse proxy
- Certbot para HTTPS (se expor para internet)

### Infraestrutura Recomendada
**Opção 1 - Raspberry Pi 4:**
- 4GB RAM mínimo
- 32GB SD Card + SSD externo para banco
- Custo: ~R$ 500

**Opção 2 - PC/Notebook sempre ligado:**
- Docker instalado
- Linux/Windows/Mac
- Custo: R$ 0 (já possui)

**Opção 3 - Servidor Cloud (fallback):**
- VPS pequena (1GB RAM)
- DigitalOcean, Linode, AWS
- Custo: ~R$ 25/mês

---

**Documento criado em:** 18/12/2025
**Versão:** 1.0
**Autor:** Sistema de Análise de Requisitos
**Status:** Aguardando aprovação para início do desenvolvimento
