# Log de Decisões Analíticas — CREDENCE

Registro cronológico das decisões tomadas na análise. Cada entrada documenta o "porquê" da escolha.

---

## [2026-05-14] Configuração inicial e exploração dos dados

### 1. Definição do target de inadimplência

**Decisão:** `default_flag = 1` para `loan_status IN ('Charged Off', 'Default', 'Does not meet the credit policy. Status:Charged Off')` e `default_flag = 0` para `loan_status IN ('Fully Paid', 'Does not meet the credit policy. Status:Fully Paid')`.

**Justificativa:** Os registros "Does not meet the credit policy" são empréstimos que o Lending Club aprovou fora dos critérios padrão mas que tiveram o mesmo desfecho de pagamento — tratá-los separadamente criaria um viés artificial. O status econômico real (pagou ou não pagou) é o que importa para a política de crédito.

**Excluídos da análise:** `Current`, `In Grace Period`, `Late (16-30 days)`, `Late (31-120 days)`, `Issued` — desfecho ainda desconhecido, incluí-los contaminaria a taxa base de inadimplência.

**Impacto:** Dataset modelável de **1.306.387 registros** (de 2.260.668 totais).

**Números reais do dataset completo:**
- Fully Paid: 1.043.940 (79,9%)
- Charged Off / Default: 262.447 (20,1%)
- **Default rate base: 20,1%** — confirma o ratio ~80/20 esperado

---

### 2. Tratamento de int_rate

**Decisão:** `int_rate` já vem como `float64` neste dataset (sem o símbolo "%"). Não é necessário conversão de string.

**Justificativa:** Verificado na exploração inicial — `df['int_rate'].dtype == float64`. O tratamento de remoção de "%" está documentado no notebook como verificação defensiva.

---

### 3. Tratamento de outliers em annual_inc

**Decisão:** Winsorização no percentil 99 para visualizações, estatísticas descritivas e a variável `annual_inc_w` usada na regressão logística inferencial.

**Justificativa:** Max observado na amostra: $5.119.032. A distribuição é altamente skewed (mean $85.879 vs mediana $70.000). Winsorizar preserva toda a amostra sem distorcer gráficos e reduz a influência de valores extremos na interpretação dos odds ratios. A regressão usa `statsmodels.Logit`, sem `class_weight` e sem balanceamento artificial de classe.

**Alternativa descartada:** Filtragem por corte fixo (ex: annual_inc > $500k) perderia registros possivelmente válidos de high-income borrowers.

---

### 4. Escopo de colunas para análise

**Decisão:** Trabalhar com as 17 colunas-chave definidas no CLAUDE.md, ignorando as ~128 restantes.

**Justificativa:** 145 colunas no dataset. Eliminar: leakage severo (11 colunas), leakage moderado (15+ colunas), texto sem valor preditivo (5 colunas), colunas de co-borrower/joint (irrelevantes para análise individual), colunas quase 100% nulas (campos de hardship/settlement).

---

### 5. Tamanho do dataset para o Looker

**Decisão:** Exportar apenas os registros modeláveis (Fully Paid + Charged Off/Default) para `exports/looker_ready.csv`.

**Justificativa:** 1,3M registros vs 2,26M totais. Exclui os "Current" (919k linhas) que não têm desfecho e poluiriam métricas de default rate no dashboard. Looker Studio suporta até 1M de linhas via upload direto; se necessário, usar amostra estratificada por grade × default_flag.

---

## [2026-05-14] Expansão sênior — análise multi-dimensional (Seções 2.7, 2.8, 6.4)

### 6. Inclusão de mapa de risco geográfico (Seção 2.7)

**Decisão:** Adicionar análise de `addr_state` com decomposição Oaxaca-Blinder em vez de
apenas plotar default rate bruto por estado.

**Justificativa:** Default rate bruto por estado confunde dois efeitos: composição da
carteira local (estados que atraem mais Grade D+E vão ter default alto sem que o estado
em si seja "ruim") e efeito geográfico puro (drivers macro locais como desemprego). A
decomposição isola o efeito puro, que é o sinal acionável para política de crédito e
gera justificativa atuarial defensável sob ECOA.

