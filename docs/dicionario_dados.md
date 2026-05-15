# Dicionário de Dados — Lending Club Loan Data

Tradução em português das descrições do `LCDataDictionary.xlsx` (aba `LoanStats`).
Os **nomes das colunas permanecem em inglês** (são as chaves usadas no CSV).

Cada linha traz também o **status de uso** segundo as regras do CREDENCE (ver `CLAUDE.md`):

| Símbolo | Significado |
|---------|-------------|
| 🟢 | Segura — disponível na originação, pode ser usada como feature de modelo |
| 🟡 | Leakage moderado — informação pós-originação; usar apenas em análise descritiva |
| 🔴 | Leakage severo — vaza o desfecho; **nunca** usar como feature |
| ⚫ | Ruído / sem valor preditivo (texto livre, identificadores, URLs) |
| 🎯 | Coluna-alvo (`loan_status`) ou derivada (`default_flag`) |
| 🤝 | Aplicação conjunta (joint) ou aplicante secundário — uso condicional |

---

## 1. Identificação e metadados

| Coluna | Descrição (PT-BR) | Status |
|--------|-------------------|--------|
| `id` | Identificador único do empréstimo atribuído pelo LC. | ⚫ |
| `member_id` | Identificador único do borrower atribuído pelo LC. | ⚫ |
| `url` | URL da página do LC com os dados da listagem (requer login de investidor). | ⚫ |
| `desc` | Descrição livre do empréstimo escrita pelo borrower. | ⚫ |
| `title` | Título do empréstimo fornecido pelo borrower (redundante com `purpose`). | ⚫ |
| `emp_title` | Cargo autodeclarado pelo borrower no momento da solicitação. | ⚫ |
| `policy_code` | `1` = produto público; `2` = produto não-público. | ⚫ |

## 2. Termos do empréstimo (originação)

| Coluna | Descrição (PT-BR) | Status |
|--------|-------------------|--------|
| `loan_amnt` | Valor do empréstimo solicitado pelo borrower (pode ser ajustado para baixo pelo crédito). | 🟢 |
| `funded_amnt` | Valor total comprometido com o empréstimo no momento. | 🟢 |
| `funded_amnt_inv` | Valor comprometido pelos investidores no momento. | 🟢 |
| `term` | Prazo do empréstimo em meses — `36` ou `60`. | 🟢 |
| `int_rate` | Taxa de juros do empréstimo (em % ao ano). | 🟢 |
| `installment` | Parcela mensal devida pelo borrower. | 🟢 |
| `grade` | Grade de risco atribuído pelo LC (`A`–`G`). | 🟢 |
| `sub_grade` | Sub-grade do LC (ex.: `B3`, `C5`). | 🟢 |
| `issue_d` | Mês em que o empréstimo foi liberado. | 🟢 |
| `purpose` | Categoria/finalidade do empréstimo declarada pelo borrower. | 🟢 |
| `application_type` | Indica se é aplicação individual ou conjunta (joint). | 🟢 |
| `initial_list_status` | Status inicial de listagem — `W` (whole) ou `F` (fractional). | 🟢 |
| `disbursement_method` | Forma de desembolso ao borrower — `CASH` ou `DIRECT_PAY`. | 🟢 |
| `pymnt_plan` | Indica se há plano de pagamento especial vigente para o empréstimo. | 🟡 |

## 3. Perfil socioeconômico do borrower

| Coluna | Descrição (PT-BR) | Status |
|--------|-------------------|--------|
| `annual_inc` | Renda anual autodeclarada pelo borrower no cadastro. | 🟢 |
| `verification_status` | Indica se a renda foi verificada pelo LC, não verificada, ou apenas a fonte foi verificada. | 🟢 |
| `emp_length` | Tempo de emprego em anos — `0` = menos de 1 ano, `10` = 10 anos ou mais. | 🟢 |
| `home_ownership` | Status de moradia — `RENT`, `OWN`, `MORTGAGE`, `OTHER`. | 🟢 |
| `addr_state` | Estado (UF) informado pelo borrower no formulário. | 🟢 |
| `zip_code` | Primeiros 3 dígitos do CEP informado pelo borrower. | 🟢 |
| `dti` | Razão dívida/renda — pagamentos mensais totais (excluindo hipoteca e o LC) ÷ renda mensal autodeclarada. | 🟢 |

