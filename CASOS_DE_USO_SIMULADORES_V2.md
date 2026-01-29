# CASOS DE USO - MÓDULO SIMULADORES V2.0

**Projeto:** Sistema de Gestão Financeira Pessoal - Flow Forecaster
**Módulo:** M7 - Simuladores Financeiros (Melhorias)
**Versão:** 2.0
**Data:** 23 de Dezembro de 2025
**Base:** Evolução do módulo M7 existente

---

## ÍNDICE

1. [Visão Geral das Melhorias](#visão-geral-das-melhorias)
2. [Casos de Uso - Histórico e Persistência](#m7a-histórico-e-persistência)
3. [Casos de Uso - Visualizações Avançadas](#m7b-visualizações-avançadas)
4. [Casos de Uso - Análise de Cenários](#m7c-análise-de-cenários)
5. [Casos de Uso - Integração com Planos](#m7d-integração-com-planos)
6. [Casos de Uso - Educação Financeira](#m7e-educação-financeira)
7. [Casos de Uso - Exportação](#m7f-exportação)
8. [Requisitos Técnicos](#requisitos-técnicos)
9. [Diagrama de Relacionamentos](#diagrama-de-relacionamentos)

---

## VISÃO GERAL DAS MELHORIAS

### Objetivos
Evoluir o módulo de simuladores de uma ferramenta de cálculo volátil para uma suite completa de planejamento financeiro com:
- **Histórico** de simulações realizadas
- **Visualizações** gráficas de evolução
- **Análise** de sensibilidade e cenários
- **Integração** direta com criação de planos
- **Educação** financeira contextual
- **Exportação** de resultados

### Módulos de Melhoria

#### M7-A: Histórico e Persistência
Salvar e gerenciar simulações realizadas

#### M7-B: Visualizações Avançadas
Gráficos interativos de evolução e composição

#### M7-C: Análise de Cenários
Comparação entre múltiplos cenários e análise de sensibilidade

#### M7-D: Integração com Planos
Criação automática de planos financeiros a partir de simulações

#### M7-E: Educação Financeira
Tooltips, guias e calculadoras educacionais

#### M7-F: Exportação
Export de simulações em PDF e Excel

---

## M7-A: HISTÓRICO E PERSISTÊNCIA

### UC-M7A-001: Salvar Simulação

**Ator:** Usuário Principal, Usuário Secundário
**Descrição:** Salvar resultado de simulação para consulta futura
**Prioridade:** Alta

#### Pré-condições
- Usuário autenticado
- Simulação calculada com sucesso
- Resultado válido exibido na tela

#### Fluxo Principal
1. Usuário realiza uma simulação (qualquer tipo)
2. Sistema calcula e exibe resultado
3. Sistema exibe botão "Salvar Simulação"
4. Usuário clica em "Salvar Simulação"
5. Sistema abre modal com campos:
   - Nome da Simulação (sugestão automática: "Simulação [Tipo] - [Data]")
   - Descrição (opcional, texto livre)
   - Tags (opcional, ex: "Aposentadoria", "Casa Própria")
6. Usuário preenche e confirma
7. Sistema valida dados
8. Sistema persiste simulação no banco de dados:
   - Tipo de simulação (goal/time/future)
   - Parâmetros de entrada (JSON)
   - Resultados calculados (JSON)
   - Timestamp
   - User_id
9. Sistema exibe mensagem de sucesso
10. Sistema adiciona link "Ver no Histórico"

#### Fluxos Alternativos

**FA1: Salvamento rápido**
- 4a. Usuário clica em "Salvar" sem editar nome
- 4b. Sistema salva com nome padrão
- 4c. Continua do passo 8

**FA2: Cancelar salvamento**
- 6a. Usuário clica em "Cancelar"
- 6b. Sistema fecha modal
- 6c. Simulação não é salva (permanece volátil)

**FA3: Nome duplicado**
- 7a. Sistema detecta nome já existente
- 7b. Sistema sugere adicionar sufixo " (2)", " (3)", etc.
- 7c. Retorna ao passo 6

#### Pós-condições
- Simulação persistida no banco de dados
- Disponível no histórico do usuário
- Pode ser consultada, editada ou deletada posteriormente

#### Regras de Negócio
- RN1: Nome da simulação é obrigatório (min 3, max 100 caracteres)
- RN2: Descrição é opcional (max 500 caracteres)
- RN3: Tags são opcionais (max 5 tags, cada uma max 30 caracteres)
- RN4: Cada usuário pode ter até 100 simulações salvas
- RN5: Simulações mais antigas são automaticamente arquivadas após 100 itens

#### Requisitos Especiais
- RE1: Salvamento deve ser rápido (<500ms)
- RE2: Modal deve ter validação em tempo real
- RE3: Sugestão de nome deve incluir tipo + data/hora
- RE4: Sistema deve confirmar salvamento visualmente (toast notification)

---

### UC-M7A-002: Consultar Histórico de Simulações

**Ator:** Usuário Principal, Usuário Secundário
**Descrição:** Visualizar lista de simulações salvas
**Prioridade:** Alta

#### Pré-condições
- Usuário autenticado
- Ao menos uma simulação salva

#### Fluxo Principal
1. Usuário acessa "Simuladores" > "Histórico"
2. Sistema carrega lista de simulações do usuário
3. Sistema exibe tabela/cards com:
   - Nome da simulação
   - Tipo (ícone: 🎯 Objetivo / ⏱️ Tempo / 📈 Montante)
   - Data de criação
   - Preview do resultado principal
   - Ações (Ver detalhes / Editar / Deletar)
4. Sistema permite ordenação por:
   - Data (mais recente/mais antigo)
   - Nome (A-Z / Z-A)
   - Tipo
5. Sistema permite filtros por:
   - Tipo de simulação
   - Período (última semana, mês, ano, tudo)
   - Tags
   - Busca por nome

#### Fluxos Alternativos

**FA1: Sem simulações salvas**
- 2a. Sistema detecta lista vazia
- 2b. Sistema exibe mensagem "Nenhuma simulação salva ainda"
- 2c. Sistema exibe botão "Criar primeira simulação"

**FA2: Busca sem resultados**
- 5a. Usuário aplica filtros/busca
- 5b. Sistema não encontra resultados
- 5c. Sistema exibe "Nenhum resultado encontrado"
- 5d. Sistema sugere limpar filtros

#### Pós-condições
- Lista de simulações exibida
- Usuário pode navegar e gerenciar simulações

#### Regras de Negócio
- RN1: Apenas simulações do usuário logado são exibidas
- RN2: Ordenação padrão: mais recentes primeiro
- RN3: Paginação de 20 itens por página
- RN4: Busca é case-insensitive e busca em nome + descrição

#### Requisitos Especiais
- RE1: Lista deve carregar em <1 segundo
- RE2: Interface responsiva (mobile-friendly)
- RE3: Preview deve mostrar valor principal formatado
- RE4: Ações devem ter confirmação para operações destrutivas

---

### UC-M7A-003: Visualizar Detalhes de Simulação Salva

**Ator:** Usuário Principal, Usuário Secundário
**Descrição:** Ver detalhes completos de uma simulação salva
**Prioridade:** Alta

#### Pré-condições
- Usuário autenticado
- Simulação existe no histórico

#### Fluxo Principal
1. Usuário acessa histórico de simulações
2. Usuário clica em "Ver detalhes" em uma simulação
3. Sistema carrega dados da simulação
4. Sistema exibe página/modal com:

   **Cabeçalho:**
   - Nome da simulação
   - Tipo (badge)
   - Data de criação
   - Tags
   - Descrição

   **Parâmetros de Entrada:**
   - Todos os valores utilizados na simulação
   - Formatados e com labels descritivos

   **Resultados:**
   - Resultado principal (destaque)
   - Resultados secundários (se aplicável)
   - Gráficos (se disponíveis)

   **Metadados:**
   - Criado em
   - Última modificação
   - Número de visualizações

   **Ações:**
   - Editar parâmetros
   - Recalcular
   - Duplicar
   - Criar plano baseado nesta simulação
   - Exportar (PDF/Excel)
   - Compartilhar (link/e-mail)
   - Deletar

5. Usuário pode interagir com as ações disponíveis

#### Fluxos Alternativos

**FA1: Editar parâmetros**
- 5a. Usuário clica em "Editar"
- 5b. Sistema carrega formulário pré-preenchido
- 5c. Usuário altera valores
- 5d. Usuário clica em "Recalcular"
- 5e. Sistema recalcula com novos parâmetros
- 5f. Sistema atualiza resultado
- 5g. Sistema pergunta se deseja salvar alterações
- 5h. Se sim: atualiza simulação existente
- 5i. Se não: descarta alterações

**FA2: Duplicar simulação**
- 5a. Usuário clica em "Duplicar"
- 5b. Sistema cria cópia com nome "Cópia de [Nome Original]"
- 5c. Sistema abre cópia para edição
- 5d. Usuário pode modificar parâmetros

**FA3: Simulação não encontrada**
- 3a. Sistema não encontra simulação (deletada por outro usuário admin)
- 3b. Sistema exibe erro 404
- 3c. Sistema redireciona para histórico

#### Pós-condições
- Detalhes da simulação exibidos
- Usuário pode tomar ações sobre a simulação
- Contador de visualizações incrementado

#### Regras de Negócio
- RN1: Apenas dono da simulação pode editar/deletar
- RN2: Admin pode visualizar mas não editar simulações de outros
- RN3: Edições criam nova versão (versionamento opcional)
- RN4: Deletar é soft-delete (pode ser recuperado por 30 dias)

#### Requisitos Especiais
- RE1: Página deve carregar em <800ms
- RE2: Botão "Criar plano" deve abrir modal pré-preenchido
- RE3: Exportar deve gerar arquivo em <2 segundos
- RE4: Layout deve destacar visualmente o resultado principal

---

### UC-M7A-004: Editar Simulação Salva

**Ator:** Usuário Principal, Usuário Secundário
**Descrição:** Modificar parâmetros de uma simulação e recalcular
**Prioridade:** Média

#### Pré-condições
- Usuário autenticado
- Usuário é dono da simulação
- Simulação existe e não está arquivada

#### Fluxo Principal
1. Usuário acessa detalhes da simulação
2. Usuário clica em "Editar Parâmetros"
3. Sistema carrega formulário interativo pré-preenchido
4. Usuário modifica um ou mais parâmetros:
   - Valor objetivo
   - Valor inicial
   - Tempo (meses/anos)
   - Rentabilidade
   - Aporte mensal (conforme tipo)
5. Sistema valida em tempo real
6. Usuário clica em "Recalcular"
7. Sistema executa cálculo com novos parâmetros
8. Sistema exibe resultado atualizado
9. Sistema pergunta: "Deseja salvar as alterações?"
10. Usuário confirma
11. Sistema atualiza registro no banco:
    - Novos parâmetros
    - Novo resultado
    - Timestamp de modificação
    - Incrementa versão (se versionamento ativo)
12. Sistema exibe confirmação
13. Sistema retorna para visualização de detalhes

#### Fluxos Alternativos

**FA1: Validação falha**
- 5a. Sistema detecta valor inválido
- 5b. Sistema exibe mensagem de erro no campo
- 5c. Botão "Recalcular" fica desabilitado
- 5d. Retorna ao passo 4

**FA2: Usuário cancela**
- *a. A qualquer momento, usuário clica "Cancelar"
- *b. Sistema pergunta "Descartar alterações?"
- *c. Se sim: retorna à visualização sem salvar
- *d. Se não: retorna ao formulário

**FA3: Comparar com versão anterior**
- 8a. Usuário clica em "Comparar"
- 8b. Sistema exibe lado a lado: Anterior vs Novo
- 8c. Sistema destaca diferenças
- 8d. Usuário decide salvar ou reverter

**FA4: Salvar como nova simulação**
- 10a. Usuário clica "Salvar como nova"
- 10b. Sistema abre modal de nome
- 10c. Sistema cria nova simulação
- 10d. Simulação original permanece inalterada

#### Pós-condições
- Simulação atualizada no banco de dados
- Histórico de versões mantido (se versionamento ativo)
- Timestamp de modificação atualizado

#### Regras de Negócio
- RN1: Validações são as mesmas do cálculo inicial
- RN2: Sistema mantém até 10 versões anteriores (opcional)
- RN3: Usuário pode reverter para qualquer versão anterior
- RN4: Alterações não afetam planos já criados baseados na simulação

#### Requisitos Especiais
- RE1: Recálculo deve ser instantâneo (<100ms client-side)
- RE2: Formulário deve ter validação em tempo real
- RE3: Comparação visual deve destacar deltas (%, R$)
- RE4: Deve haver undo/redo durante edição

---

### UC-M7A-005: Deletar Simulação

**Ator:** Usuário Principal, Usuário Secundário (próprias), Usuário Admin
**Descrição:** Remover simulação do histórico
**Prioridade:** Média

#### Pré-condições
- Usuário autenticado
- Usuário é dono da simulação OU é admin
- Simulação existe

#### Fluxo Principal
1. Usuário acessa histórico ou detalhes da simulação
2. Usuário clica em "Deletar" (ícone lixeira)
3. Sistema exibe modal de confirmação:
   - "Tem certeza que deseja deletar '[Nome]'?"
   - Preview dos dados que serão perdidos
   - Checkbox "Tenho certeza" (segurança extra)
   - Botões: "Cancelar" | "Deletar"
4. Usuário marca checkbox
5. Usuário clica em "Deletar"
6. Sistema executa soft-delete:
   - Marca registro como deleted=True
   - Mantém dados por 30 dias (recuperação)
   - Remove da visualização do usuário
7. Sistema exibe mensagem de sucesso com opção "Desfazer" (30s)
8. Sistema atualiza lista/histórico removendo o item

#### Fluxos Alternativos

**FA1: Usuário cancela**
- 4a. Usuário clica "Cancelar"
- 4b. Sistema fecha modal
- 4c. Nenhuma alteração feita

**FA2: Desfazer deleção**
- 7a. Dentro de 30 segundos, usuário clica "Desfazer"
- 7b. Sistema restaura simulação (deleted=False)
- 7c. Item reaparece na lista

**FA3: Simulação vinculada a plano**
- 6a. Sistema detecta que existe plano criado baseado na simulação
- 6b. Sistema exibe aviso: "Existe 1 plano vinculado a esta simulação"
- 6c. Sistema oferece opções:
   - Deletar mesmo assim (plano mantém cópia dos dados)
   - Cancelar deleção
- 6d. Usuário escolhe

**FA4: Deleção permanente (admin)**
- 1a. Admin acessa "Simulações Deletadas"
- 1b. Admin seleciona simulação deletada há >30 dias
- 1c. Admin clica "Deletar Permanentemente"
- 1d. Sistema remove registro do banco (irreversível)

#### Pós-condições
- Simulação marcada como deletada (soft-delete)
- Não aparece mais nas listas do usuário
- Pode ser recuperada por admin em até 30 dias
- Após 30 dias: deleção permanente automática

#### Regras de Negócio
- RN1: Soft-delete preserva dados por 30 dias
- RN2: Após 30 dias, job automatizado faz hard-delete
- RN3: Admin pode recuperar simulações deletadas
- RN4: Planos vinculados mantêm snapshot dos parâmetros da simulação
- RN5: Deleção em lote permite até 50 itens simultâneos

#### Requisitos Especiais
- RE1: Confirmação visual clara (modal vermelho)
- RE2: "Desfazer" deve funcionar mesmo após navegação
- RE3: Auditoria: registrar quem deletou e quando
- RE4: Notificar se há dependências (planos, compartilhamentos)

---

## M7-B: VISUALIZAÇÕES AVANÇADAS

### UC-M7B-001: Visualizar Gráfico de Evolução do Montante

**Ator:** Usuário Principal, Usuário Secundário
**Descrição:** Exibir gráfico interativo mostrando evolução mês a mês do investimento
**Prioridade:** Alta

#### Pré-condições
- Simulação calculada ou salva
- Parâmetros válidos (tempo > 0)

#### Fluxo Principal
1. Usuário realiza simulação ou abre simulação salva
2. Sistema calcula resultado
3. Sistema gera série temporal com dados mensais:
   ```
   Mês 0:  Principal = Inicial, Juros = 0, Total = Inicial
   Mês 1:  Principal = Inicial + Aporte, Juros = X, Total = Y
   ...
   Mês N:  Principal = P, Juros = J, Total = Montante
   ```
4. Sistema renderiza gráfico de linha/área com:
   - Eixo X: Meses (0 a N)
   - Eixo Y: Valores (R$)
   - Linhas:
     - **Total** (linha sólida, cor primária)
     - **Principal** (linha tracejada, cor secundária)
     - **Juros** (área preenchida, transparente)
5. Sistema adiciona interatividade:
   - Hover: tooltip com valores detalhados
   - Click: marcar mês específico
   - Zoom: arrastar para ampliar período
   - Pan: mover horizontalmente
6. Sistema exibe legenda explicativa
7. Sistema permite alternar visualização:
   - Gráfico de linha
   - Gráfico de área empilhada
   - Gráfico de barras (Principal vs Juros)

#### Fluxos Alternativos

**FA1: Período muito longo (>120 meses)**
- 3a. Sistema detecta período extenso
- 3b. Sistema agrupa dados por trimestre ou ano
- 3c. Sistema exibe nota: "Dados agrupados para melhor visualização"

**FA2: Exportar gráfico**
- 7a. Usuário clica "Exportar Gráfico"
- 7b. Sistema oferece formatos: PNG, SVG, PDF
- 7c. Sistema gera imagem em alta resolução
- 7d. Sistema faz download

**FA3: Comparar com meta**
- 7a. Usuário ativa opção "Mostrar Meta"
- 7b. Sistema adiciona linha horizontal no valor objetivo
- 7c. Gráfico destaca quando objetivo é atingido

#### Pós-condições
- Gráfico renderizado e interativo
- Usuário compreende evolução temporal
- Dados exportáveis se necessário

#### Regras de Negócio
- RN1: Gráfico calcula juros compostos mês a mês
- RN2: Principal = Inicial + (Aporte × Mês)
- RN3: Juros = Total - Principal
- RN4: Valores formatados em BRL (R$)
- RN5: Eixo Y inicia em 0 para perspectiva correta

#### Requisitos Especiais
- RE1: Renderização deve ser fluida (60fps)
- RE2: Biblioteca: Recharts ou Chart.js
- RE3: Responsivo (adaptar a mobile)
- RE4: Acessível (suporte a leitores de tela)
- RE5: Tooltip deve mostrar % de crescimento vs mês anterior

---

### UC-M7B-002: Visualizar Gráfico de Composição (Principal vs Juros)

**Ator:** Usuário Principal, Usuário Secundário
**Descrição:** Exibir gráfico de pizza/rosca mostrando distribuição final
**Prioridade:** Média

#### Pré-condições
- Simulação calculada
- Resultado > 0

#### Fluxo Principal
1. Sistema calcula valores finais:
   - Total investido pelo usuário
   - Total de juros acumulados
   - Montante final
2. Sistema calcula percentuais:
   - % Principal = (Investido / Montante) × 100
   - % Juros = (Juros / Montante) × 100
3. Sistema renderiza gráfico de rosca com:
   - Segmento 1: Principal (cor primária)
   - Segmento 2: Juros (cor de sucesso)
   - Centro: Montante total (R$)
4. Sistema exibe legenda com:
   - Principal: R$ X.XXX,XX (Y%)
   - Juros: R$ X.XXX,XX (Y%)
5. Sistema adiciona interatividade:
   - Hover: destaca segmento e exibe tooltip
   - Click: expande segmento (explode effect)

#### Fluxos Alternativos

**FA1: Juros muito pequenos (<1%)**
- 2a. Sistema detecta juros insignificantes
- 2b. Sistema exibe nota: "Período ou rentabilidade muito baixos"
- 2c. Gráfico ainda é exibido para referência

**FA2: Detalhamento de Principal**
- 5a. Usuário clica em segmento "Principal"
- 5b. Sistema expande mostrando:
   - Valor Inicial
   - Total de Aportes
- 5c. Gráfico vira 3 segmentos

#### Pós-condições
- Usuário compreende composição do montante
- Visualização clara do efeito dos juros compostos

#### Regras de Negócio
- RN1: Cores padronizadas: Azul (principal), Verde (juros)
- RN2: Percentuais com 2 casas decimais
- RN3: Montante no centro do donut chart
- RN4: Legenda sempre visível

#### Requisitos Especiais
- RE1: Animação suave ao renderizar (transition)
- RE2: Tooltip com formatação rica (ícones + valores)
- RE3: Acessibilidade: aria-labels descritivos

---

### UC-M7B-003: Visualizar Tabela Detalhada Mês a Mês

**Ator:** Usuário Principal, Usuário Secundário
**Descrição:** Exibir tabela expandível com valores detalhados de cada mês
**Prioridade:** Baixa

#### Pré-condições
- Simulação calculada
- Tempo > 0 meses

#### Fluxo Principal
1. Sistema exibe botão "Ver Tabela Detalhada" abaixo do gráfico
2. Usuário clica no botão
3. Sistema expande seção com tabela responsiva
4. Tabela exibe colunas:
   - **Mês**: Número sequencial (0, 1, 2, ..., N)
   - **Data**: Projeção de data (Mês/Ano)
   - **Aporte**: Valor investido no mês
   - **Saldo Inicial**: Saldo no início do mês
   - **Juros do Mês**: Juros gerados no período
   - **Saldo Final**: Total ao fim do mês
   - **Total Investido**: Acumulado de aportes
   - **Total Juros**: Acumulado de juros
5. Sistema permite:
   - Ordenação por qualquer coluna
   - Busca por mês específico
   - Paginação (20 linhas por página)
   - Export para CSV/Excel
6. Sistema destaca marcos importantes:
   - Mês que atinge objetivo (se aplicável)
   - Mês que juros superam principal
   - Aniversários (12, 24, 36 meses...)

#### Fluxos Alternativos

**FA1: Período longo (>60 meses)**
- 3a. Sistema pergunta: "Exibir todos os meses ou resumo anual?"
- 3b. Se resumo: agrupa por ano
- 3c. Se todos: exibe com paginação

**FA2: Export para Excel**
- 5a. Usuário clica "Exportar Excel"
- 5b. Sistema gera XLSX com:
   - Planilha 1: Dados mensais
   - Planilha 2: Resumo e gráficos
   - Planilha 3: Parâmetros da simulação
- 5c. Sistema faz download

#### Pós-condições
- Tabela detalhada disponível para análise
- Dados exportáveis para uso externo

#### Regras de Negócio
- RN1: Data projetada = Data atual + N meses
- RN2: Todos os valores em BRL formatados
- RN3: Destaque visual para marcos importantes
- RN4: Fórmulas expostas em tooltip (educacional)

#### Requisitos Especiais
- RE1: Tabela responsiva (scroll horizontal em mobile)
- RE2: Zebra striping para legibilidade
- RE3: Totalizadores no rodapé da tabela
- RE4: Suporte a impressão (print-friendly CSS)

---

## M7-C: ANÁLISE DE CENÁRIOS

### UC-M7C-001: Criar Análise de Sensibilidade

**Ator:** Usuário Principal, Usuário Secundário
**Descrição:** Gerar tabela "E se?" com variações de parâmetros
**Prioridade:** Alta

#### Pré-condições
- Usuário autenticado
- Simulação realizada (qualquer tipo)

#### Fluxo Principal
1. Usuário acessa simulação
2. Usuário clica em "Análise de Sensibilidade"
3. Sistema abre modal/seção com opções:
   - **Parâmetro a variar**: Dropdown (Rentabilidade / Tempo / Aporte / Valor Inicial)
   - **Valor base**: Atual da simulação
   - **Variação**: % ou valor absoluto
   - **Número de cenários**: 3, 5 ou 7
4. Usuário seleciona:
   - Parâmetro: "Rentabilidade"
   - Valor base: 10% a.a.
   - Variação: ±2% a.a.
   - Cenários: 5
5. Usuário clica "Gerar Análise"
6. Sistema calcula 5 cenários:
   - Cenário 1: 6% a.a. (base -4%)
   - Cenário 2: 8% a.a. (base -2%)
   - **Cenário 3: 10% a.a. (BASE)** ← destaque
   - Cenário 4: 12% a.a. (base +2%)
   - Cenário 5: 14% a.a. (base +4%)
7. Sistema exibe tabela comparativa:
   ```
   | Rentabilidade | Aporte Mensal | Montante Final | Diferença vs Base |
   |---------------|---------------|----------------|-------------------|
   | 6% a.a.       | R$ 1.500,00   | R$ 95.000,00   | -15% 🔴          |
   | 8% a.a.       | R$ 1.300,00   | R$ 98.000,00   | -8% 🟡           |
   | 10% a.a.      | R$ 1.200,00   | R$ 100.000,00  | BASE 🟢          |
   | 12% a.a.      | R$ 1.100,00   | R$ 103.000,00  | +8% 🟢           |
   | 14% a.a.      | R$ 1.000,00   | R$ 107.000,00  | +15% 🟢          |
   ```
8. Sistema renderiza gráfico de barras comparativo
9. Sistema permite:
   - Salvar análise
   - Exportar (PDF/Excel)
   - Alterar parâmetro variável
   - Criar plano baseado em cenário específico

#### Fluxos Alternativos

**FA1: Variação customizada**
- 4a. Usuário seleciona "Customizado"
- 4b. Sistema permite inserir valores específicos manualmente
- 4c. Exemplo: 5%, 7.5%, 10%, 12.5%, 15%
- 4d. Continua do passo 5

**FA2: Análise multivariável (2 parâmetros)**
- 3a. Usuário seleciona "Análise Avançada"
- 3b. Sistema permite escolher 2 parâmetros
- 3c. Sistema gera matriz 3x3 ou 5x5
- 3d. Resultado: heatmap colorido

**FA3: Nenhuma variação significativa**
- 7a. Sistema detecta que todas variações resultam em valores muito próximos
- 7b. Sistema exibe nota: "Baixa sensibilidade a este parâmetro"
- 7c. Sistema sugere analisar outro parâmetro

#### Pós-condições
- Tabela de sensibilidade gerada
- Usuário compreende impacto de variações
- Pode tomar decisão informada

#### Regras de Negócio
- RN1: Variação padrão: ±20% do valor base
- RN2: Número de cenários: ímpar (para ter ponto central)
- RN3: Cenário base sempre destacado visualmente
- RN4: Diferenças calculadas em % e R$
- RN5: Cores semafóricas: Verde (melhor), Vermelho (pior)

#### Requisitos Especiais
- RE1: Cálculo de todos cenários deve ser <500ms
- RE2: Tabela ordenada automaticamente (pior → melhor)
- RE3: Gráfico deve destacar visualmente o cenário base
- RE4: Tooltip deve explicar "sensibilidade" (educacional)
- RE5: Responsivo: tabela vira cards em mobile

---

### UC-M7C-002: Comparar Múltiplos Cenários Salvos

**Ator:** Usuário Principal, Usuário Secundário
**Descrição:** Selecionar 2-4 simulações salvas e compará-las lado a lado
**Prioridade:** Média

#### Pré-condições
- Usuário autenticado
- Ao menos 2 simulações salvas

#### Fluxo Principal
1. Usuário acessa "Histórico" > "Comparar Simulações"
2. Sistema exibe lista de simulações salvas com checkbox
3. Usuário seleciona 2 a 4 simulações
4. Sistema valida que todas são do mesmo tipo (goal/time/future)
5. Usuário clica "Comparar Selecionadas"
6. Sistema carrega dados das simulações
7. Sistema exibe visualização comparativa:

   **Layout:**
   ```
   ┌────────────┬────────────┬────────────┬────────────┐
   │ Simulação 1│ Simulação 2│ Simulação 3│ Simulação 4│
   ├────────────┼────────────┼────────────┼────────────┤
   │ PARÂMETROS                                         │
   │ Objetivo   │ R$ 100k    │ R$ 120k    │ R$ 100k    │
   │ Inicial    │ R$ 10k     │ R$ 5k      │ R$ 10k     │
   │ Tempo      │ 60 meses   │ 60 meses   │ 48 meses   │
   │ Rent.      │ 10% a.a.   │ 12% a.a.   │ 10% a.a.   │
   ├────────────┼────────────┼────────────┼────────────┤
   │ RESULTADOS                                         │
   │ Aporte     │ R$ 1.200   │ R$ 1.500   │ R$ 1.600   │
   │ Investido  │ R$ 82k     │ R$ 95k     │ R$ 86.8k   │
   │ Juros      │ R$ 18k     │ R$ 25k     │ R$ 13.2k   │
   │ ROI        │ 22%        │ 26%        │ 15%        │
   └────────────┴────────────┴────────────┴────────────┘
   ```

8. Sistema destaca:
   - Melhor cenário (verde)
   - Pior cenário (vermelho)
   - Diferenças relativas entre cenários
9. Sistema renderiza gráfico comparativo:
   - Barras lado a lado (Principal vs Juros)
   - Linhas de evolução temporal sobrepostas
10. Sistema permite:
    - Adicionar/remover simulações da comparação
    - Exportar relatório comparativo
    - Marcar favorita

#### Fluxos Alternativos

**FA1: Tipos diferentes de simulação**
- 4a. Sistema detecta simulações de tipos diferentes
- 4b. Sistema exibe aviso: "Selecione apenas simulações do mesmo tipo"
- 4c. Sistema desabilita botão "Comparar"
- 4d. Retorna ao passo 3

**FA2: Comparação de 2 simulações apenas**
- 3a. Usuário seleciona apenas 2
- 3b. Sistema exibe visualização lado a lado (50/50)
- 3c. Mais espaço para gráficos e detalhes

**FA3: Criar nova simulação baseada em mix**
- 10a. Usuário clica "Criar Cenário Híbrido"
- 10b. Sistema permite escolher parâmetros de diferentes simulações
- 10c. Exemplo: Tempo da Sim1 + Rentabilidade da Sim2
- 10d. Sistema calcula novo resultado
- 10e. Usuário pode salvar como nova simulação

#### Pós-condições
- Comparação visual clara exibida
- Usuário identifica melhor cenário
- Decisão facilitada

#### Regras de Negócio
- RN1: Máximo 4 simulações por comparação (UX)
- RN2: Simulações devem ser do mesmo tipo
- RN3: Destaque visual para extremos (melhor/pior)
- RN4: Percentuais calculados em relação ao melhor cenário

#### Requisitos Especiais
- RE1: Layout responsivo (stack vertical em mobile)
- RE2: Cores distintas para cada simulação (legenda)
- RE3: Botão "Favoritar" para marcar cenário preferido
- RE4: Compartilhamento: gerar link público temporário

---

### UC-M7C-003: Gerar Recomendação Baseada em Cenários

**Ator:** Sistema (automático após análise de cenários)
**Descrição:** IA/sistema sugere melhor cenário baseado em critérios
**Prioridade:** Baixa

#### Pré-condições
- Análise de sensibilidade ou comparação realizada
- Múltiplos cenários calculados

#### Fluxo Principal
1. Sistema analisa todos os cenários calculados
2. Sistema aplica heurísticas:
   - **Viabilidade**: Aporte mensal < 30% da renda declarada
   - **Eficiência**: Maior % de juros (efeito composto)
   - **Prazo**: Preferência por prazos intermediários (nem muito curto, nem muito longo)
   - **Risco**: Rentabilidade realista para tipo de investimento
3. Sistema pontua cada cenário (0-100)
4. Sistema seleciona top 3 cenários
5. Sistema exibe card de recomendação:
   ```
   💡 RECOMENDAÇÃO DO SISTEMA

   Com base em sua análise, sugerimos o Cenário 2:

   ✓ Aporte mensal viável (R$ 1.200 = 20% da renda)
   ✓ Prazo equilibrado (5 anos)
   ✓ Rentabilidade realista (10% a.a.)
   ✓ ROI atrativo (22%)

   Alternativas:
   • Cenário 4: Prazo mais longo, aporte menor
   • Cenário 1: Aporte maior, prazo mais curto

   [Criar Plano Baseado neste Cenário]
   ```
6. Usuário pode aceitar sugestão ou escolher outro

#### Fluxos Alternativos

**FA1: Nenhum cenário viável**
- 2a. Sistema detecta que todos cenários requerem aporte > 30% renda
- 2b. Sistema exibe alerta: "Objetivo pode ser inviável com renda atual"
- 2c. Sistema sugere:
   - Aumentar prazo
   - Reduzir objetivo
   - Aumentar valor inicial

**FA2: Usuário fornece contexto adicional**
- 1a. Sistema pergunta preferências:
   - "Prefere aporte menor ou prazo menor?"
   - "Qual sua tolerância a risco?"
- 1b. Usuário responde
- 1c. Sistema ajusta heurísticas
- 1d. Continua do passo 2

#### Pós-condições
- Recomendação clara exibida
- Justificativa transparente
- Usuário pode tomar ação imediata

#### Regras de Negócio
- RN1: Aporte máximo: 30% da renda (se informada)
- RN2: Rentabilidade conservadora: 8-12% a.a.
- RN3: Prazo ótimo: 3-10 anos
- RN4: Sempre explicar critérios de recomendação

#### Requisitos Especiais
- RE1: Linguagem clara e não técnica
- RE2: Ícones visuais para cada critério
- RE3: Botão direto "Criar Plano" pré-configurado
- RE4: Feedback: "Esta recomendação foi útil?" (ML)

---

## M7-D: INTEGRAÇÃO COM PLANOS

### UC-M7D-001: Criar Plano Financeiro a Partir de Simulação

**Ator:** Usuário Principal, Usuário Secundário
**Descrição:** Converter simulação em plano financeiro rastreável com 1 clique
**Prioridade:** Alta

#### Pré-condições
- Usuário autenticado
- Simulação calculada ou salva
- Ao menos uma instituição financeira cadastrada

#### Fluxo Principal
1. Usuário visualiza resultado de simulação
2. Sistema exibe botão destacado: "🎯 Criar Plano Baseado nesta Simulação"
3. Usuário clica no botão
4. Sistema abre modal pré-preenchido:

   **Dados Automáticos (da simulação):**
   - Nome: "Plano: [Nome da Simulação]"
   - Valor Objetivo: [Do resultado da simulação]
   - Aporte Mensal: [Do resultado/parâmetro]
   - Data Alvo: [Data atual + tempo da simulação]

   **Dados a Preencher:**
   - Instituição Financeira: [Dropdown]
   - Descrição: [Opcional, texto livre]
   - Tipo de Investimento: [CDB, Tesouro, etc.]
   - Notificações: [Checkbox] Lembrar-me de aportar mensalmente

5. Usuário confirma ou ajusta dados
6. Usuário clica "Criar Plano"
7. Sistema valida dados
8. Sistema cria registro em `financial_plans`:
   ```python
   {
     name: "Plano: Aposentadoria 2035",
     goal_amount: 100000.00,
     current_balance: 10000.00,  # Valor inicial da simulação
     monthly_contribution: 1200.00,
     target_date: "2029-12-23",
     institution_id: 5,
     simulation_id: 42,  # Vincula à simulação original
     created_from_simulation: True
   }
   ```
9. Sistema exibe confirmação com ações:
   - "Plano criado com sucesso!"
   - [Ver Plano] [Ir para Planejamento] [Registrar Primeiro Aporte]
10. Sistema redireciona para página de Planejamento

#### Fluxos Alternativos

**FA1: Múltiplas instituições**
- 5a. Usuário quer dividir plano entre 2 instituições
- 5b. Sistema permite criar 2 planos vinculados
- 5c. Usuário define % de cada instituição
- 5d. Sistema cria 2 registros proporcionais

**FA2: Ajustar parâmetros antes de criar**
- 5a. Usuário altera aporte mensal sugerido
- 5b. Sistema recalcula data alvo automaticamente
- 5c. Sistema exibe aviso se mudança for significativa
- 5d. Usuário confirma

**FA3: Instituição não cadastrada**
- 4a. Usuário não encontra instituição no dropdown
- 4b. Usuário clica "+ Nova Instituição"
- 4c. Sistema abre modal rápido de cadastro
- 4d. Usuário preenche: Nome, Tipo de Conta
- 4e. Sistema salva e retorna ao formulário do plano
- 4f. Nova instituição já vem selecionada

**FA4: Plano similar já existe**
- 7a. Sistema detecta plano com nome/objetivo similar
- 7b. Sistema pergunta: "Já existe um plano parecido. Deseja:"
   - Criar mesmo assim
   - Atualizar plano existente
   - Cancelar
- 7c. Usuário escolhe

#### Pós-condições
- Plano financeiro criado no banco de dados
- Vinculado à simulação original (rastreabilidade)
- Disponível em "Planejamento" para acompanhamento
- Notificações configuradas (se selecionado)

#### Regras de Negócio
- RN1: Plano herda todos parâmetros relevantes da simulação
- RN2: Simulação permanece inalterada (read-only para o plano)
- RN3: Usuário pode criar múltiplos planos da mesma simulação
- RN4: Data alvo = Data atual + Tempo (meses) da simulação
- RN5: Current_balance inicial = Valor inicial da simulação

#### Requisitos Especiais
- RE1: Modal deve abrir em <300ms
- RE2: Campos pré-preenchidos claramente destacados
- RE3: Botão "Criar Plano" visualmente proeminente
- RE4: Confirmação deve incluir próximo passo sugerido
- RE5: Se simulação for editada, plano NÃO é afetado (snapshot)

---

### UC-M7D-002: Vincular Plano Existente a Simulação

**Ator:** Usuário Principal
**Descrição:** Associar simulação a plano já criado para rastreamento
**Prioridade:** Baixa

#### Pré-condições
- Usuário autenticado
- Simulação salva
- Ao menos um plano financeiro existente

#### Fluxo Principal
1. Usuário acessa detalhes de simulação salva
2. Sistema exibe seção "Planos Relacionados"
3. Se não há vínculo: Sistema exibe "Nenhum plano vinculado"
4. Sistema exibe botão "+ Vincular a Plano Existente"
5. Usuário clica no botão
6. Sistema abre modal com:
   - Lista de planos existentes (nome, objetivo, progresso)
   - Campo de busca
   - Filtro por status (ativo/concluído)
7. Usuário seleciona plano
8. Usuário clica "Vincular"
9. Sistema valida compatibilidade:
   - Objetivo do plano ≈ Objetivo da simulação (±20%)
   - Tipo de investimento compatível
10. Sistema cria vínculo (simulation_id no plano)
11. Sistema exibe confirmação
12. Sistema atualiza visualização com plano vinculado

#### Fluxos Alternativos

**FA1: Incompatibilidade detectada**
- 9a. Sistema detecta objetivos muito diferentes
- 9b. Sistema exibe alerta: "Valores divergem em X%. Vincular mesmo assim?"
- 9c. Usuário confirma ou cancela

**FA2: Plano já vinculado a outra simulação**
- 9a. Sistema detecta que plano já tem simulação vinculada
- 9b. Sistema pergunta: "Substituir vínculo anterior?"
- 9c. Usuário escolhe

**FA3: Desvincular plano**
- 12a. Usuário clica "Desvincular"
- 12b. Sistema remove simulation_id do plano
- 12c. Plano continua existindo normalmente

#### Pós-condições
- Vínculo criado entre simulação e plano
- Ambos permanecem independentes (não afetam um ao outro)
- Rastreabilidade para análise futura

#### Regras de Negócio
- RN1: Plano pode ter apenas 1 simulação vinculada
- RN2: Simulação pode ter múltiplos planos vinculados
- RN3: Vínculo é informativo, não altera comportamento
- RN4: Desvincular não deleta nem simulação nem plano

#### Requisitos Especiais
- RE1: Lista de planos ordenada por relevância (similaridade)
- RE2: Indicador visual de compatibilidade (score)
- RE3: Preview de ambos lado a lado antes de vincular

---

### UC-M7D-003: Comparar Simulação vs Realidade do Plano

**Ator:** Usuário Principal, Usuário Secundário
**Descrição:** Exibir dashboard comparando projeção da simulação vs execução real do plano
**Prioridade:** Média

#### Pré-condições
- Plano criado a partir de simulação (ou vinculado)
- Plano com ao menos 1 mês de histórico
- Aportes registrados no plano

#### Fluxo Principal
1. Usuário acessa página de detalhes do plano
2. Sistema detecta que plano tem simulação vinculada
3. Sistema exibe seção "📊 Simulado vs Realizado"
4. Sistema calcula métricas comparativas:

   **Projetado (da simulação):**
   - Aporte mensal: R$ 1.200,00
   - Saldo esperado mês N: R$ 15.000,00
   - Data projetada de conclusão: Dez/2029

   **Realizado (do plano):**
   - Aporte mensal médio: R$ 1.150,00
   - Saldo atual: R$ 14.500,00
   - Projeção de conclusão: Jan/2030

   **Diferenças:**
   - Aporte: -4.2% (R$ 50 a menos)
   - Saldo: -3.3% (R$ 500 a menos)
   - Prazo: +1 mês de atraso

5. Sistema renderiza gráfico de linhas:
   - Linha azul: Projeção da simulação
   - Linha verde: Execução real (até mês atual)
   - Área sombreada: Projeção futura ajustada
6. Sistema exibe indicadores:
   - 🟢 No ritmo (diferença < 5%)
   - 🟡 Atenção (diferença 5-15%)
   - 🔴 Fora do ritmo (diferença > 15%)
7. Sistema sugere ações corretivas:
   - "Aumente o aporte em R$ 50 para voltar ao ritmo"
   - "Ou aceite 1 mês de atraso no objetivo"

#### Fluxos Alternativos

**FA1: Desempenho melhor que simulado**
- 4a. Sistema detecta saldo real > saldo projetado
- 4b. Sistema exibe mensagem positiva: "🎉 Você está à frente do planejado!"
- 4c. Sistema calcula: "Você pode atingir o objetivo X meses antes"

**FA2: Grande divergência (>30%)**
- 6a. Sistema detecta divergência crítica
- 6b. Sistema exibe alerta destacado
- 6c. Sistema sugere: "Recalcular simulação com dados reais"
- 6d. Botão: "Criar Nova Simulação Ajustada"

**FA3: Atualizar simulação base**
- 7a. Usuário clica "Ajustar Projeção"
- 7b. Sistema abre simulador pré-preenchido com:
   - Valor inicial = Saldo atual real
   - Aporte mensal = Média real dos últimos 3 meses
   - Tempo = Tempo restante ajustado
- 7c. Usuário recalcula
- 7d. Sistema vincula nova simulação ao plano

#### Pós-condições
- Usuário tem visão clara de aderência ao plano
- Ações corretivas sugeridas
- Motivação para manter disciplina

#### Regras de Negócio
- RN1: Comparação começa após 1º mês completo
- RN2: Aporte mensal real = média dos últimos 3 meses
- RN3: Projeção futura usa taxa real (se rentabilidade for rastreada)
- RN4: Indicadores coloridos baseados em % de diferença

#### Requisitos Especiais
- RE1: Gráfico atualiza em tempo real ao registrar aportes
- RE2: Linguagem motivacional (gamificação sutil)
- RE3: Botões de ação direta (sem múltiplos cliques)
- RE4: Exportar relatório "Simulado vs Realizado" (PDF)

---

## M7-E: EDUCAÇÃO FINANCEIRA

### UC-M7E-001: Exibir Tooltips Educacionais

**Ator:** Usuário Principal, Usuário Secundário (especialmente iniciantes)
**Descrição:** Mostrar explicações contextuais sobre conceitos financeiros
**Prioridade:** Média

#### Pré-condições
- Usuário acessando qualquer simulador
- Elementos com conceitos financeiros visíveis

#### Fluxo Principal
1. Usuário acessa página de simuladores
2. Sistema identifica campos e resultados com conceitos técnicos
3. Sistema adiciona ícone "ℹ️" ou "?" ao lado de cada termo
4. Usuário passa mouse sobre ícone (desktop) ou toca (mobile)
5. Sistema exibe tooltip com:

   **Exemplo: "Rentabilidade % a.a."**
   ```
   📚 Rentabilidade Anual

   É o percentual de retorno que seu investimento
   gera em um ano.

   Exemplos:
   • Conservador: 6-8% a.a. (Tesouro Selic, CDB)
   • Moderado: 10-12% a.a. (Fundos, ações blue chip)
   • Agressivo: 15%+ a.a. (Ações growth, FIIs)

   ⚠️ Rentabilidades passadas não garantem futuras.
   ```

6. Tooltip permanece aberto enquanto mouse estiver sobre ele
7. Usuário pode clicar em "Saiba Mais" para artigo completo
8. Sistema registra interação (analytics)

#### Fluxos Alternativos

**FA1: Modo Tutorial (primeira vez)**
- 1a. Sistema detecta primeiro acesso do usuário
- 1b. Sistema ativa tour guiado automático
- 1c. Tooltips aparecem sequencialmente
- 1d. Usuário pode pular tour

**FA2: Glossário completo**
- 7a. Usuário clica "Ver Glossário Completo"
- 7b. Sistema abre modal com todos os termos
- 7c. Termos organizados alfabeticamente
- 7d. Campo de busca disponível

**FA3: Vídeo explicativo**
- 7a. Usuário clica "Ver Vídeo"
- 7b. Sistema abre modal com vídeo curto (1-2min)
- 7c. Vídeo explica conceito com animações
- 7d. Player embutido (YouTube/Vimeo)

#### Pós-condições
- Usuário compreende melhor conceitos financeiros
- Redução de dúvidas e erros de input
- Maior confiança nas simulações

#### Regras de Negócio
- RN1: Tooltips em linguagem simples (evitar jargão)
- RN2: Máximo 150 palavras por tooltip
- RN3: Sempre incluir exemplos práticos
- RN4: Links para conteúdo aprofundado opcional

#### Requisitos Especiais
- RE1: Tooltips acessíveis (ARIA labels)
- RE2: Funcionar em touch devices
- RE3: Não atrapalhar workflow (não-intrusivo)
- RE4: Conteúdo revisado por educador financeiro

**Termos com Tooltips:**
- Rentabilidade % a.a.
- Juros compostos
- Aporte mensal
- Montante futuro
- Principal
- ROI (Return on Investment)
- Inflação (se incluído)
- Taxa real vs nominal
- Risco
- Liquidez

---

### UC-M7E-002: Fornecer Calculadora de Regra 72

**Ator:** Usuário Principal, Usuário Secundário
**Descrição:** Mini-calculadora educacional: tempo para dobrar investimento
**Prioridade:** Baixa

#### Pré-condições
- Usuário na página de simuladores

#### Fluxo Principal
1. Sistema exibe widget lateral "🧮 Calculadora Rápida"
2. Widget mostra "Regra 72: Em quanto tempo dobro meu dinheiro?"
3. Usuário insere rentabilidade esperada (% a.a.)
4. Sistema calcula instantaneamente: **Anos = 72 ÷ Rentabilidade**
5. Sistema exibe resultado:
   ```
   Com 10% a.a., você dobra seu dinheiro em ~7.2 anos

   R$ 10.000 → R$ 20.000 em 7 anos e 2 meses
   ```
6. Sistema exibe gráfico mini:
   - Linha mostrando duplicações sucessivas
   - 1x → 2x → 4x → 8x → 16x
7. Sistema adiciona nota educacional:
   "📚 A Regra 72 é uma aproximação. Use os simuladores
   para cálculos precisos com aportes mensais."

#### Fluxos Alternativos

**FA1: Outras regras rápidas**
- 2a. Widget tem abas: Regra 72 | Regra 114 (triplicar)
- 2b. Usuário alterna entre abas
- 2c. Mesma interface, fórmulas diferentes

**FA2: Comparação visual**
- 6a. Sistema permite inserir 2 rentabilidades
- 6b. Exibe barras comparativas lado a lado
- 6c. Exemplo: 8% a.a. (9 anos) vs 12% a.a. (6 anos)

#### Pós-condições
- Usuário compreende poder dos juros compostos
- Motivação para investir em rentabilidades maiores
- Transição natural para simuladores completos

#### Regras de Negócio
- RN1: Regra 72: Anos = 72 ÷ Taxa
- RN2: Regra 114: Anos = 114 ÷ Taxa (triplicar)
- RN3: Válido para taxas entre 4% e 20%
- RN4: Sempre incluir disclaimer sobre aproximação

#### Requisitos Especiais
- RE1: Cálculo instantâneo (onChange)
- RE2: Visual simples e direto
- RE3: Link "Usar no Simulador Completo"
- RE4: Animação ao mostrar duplicações

---

### UC-M7E-003: Mostrar Artigos Relacionados

**Ator:** Usuário Principal, Usuário Secundário
**Descrição:** Sugerir conteúdo educacional baseado em contexto
**Prioridade:** Baixa

#### Pré-condições
- Usuário realizou simulação
- Base de artigos educacionais disponível

#### Fluxo Principal
1. Usuário conclui simulação
2. Sistema analisa contexto:
   - Tipo de simulação
   - Valores envolvidos
   - Prazo (curto/médio/longo)
   - Rentabilidade (conservadora/agressiva)
3. Sistema seleciona 2-3 artigos relevantes
4. Sistema exibe seção "📖 Leitura Recomendada":
   ```
   Baseado em sua simulação, você pode se interessar por:

   📄 "Como escolher investimentos de longo prazo"
      5 min de leitura
      [Ler Artigo]

   📄 "Diversificação: Por que não colocar tudo em um cesto"
      3 min de leitura
      [Ler Artigo]
   ```
5. Usuário pode clicar para ler
6. Artigo abre em modal ou página nova
7. Sistema rastreia leituras (analytics)

#### Fluxos Alternativos

**FA1: Vídeos ao invés de artigos**
- 4a. Sistema oferece vídeos curtos
- 4b. Thumbnail + duração + título
- 4c. Player embutido

**FA2: Quiz educacional**
- 4a. Sistema sugere "Teste seus conhecimentos"
- 4b. Quiz de 5 perguntas sobre conceitos da simulação
- 4c. Feedback imediato com explicações
- 4d. Certificado/badge ao acertar >80%

#### Pós-condições
- Usuário mais educado financeiramente
- Maior confiança em decisões
- Engajamento com plataforma

#### Regras de Negócio
- RN1: Relevância baseada em ML ou regras manuais
- RN2: Conteúdo sempre atualizado
- RN3: Linguagem acessível (não técnica)
- RN4: Fontes confiáveis (CVM, Bacen, etc.)

#### Requisitos Especiais
- RE1: Não ser intrusivo (seção opcional)
- RE2: Conteúdo responsivo (mobile)
- RE3: Opção "Não mostrar novamente"
- RE4: Integração com blog (se existir)

---

## M7-F: EXPORTAÇÃO

### UC-M7F-001: Exportar Simulação em PDF

**Ator:** Usuário Principal, Usuário Secundário
**Descrição:** Gerar relatório PDF formatado da simulação
**Prioridade:** Alta

#### Pré-condições
- Simulação calculada ou salva
- Biblioteca de geração de PDF configurada (backend)

#### Fluxo Principal
1. Usuário visualiza resultado de simulação
2. Usuário clica em "Exportar" > "PDF"
3. Sistema abre modal de configuração:
   - **Incluir:**
     - ☑️ Parâmetros de entrada
     - ☑️ Resultados principais
     - ☑️ Gráficos de evolução
     - ☑️ Tabela detalhada mês a mês
     - ☐ Análise de sensibilidade (se gerada)
     - ☐ Notas pessoais
   - **Estilo:**
     - Tema: Claro / Escuro
     - Logo: Incluir / Sem logo
4. Usuário configura e clica "Gerar PDF"
5. Sistema envia requisição ao backend
6. Backend gera PDF com:

   **Estrutura do Documento:**
   ```
   ┌─────────────────────────────────────┐
   │ RELATÓRIO DE SIMULAÇÃO FINANCEIRA   │
   │ Flow Forecaster                     │
   │ Data: 23/12/2025                    │
   ├─────────────────────────────────────┤
   │ 1. RESUMO EXECUTIVO                 │
   │    • Objetivo: R$ 100.000,00        │
   │    • Prazo: 60 meses (5 anos)       │
   │    • Aporte necessário: R$ 1.200/mês│
   ├─────────────────────────────────────┤
   │ 2. PARÂMETROS DA SIMULAÇÃO          │
   │    [Tabela com inputs]              │
   ├─────────────────────────────────────┤
   │ 3. RESULTADOS DETALHADOS            │
   │    [Métricas calculadas]            │
   ├─────────────────────────────────────┤
   │ 4. EVOLUÇÃO TEMPORAL                │
   │    [Gráfico de linha]               │
   ├─────────────────────────────────────┤
   │ 5. COMPOSIÇÃO DO MONTANTE           │
   │    [Gráfico de pizza]               │
   ├─────────────────────────────────────┤
   │ 6. TABELA MÊS A MÊS (Opcional)      │
   │    [Dados mensais]                  │
   ├─────────────────────────────────────┤
   │ 7. OBSERVAÇÕES                      │
   │    [Notas do usuário]               │
   ├─────────────────────────────────────┤
   │ Gerado em: 23/12/2025 14:35         │
   │ Por: João Silva                     │
   └─────────────────────────────────────┘
   ```

7. Backend retorna arquivo PDF
8. Sistema faz download automático ou abre em nova aba
9. Sistema exibe confirmação "PDF gerado com sucesso"

#### Fluxos Alternativos

**FA1: Geração demora (>5s)**
- 6a. Sistema exibe loader com progresso
- 6b. Mensagem: "Gerando PDF... 75% concluído"
- 6c. Permite cancelar geração

**FA2: Erro na geração**
- 6a. Backend retorna erro (ex: timeout)
- 6b. Sistema exibe erro amigável
- 6c. Sistema oferece tentar novamente ou exportar Excel

**FA3: Pré-visualização antes de gerar**
- 4a. Usuário clica "Pré-visualizar"
- 4b. Sistema gera preview em HTML (rápido)
- 4c. Usuário revisa e confirma
- 4d. Sistema gera PDF final

#### Pós-condições
- Arquivo PDF gerado e baixado
- Usuário tem relatório offline da simulação
- Pode compartilhar ou imprimir

#### Regras de Negócio
- RN1: PDF deve ser profissional (formatação limpa)
- RN2: Gráficos em alta resolução (300 DPI)
- RN3: Marca d'água "Flow Forecaster" discreta
- RN4: Tamanho máximo: 5 MB

#### Requisitos Especiais
- RE1: Geração deve ser <3 segundos
- RE2: Biblioteca: ReportLab (Python) ou jsPDF (JS)
- RE3: PDF/A compliant (arquivamento)
- RE4: Acessível (tags estruturais)
- RE5: Watermark com timestamp (auditoria)

---

### UC-M7F-002: Exportar Simulação em Excel

**Ator:** Usuário Principal, Usuário Secundário
**Descrição:** Gerar planilha Excel editável com dados e fórmulas
**Prioridade:** Média

#### Pré-condições
- Simulação calculada ou salva
- Biblioteca de geração de Excel configurada

#### Fluxo Principal
1. Usuário clica em "Exportar" > "Excel"
2. Sistema gera arquivo XLSX com múltiplas planilhas:

   **Sheet 1: "Resumo"**
   - Parâmetros de entrada (formatados)
   - Resultados principais (calculados)
   - Gráfico de pizza (embedded)

   **Sheet 2: "Evolução Mensal"**
   - Tabela detalhada mês a mês
   - Colunas: Mês | Data | Aporte | Saldo Inicial | Juros | Saldo Final
   - Fórmulas Excel (usuário pode editar e recalcular)
   - Gráfico de linha (embedded)

   **Sheet 3: "Análise de Sensibilidade" (se gerada)**
   - Tabela de cenários
   - Formatação condicional (heatmap)

   **Sheet 4: "Fórmulas"**
   - Explicação das fórmulas utilizadas
   - Exemplos didáticos
   - Links para recursos educacionais

3. Sistema faz download do arquivo
4. Usuário abre no Excel/Google Sheets/LibreOffice

#### Fluxos Alternativos

**FA1: Compatibilidade com Google Sheets**
- 2a. Sistema gera formato compatível
- 2b. Evita features avançadas do Excel
- 2c. Testa compatibilidade antes de enviar

**FA2: Template personalizável**
- 1a. Usuário clica "Exportar com Template"
- 1b. Sistema oferece templates:
   - Profissional (formal)
   - Simples (minimalista)
   - Educacional (com explicações)
- 1c. Usuário escolhe
- 1d. Sistema aplica template

#### Pós-condições
- Arquivo Excel gerado e baixado
- Usuário pode editar, recalcular, personalizar
- Útil para análises avançadas

#### Regras de Negócio
- RN1: Fórmulas devem ser editáveis (não valores fixos)
- RN2: Formatação consistente (cores, fontes)
- RN3: Proteção opcional de células (evitar quebrar fórmulas)
- RN4: Compatível com Excel 2016+

#### Requisitos Especiais
- RE1: Biblioteca: openpyxl (Python) ou ExcelJS (Node)
- RE2: Gráficos embutidos (não apenas dados)
- RE3: Formatação condicional para destaques
- RE4: Tamanho otimizado (<2 MB)

---

### UC-M7F-003: Compartilhar Simulação via Link

**Ator:** Usuário Principal
**Descrição:** Gerar link público temporário para compartilhar simulação
**Prioridade:** Baixa

#### Pré-condições
- Usuário autenticado
- Simulação salva
- Feature de compartilhamento habilitada

#### Fluxo Principal
1. Usuário acessa detalhes da simulação
2. Usuário clica em "Compartilhar"
3. Sistema abre modal com opções:
   - **Tipo:**
     - 🔗 Link público (qualquer pessoa com link)
     - 📧 Enviar por e-mail
     - 💬 Copiar para WhatsApp
   - **Expiração:**
     - 24 horas
     - 7 dias
     - 30 dias
     - Sem expiração
   - **Permissões:**
     - Apenas visualizar
     - Visualizar e copiar (criar própria versão)
4. Usuário configura e clica "Gerar Link"
5. Sistema cria registro em `shared_simulations`:
   ```python
   {
     simulation_id: 42,
     share_token: "abc123xyz789",  # UUID único
     expires_at: "2026-01-23",
     view_count: 0,
     allow_copy: True
   }
   ```
6. Sistema gera URL:
   `https://flowforecaster.app/share/sim/abc123xyz789`
7. Sistema exibe link com botões:
   - [Copiar Link] [Enviar Email] [WhatsApp] [QR Code]
8. Usuário copia e compartilha

#### Fluxos Alternativos

**FA1: Acesso ao link compartilhado**
- 1a. Visitante acessa URL compartilhada
- 1b. Sistema valida token e expiração
- 1c. Sistema renderiza versão pública da simulação:
   - Sem botões de edição
   - Sem dados pessoais do dono
   - Watermark "Compartilhado por [Nome]"
- 1d. Se allow_copy=True: botão "Copiar para minha conta"
- 1e. Visitante pode visualizar/copiar

**FA2: Revogar compartilhamento**
- 8a. Usuário clica "Gerenciar Links"
- 8b. Sistema lista todos links ativos
- 8c. Usuário clica "Revogar" em um link
- 8d. Sistema marca share_token como inativo
- 8e. Link para de funcionar imediatamente

**FA3: Rastreamento de visualizações**
- 1e (FA1). Sistema incrementa view_count
- 1f. Dono pode ver quantas vezes foi acessado

#### Pós-condições
- Link gerado e copiado
- Simulação acessível publicamente via link
- Dono mantém controle (revogar, expiração)

#### Regras de Negócio
- RN1: Token deve ser criptograficamente seguro (UUID4)
- RN2: Expiração automática remove acesso
- RN3: Visualizações são anônimas (não rastreia quem)
- RN4: Máximo 10 links ativos por simulação

#### Requisitos Especiais
- RE1: Link curto e fácil de compartilhar
- RE2: QR Code gerado automaticamente
- RE3: Preview ao compartilhar (Open Graph tags)
- RE4: Rate limiting (evitar abuso)

---

## REQUISITOS TÉCNICOS

### Backend (Python/Flask)

#### Novos Endpoints

```python
# Simulações
POST   /api/simulations                    # Salvar simulação
GET    /api/simulations                    # Listar minhas simulações
GET    /api/simulations/<id>               # Detalhes de simulação
PUT    /api/simulations/<id>               # Editar simulação
DELETE /api/simulations/<id>               # Deletar (soft-delete)

# Análise
POST   /api/simulations/<id>/sensitivity   # Gerar análise de sensibilidade
POST   /api/simulations/compare            # Comparar múltiplas simulações
POST   /api/simulations/<id>/recommend     # Gerar recomendação

# Integração
POST   /api/simulations/<id>/create-plan   # Criar plano a partir de simulação
POST   /api/plans/<id>/link-simulation     # Vincular plano existente
GET    /api/plans/<id>/vs-simulation       # Comparar plano vs simulação

# Exportação
GET    /api/simulations/<id>/export/pdf    # Exportar PDF
GET    /api/simulations/<id>/export/xlsx   # Exportar Excel

# Compartilhamento
POST   /api/simulations/<id>/share         # Criar link de compartilhamento
GET    /api/share/sim/<token>              # Acesso público
DELETE /api/simulations/shares/<id>        # Revogar compartilhamento

# Educação
GET    /api/educational/articles           # Artigos educacionais
GET    /api/educational/glossary           # Glossário de termos
```

#### Novos Models

```python
class Simulation(Base):
    __tablename__ = 'simulations'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    simulation_type = Column(Enum('goal', 'time', 'future'), nullable=False)

    # Parâmetros (JSON flexível)
    parameters = Column(JSON, nullable=False)
    # Exemplo:
    # {
    #   "goal_amount": 100000,
    #   "initial_amount": 10000,
    #   "months": 60,
    #   "annual_rate": 10.0
    # }

    # Resultados (JSON)
    results = Column(JSON, nullable=False)
    # Exemplo:
    # {
    #   "monthly_contribution": 1200.00,
    #   "total_invested": 82000.00,
    #   "total_interest": 18000.00,
    #   "final_amount": 100000.00
    # }

    # Metadados
    tags = Column(ARRAY(String(30)))  # PostgreSQL
    view_count = Column(Integer, default=0)
    version = Column(Integer, default=1)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime)  # Soft delete

    # Relacionamentos
    user = relationship('User', back_populates='simulations')
    plans = relationship('FinancialPlan', back_populates='simulation')
    shares = relationship('SimulationShare', back_populates='simulation', cascade='all, delete-orphan')


class SimulationShare(Base):
    __tablename__ = 'simulation_shares'

    id = Column(Integer, primary_key=True)
    simulation_id = Column(Integer, ForeignKey('simulations.id'), nullable=False)
    share_token = Column(String(64), unique=True, nullable=False, index=True)

    expires_at = Column(DateTime)
    allow_copy = Column(Boolean, default=True)
    view_count = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    simulation = relationship('Simulation', back_populates='shares')


class EducationalArticle(Base):
    __tablename__ = 'educational_articles'

    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    slug = Column(String(200), unique=True, nullable=False)
    content = Column(Text, nullable=False)
    summary = Column(String(500))

    # Metadados
    category = Column(String(50))  # 'investing', 'planning', 'basics'
    tags = Column(ARRAY(String(30)))
    reading_time_minutes = Column(Integer)
    difficulty_level = Column(Enum('beginner', 'intermediate', 'advanced'))

    # Associações
    related_simulation_types = Column(ARRAY(String(20)))
    # ['goal', 'time', 'future']

    published_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
```

#### Alterações em Models Existentes

```python
class FinancialPlan(Base):
    # ... campos existentes ...

    # Novo campo
    simulation_id = Column(Integer, ForeignKey('simulations.id'))
    created_from_simulation = Column(Boolean, default=False)

    # Novo relacionamento
    simulation = relationship('Simulation', back_populates='plans')
```

### Frontend (React)

#### Novos Componentes

```javascript
// Componentes principais
src/components/simulators/
├── SimulationHistory.jsx          // Lista de simulações salvas
├── SimulationDetail.jsx           // Detalhes de simulação
├── SimulationCompare.jsx          // Comparação lado a lado
├── SensitivityAnalysis.jsx        // Análise "E se?"
├── SimulationChart.jsx            // Gráfico de evolução
├── CompositionChart.jsx           // Pizza Principal vs Juros
├── DetailedTable.jsx              // Tabela mês a mês
├── CreatePlanFromSim.jsx          // Modal criar plano
├── PlanVsSimulation.jsx           // Dashboard comparativo
├── EducationalTooltip.jsx         // Tooltip educacional
├── Rule72Calculator.jsx           // Mini calculadora
├── ArticleSuggestions.jsx         // Artigos relacionados
├── ExportModal.jsx                // Modal de exportação
└── ShareModal.jsx                 // Modal de compartilhamento

// Páginas
src/pages/
├── Simulators.jsx (existente - atualizar)
├── SimulationHistory.jsx (novo)
├── SimulationDetail.jsx (novo)
└── PublicSimulation.jsx (novo - acesso via share link)
```

#### Bibliotecas Necessárias

```json
{
  "dependencies": {
    "recharts": "^2.10.0",           // Gráficos
    "react-chartjs-2": "^5.2.0",     // Alternativa
    "jspdf": "^2.5.1",               // PDF client-side
    "xlsx": "^0.18.5",               // Excel client-side
    "qrcode.react": "^3.1.0",        // QR codes
    "react-tooltip": "^5.25.0",      // Tooltips
    "framer-motion": "^10.16.0"      // Animações
  }
}
```

### Banco de Dados

#### Migrations

```sql
-- Migration: create_simulations_tables.sql

CREATE TABLE simulations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    simulation_type VARCHAR(20) NOT NULL CHECK (simulation_type IN ('goal', 'time', 'future')),
    parameters JSONB NOT NULL,
    results JSONB NOT NULL,
    tags VARCHAR(30)[],
    view_count INTEGER DEFAULT 0,
    version INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    deleted_at TIMESTAMP
);

CREATE INDEX idx_simulations_user_id ON simulations(user_id);
CREATE INDEX idx_simulations_type ON simulations(simulation_type);
CREATE INDEX idx_simulations_deleted_at ON simulations(deleted_at);

CREATE TABLE simulation_shares (
    id SERIAL PRIMARY KEY,
    simulation_id INTEGER NOT NULL REFERENCES simulations(id) ON DELETE CASCADE,
    share_token VARCHAR(64) UNIQUE NOT NULL,
    expires_at TIMESTAMP,
    allow_copy BOOLEAN DEFAULT TRUE,
    view_count INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_shares_token ON simulation_shares(share_token);
CREATE INDEX idx_shares_simulation_id ON simulation_shares(simulation_id);

CREATE TABLE educational_articles (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    slug VARCHAR(200) UNIQUE NOT NULL,
    content TEXT NOT NULL,
    summary VARCHAR(500),
    category VARCHAR(50),
    tags VARCHAR(30)[],
    reading_time_minutes INTEGER,
    difficulty_level VARCHAR(20) CHECK (difficulty_level IN ('beginner', 'intermediate', 'advanced')),
    related_simulation_types VARCHAR(20)[],
    published_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE INDEX idx_articles_slug ON educational_articles(slug);
CREATE INDEX idx_articles_category ON educational_articles(category);

-- Adicionar coluna em financial_plans
ALTER TABLE financial_plans ADD COLUMN simulation_id INTEGER REFERENCES simulations(id);
ALTER TABLE financial_plans ADD COLUMN created_from_simulation BOOLEAN DEFAULT FALSE;
```

---

## DIAGRAMA DE RELACIONAMENTOS

```
┌──────────────────────────────────────────────────────────────┐
│                    MÓDULO SIMULADORES V2                     │
└──────────────────────────────────────────────────────────────┘
                                │
                ┌───────────────┴───────────────┐
                │                               │
         ┌──────▼──────┐                 ┌──────▼──────┐
         │ SIMULATORS  │                 │   HISTORY   │
         │   (Calc)    │                 │   (CRUD)    │
         └──────┬──────┘                 └──────┬──────┘
                │                               │
                ├───────────────┬───────────────┤
                │               │               │
         ┌──────▼──────┐ ┌─────▼─────┐ ┌───────▼────────┐
         │  ANALYSIS   │ │  VISUALS  │ │  INTEGRATION  │
         │ Sensitivity │ │  Charts   │ │  with Plans   │
         │  Scenarios  │ │  Tables   │ │               │
         └──────┬──────┘ └─────┬─────┘ └───────┬────────┘
                │               │               │
                └───────────────┴───────────────┘
                                │
                ┌───────────────┴───────────────┐
                │                               │
         ┌──────▼──────┐                 ┌──────▼──────┐
         │  EDUCATION  │                 │   EXPORT    │
         │  Tooltips   │                 │  PDF/Excel  │
         │  Articles   │                 │   Share     │
         └─────────────┘                 └─────────────┘

DATABASE SCHEMA:

┌─────────────┐         ┌──────────────────┐         ┌────────────────┐
│    User     │────────<│   Simulation     │>────────│  FinancialPlan │
│             │ 1    N  │                  │ 1    N  │                │
│ - id        │         │ - id             │         │ - id           │
│ - email     │         │ - user_id (FK)   │         │ - simulation_id│
└─────────────┘         │ - name           │         │ - goal_amount  │
                        │ - type           │         └────────────────┘
                        │ - parameters     │
                        │ - results        │
                        │ - tags           │
                        └────────┬─────────┘
                                 │ 1
                                 │
                                 │ N
                        ┌────────▼─────────┐
                        │ SimulationShare  │
                        │                  │
                        │ - simulation_id  │
                        │ - share_token    │
                        │ - expires_at     │
                        │ - allow_copy     │
                        └──────────────────┘

FLUXO DE DADOS:

[Usuário]
    │
    ▼
[Calcula Simulação] ──────────> [Resultados Voláteis]
    │                                   │
    │ Salvar?                           │
    ▼                                   │
[POST /api/simulations] ───────────────┘
    │
    ▼
[Banco: simulations] <──────> [GET /api/simulations]
    │                                   │
    │                                   ▼
    │                         [SimulationHistory.jsx]
    │                                   │
    │                         ┌─────────┴─────────┐
    │                         │                   │
    │                         ▼                   ▼
    │                   [Editar/Ver]        [Comparar]
    │                         │                   │
    │                         ▼                   ▼
    │                 [Análise Sensib.]    [2-4 Sims]
    │                         │                   │
    │                         └─────────┬─────────┘
    │                                   │
    │                                   ▼
    │                          [Criar Plano]
    │                                   │
    ▼                                   ▼
[Vincular] ──────────────────> [FinancialPlan.simulation_id]
                                        │
                                        ▼
                               [Simulado vs Real]
```

---

## PRIORIZAÇÃO DE IMPLEMENTAÇÃO

### Fase 1 - Persistência Básica (Sprint 1-2 semanas)
**Objetivo:** Salvar e gerenciar simulações

- ✅ UC-M7A-001: Salvar Simulação
- ✅ UC-M7A-002: Consultar Histórico
- ✅ UC-M7A-003: Visualizar Detalhes
- ✅ UC-M7A-004: Editar Simulação
- ✅ UC-M7A-005: Deletar Simulação

**Entregas:**
- Modelo `Simulation` + migrations
- CRUD completo no backend
- Componentes History + Detail no frontend
- Testes unitários

---

### Fase 2 - Visualizações (Sprint 2-3 semanas)
**Objetivo:** Gráficos e tabelas interativas

- ✅ UC-M7B-001: Gráfico de Evolução
- ✅ UC-M7B-002: Gráfico de Composição
- ✅ UC-M7B-003: Tabela Detalhada

**Entregas:**
- Integração Recharts
- Componentes de gráficos reutilizáveis
- Responsividade mobile
- Export de gráficos (PNG)

---

### Fase 3 - Integração com Planos (Sprint 3-2 semanas)
**Objetivo:** Conectar simulações a planos reais

- ✅ UC-M7D-001: Criar Plano a partir de Simulação
- ✅ UC-M7D-002: Vincular Plano Existente
- ✅ UC-M7D-003: Comparar Simulado vs Real

**Entregas:**
- Campo `simulation_id` em `financial_plans`
- Modal de criação de plano pré-preenchido
- Dashboard comparativo
- Sugestões de ação corretiva

---

### Fase 4 - Análise de Cenários (Sprint 4-2 semanas)
**Objetivo:** Análise "E se?" e comparações

- ✅ UC-M7C-001: Análise de Sensibilidade
- ✅ UC-M7C-002: Comparar Múltiplas Simulações
- ✅ UC-M7C-003: Recomendação Automática

**Entregas:**
- Gerador de cenários
- Visualização de heatmap
- Algoritmo de recomendação
- Componente de comparação

---

### Fase 5 - Exportação (Sprint 5-1 semana)
**Objetivo:** Export PDF/Excel e compartilhamento

- ✅ UC-M7F-001: Exportar PDF
- ✅ UC-M7F-002: Exportar Excel
- ✅ UC-M7F-003: Compartilhar via Link

**Entregas:**
- Integração ReportLab (PDF)
- Integração openpyxl (Excel)
- Sistema de share tokens
- Página pública de simulações

---

### Fase 6 - Educação (Sprint 6-1 semana)
**Objetivo:** Conteúdo educacional contextual

- ✅ UC-M7E-001: Tooltips Educacionais
- ✅ UC-M7E-002: Calculadora Regra 72
- ✅ UC-M7E-003: Artigos Relacionados

**Entregas:**
- Biblioteca de tooltips
- Widgets educacionais
- Modelo `EducationalArticle`
- CMS básico para artigos

---

## MÉTRICAS DE SUCESSO

### KPIs Técnicos
- ✅ Tempo de salvamento de simulação: <500ms
- ✅ Tempo de geração de PDF: <3s
- ✅ Carregamento de histórico: <1s
- ✅ Renderização de gráficos: 60fps

### KPIs de Produto
- 📊 Taxa de salvamento de simulações: >40%
- 📊 Simulações salvas por usuário: média >3
- 📊 Taxa de conversão Simulação → Plano: >25%
- 📊 Uso de análise de sensibilidade: >15%
- 📊 Taxa de compartilhamento: >5%

### KPIs de Educação
- 📚 Cliques em tooltips: >30% dos usuários
- 📚 Leitura de artigos: >10% dos usuários
- 📚 Tempo médio em conteúdo educacional: >2min

---

## GLOSSÁRIO

**Simulação:** Cálculo projetivo de cenário financeiro futuro

**Sensibilidade:** Análise de como variações de parâmetros afetam resultado

**Cenário:** Conjunto específico de parâmetros e resultado correspondente

**Persistência:** Salvamento permanente de dados no banco

**Soft Delete:** Marcação de registro como deletado sem remoção física

**Snapshot:** Cópia congelada de dados em determinado momento

**Heatmap:** Mapa de calor mostrando variações com cores

**ROI:** Return on Investment (retorno sobre investimento)

**Regra 72:** Fórmula aproximada: Anos para dobrar = 72 ÷ Taxa

**Share Token:** Identificador único para compartilhamento público

---

**Documento criado em:** 23/12/2025
**Versão:** 2.0
**Autor:** Sistema de Análise de Requisitos - Flow Forecaster
**Status:** Pronto para aprovação e desenvolvimento
**Próximo passo:** Iniciar Fase 1 - Persistência Básica
