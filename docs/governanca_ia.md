# Validação da Resposta do Agente de IA — FinLend

## 1. Objetivo da Validação

O objetivo desta entrega é auditar a resposta de um agente de IA generativa sobre o perfil de risco dos clientes que tomam empréstimos para consolidação de dívidas. A validação combina três camadas:

1. validação quantitativa determinística dos números citados pelo agente;
2. avaliação qualitativa da resposta em termos de completude, rastreabilidade e risco interpretativo;
3. proposta prática de governança para uso corporativo de IA analítica em crédito.

A Parte 3 foi tratada como uma auditoria da IA generativa contra a base analítica oficial construída no notebook.

Pergunta do gestor:

> "Qual é o perfil de risco dos nossos clientes que tomam empréstimos para consolidação de dívidas?"

Resposta do agente auditada:

> "Os clientes que tomam empréstimos para consolidação de dívidas representam 48% da carteira total. A taxa de inadimplência desse segmento é de 12,3%, ligeiramente abaixo da média geral de 14,1%. O ticket médio é de 72.000. A renda média anual é de 15.200 e a maioria dos clientes está classificada nas grades B e C (62%), indicando um perfil de risco moderado. A taxa de juros média é de 13,8%."

## 2. Base Analítica Utilizada

Para garantir consistência entre a análise estatística e a validação do agente de IA, utilizei na Parte 3 a mesma base analítica construída no notebook da Parte 2: o período completo disponível no dataset Lending Club.

Critérios utilizados:

- fonte: `data/raw/loan.csv`;
- período disponível: 2007 a 2018;
- unidade de análise: empréstimo, não cliente único;
- sem recorte temporal na validação principal;
- mesmas colunas centrais de risco usadas no notebook;
- mesma lógica de carteira analisável: contratos com desfecho conhecido.

Resumo da preparação executada:

| Item | Valor |
|---|---:|
| Registros brutos | 2.260.668 |
| Registros elegíveis para validação principal | 1.306.387 |
| Registros excluídos por status ambíguo/sem desfecho final | 954.281 |
| Segmento `debt_consolidation` elegível | 758.710 |
| Período elegível | 2007–2018 |

Os registros `Current`, `In Grace Period`, `Late (16-30 days)` e `Late (31-120 days)` foram classificados como ambíguos na validação principal para manter coerência com o notebook da Parte 2, que avalia inadimplência com desfecho conhecido. `Late (31-120 days)` pode ser tratado como default em uma regra alternativa de stress, mas essa não foi a regra oficial usada para comparar o LLM nesta entrega.

Código reutilizável: [scripts/validate_llm_response.py](/Users/administrador/Desktop/projetos/credence/scripts/validate_llm_response.py)

Execução:

```bash
.venv/bin/python scripts/validate_llm_response.py --csv data/raw/loan.csv
```

## 3. Definição de Inadimplência

A definição de inadimplência precisa ser explícita porque altera diretamente a taxa calculada. Uma resposta analítica de IA que reporta default rate sem explicar a regra de default não é plenamente rastreável.

Regra principal usada nesta auditoria:

| Categoria | `loan_status` |
|---|---|
| `default` | `Charged Off`, `Default`, `Does not meet the credit policy. Status:Charged Off` |
| `non_default` | `Fully Paid`, `Does not meet the credit policy. Status:Fully Paid` |
| `ambiguous` | `Current`, `In Grace Period`, `Late (16-30 days)`, `Late (31-120 days)`, `Issued` |
| `unknown` | status nulo ou não mapeado |

Função de classificação:

```python
def classify_status(status, include_late_31_as_default=False):
    if pd.isna(status):
        return "unknown"

    default_statuses = {
        "Charged Off",
        "Default",
        "Does not meet the credit policy. Status:Charged Off",
    }
    non_default_statuses = {
        "Fully Paid",
        "Does not meet the credit policy. Status:Fully Paid",
    }
    ambiguous_statuses = {
        "Current",
        "In Grace Period",
        "Late (16-30 days)",
        "Late (31-120 days)",
        "Issued",
    }

    if include_late_31_as_default:
        default_statuses.add("Late (31-120 days)")
        ambiguous_statuses.discard("Late (31-120 days)")

    if status in default_statuses:
        return "default"
    if status in non_default_statuses:
        return "non_default"
    if status in ambiguous_statuses:
        return "ambiguous"
    return "unknown"
```

