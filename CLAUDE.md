# CREDENCE — Credit Risk Edge: Analytics, Intelligence

Teste técnico FinLend. Análise de risco de crédito usando Lending Club Loan Data (2007–2018).
Prazo: 4 dias. Três entregáveis: notebook Python, dashboard Looker Studio, documento de governança de IA.

## Estrutura do projeto

```
credence/
├── CLAUDE.md
├── data/
│   ├── raw/                  # CSV original do Kaggle (não commitar)
│   └── processed/            # CSVs tratados (exportados pelo notebook)
├── notebooks/
│   ├── credence_analise.ipynb          # versão canônica (markdowns PT, código EN)
│   ├── credence_analise_pt.ipynb       # versão 100% PT (variáveis e colunas traduzidas)
│   └── credence_analise_avancado.ipynb # versão avançada (survival, calibração, validação temporal)
├── docs/
│   ├── governanca_ia.md      # Parte 3 — validação do agente LLM
│   ├── decisoes.md           # Log de decisões analíticas
│   ├── dicionario_dados.md   # Dicionário PT-BR das colunas do dataset
│   ├── dashboard_looker.md   # Spec do dashboard (Parte 1)
│   ├── defesa_oral.md        # Defesa oral — domínio completo da versão avançada
│   ├── defesa_oral_analise_avancada.md  # Defesa oral — versão estendida
│   ├── defesa_slides.md      # Roteiro de slides da apresentação
│   └── defesa_cartao.md      # Cartão de defesa de 1 página
├── exports/
│   └── looker_ready.csv      # CSV limpo para o Looker Studio
└── assets/                   # Gráficos exportados se necessário
```

## Definições críticas — nunca desviar

### Target de inadimplência
- **Inadimplente:** loan_status IN ('Charged Off', 'Default')
- **Adimplente:** loan_status = 'Fully Paid'
- **Excluir da análise:** 'Current', 'In Grace Period', 'Late (16-30 days)', 'Late (31-120 days)', 'Issued'
- Late 31-120 fica disponível como definição alternativa no parâmetro self-service do Looker

### Colunas-chave (usar estas, ignorar as ~130 restantes)
loan_amnt, int_rate, grade, sub_grade, annual_inc, dti, purpose, term, home_ownership,
emp_length, verification_status, issue_d, loan_status, installment, addr_state, revol_util, total_acc

> **Nota:** `addr_state` e `verification_status` são fundamentais para as Seções 2.7, 2.8 e 6.4
> (mapa geográfico, segmentação por renda × verificação, combinação tóxica multi-dim).
> Ver `docs/dicionario_dados.md` para descrições completas de todas as colunas.

## Stack e convenções

### Python
- Python 3.10+
- Notebook .ipynb com markdown narrativo entre cada bloco de código
- Cada seção do notebook começa com markdown explicando o "porquê" antes do código

### Três versões do notebook
- `credence_analise.ipynb` — **versão canônica**. Markdowns em PT, nomes de variáveis/funções
  em inglês (convenção padrão de engenharia). É a versão a manter quando houver mudanças.
- `credence_analise_pt.ipynb` — **versão 100% PT**. Variáveis, funções e colunas do DataFrame
  traduzidas. Mantém em inglês apenas `grade`/`sub_grade`/`dti` (jargão consagrado) e os
  valores de dados do CSV. Renomeia as colunas via `MAPA_COLUNAS` logo após o load.
- `credence_analise_avancado.ipynb` — **versão avançada**. Cópia completa da canônica + quatro
  técnicas de modelagem de nível comitê (ver seção abaixo). É uma extensão exploratória, não a
  análise oficial.

> Ao alterar a análise **canônica**, replicar a mudança na versão 100% PT. A versão avançada é
> uma extensão independente — não precisa ser replicada a cada mudança do canônico, mas se o
> tratamento de dados base mudar, propagar também para ela.

### requirements.txt (gerar este arquivo na raiz do projeto)