## 4. Histórico de crédito (bureau, na originação)

| Coluna | Descrição (PT-BR) | Status |
|--------|-------------------|--------|
| `fico_range_low` | Limite inferior da faixa FICO do borrower na originação. | 🟢 |
| `fico_range_high` | Limite superior da faixa FICO do borrower na originação. | 🟢 |
| `earliest_cr_line` | Mês de abertura da linha de crédito mais antiga reportada. | 🟢 |
| `inq_last_6mths` | Nº de consultas de crédito nos últimos 6 meses (excluindo auto e hipoteca). | 🟢 |
| `inq_last_12m` | Nº de consultas de crédito nos últimos 12 meses. | 🟢 |
| `inq_fi` | Nº de consultas em finanças pessoais. | 🟢 |
| `open_acc` | Nº de linhas de crédito abertas no cadastro do borrower. | 🟢 |
| `total_acc` | Nº total de linhas de crédito no cadastro do borrower. | 🟢 |
| `pub_rec` | Nº de registros públicos depreciativos. | 🟢 |
| `pub_rec_bankruptcies` | Nº de falências em registros públicos. | 🟢 |
| `delinq_2yrs` | Nº de incidências de inadimplência (30+ dias) nos últimos 2 anos. | 🟢 |
| `delinq_amnt` | Valor em atraso devido nas contas atualmente inadimplentes. | 🟢 |
| `acc_now_delinq` | Nº de contas em que o borrower está atualmente inadimplente. | 🟢 |
| `mths_since_last_delinq` | Meses desde a última inadimplência do borrower. | 🟢 |
| `mths_since_last_major_derog` | Meses desde a última depreciação grave (90+ dias). | 🟢 |
| `mths_since_last_record` | Meses desde o último registro público. | 🟢 |
| `tax_liens` | Nº de penhoras fiscais (tax liens). | 🟢 |
| `revol_bal` | Saldo total em crédito rotativo. | 🟢 |
| `revol_util` | Utilização do crédito rotativo (% do limite total em uso). | 🟢 |

## 5. Detalhamento de contas (bureau, granular)