## 4. Validação Quantitativa

As métricas foram recalculadas deterministicamente na base oficial e comparadas com os valores declarados pelo agente.

Tolerâncias aplicadas:

| Tipo de métrica | Tolerância |
|---|---:|
| Percentuais | até 1 ponto percentual |
| Distribuições | até 2 pontos percentuais |
| Valores monetários | até 5% de diferença relativa |
| Médias | até 5% de diferença relativa |
| Métrica sem unidade, período ou definição | alerta qualitativo |

Tabela comparativa:

| Métrica | Valor informado pelo LLM | Valor calculado | Diferença absoluta | Diferença percentual | Status | Observação analítica |
|---|---:|---:|---:|---:|---|---|
| Participação de `debt_consolidation` | 48,00% | 58,08% | +10,08 p.p. | +20,99% | Crítico | O agente subestima a participação do maior segmento da carteira. |
| Default rate de `debt_consolidation` | 12,30% | 21,27% | +8,97 p.p. | +72,90% | Crítico | Divergência material em métrica central de risco. |
| Default rate geral | 14,10% | 20,09% | +5,99 p.p. | +42,48% | Crítico | A média usada pelo agente não bate com a base oficial. |
| Ticket médio de `debt_consolidation` | 72.000 | 15.215 | -56.785 | -78,87% | Crítico | O valor parece trocado com renda anual ou sem unidade correta. |
| Renda anual média de `debt_consolidation` | 15.200 | 74.875 | +59.675 | +392,60% | Crítico | O valor informado é incompatível com a renda anual média calculada. |
| % grades B ou C no segmento | 62,00% | 57,91% | -4,09 p.p. | -6,60% | Divergente | Fora da tolerância de 2 p.p.; ainda indica concentração em B/C, mas o número está errado. |
| Taxa média de juros no segmento | 13,80% | 13,64% | -0,16 p.p. | -1,16% | OK | Dentro da tolerância. |

Distribuição real de grades no segmento `debt_consolidation`:

| Grade | Participação |
|---|---:|
| A | 14,62% |
| B | 28,20% |
| C | 29,70% |
| D | 16,18% |
| E | 7,85% |
| F | 2,69% |
| G | 0,75% |

Diagnóstico quantitativo: 5 claims críticos, 1 claim divergente e 1 claim OK. A resposta falha nas principais métricas de risco e de perfil financeiro.

## 5. Avaliação Qualitativa

A resposta responde ao tema geral da pergunta, mas não atende aos requisitos mínimos para uso corporativo sem revisão.

Checklist qualitativo:

| Critério | Avaliação |
|---|---|
| Responde diretamente à pergunta do gestor | Parcial |
| Usa métricas relevantes de risco | Parcial |
| Informa o período analisado | Não |
| Informa tamanho da base ou amostra | Não |
| Explica a definição de inadimplência | Não |
| Declara unidade de análise: empréstimo vs cliente | Não |
| Diferencia carteira total de carteira analisável | Não |
| Informa unidade monetária e escala | Não |
| Evita causalidade indevida | Sim |
| Mostra incerteza, limitações ou premissas | Não |
| Possui rastreabilidade para cálculo, query ou fonte | Não |
| Pode induzir o gestor a decisão errada | Sim |

A resposta do agente não informa explicitamente o recorte temporal utilizado. Essa ausência reduz a rastreabilidade da resposta, pois métricas como taxa de inadimplência, ticket médio, distribuição de grades e taxa média de juros podem variar significativamente conforme o período analisado.

Também não informa definição de inadimplência, denominador, escopo da carteira, nem se a análise é por empréstimo ou por cliente. No Lending Club, um mesmo tomador pode ter mais de um empréstimo; portanto, dizer "clientes" quando a base está em nível de empréstimo cria ambiguidade.

Mesmo quando uma resposta de IA apresenta números aparentemente plausíveis, ela não deve ser considerada confiável sem rastreabilidade para a base, definição das métricas, período analisado e regra de cálculo.

## 6. Diagnóstico da Resposta do LLM

Classificação: não confiável.

Justificativa:

- o agente erra de forma crítica a participação do segmento;
- subestima a inadimplência de `debt_consolidation`;
- afirma que o segmento está abaixo da média, mas a base oficial mostra o oposto;
- troca ou confunde ticket médio e renda anual média;
- não declara período, regra de default, denominador nem unidade de análise;
- não fornece rastreabilidade para query, cálculo ou fonte.