**Filtro de confiabilidade:** N ≥ 500 loans por estado. Estados com volume menor ficam
fora do ranking — IC de proporção dominado por ruído.

**Decisão complementar — granularidade UF e não ZIP code:** apesar do dataset trazer a
coluna `zip_code`, a análise foi conduzida no nível estadual. Razões:

1. **Dado incompleto:** o LC publica apenas os 3 primeiros dígitos do ZIP por privacidade
   (ex.: `100xx`). Não é o ZIP completo (5 dígitos) que um banco usa internamente —
   identifica região postal ampla, não bairro.
2. **N por bucket:** ZIP-3 gera ~900 buckets vs ~50 estados; 30–40% precisariam ser
   excluídos por `N < 500`, perdendo robustez estatística.
3. **Risco regulatório:** quanto mais granular a geografia, mais perto da fronteira de
   *disparate impact* sob ECOA. UF é defensável como variável atuarial; ZIP-3 exige
   documentação adicional de fair lending.
4. **Interpretabilidade de negócio:** "cap em CA" vai a comitê; "cap em ZIP 941xx" não.

**Limitação aceita e documentada:** UF esconde heterogeneidade intra-estado (Beverly Hills
e Compton estão ambos em "CA"). Refinamento natural em produção: ZIP completo (5 dígitos) +
mapeamento para MSA — fora do escopo do teste técnico.