```txt
# CREDENCE — dependências com versões pinadas
# Instalar: pip install -r requirements.txt

# Core data
pandas==2.2.3
numpy==2.2.6
openpyxl==3.1.5

# Estatística e modelagem
scipy==1.15.3
statsmodels==0.14.6
scikit-learn==1.8.0

# Visualização
matplotlib==3.10.9
seaborn==0.13.2
plotly==6.7.0

# Jupyter
jupyter==1.1.1
nbformat==5.10.4
nbconvert==7.16.6
ipykernel==6.29.5

# Utilitários
missingno==0.5.2
```

> **Por que pinar versões estáveis e não latest?** pandas 3.x introduziu breaking changes
> (ex: `inplace` deprecations, copy-on-write como default). O 2.2.3 é a última release estável
> da série 2.x — madura, sem surpresas, compatível com todo o ecossistema.
> numpy 2.2.6 é compatível com pandas 2.2.x e scipy 1.15.x sem conflitos.

### Setup rápido

```bash
# Criar ambiente virtual (recomendado)
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# Instalar dependências
pip install -r requirements.txt

# Registrar kernel do Jupyter
python -m ipykernel install --user --name credence --display-name "CREDENCE"

# Verificar instalação
python -c "import pandas; import scipy; import sklearn; print('✓ Stack OK')"
```
- Visualizações: usar seaborn para estáticos, plotly para interativos
- Estilo: português nos markdowns, inglês nos nomes de variáveis e funções

### Tratamentos padrão
- int_rate: remover "%" e converter para float se vier como string
- term: converter " 36 months" → 36 (int)
- emp_length: converter "10+ years" → 10, "< 1 year" → 0, NaN → NaN
- issue_d: converter para datetime, extrair ano e mês
- Criar coluna `default_flag`: 1 se inadimplente, 0 se adimplente
- Criar coluna `issue_year` e `issue_month` a partir de issue_d

## Estrutura do notebook (7 seções principais — seguir esta ordem)

1. **Contexto e setup** — imports, load, shape, definição de inadimplência com justificativa
2. **EDA** — distribuições por grade, purpose, term; perfil socioeconômico; evolução temporal
   - **2.7 Mapa de risco geográfico** — choropleth + decomposição Oaxaca por `addr_state`
     (separar efeito de composição vs residual geográfico; tratar como associação, não causalidade)
   - **2.8 Risco por faixa de renda × verificação** — testa se renda alta não-verificada
     performa pior que renda média verificada (efeito de superdeclaração)
3. **Teste de hipótese** — H₀: default rate D+E = demais; H₁: D+E > demais. Usar chi² e teste z de proporções. Reportar p-valor, IC 95%, effect size
4. **Decomposição** — separar efeito de mix (volume de D+E cresceu?) vs deterioração (taxa dentro de D+E piorou?)
5. **Regressão logística** — variável dependente: default_flag. Independentes: grade, dti, term, purpose, annual_inc. Interpretar via odds ratio, NÃO via métricas de ML. É ferramenta explicativa para associações controladas, não modelo final de produção; produção exigiria validação temporal, calibração, drift, estabilidade e fairness.
6. **Insight não-óbvio** — encontrar combinações tóxicas (ex: Grade C + 60 meses + DTI > 20 com default rate de Grade F). Vintage analysis se os dados permitirem
   - **6.4 Combinação tóxica multi-dimensional + simulação direcional de P&L** — score de 4 fatores
     (grade × term × dti × geo_tier; `verification_status` excluída por endogeneidade) e curva de otimização de corte com
     premissas documentadas (LGD, custo de funding). Não tratar como lucro real da carteira.
7. **Recomendação** — ações concretas para política de crédito. Linguagem de negócio, não técnica
   - Inclui considerações regulatórias (ECOA / Reg B) para recomendações que envolvem `addr_state`

## Estrutura do notebook avançado (`credence_analise_avancado.ipynb`)

Cópia completa da canônica (9 seções — as antigas 6/7/8 renumeradas para 7/8/9) com quatro
técnicas adicionais que respondem a lacunas que um avaliador sênior aponta sobre a regressão
logística:

- **5.4 Validação temporal** — treino 2007–2015 × teste 2016–2018; AUC e Brier nos dois
  recortes, medindo a degradação out-of-time.
- **5.5 Calibração probabilística** — diagrama de confiabilidade no teste, Brier score,
  recalibração isotônica como referência diagnóstica.