O erro mais relevante é de framing. O agente afirma que o segmento tem risco "ligeiramente abaixo da média". Na base oficial:

- default rate do segmento: 21,27%;
- default rate geral: 20,09%;
- diferença: +1,18 p.p.

Ou seja, `debt_consolidation` está acima da média, não abaixo. Um gestor poderia interpretar a resposta como autorização para expandir exposição ou reduzir pricing em um segmento que representa 58,08% da carteira elegível.

Score de confiança proposto:

| Critério | Peso | Avaliação | Pontos |
|---|---:|---|---:|
| Acurácia quantitativa | 40% | 1 de 7 claims dentro da tolerância | 6 |
| Completude da resposta | 20% | Métricas relevantes, mas sem base, N ou definição | 8 |
| Rastreabilidade | 20% | Sem query, fonte ou fórmula | 0 |
| Clareza metodológica | 10% | Sem período, unidade e regra de default | 2 |
| Ausência de risco interpretativo | 10% | Framing inverte o sinal de risco | 0 |
| Total | 100% | Reprovada | 16 |

Faixas de decisão:

| Score | Classificação |
|---:|---|
| 85 a 100 | resposta aprovada |
| 70 a 84 | resposta aprovada com ressalvas |
| 50 a 69 | resposta requer revisão humana |
| abaixo de 50 | resposta reprovada |

Para decisões de crédito, risco ou diretoria, respostas abaixo do nível aprovado não devem ser liberadas automaticamente.

## 7. Ontologia de Domínio

A ontologia serve para padronizar conceitos de negócio e evitar ambiguidade semântica nas respostas do agente. Ela não precisa ser o centro da entrega, mas funciona como camada de maturidade de AI Readiness.

Entidades:

| Entidade | Definição |
|---|---|
| `Borrower` | Tomador de crédito, quando identificável |
| `Loan` | Empréstimo individual, unidade principal do dataset |
| `LoanPurpose` | Finalidade do empréstimo |
| `RiskGrade` | Grade de risco A-G |
| `SubGrade` | Subgrade de risco |
| `PaymentStatus` | Status bruto do empréstimo |
| `DefaultEvent` | Evento de inadimplência conforme regra definida |
| `InterestRate` | Taxa de juros contratada |
| `Income` | Renda anual reportada |
| `DebtToIncome` | Razão dívida/renda |
| `PortfolioSegment` | Segmento analítico da carteira |
| `RiskMetric` | Métrica de risco ou perfil |
| `ValidationRule` | Regra para validar claims |
| `LLMAnswer` | Resposta gerada pelo agente |
| `LLMClaim` | Claim extraído da resposta |
| `GroundTruthMetric` | Métrica oficial calculada deterministicamente |
| `Dataset` | Fonte de dados usada |
| `CalculationRule` | Fórmula ou query certificada |

Relações:

| Relação | Exemplo |
|---|---|
| `Borrower HAS_LOAN Loan` | um tomador possui empréstimo |
| `Loan HAS_PURPOSE LoanPurpose` | empréstimo tem finalidade |
| `Loan HAS_GRADE RiskGrade` | empréstimo tem grade |
| `Loan HAS_SUBGRADE SubGrade` | empréstimo tem subgrade |
| `Loan HAS_STATUS PaymentStatus` | empréstimo tem status |
| `Loan HAS_INTEREST_RATE InterestRate` | empréstimo tem taxa |
| `Loan HAS_INCOME Income` | empréstimo tem renda reportada |
| `Loan HAS_DTI DebtToIncome` | empréstimo tem DTI |
| `Loan MAY_HAVE DefaultEvent` | empréstimo pode ter default |
| `PortfolioSegment CONTAINS Loan` | segmento contém empréstimos |
| `RiskMetric DESCRIBES PortfolioSegment` | métrica descreve segmento |
| `LLMAnswer CONTAINS LLMClaim` | resposta contém claims |
| `LLMClaim CLAIMS_VALUE RiskMetric` | claim declara valor de métrica |
| `GroundTruthMetric VALIDATES LLMClaim` | métrica oficial valida claim |
| `ValidationRule CHECKS LLMClaim` | regra checa claim |
| `CalculationRule PRODUCES GroundTruthMetric` | fórmula produz métrica oficial |
| `Dataset SUPPORTS CalculationRule` | dataset sustenta cálculo |