| Coluna | Descrição (PT-BR) | Status |
|--------|-------------------|--------|
| `acc_open_past_24mths` | Nº de contas (trades) abertas nos últimos 24 meses. | 🟢 |
| `avg_cur_bal` | Saldo médio atual de todas as contas. | 🟢 |
| `bc_open_to_buy` | Disponível total para compra em cartões rotativos. | 🟢 |
| `bc_util` | Razão saldo/limite em todas as contas de bankcard. | 🟢 |
| `mort_acc` | Nº de contas hipotecárias. | 🟢 |
| `mo_sin_old_il_acct` | Meses desde a abertura da conta de installment mais antiga. | 🟢 |
| `mo_sin_old_rev_tl_op` | Meses desde a abertura da conta rotativa mais antiga. | 🟢 |
| `mo_sin_rcnt_rev_tl_op` | Meses desde a abertura da conta rotativa mais recente. | 🟢 |
| `mo_sin_rcnt_tl` | Meses desde a abertura da conta mais recente (qualquer tipo). | 🟢 |
| `mths_since_recent_bc` | Meses desde a abertura da conta de bankcard mais recente. | 🟢 |
| `mths_since_recent_bc_dlq` | Meses desde a inadimplência mais recente em bankcard. | 🟢 |
| `mths_since_recent_inq` | Meses desde a consulta de crédito mais recente. | 🟢 |
| `mths_since_recent_revol_delinq` | Meses desde a inadimplência mais recente em conta rotativa. | 🟢 |
| `mths_since_rcnt_il` | Meses desde a abertura da conta de installment mais recente. | 🟢 |
| `num_accts_ever_120_pd` | Nº de contas que já estiveram 120+ dias em atraso. | 🟢 |
| `num_actv_bc_tl` | Nº de contas de bankcard atualmente ativas. | 🟢 |
| `num_actv_rev_tl` | Nº de trades rotativos atualmente ativos. | 🟢 |
| `num_bc_sats` | Nº de contas de bankcard em situação satisfatória. | 🟢 |
| `num_bc_tl` | Nº total de contas de bankcard. | 🟢 |
| `num_il_tl` | Nº de contas de installment. | 🟢 |
| `num_op_rev_tl` | Nº de contas rotativas abertas. | 🟢 |
| `num_rev_accts` | Nº de contas rotativas. | 🟢 |
| `num_rev_tl_bal_gt_0` | Nº de trades rotativos com saldo > 0. | 🟢 |
| `num_sats` | Nº de contas em situação satisfatória. | 🟢 |
| `num_tl_90g_dpd_24m` | Nº de contas com 90+ dias de atraso nos últimos 24 meses. | 🟢 |
| `num_tl_op_past_12m` | Nº de contas abertas nos últimos 12 meses. | 🟢 |
| `num_tl_120dpd_2m` | Nº de contas com 120 dias de atraso (atualizado nos últimos 2 meses). | 🟡 |
| `num_tl_30dpd` | Nº de contas com 30 dias de atraso (atualizado nos últimos 2 meses). | 🟡 |
| `open_acc_6m` | Nº de trades abertos nos últimos 6 meses. | 🟢 |
| `open_il_12m` | Nº de contas de installment abertas nos últimos 12 meses. | 🟢 |
| `open_il_24m` | Nº de contas de installment abertas nos últimos 24 meses. | 🟢 |
| `open_act_il` | Nº de trades de installment atualmente ativos. | 🟢 |
| `open_rv_12m` | Nº de trades rotativos abertos nos últimos 12 meses. | 🟢 |
| `open_rv_24m` | Nº de trades rotativos abertos nos últimos 24 meses. | 🟢 |
| `pct_tl_nvr_dlq` | % de trades que nunca ficaram inadimplentes. | 🟢 |
| `percent_bc_gt_75` | % de contas de bankcard com utilização acima de 75% do limite. | 🟢 |
| `tot_coll_amt` | Valor total já enviado para cobrança. | 🟢 |
| `tot_cur_bal` | Saldo atual total em todas as contas. | 🟢 |
| `tot_hi_cred_lim` | Limite total alto de crédito. | 🟢 |
| `total_bal_ex_mort` | Saldo total em crédito excluindo hipoteca. | 🟢 |
| `total_bal_il` | Saldo atual total em todas as contas de installment. | 🟢 |
| `total_bc_limit` | Limite total alto em bankcard. | 🟢 |
| `total_cu_tl` | Nº de finance trades. | 🟢 |
| `total_il_high_credit_limit` | Limite total alto em installment. | 🟢 |
| `total_rev_hi_lim` | Limite total alto em crédito rotativo. | 🟢 |
| `max_bal_bc` | Saldo atual máximo em todas as contas rotativas. | 🟢 |
| `all_util` | Razão saldo/limite em todos os trades. | 🟢 |
| `il_util` | Razão saldo/limite nas contas de installment. | 🟢 |

## 6. Status do empréstimo (alvo e variáveis pós-originação)