- **5.6 Efeitos marginais e elasticidade** — traduz odds ratios em pontos percentuais de
  probabilidade (AME), na linguagem de um comitê de crédito.
- **Seção 6 — Análise de sobrevivência** — Kaplan-Meier + log-rank, modelo de Cox de riscos
  proporcionais, vintage analysis via sobrevivência (horizonte comum).

> **`last_pymnt_d` na Seção 6 — não é violação da regra de leakage.** A coluna é LEAKAGE SEVERO
> *como feature preditiva* (ver alerta abaixo). Na análise de sobrevivência ela não é feature:
> deriva a **duração observada** (eixo do tempo do estudo). É o uso padrão e legítimo dela na
> literatura de risco de crédito — e está documentado como tal no notebook.

> **Limitação conhecida da Seção 6.4 (vintage via survival):** a base contém apenas loans com
> desfecho resolvido; para safras 2016–2018 isso gera viés de seleção. A leitura é confiável
> apenas para coortes maduras (≤ 2015). Ver `docs/decisoes.md`, decisão #13.

Suporte à apresentação: `docs/defesa_oral.md`, `docs/defesa_slides.md`, `docs/defesa_cartao.md`.

## Parte 3 — Governança de IA (docs/governanca_ia.md)

Usar a mesma base analítica oficial da Parte 2: período completo disponível (2007–2018),
mesma definição de inadimplência, mesma unidade de análise em nível de empréstimo e mesmas
regras de elegibilidade. A Parte 3 é auditoria determinística da resposta do LLM contra
ground truth, com avaliação qualitativa, score de confiança, ontologia simples, axiomas
de validação e proposta de Knowledge Graph como camada de AI Readiness.

### Resposta do agente a ser validada
O gestor perguntou: "Qual é o perfil de risco dos clientes que tomam empréstimos para consolidação de dívidas?"

Claims do agente para validar contra os dados:
- "48% da carteira total" → verificar df[df.purpose=='debt_consolidation'].shape[0] / len(df)
- "taxa de inadimplência de 12,3%" → verificar default_rate do segmento
- "abaixo da média geral de 14,1%" → verificar default_rate geral
- "ticket médio de 72.000" → verificar loan_amnt.mean() do segmento
- "renda média anual de 15.200" → verificar annual_inc.mean() do segmento
- "grades B e C (62%)" → verificar distribuição de grade no segmento
- "taxa de juros média de 13,8%" → verificar int_rate.mean() do segmento

### Taxonomia de erros (usar esta classificação)
| Tipo | Definição | Severidade |
|------|-----------|------------|
| Erro Factual | Número verificável que diverge dos dados | Média |
| Alucinação | Informação inventada sem base nos dados | Alta |
| Omissão Material | Fato relevante não mencionado | Média |
| Framing Enganoso | Número correto em contexto que induz erro | Alta |

### Framework de auditoria (6 etapas)
1. Captura — receber pergunta + resposta do agente
2. Extração — isolar cada claim numérico/qualitativo
3. Validação — query nos dados para cada claim
4. Classificação — tipo de erro + severidade
5. Registro — log com timestamp
6. Monitoramento — taxa de erro ao longo do tempo + trigger de reavaliação

## ⚠️ ALERTA CRÍTICO: Data Leakage e Classes Desbalanceadas

### Data Leakage — colunas que VAZAM o futuro

Estas colunas contêm informação que SÓ EXISTE DEPOIS que o loan já foi concedido.
Usar qualquer uma delas como feature num modelo é trapaça — o modelo "vê o futuro".
Na EDA descritiva, podem ser usadas para entender o dataset, mas NUNCA como input de regressão/classificação.

**LEAKAGE SEVERO (eliminar de qualquer modelo):**
- `total_pymnt` — total pago pelo borrower (se pagou tudo, é Fully Paid por definição)
- `total_pymnt_inv` — idem, porção paga aos investidores
- `total_rec_prncp` — principal recebido (correlação quase perfeita com loan_status)
- `total_rec_int` — juros recebidos
- `total_rec_late_fee` — taxas de atraso recebidas (só existe se atrasou)
- `recoveries` — valor recuperado após charge-off
- `collection_recovery_fee` — taxa de cobrança pós charge-off
- `last_pymnt_d` — data do último pagamento
- `last_pymnt_amnt` — valor do último pagamento
- `out_prncp` / `out_prncp_inv` — saldo devedor (se é zero, loan foi pago)
- `last_credit_pull_d` — última consulta de crédito pelo LC