**Decisão de visualização — mapa duplo (bruto + efeito puro):** a célula `2.7.3` mostra
os DOIS choropleths lado a lado em vez de só o efeito puro. O bruto é mantido como leitura
intuitiva ("vermelho = ruim"), e o efeito puro como leitura analítica ("vermelho = ruim
*depois* de controlar pelo perfil dos borrowers"). A tabela de "estados enganosos" complementa
mostrando explicitamente quais estados mudam de cor entre os dois mapas — é o golpe didático
que justifica visualmente por que o controle de mix é necessário.

Asset: `assets/13_mapa_geo_dual.html` (substituiu o `13_mapa_geo_efeito_puro.html` da versão
anterior).

---

### 7. Faixas de renda e cruzamento com verificação (Seção 2.8) — HIPÓTESE REFUTADA

**Decisão:** Cortar `annual_inc` em 5 faixas (`<40k`, `40-60k`, `60-100k`, `100-150k`, `>150k`)
e cruzar com `verification_status`.

**Hipótese inicial:** renda alta NÃO-verificada performa PIOR que renda média verificada
(viés de superdeclaração).

**Resultado real (execução 2026-05-15):** a hipótese foi **refutada**. `Not Verified` tem a
*menor* taxa de inadimplência em todas as faixas (ex.: renda >$150k não-verificada = 10,7%
vs renda $60-100k verificada = 23,4%).

**Reinterpretação — viés de seleção:** `verification_status` é uma **variável endógena**.
O Lending Club não verificava a renda aleatoriamente — verificava com mais frequência
justamente os pedidos que já pareciam arriscados. Logo, "verificado" é um marcador de
triagem de risco anterior do LC, não uma causa. A variável é quase um *leakage* suave.

**Consequências da reinterpretação:**
- Seção 2.8 reescrita como caso de viés de seleção / endogeneidade.
- `verification_status` removida da combinação tóxica da Seção 6.4 (passou de 5 → 4 dimensões).
- Recomendação "verificação obrigatória >$100k" **removida** da Seção 7 — não se pode
  concluir que mexer na política de verificação reduz risco (correlação é seleção, não causa).
- `verification_status` mantida apenas como coluna descritiva no export do Looker.

**Lição metodológica:** antes de construir recomendação sobre uma variável, checar se ela
é exógena. `verification_status` falha nesse teste.

**Faixas escolhidas com base em:** quintis aproximados da distribuição de renda dos EUA
no período 2014–2018, ajustados para serem interpretáveis em narrativa de negócio.

---

### 8. Premissas para cálculo de P&L (Seção 6.4) — modelo de receita corrigido

**Decisão:** Usar LGD = 60%, custo de funding = 4% a.a., duration = term/24 anos,
**fração de juros coletada em loans inadimplentes = 50%**.

**Justificativa:**
- LGD 60%: dataset não traz LGD realizado por loan. 60% é o ponto médio da literatura
  empírica para *unsecured retail* (faixa 55–65%), alinhado com Foundation IRB de Basileia.
- Custo de funding 4%: proxy do *cost of capital* de fintech P2P 2014–2018.
- Duration term/24: duration média ≈ metade do prazo (amortização linear).
- **Fração de juros 50%:** a primeira versão dava **receita cheia** a todo loan, inclusive
  os inadimplentes. Erro: um loan que vira charge-off **para de pagar juros no meio do
  caminho**. Sem o ajuste, o modelo superestimava a lucratividade dos segmentos de alto
  risco. Corrigido: loans inadimplentes coletam ~50% dos juros agendados antes do default.

**Achado corrigido (execução 2026-05-15):** com o modelo certo, a conclusão da Seção 6.4
mudou. **Default rate alto ≠ destruição de valor.** As combinações de maior inadimplência
(F/G, 60m, DTI alto, 50-70% default) são *lucrativas* — os juros de 25-29% compensam o
risco. A destruição de valor está no **meio mal precificado**: ~32 combinações de 36 meses,
DTI 20-35, geografia de risco, nos Grades A-E (defaultam 8-39%, precificadas só pelo grade).
Cortar/reprecificar essas combinações gera ~+$37M e reduz a inadimplência em ~120 bps.

**Limitação documentada:** premissas para *ranking relativo* — não projeção absoluta de P&L.
O sinal do resultado (cortar tóxicas = perda; reprecificar mal-precificadas = ganho) é
robusto à premissa de fração de juros (testado em 30%–100%). Em produção, ALM e modelo de
LGD próprios substituiriam as premissas.

---

### 9. Tiering de geografia para Seção 6.4

**Decisão:**
- `geo_tier`: `HIGH` se `pure_geo_effect_pp ≥ Q3`, `LOW` se `≤ Q1`, `MED` no meio.
- `verif_tier` foi **descartado** como feature de risco (ver decisão #7 — variável endógena).
  A combinação tóxica da Seção 6.4 usa 4 dimensões (grade × term × dti × geo_tier).

**Justificativa:** Tiers em quartis (em vez de cutoffs absolutos) tornam o método
robusto a mudanças no dataset — funciona para qualquer carteira, não depende de
benchmark fixo. Consolidar `Verified` e `Source Verified` em uma só categoria evita
fragmentar células com N pequeno; a literatura LC mostra performance similar entre
as duas modalidades.

---

### 10. Considerações regulatórias adicionadas à Seção 7

**Decisão:** Incluir bloco explícito sobre ECOA / Reg B nas recomendações que tocam
`addr_state` (Recomendações 4 e 7).

**Justificativa:** Diferenciador sênior — mostra ao avaliador que o candidato entende
a fronteira entre *risk-based pricing* (permitido) e *underwriting cutoff* por região
(proibido). Sem essa nota, as recomendações poderiam ser implementadas de forma
ilegal por uma equipe júnior.

---

## [2026-05-16] Versão avançada do notebook + documentos de defesa

### 11. Criação do notebook em versão avançada

**Decisão:** criar `credence_analise_avancado.ipynb` — terceira versão do notebook, cópia
completa da canônica (9 seções) acrescida de quatro técnicas de modelagem de nível comitê.
Não substitui o notebook canônico.

**Justificativa:** responde a quatro lacunas que um avaliador sênior aponta sobre a regressão
logística da Seção 5 — validação temporal, calibração probabilística, tempo-até-evento e
interpretação econômica dos coeficientes. As Seções 6/7/8 do canônico foram renumeradas para
7/8/9; a nova Seção 6 é a análise de sobrevivência.

**Replicação:** não replicada na versão 100% PT — é extensão exploratória, não a análise
oficial. O canônico segue como versão a manter.

---

### 12. Validação temporal — split treino 2007–2015 / teste 2016–2018

**Decisão:** treinar a regressão logística apenas com loans de 2007–2015 e validá-la nos de
2016–2018.

**Justificativa:** avaliar o modelo no mesmo período em que foi treinado superestima a
performance. O corte em 2015 deixa N robusto nos dois lados (treino 825.569; teste 480.502).

**Resultado (execução 2026-05-16):** AUC 0,706 → 0,684 (degradação 0,022); Brier 0,138 → 0,166;
default rate 18,5% → 22,9%. Leitura: o ranking de risco é estável out-of-time, mas o nível
absoluto da probabilidade é subestimado — compatível com drift do regime de risco.

---

### 13. Análise de sobrevivência — `last_pymnt_d` como eixo do tempo

**Decisão:** derivar a duração observada (meses entre `issue_d` e `last_pymnt_d`); evento =
`default_flag`; loans `Fully Paid` tratados como observações censuradas à direita.

**Conflito aparente com a regra de leakage — resolvido:** o CLAUDE.md classifica `last_pymnt_d`
como LEAKAGE SEVERO, e está certo *para uso como feature preditiva*. Na análise de sobrevivência
ela **não é feature** — define o eixo do tempo do estudo. Uso padrão e legítimo na literatura
de risco de crédito; documentado explicitamente no notebook (Seção 6.1) e no CLAUDE.md.

**Ferramenta:** `statsmodels` (`SurvfuncRight`, `survdiff`, `PHReg`) — evita introduzir
`lifelines`/`scikit-survival`, mantendo a stack pinada do projeto.

**Resultado:** 1.241.223 loans com tempo-até-evento válido; duração mediana 19 meses; 20,9% de
eventos. Log-rank 36m × 60m: χ² ≈ 25.335 (p < 0,001). Cox HR — grade 1,44/passo, term60 1,19,
dti 1,003/ponto, log(renda) 0,85.

**Limitação documentada — viés de resolução:** a base contém apenas loans com desfecho
resolvido. Para as safras 2016–2018 isso introduz viés de seleção (loans `Current` excluídos;
defaults precoces resolvem primeiro). A leitura de vintage via sobrevivência é confiável apenas
para coortes maduras (≤ 2015). Correção de produção: incluir loans `Current` como observações
censuradas na data do snapshot. Sinalizado no notebook (ressalva da Seção 6.4 + síntese).

---

### 14. Calibração probabilística — isotônica como referência diagnóstica

**Decisão:** avaliar a calibração no recorte de teste (diagrama de confiabilidade + Brier
score) e incluir uma recalibração isotônica apenas como referência do ganho possível, não
como modelo final.

**Resultado:** o gap (default observado − probabilidade prevista) é positivo nos dez decis,
chegando a +7 p.p. — o modelo subestima sistematicamente o risco das safras recentes. Brier
0,166 → 0,163 com a isotônica. Consequência: adicionada a Recomendação 8 à Seção 8 do notebook
avançado — recalibrar o modelo antes de uso em provisão/pricing e monitorar calibração por
safra (não só AUC).

---

### 15. Documentos de defesa oral

**Decisão:** criar `docs/defesa_oral.md` (domínio completo), `docs/defesa_slides.md` (roteiro
de 9 slides) e `docs/defesa_cartao.md` (cartão de 1 página).

**Justificativa:** sustentar a apresentação da versão avançada em três níveis de profundidade —
estudo, apresentação e consulta rápida. Todos usam apenas números conferidos na execução de
referência do notebook (2026-05-16) e seguem a régua de linguagem analítica do CLAUDE.md.

---

## Pendências para documentar após análise

- [ ] Resultado real dos claims da Parte 3 (Governança de IA)
- [ ] Combinações tóxicas encontradas na Seção 6
- [ ] Resultado do teste de hipótese (p-valor, IC 95%, effect size)
- [ ] Odds ratios da regressão logística
- [ ] Estados em `geo_tier=HIGH` (resultado da Seção 2.7)
- [ ] Default rate de renda > $150k não-verificada vs $60–100k verificada (Seção 2.8)
- [ ] Ponto ótimo de corte da curva da Seção 6.4 (% volume + ganho em P&L)