| Coluna | Descrição (PT-BR) | Status |
|--------|-------------------|--------|
| `loan_status` | Status atual do empréstimo (`Fully Paid`, `Charged Off`, `Default`, `Current`, `Late ...`, etc.). | 🎯 |
| `out_prncp` | Saldo principal remanescente para o valor total financiado. | 🔴 |
| `out_prncp_inv` | Saldo principal remanescente da porção financiada por investidores. | 🔴 |
| `total_pymnt` | Pagamentos recebidos até o momento (valor total financiado). | 🔴 |
| `total_pymnt_inv` | Pagamentos recebidos até o momento (porção dos investidores). | 🔴 |
| `total_rec_prncp` | Principal recebido até o momento. | 🔴 |
| `total_rec_int` | Juros recebidos até o momento. | 🔴 |
| `total_rec_late_fee` | Taxas de atraso recebidas até o momento. | 🔴 |
| `recoveries` | Recuperação bruta após charge-off. | 🔴 |
| `collection_recovery_fee` | Taxa de cobrança pós charge-off. | 🔴 |
| `last_pymnt_d` | Mês do último pagamento recebido. | 🔴 |
| `last_pymnt_amnt` | Valor do último pagamento recebido. | 🔴 |
| `next_pymnt_d` | Data do próximo pagamento agendado. | 🔴 |
| `last_credit_pull_d` | Mês mais recente em que o LC consultou crédito para este empréstimo. | 🔴 |
| `last_fico_range_high` | Limite superior da faixa FICO da última consulta. | 🔴 |
| `last_fico_range_low` | Limite inferior da faixa FICO da última consulta. | 🔴 |
| `chargeoff_within_12_mths` | Nº de charge-offs nos últimos 12 meses. | 🟡 |
| `collections_12_mths_ex_med` | Nº de cobranças nos últimos 12 meses (excluindo médicas). | 🟡 |

## 7. Hardship (programa de dificuldades) — todas pós-originação

| Coluna | Descrição (PT-BR) | Status |
|--------|-------------------|--------|
| `hardship_flag` | Indica se o borrower está em plano de hardship. | 🔴 |
| `hardship_type` | Tipo do plano de hardship oferecido. | 🔴 |
| `hardship_reason` | Motivo pelo qual o plano foi oferecido. | 🔴 |
| `hardship_status` | Status do plano (active, pending, canceled, completed, broken). | 🔴 |
| `deferral_term` | Meses em que o borrower pagará menos que a parcela contratual. | 🔴 |
| `hardship_amount` | Valor de juros que o borrower se comprometeu a pagar mensalmente no plano. | 🔴 |
| `hardship_start_date` | Data de início do plano de hardship. | 🔴 |
| `hardship_end_date` | Data de término do plano de hardship. | 🔴 |
| `payment_plan_start_date` | Dia em que o primeiro pagamento do plano é devido. | 🔴 |
| `hardship_length` | Nº de meses em que o borrower fará pagamentos reduzidos. | 🔴 |
| `hardship_dpd` | Dias de atraso da conta na data de início do hardship. | 🔴 |
| `hardship_loan_status` | Status do empréstimo na data de início do hardship. | 🔴 |
| `orig_projected_additional_accrued_interest` | Juros adicionais projetados originalmente para o plano (null se quebrado). | 🔴 |
| `hardship_payoff_balance_amount` | Saldo de quitação na data de início do hardship. | 🔴 |
| `hardship_last_payment_amount` | Valor do último pagamento na data de início do hardship. | 🔴 |

## 8. Settlement (acordo de dívida) — todas pós-originação

| Coluna | Descrição (PT-BR) | Status |
|--------|-------------------|--------|
| `debt_settlement_flag` | Indica se o borrower (em charge-off) está negociando com empresa de settlement. | 🔴 |
| `debt_settlement_flag_date` | Data mais recente em que `debt_settlement_flag` foi marcado. | 🔴 |
| `settlement_status` | Status do plano de settlement (`COMPLETE`, `ACTIVE`, `BROKEN`, `CANCELLED`, `DENIED`, `DRAFT`). | 🔴 |
| `settlement_date` | Data em que o borrower aceitou o plano de settlement. | 🔴 |
| `settlement_amount` | Valor que o borrower concordou em pagar para liquidar. | 🔴 |
| `settlement_percentage` | Valor do settlement como % do saldo de quitação. | 🔴 |
| `settlement_term` | Nº de meses do plano de settlement. | 🔴 |

## 9. Aplicação conjunta e segundo aplicante

> Só preenchidas quando `application_type = 'Joint App'`. Em uma análise individual, podem ser ignoradas — em modelos joint, devem ser tratadas separadamente.