**LEAKAGE MODERADO (colunas pós-originação):**
- `chargeoff_within_12_mths` — charge-offs em 12 meses (futuro)
- `collections_12_mths_ex_med` — cobranças em 12 meses
- `debt_settlement_flag` — se entrou em acordo de dívida
- `hardship_flag` e todas as colunas `hardship_*` — programa de hardship é posterior
- `settlement_*` — todas as colunas de settlement
- `payment_plan_start_date`
- `num_tl_120dpd_2m` / `num_tl_30dpd` — "updated in past 2 months"

**COLUNAS DE TEXTO SEM VALOR PREDITIVO (eliminar):**
- `url` — link interno do LC (requer login de investidor)
- `desc` — descrição livre do borrower (ruído)
- `emp_title` — cargo autodeclarado (alta cardinalidade, sem padronização)
- `title` — título do loan (redundante com `purpose`)
- `id` / `member_id` — identificadores (geralmente nulos)

**COLUNAS SEGURAS PARA MODELAGEM (disponíveis na originação):**
loan_amnt, term, int_rate, installment, grade, sub_grade, emp_length,
home_ownership, annual_inc, verification_status, issue_d, purpose,
addr_state, dti, delinq_2yrs, earliest_cr_line, fico_range_low,
fico_range_high, inq_last_6mths, open_acc, pub_rec, revol_bal,
revol_util, total_acc, application_type

> **REGRA DE OURO:** Pergunte "essa informação existia no momento em que o LC decidiu aprovar o loan?"
> Se a resposta for NÃO, a coluna é leakage.

### Classes Desbalanceadas — o dataset é ~80/20

O ratio típico do Lending Club é aproximadamente:
- **~80% Fully Paid** (adimplentes)
- **~20% Charged Off** (inadimplentes)

Quando se incluem Current/In Grace Period e depois se exclui, o desbalanceamento pode variar.

**Impacto no CREDENCE:**

1. **Na EDA e teste de hipótese (Partes 1 e 2):** desbalanceamento NÃO é problema.
   Estamos calculando taxas e proporções, não treinando classificador. Usar os dados como estão.

2. **Na regressão logística (Seção 5 do notebook):** o desbalanceamento deve ser declarado, mas não corrigido artificialmente.
   - A regressão logística é usada aqui para INTERPRETAR associações ajustadas (odds ratios), não para prever.
   - O notebook canônico usa `statsmodels.Logit` sem `class_weight` e sem pesos de amostra.
   - NÃO usar SMOTE, oversampling ou undersampling — não estamos otimizando AUC,
     estamos estimando odds ratios na população modelável observada.
   - Se o avaliador perguntar: "Reconhecemos o desbalanceamento de ~80/20. Na regressão
     inferencial em statsmodels, não aplicamos balanceamento de classe; reportamos o
     desbalanceamento como característica da amostra e interpretamos odds ratios ajustados."

3. **No dashboard Looker (Parte 1):** mostrar o N absoluto junto com as taxas.
   Uma taxa de 45% de default num segmento com N=12 não é a mesma coisa que
   uma taxa de 25% num segmento com N=50.000. O dashboard deve sempre mostrar
   "Taxa de default: X% (N = Y loans)" para evitar interpretações enganosas.

4. **Na validação da IA (Parte 3):** o agente LLM pode ter sido treinado sem
   consciência do desbalanceamento. Checar se os números citados fazem sentido
   dado o ratio real do dataset.

### Resumo visual rápido

```
COLUNAS DO DATASET:
├── 🟢 SEGURAS (originação)     → usar na análise e modelo
├── 🟡 LEAKAGE MODERADO         → eliminar de modelos, ok para contexto descritivo
├── 🔴 LEAKAGE SEVERO           → eliminar sempre (exceto se explorando o dataset)
└── ⚫ RUÍDO / SEM VALOR        → eliminar sempre
```

## Gotchas e avisos

