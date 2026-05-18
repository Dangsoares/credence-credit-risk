# Métricas do Dashboard — CREDENCE

Documento operacional para montar o dashboard no Looker Studio a partir de
`exports/looker_ready.csv`.

## Regras base

### Definição de inadimplência

Usar `default_flag` como regra principal:

| Valor | Interpretação |
|-------|---------------|
| `1` | Inadimplente finalizado |
| `0` | Adimplente finalizado |
| `NULL` / vazio | Em andamento, sem desfecho final |

Regra:
- Inadimplente: `loan_status IN ('Charged Off', 'Default', 'Does not meet the credit policy. Status:Charged Off')`
- Adimplente: `loan_status IN ('Fully Paid', 'Does not meet the credit policy. Status:Fully Paid')`
- Em andamento: `Current`, `In Grace Period`, `Late (16-30 days)`, `Late (31-120 days)`, `Issued`

Para análise alternativa, usar `default_flag_alt`, que considera `Late (31-120 days)` como
inadimplência.

### Regra crítica

Não tratar contratos em andamento como `0`. Eles não são adimplentes; eles ainda não têm
desfecho final. Para taxas de inadimplência estritas, usar apenas linhas em que
`status_finalizado = 1`.

## Campos calculados recomendados no Looker

### Taxa de inadimplência estrita

Usar como métrica:

```sql
AVG(default_flag)
```

Condição recomendada:

```sql
status_finalizado = 1
```

### Taxa de inadimplência alternativa

Usar quando o painel precisar incluir `Late (31-120 days)` como inadimplência:

```sql
AVG(default_flag_alt)
```

### Volume de contratos

```sql
COUNT(loan_amnt)
```

### Valor total concedido

```sql
SUM(loan_amnt)
```

### Valor total inadimplente

Regra estrita:

```sql
SUM(CASE WHEN default_flag = 1 THEN loan_amnt ELSE 0 END)
```

Regra alternativa:

```sql
SUM(CASE WHEN default_flag_alt = 1 THEN loan_amnt ELSE 0 END)
```

### Ticket médio

```sql
AVG(loan_amnt)
```

### Taxa média de juros

```sql
AVG(int_rate)
```

### Renda média

```sql
AVG(annual_inc)
```

### DTI médio

```sql
AVG(dti)
```

					

## Página 2 — Risco e Inadimplência

Objetivo: entender onde está o problema.

| Bloco | Visual | Dimensão | Métrica | Condição / Observação |
|-------|--------|----------|---------|-----------------------|
| Default rate por grade | Barras | `grade` | `AVG(default_flag)` | Filtrar `status_finalizado = 1`; ordenar por `grade` A-G |
| Default rate por purpose | Barras | `purpose` | `AVG(default_flag)` | Filtrar `status_finalizado = 1`; exibir também `COUNT(loan_amnt)` |
| Default rate por prazo | Barras | `term` | `AVG(default_flag)` | Filtrar `status_finalizado = 1`; prazo está em meses |
| Default rate por estado | Mapa ou tabela | `addr_state` | `AVG(default_flag)` | Filtrar `status_finalizado = 1`; sinalizar baixo volume |
| Evolução da inadimplência | Linha temporal | `issue_year`, `issue_month` | `AVG(default_flag)` | Filtrar `status_finalizado = 1`; usar por safra de originação |

### Campos de apoio para Página 2

| Uso | Coluna |
|-----|--------|
| Risco de crédito | `grade`, `sub_grade`, `grade_group` |
| Finalidade | `purpose` |
| Prazo | `term` |
| Geografia | `addr_state`, `geo_tier` |
| Tempo | `issue_year`, `issue_month` |
| Inadimplência | `default_flag`, `default_flag_alt`, `desfecho_credito`, `status_finalizado` |

### Condição de qualidade

Evitar interpretar segmentos com pouco volume. Regra recomendada:

```sql
COUNT(loan_amnt) >= 100
```

Para estado, usar preferencialmente:

```sql
COUNT(loan_amnt) >= 500
```

## Página 3 — Self-Service Explorer

Objetivo: permitir exploração pelos usuários.

| Bloco | Visual | Colunas | Métrica | Condição / Observação |
|-------|--------|---------|---------|-----------------------|
| Filtros interativos | Controles | `issue_year`, `grade`, `term`, `purpose`, `addr_state`, `income_bucket`, `dti_bucket`, `geo_tier`, `desfecho_credito` | Não se aplica | Usar como filtros globais da página |
| Tabela detalhada por segmento | Tabela dinâmica | `grade`, `term`, `purpose`, `dti_bucket`, `income_bucket`, `addr_state` | `COUNT(loan_amnt)`, `SUM(loan_amnt)`, `AVG(default_flag)`, `AVG(int_rate)` | Filtrar `status_finalizado = 1` para taxa de default |
| Matriz volume x risco | Dispersão ou tabela | Segmento escolhido, `loan_amnt`, `default_flag` | X = `COUNT(loan_amnt)` ou `SUM(loan_amnt)`; Y = `AVG(default_flag)` | Tamanho da bolha pode ser `SUM(loan_amnt)` |
| Ranking de segmentos críticos | Tabela ordenada | `grade`, `term`, `purpose`, `dti_bucket`, `addr_state` | `AVG(default_flag)`, `COUNT(loan_amnt)`, `SUM(loan_amnt)` | Ordenar por taxa de inadimplência ou valor inadimplente |
| Campo de busca ou drill-down | Filtro/text search | `purpose`, `addr_state`, `grade`, `sub_grade`, `loan_status` | Não se aplica | Permite navegação por segmento |

### Ranking de segmentos críticos

Campos recomendados:

| Coluna | Função |
|--------|--------|
| `grade` | Risco base |
| `term` | Prazo |
| `purpose` | Finalidade |
| `dti_bucket` | Faixa de comprometimento de renda |
| `income_bucket` | Faixa de renda |
| `addr_state` | Estado |
| `geo_tier` | Risco geográfico |

Métricas recomendadas:

| Métrica | Cálculo |
|---------|---------|
| Volume de contratos | `COUNT(loan_amnt)` |
| Valor originado | `SUM(loan_amnt)` |
| Taxa de inadimplência | `AVG(default_flag)` com `status_finalizado = 1` |
| Valor inadimplente | `SUM(CASE WHEN default_flag = 1 THEN loan_amnt ELSE 0 END)` |
| Taxa média de juros | `AVG(int_rate)` |
| DTI médio | `AVG(dti)` |

Condição mínima:

```sql
COUNT(loan_amnt) >= 100
```

## Checklist de implementação

- Usar `exports/looker_ready.csv` como fonte do dashboard.
- Usar `default_flag` para inadimplência principal.
- Usar `status_finalizado = 1` sempre que calcular taxa de inadimplência estrita.
- Usar `default_flag_alt` apenas quando a análise quiser incluir `Late (31-120 days)`.
- Exibir volume `COUNT(loan_amnt)` junto de qualquer taxa.
- Sinalizar ou ocultar segmentos com baixo volume.
- Não preencher `default_flag` vazio com zero.