## 8. Axiomas e Regras Determinísticas

Axiomas para uma resposta analítica validável:

1. Toda métrica de risco deve estar associada a período de referência, unidade de análise, definição de default, fonte de dados e fórmula de cálculo.
2. Uma taxa de inadimplência só é válida se declarar numerador, denominador e regra de elegibilidade da base.
3. Toda métrica declarada pelo LLM deve ser rastreável para uma query, função ou cálculo determinístico.
4. Uma resposta analítica não deve afirmar causalidade sem teste estatístico, desenho causal ou evidência apropriada.
5. Valores monetários devem informar unidade, moeda e escala.
6. Toda resposta com impacto gerencial deve possuir score de confiança ou status de validação.
7. A ausência de período, base ou definição da métrica reduz o grau de confiabilidade da resposta, mesmo que o número esteja numericamente próximo.
8. Uma resposta sobre perfil de risco deve considerar, no mínimo, finalidade do empréstimo, grade, status, taxa de inadimplência, taxa de juros e alguma proxy de capacidade de pagamento, como renda ou DTI.

Pseudo-código:

```python
def validate_metric_context(metric):
    required = ["period", "unit_of_analysis", "default_definition", "data_source", "formula"]
    missing = [field for field in required if not metric.get(field)]
    return {
        "valid": len(missing) == 0,
        "missing": missing,
    }


def validate_default_rate_claim(claim):
    required = ["numerator", "denominator", "eligibility_rule", "default_rule"]
    return all(claim.get(field) is not None for field in required)


def validate_money_claim(claim):
    return bool(claim.get("currency") and claim.get("scale"))
```

## 9. Fórmulas Oficiais de Validação

Camada determinística usada como ground truth:

```text
share_debt_consolidation =
    loans_debt_consolidation / total_eligible_loans

default_rate_segment =
    default_loans_debt_consolidation / eligible_loans_debt_consolidation

default_rate_overall =
    default_loans_total / eligible_loans_total

avg_ticket_segment =
    sum(loan_amnt_debt_consolidation) / count(loans_debt_consolidation)

avg_income_segment =
    sum(annual_inc_debt_consolidation) / count(loans_debt_consolidation)

avg_interest_rate_segment =
    mean(int_rate_debt_consolidation)

share_grade_bc =
    loans_debt_consolidation_grade_b_or_c / loans_debt_consolidation_total
```

A validação de um agente de IA analítico não deve depender apenas da avaliação humana pontual. Ela deve ser sustentada por uma camada determinística de métricas oficiais, regras de domínio, rastreabilidade semântica e validação recorrente contra ground truth.

## 10. Knowledge Graph Conceitual

Um Knowledge Graph ajudaria a conectar pergunta, resposta, métrica, cálculo, dataset e regra de validação. Ele reduz ambiguidade porque força cada claim a apontar para uma métrica oficial, uma fórmula e uma fonte.

Nós:

- `Loan`;
- `LoanPurpose`;
- `RiskGrade`;
- `PaymentStatus`;
- `PortfolioSegment`;
- `RiskMetric`;
- `LLMAnswer`;
- `LLMClaim`;
- `GroundTruthMetric`;
- `ValidationRule`;
- `CalculationRule`;
- `Dataset`.

Arestas:

- `HAS_PURPOSE`;
- `HAS_GRADE`;
- `HAS_STATUS`;
- `CONTAINS`;
- `DESCRIBES`;
- `CONTAINS_CLAIM`;
- `CLAIMS_VALUE`;
- `VALIDATES`;
- `CHECKS`;
- `PRODUCES`;
- `SUPPORTS`.

Exemplos de tripletas:

```text
Loan_123 HAS_PURPOSE debt_consolidation
Loan_123 HAS_GRADE C
Loan_123 HAS_STATUS Charged_Off
Segment_debt_consolidation HAS_DEFAULT_RATE 0.2127
Segment_debt_consolidation HAS_AVG_INTEREST_RATE 0.1364
LLM_Answer_001 CONTAINS Claim_001
Claim_001 CLAIMS_VALUE default_rate_debt_consolidation_12_3
GroundTruthMetric_001 VALIDATES Claim_001
ValidationRule_001 CHECKS Claim_001
CalculationRule_001 PRODUCES GroundTruthMetric_001
Dataset_LendingClub SUPPORTS CalculationRule_001
```