| Coluna | Descrição (PT-BR) | Status |
|--------|-------------------|--------|
| `annual_inc_joint` | Renda anual combinada autodeclarada pelos co-borrowers. | 🤝 |
| `dti_joint` | DTI calculado para o casal de co-borrowers. | 🤝 |
| `verified_status_joint` | Indica se a renda conjunta foi verificada pelo LC. | 🤝 |
| `revol_bal_joint` | Soma do saldo rotativo dos co-borrowers, líquida de duplicidades. | 🤝 |
| `sec_app_fico_range_low` | Faixa FICO (low) do segundo aplicante. | 🤝 |
| `sec_app_fico_range_high` | Faixa FICO (high) do segundo aplicante. | 🤝 |
| `sec_app_earliest_cr_line` | Linha de crédito mais antiga do segundo aplicante na aplicação. | 🤝 |
| `sec_app_inq_last_6mths` | Consultas nos últimos 6 meses do segundo aplicante. | 🤝 |
| `sec_app_mort_acc` | Nº de contas hipotecárias do segundo aplicante. | 🤝 |
| `sec_app_open_acc` | Nº de trades abertos do segundo aplicante. | 🤝 |
| `sec_app_revol_util` | Razão saldo/limite em rotativo do segundo aplicante. | 🤝 |
| `sec_app_open_act_il` | Nº de trades de installment ativos do segundo aplicante. | 🤝 |
| `sec_app_num_rev_accts` | Nº de contas rotativas do segundo aplicante. | 🤝 |
| `sec_app_chargeoff_within_12_mths` | Charge-offs do segundo aplicante nos últimos 12 meses. | 🤝 |
| `sec_app_collections_12_mths_ex_med` | Cobranças do segundo aplicante nos últimos 12 meses (excluindo médicas). | 🤝 |
| `sec_app_mths_since_last_major_derog` | Meses desde a última depreciação grave do segundo aplicante. | 🤝 |

## 10. Colunas derivadas no notebook CREDENCE

Não fazem parte do CSV bruto — são criadas no pipeline de tratamento.

| Coluna | Descrição (PT-BR) | Origem |
|--------|-------------------|--------|
| `default_flag` | `1` se `loan_status ∈ {Charged Off, Default, "Does not meet... Charged Off"}`, senão `0`. | 🎯 derivada |
| `issue_year` | Ano de originação extraído de `issue_d`. | derivada |
| `issue_month` | Mês de originação extraído de `issue_d`. | derivada |
| `annual_inc_w` | `annual_inc` winsorizada no percentil 99 (corte de outliers). | derivada |
| `grade_group` | `'D+E'` se `grade ∈ {D, E}`, senão `'Demais'`. | derivada |
| `dti_bucket` | Faixa categórica de `dti`: `≤10`, `10–20`, `20–35`, `>35`. | derivada |
| `income_bucket` | Faixa categórica de `annual_inc`: `<$40k`, `$40k-60k`, `$60k-100k`, `$100k-150k`, `>$150k`. Usada na Seção 2.8. | derivada |
| `geo_tier` | `HIGH`/`MED`/`LOW`/`UNKNOWN` baseado em quartis do *efeito geográfico puro* (Seção 2.7). | derivada |
| `verif_tier` | `VERIFIED` (consolida `Verified` + `Source Verified`) vs `NOT_VERIFIED`. Usada na Seção 6.4. | derivada |
| `pure_geo_effect_pp` | Excesso de default rate por estado após controlar pelo mix de grade (decomposição Oaxaca, Seção 2.7). | derivada |
| `toxic_flag` | `1` se a combinação `(grade, term, dti_bucket, geo_tier, verif_tier)` está entre as Top 15 mais tóxicas (Seção 6.4). | derivada |

---

## Regra de ouro para uso em modelagem

> Para cada coluna, pergunte-se:
> **"Esta informação existia no momento em que o LC decidiu aprovar o loan?"**
>
> - Se SIM → 🟢 segura para feature
> - Se NÃO → 🔴/🟡 leakage; usar apenas em análise descritiva

Fonte original: `data/raw/LCDataDictionary.xlsx` (aba `LoanStats`, 153 entradas).
Classificações de leakage: `CLAUDE.md` § *Data Leakage*.