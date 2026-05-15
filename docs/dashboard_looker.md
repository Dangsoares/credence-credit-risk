# Dashboard Looker Studio — Especificação

Parte 1 do CREDENCE. Este documento especifica o dashboard a ser construído no
Looker Studio a partir de `exports/looker_ready.csv`.

## Fonte de dados

- **Arquivo:** `exports/looker_ready.csv` (gerado pela Seção 8 do notebook)
- **Conector:** File Upload (ou Google Sheets / BigQuery se o arquivo exceder 100 MB)
- **Granularidade:** 1 linha = 1 empréstimo

### Colunas disponíveis

| Coluna | Uso no dashboard |
|--------|------------------|
| `default_flag` | Definição **estrita** de inadimplência (Charged Off + Default) |
| `default_flag_alt` | Definição **alternativa** (inclui Late 31-120 days) |
| `grade`, `sub_grade` | Dimensão de risco |
| `purpose` | Finalidade do empréstimo |
| `term` | Prazo (36 / 60) |
| `addr_state` | Mapa geográfico |
| `grade_group` | D+E vs Demais |
| `dti_bucket` | Faixa de DTI |
| `income_bucket` | Faixa de renda |
| `geo_tier` | Nível de risco geográfico (HIGH/MED/LOW) |
| `verif_tier` | Verificação de renda (VERIFIED/NOT_VERIFIED) |
| `loan_amnt`, `int_rate`, `annual_inc`, `dti` | Métricas contínuas |
| `issue_year`, `issue_month` | Série temporal |

## Parâmetro self-service: definição de inadimplência

Criar um **parâmetro** (`Adicionar parâmetro`) chamado `def_inadimplencia`:

- Tipo: lista de seleção
- Valores: `Estrita` (default) | `Inclui Late 31-120`
- Campo calculado `taxa_default`:
  ```
  CASE WHEN def_inadimplencia = "Estrita"
       THEN default_flag
       ELSE default_flag_alt END
  ```
- Todos os gráficos usam `AVG(taxa_default)` como métrica de inadimplência, de modo que
  o gestor alterna a definição e o dashboard inteiro recalcula.

## Métrica padrão: sempre exibir N

Regra do CLAUDE.md: toda taxa vem acompanhada do N absoluto. Criar campo calculado
`rotulo_taxa`:
```
CONCAT(ROUND(AVG(taxa_default)*100,1), "% (N=", COUNT(loan_amnt), ")")
```
Usar como rótulo de dados nos gráficos de barras.

## Estrutura — 4 páginas

### Página 1 — Visão Geral da Carteira
- **Scorecard:** taxa de inadimplência geral + N total
- **Série temporal:** inadimplência por `issue_year` (linha) + volume (barra)
- **Barras:** taxa por `grade` — com `rotulo_taxa`
- **Barras:** taxa por `purpose` — destacar `small_business` / `renewable_energy`
- **Filtros:** `issue_year`, `term`, `grade`

### Página 2 — Mapa de Risco Geográfico
- **Mapa preenchido (Geo chart):** `addr_state` colorido por taxa de inadimplência
- **Tabela:** estados ordenados por taxa, com N e `geo_tier`
- **Barras:** taxa por `geo_tier` (HIGH/MED/LOW)
- Nota de rodapé: estados com N < 500 sinalizados (baixa confiabilidade)

### Página 3 — Renda, Verificação e Combinações Tóxicas
- **Heatmap (tabela com gradiente):** `income_bucket` × `verif_tier`
- **Barras:** taxa por `dti_bucket`
- **Tabela dinâmica:** `grade` × `term` × `dti_bucket` — a combinação tóxica
- **Scatter:** `int_rate` vs taxa de inadimplência por `grade` (mostra subprecificação)

### Página 4 — Tese Central
- **Comparativo:** Grade C+60m+DTI>20 vs Grade A vs Grade F
- **Texto:** a tese do CREDENCE — "o grade é um proxy imperfeito de risco"
- Foco em comunicação executiva, não técnica

## Cuidados

- Filtrar `loan_status = 'Late (31-120 days)'` **fora** das páginas quando a definição
  estrita estiver ativa — esses registros só entram pela definição alternativa.
- Cores consistentes: verde = baixo risco, vermelho = alto risco, em todas as páginas.
- Não exibir taxa de segmento com N < 100 sem aviso visual.