Como o KG reduz alucinação:

- impede que uma métrica seja citada sem conceito de negócio associado;
- exige ligação entre claim e cálculo oficial;
- permite checar se o período e a unidade de análise existem;
- ajuda o agente a recuperar a métrica correta por semântica, não por texto solto;
- permite auditar respostas com trilha de evidência.

O KG não precisa ser implementado integralmente neste teste. Ele é uma proposta de arquitetura de maturidade para AI Readiness.

## 11. Processo Recorrente de Validação

Pipeline recomendado:

1. Criar catálogo de perguntas críticas de negócio.
2. Definir métricas oficiais e glossário semântico.
3. Criar queries ou funções determinísticas para ground truth.
4. Fazer o agente responder perguntas benchmark.
5. Extrair claims quantitativos da resposta do LLM.
6. Comparar claims contra ground truth.
7. Aplicar tolerâncias por tipo de métrica.
8. Gerar score de confiança.
9. Registrar divergências e classificá-las por criticidade.
10. Submeter respostas críticas para revisão humana.
11. Atualizar prompt, camada semântica, base vetorial ou regras de validação.
12. Reexecutar testes periodicamente.
13. Monitorar drift de dados e mudanças nas métricas oficiais.

Registro mínimo por auditoria:

```json
{
  "answer_id": "LLM_Answer_001",
  "question": "Qual é o perfil de risco dos clientes de debt_consolidation?",
  "dataset": "LendingClub 2007-2018",
  "unit_of_analysis": "loan",
  "claims_validated": 7,
  "ok": 1,
  "divergent": 1,
  "critical": 5,
  "confidence_score": 16,
  "decision": "reproved",
  "requires_human_review": true
}
```

## 12. Recomendações

Recomendações práticas para a FinLend:

1. Implementar RAG conectado a dados oficiais ou tabelas certificadas, não a documentos soltos.
2. Criar camada semântica de métricas: definição, fórmula, fonte, unidade, elegibilidade e owner.
3. Manter glossário de negócio para termos como carteira, inadimplência, cliente, empréstimo, ticket e renda.
4. Usar queries certificadas para perguntas recorrentes de risco e negócio.
5. Adicionar guardrails para respostas analíticas: sem período, N, unidade e regra de cálculo, a resposta deve incluir alerta.
6. Exigir score de confiança para respostas com impacto gerencial.
7. Encaminhar respostas críticas para revisão humana antes de publicação.
8. Registrar divergências por claim para análise de causa raiz.
9. Monitorar drift de dados e reexecutar benchmarks após atualização de dataset, modelo ou prompt.
10. Separar linguagem executiva de evidência técnica: resposta curta para o gestor, anexo rastreável para auditoria.

Exemplo de resposta esperada do agente após melhorias:

> "Na base analítica oficial 2007–2018, considerando empréstimos com desfecho conhecido e unidade de análise em nível de empréstimo, `debt_consolidation` representa 58,08% da carteira elegível (N = 758.710 de 1.306.387). A taxa de inadimplência do segmento é 21,27%, acima da média geral de 20,09% em 1,18 p.p. O ticket médio é US$ 15.215, a renda anual média é US$ 74.875, 57,91% dos empréstimos estão nas grades B ou C e a taxa média de juros é 13,64%. Portanto, o segmento é relevante em volume e ligeiramente mais arriscado que a média, apesar de concentrado em grades intermediárias."

## 13. Conclusão Executiva

A resposta do agente não deve ser liberada automaticamente para stakeholders.

Embora use métricas aparentemente relevantes, ela erra os principais números de risco, confunde ticket médio com renda anual, omite período, denominador, unidade de análise, regra de inadimplência e fonte dos cálculos. O ponto mais crítico é o framing: o agente conclui que `debt_consolidation` tem risco abaixo da média, quando a base oficial mostra risco acima da média.

Para uso corporativo em uma fintech, a resposta só poderia ser liberada após:

- recalcular métricas contra a base oficial;
- exibir N, período, unidade e definição de default;
- anexar rastreabilidade para query ou função determinística;
- aplicar score de confiança;
- submeter claims críticos a revisão humana.

Essa abordagem demonstra AI Readiness porque combina análise quantitativa, governança semântica, regras determinísticas, rastreabilidade e processo recorrente de validação de IA generativa.