- O dataset pode ter >800K linhas. Para o Looker, exportar versão filtrada (só Fully Paid + Charged Off + Default) ou amostra estratificada se necessário
- annual_inc tem outliers extremos (>$1M). Decidir se filtra ou winsoriza — documentar em decisoes.md
- Alguns registros têm loan_status = "Does not meet the credit policy. Status:Fully Paid" — tratar como Fully Paid
- "Does not meet the credit policy. Status:Charged Off" — tratar como Charged Off
- int_rate pode vir como string com "%" em algumas versões do dataset
- Não rodar o notebook inteiro sem checar memória — usar chunks se necessário

## Comandos úteis

```bash
# Rodar notebook completo
jupyter nbconvert --to notebook --execute credence_analise.ipynb

# Exportar para HTML (entrega)
jupyter nbconvert --to html credence_analise.ipynb

# Verificar tamanho do CSV
wc -l data/raw/loan.csv
```

## Premissas para análise de P&L (Seção 6.4)

O dataset não traz custo de funding nem LGD por loan. A Seção 6.4 é uma **simulação
direcional de rentabilidade risco-ajustada** para comparar segmentos, não uma apuração
de lucro real da carteira. Para essa simulação usamos premissas conservadoras e padrão
de mercado para *unsecured retail*:

| Parâmetro | Valor | Racional |
|-----------|-------|----------|
| LGD       | 60%   | Padrão Basileia para *unsecured retail*; literatura empírica em 55–65% |
| Custo de funding | 4% a.a. | Proxy do *cost of capital* de fintech P2P 2014–2018 |
| Duration  | `term / 24` anos | Aproximação de duration média (metade do prazo, amortização linear) |
| Fração de juros coletada em loans inadimplentes | 50% | Loan que vira charge-off para de pagar no meio — não recebe receita cheia |
| Receita | `spread × duration × loan_amnt × (1 se adimplente; 0,5 se inadimplente)` | Receita ajustada |
| Perda   | `default_flag × LGD × loan_amnt` | EL = PD × LGD × EAD |

> **Importante:** as premissas servem para *ranking relativo* — não projeção absoluta de P&L
> nem apuração de lucro real. A Seção 6.4 distingue **default rate alto** de **P&L estimado
> negativo**: combinações de alto default podem aparecer rentáveis na simulação se o juro
> compensa. "Tóxica" = P&L risco-ajustado estimado negativo, não default rate alto. Em
> produção, LGD, curva de recuperação, pré-pagamento, servicing, impostos, custos operacionais
> e custo de funding viriam de modelos próprios / ALM.

## Considerações regulatórias (Fair Lending — ECOA / Reg B)

Recomendações que envolvem `addr_state` devem respeitar regras de fair lending nos EUA:

- **Permitido:** *risk-based pricing* documentado, *caps de exposição* atuarialmente justificados,
  monitoramento de concentração geográfica.
- **Proibido:** *underwriting cutoff* individual baseado apenas em estado/região (caracteriza
  *disparate impact*), uso de variáveis proxy de raça/etnia.

A análise da Seção 2.7 usa decomposição Oaxaca-Blinder para estimar risco residual acima do
esperado dado o mix de grade. Tratar como sinal atuarial para monitoramento, pricing ou cap
de exposição, não como evidência causal de que o estado seja causa de inadimplência.

## Princípio guia

A tese central do CREDENCE: "O grade é um proxy imperfeito de risco. O principal padrão observado de default não está no grade isoladamente, mas na combinação de term longo + DTI elevado + purpose de alto risco. Dentro de Grade C, essa combinação pode atingir default rate comparável a Grade F."

Toda análise, visualização e recomendação deve orbitar em torno dessa tese — confirmando, refinando ou refutando.

## Régua de linguagem analítica

Evitar linguagem causal forte sem desenho causal, teste específico ou evidência apropriada.
Preferir:
- "está associado a";
- "é compatível com";
- "sugere";
- "contribui para";
- "aparece como principal vetor observado";
- "P&L estimado na simulação".

Evitar:
- "causou";
- "prova" / "comprova";
- "explica" em sentido causal;
- "driver real";
- "impacto" quando o correto for efeito estimado ou cenário simulado.
