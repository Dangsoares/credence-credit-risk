# CREDENCE — Documento de Defesa Oral

**Notebook em defesa:** `notebooks/credence_analise_avancado.ipynb`
**Objetivo deste documento:** dar a você o domínio necessário para apresentar e sustentar a
versão avançada da análise — entender *o que* foi feito, *por que* foi feito assim, *o que os
números significam* e *como responder* às perguntas difíceis de um avaliador técnico.

> Como usar: leia a Parte 1 e a Parte 2 para apresentar; estude a Parte 3 para defender; tenha
> a Parte 4 na ponta da língua para **admitir as limitações antes de perguntarem** — admitir
> primeiro é o que separa um analista sênior de um júnior.

---

## Resumo em 60 segundos (o "elevator pitch")

> "A versão canônica do CREDENCE responde *quem* inadimple. A versão avançada responde três
> perguntas que um comitê de crédito de verdade faz a seguir: o modelo **ainda funciona** quando
> o tempo passa? As probabilidades dele são **confiáveis em nível absoluto**, não só em ranking?
> E *quando* o default acontece — não só *se* acontece? Para isso adicionei quatro técnicas:
> validação temporal, calibração probabilística, efeitos marginais e análise de sobrevivência.
> O resultado central: o modelo **ordena bem o risco mesmo fora do tempo**, mas **subestima o
> nível de risco** nas safras recentes porque a inadimplência piorou — e a análise de
> sobrevivência confirma, por um caminho independente, a tese do projeto: prazo de 60 meses e
> DTI elevado aparecem como os principais fatores associados à aceleração do default."

---

## Parte 1 — Por que esta versão avançada existe

A versão canônica usa **regressão logística** para estimar associações ajustadas (odds ratios).
Isso é correto e suficiente para *explicar* o risco. Mas um avaliador sênior aponta quatro
lacunas — e esta versão responde a cada uma:

| Crítica ao notebook canônico | Resposta da versão avançada |
|---|---|
| "Você treina e interpreta no mesmo período — performance inflada." | **Seção 5.4** — split temporal: treino 2007–2015, teste 2016–2018. |
| "Você reporta odds ratios, mas não prova que P(default)=0,30 ⇒ 30% inadimple." | **Seção 5.5** — calibração probabilística (diagrama de confiabilidade + Brier). |
| "Crédito é tempo-até-evento; logística só vê o desfecho binário." | **Seção 6** — Kaplan-Meier + Cox de riscos proporcionais. |
| "'DTI aumenta risco' não é acionável; o comitê decide em p.p." | **Seção 5.6** — efeitos marginais médios e elasticidade econômica. |

**Mensagem de enquadramento (use isto se perguntarem o escopo):** "Nenhuma dessas técnicas é
um modelo de produção. São camadas de *rigor* sobre uma análise explicativa — mostram que as
conclusões sobrevivem a testes mais duros, e onde elas param de valer."

---

## Parte 2 — As quatro técnicas: o que é, por que, o que deu

### 2.1 — Validação temporal (Seção 5.4)

**O que é.** Treinar o modelo apenas com empréstimos de 2007–2015 e testá-lo nos de 2016–2018.
Avaliar no mesmo período em que se treina superestima a performance — o modelo já "conheceu"
aquele regime macroeconômico.

**O que deu (números do notebook):**

| Métrica | Treino 2007–2015 | Teste 2016–2018 |
|---|---|---|
| Nº de loans | 825.569 | 480.502 |
| Default rate | 18,5 % | 22,9 % |
| AUC | 0,706 | 0,684 |
| Brier score | 0,138 | 0,166 |

**Como interpretar — e este é o ponto fino:** dois resultados puxam para lados diferentes.
- O **AUC quase não cai** (−0,022). O modelo continua **ordenando** bem: separa bons de maus
  pagadores mesmo em safras que nunca viu.
- O **Brier piora bastante** (+0,028). O modelo erra o **nível** da probabilidade.

A explicação une os dois: a inadimplência **subiu de 18,5 % para 22,9 %** entre os períodos. O
modelo aprendeu um mundo mais brando do que o que encontrou. **Ranking ≠ calibração** — e essa
distinção é a ponte natural para a Seção 5.5.

**Frase de defesa:** "AUC mede se eu coloco os loans na ordem certa de risco. Brier mede se eu
acerto o número. O modelo passa no primeiro teste e falha no segundo — e isso não é um defeito
do modelo, é o sintoma de um regime de risco que se deteriorou."

---

### 2.2 — Calibração probabilística (Seção 5.5)

**O que é.** Um modelo é *calibrado* quando, entre os loans aos quais ele atribui 30 % de
risco, aproximadamente 30 % de fato inadimplem. O **diagrama de confiabilidade** agrupa o teste
em decis de score e compara a probabilidade prevista média com o default observado.

**O que deu.** A coluna `gap` (observado − previsto) é **positiva nos dez decis** — o modelo
**subestima o risco em toda a faixa de score**. O desvio chega a **+7 p.p.** nos decis
intermediários: loans pontuados em ~20 % de risco inadimplem perto de **28 %**. A recalibração
**isotônica** reduz o Brier de 0,166 para 0,163 — corrige o nível, mas não recupera poder de
discriminação (não é função dela).

**Por que isso importa para o negócio.** Provisão de perda, pricing e capital econômico dependem
do **nível absoluto** da probabilidade, não do ranking. Usar as probabilidades cruas deste
modelo levaria a **subprovisionar** a carteira recente — um erro material.

**Frase de defesa:** "A subestimação não é viés do estimador — `statsmodels.Logit` é calibrado
*dentro* da amostra de treino por construção (é máxima verossimilhança). O que o diagrama
mostra é *drift*: o mundo de 2016–2018 é mais arriscado que o de treino. Por isso a recomendação
não é 'trocar o modelo', é 'adicionar uma camada de recalibração e monitorá-la por safra'."

---

### 2.3 — Efeitos marginais e elasticidade (Seção 5.6)

**O que é.** O odds ratio é multiplicativo e pouco intuitivo. O **efeito marginal médio (AME)**
traduz cada coeficiente em **pontos percentuais de probabilidade de default** — a unidade em
que um comitê de crédito decide.

**O que deu (principais AMEs):**

| Fator | Efeito sobre P(default) | Leitura |
|---|---|---|
| Grade G (vs A) | +33,5 p.p. | grade domina em magnitude, mas é atribuído |
| Grade C (vs A) | +19,2 p.p. | — |
| `small_business` (vs car) | +8,1 p.p. | uso de capital de giro é o purpose mais arriscado |
| **Term 60 meses** | **+6,7 p.p.** | **alavanca acionável** |
| **DTI (+10 p.p.)** | **+1,7 p.p.** | **alavanca acionável** |
| Renda (+US$ 10 mil/ano) | −0,43 p.p. | renda alta, sozinha, quase não protege |
| `wedding` (vs car) | −6,2 p.p. | purpose mais protetor |

**A leitura que vai ao comitê:** "Mantendo grade, term, purpose e renda constantes, um aumento
de 10 p.p. no DTI está associado a +1,7 p.p. na probabilidade de default." Isso é elasticidade —
e é acionável: um teto de DTI tem efeito quantificável.

**Conexão com a tese central (use isto):** na escala de probabilidade os efeitos são
aproximadamente aditivos. Um **Grade C** (+19,2 p.p. sobre A) que **também** toma 60 meses
(+6,7 p.p.) e tem DTI ~20 pontos acima da média (≈ +3,3 p.p.) acumula um excedente que o
aproxima do **território de Grade E** (+28,1 p.p.). É a tese do CREDENCE — "a combinação, não o
grade isolado" — agora **quantificada em pontos percentuais**.

---

### 2.4 — Análise de sobrevivência (Seção 6)

**O que é e por que.** Crédito é um problema de **tempo-até-evento**. Um empréstimo de 60 meses
que inadimple no mês 10 não é o mesmo que um que inadimple no mês 55 — e a logística, que só vê
o desfecho 0/1, não distingue os dois. A análise de sobrevivência modela **quando** o default
ocorre e trata corretamente a **censura à direita**: um loan `Fully Paid` não é um "não-evento",
é uma observação **censurada** — acompanhada sem default até o fim do contrato.

**Construção do dataset (6.1).** `duração` = meses entre `issue_d` e `last_pymnt_d`; `evento` = 1
se default observado, 0 se censurado. Resultado: **1.241.223 loans válidos**, duração mediana de
**19 meses**, 259.557 eventos (20,9 %) e 981.666 censurados.

> **Sobre `last_pymnt_d` ser "leakage":** o CLAUDE.md a classifica como vazamento — e está
> certo *para um modelo preditivo*, onde ela seria uma feature que enxerga o futuro. Aqui ela
> **não é feature**: define o **eixo do tempo** do estudo. É o uso padrão e legítimo dela na
> literatura de risco de crédito. Saiba explicar essa distinção — é uma pergunta provável.

**Kaplan-Meier (6.2).** Curva S(t) não-paramétrica por term e por grade. O **teste log-rank**
entre 36 e 60 meses dá **χ² ≈ 25.335, p < 0,001** — as curvas de sobrevivência são
inequivocamente distintas.

**Modelo de Cox (6.3) — hazard ratios:**

| Fator | Hazard Ratio | Leitura |
|---|---|---|
| Grade (por passo A→B→C…) | 1,44 | cada degrau de grade multiplica o risco instantâneo por 1,44 |
| Term 60 meses | 1,19 | 60 meses acelera o default |
| DTI (por ponto) | 1,003 | +10 pontos de DTI ⇒ ~1,03× o hazard |
| log(renda) | 0,85 | mais renda retarda o default |

**Vintage via sobrevivência (6.4).** Compara safras num **horizonte comum** (default acumulado
em 12/24/36 meses), em vez do default rate bruto — que é injusto porque safras recentes tiveram
menos tempo de maturar. Para as coortes **maduras (≤ 2015)**, o default em 36 meses sobe de
~21 % (2009–2013) para **~26–31 % (2014–2015)** — confirmando, por um caminho independente, a
deterioração identificada na Seção 4.

---

## Parte 3 — Banco de perguntas difíceis (e como responder)

> Cada resposta abaixo é curta de propósito. Diga a frase-chave, depois pare. Não floreie.

**P1. "Por que o hazard ratio de term60 é só 1,19, se o efeito marginal na logística é +6,7
p.p.? Parece inconsistente."**
R: "Não é — medem coisas diferentes. O AME é o efeito **cumulativo** sobre a probabilidade de
default em algum momento. O HR é o efeito sobre o risco **instantâneo, por unidade de tempo**.
Loans de 60 meses espalham seus defaults numa janela duas vezes mais longa, então o risco
*por mês* é diluído mesmo quando o risco *total* é bem maior. Os dois resultados são
consistentes: 60 meses é mais arriscado, e a sobrevivência mostra que também é mais arriscado
por mais tempo."

**P2. "Sua análise de sobrevivência tem viés — você só usou loans já resolvidos."**
R: "Correto, e é por isso que eu sinalizo explicitamente no notebook. A base do projeto, por
definição-alvo, contém apenas Fully Paid e Charged Off. Para as coortes **maduras (≤ 2015)**
isso é inofensivo — esses loans já chegaram todos ao desfecho. Para **2016–2018** há viés de
seleção: loans ainda `Current` ficaram de fora, e os defaults precoces resolvem primeiro, então
as safras recentes super-representam quem quebrou rápido. Por isso o 'default em 12 meses' de
2017–2018 aparece inflado e **eu digo, no próprio notebook, para não lê-lo como taxa final**.
A correção de produção é incluir os loans `Current` como observações **censuradas na data do
snapshot** — está escrito como recomendação metodológica."
*(Admitir isto antes de ser perguntado vale mais do que defendê-lo depois.)*

**P3. "Por que statsmodels e não lifelines / scikit-survival?"**
R: "Para não introduzir uma dependência nova. `statsmodels` já está na stack pinada do projeto
e oferece `SurvfuncRight` (Kaplan-Meier), `survdiff` (log-rank) e `PHReg` (Cox). Mesma
matemática, zero risco de conflito de versão."

**P4. "O modelo de Cox supõe riscos proporcionais. Você testou essa hipótese?"**
R: "Não formalmente neste notebook — é uma limitação que eu reconheço. Os hazard ratios devem
ser lidos como **efeito médio** ao longo do acompanhamento. O passo seguinte natural seria um
teste de resíduos de Schoenfeld; se a proporcionalidade falhar, a resposta é um termo de
interação com o tempo ou um modelo estratificado. Para o nível desta análise — confirmar
direção e ordem de grandeza dos fatores — o Cox padrão é adequado."

**P5. "AUC de 0,68 é baixo. O modelo presta?"**
R: "Para crédito *unsecured retail*, AUC na casa de 0,68–0,72 é normal — o desfecho tem um
componente macroeconômico e idiossincrático grande e irredutível. Mas o ponto-chave: este
modelo **não é para prever**, é para **explicar** associações ajustadas. O AUC entra aqui
apenas como evidência de que o ranking **sobrevive ao tempo**, não como métrica de produto."

**P6. "Por que não corrigiu o desbalanceamento de 80/20 com SMOTE ou pesos de classe?"**
R: "Porque seria errado para o objetivo. SMOTE e reponderação otimizam métricas de
classificação; aqui eu estimo **odds ratios e efeitos marginais inferenciais**. Reponderar
distorceria o intercepto e as probabilidades previstas — exatamente o que a Seção 5.5 precisa
medir sem contaminação. O desbalanceamento é reportado como característica da amostra, não
'corrigido'."

**P7. "A recalibração isotônica melhorou o Brier de 0,166 só para 0,163. Valeu a pena?"**
R: "A isotônica está no notebook como **referência diagnóstica** — mostra o teto do ganho
possível só recalibrando, sem mudar as features. O ganho pequeno é, ele mesmo, uma informação:
o problema das safras recentes não é só de nível, é também de poder discriminante, que
recalibração nenhuma recupera. A recomendação real é re-treinar com dados recentes **e**
recalibrar, com monitoramento por safra."

**P8. "Você usou a base 2007–2018 inteira. Não há quebra estrutural nisso?"**
R: "Há, e a análise a torna **visível** em vez de escondê-la. O split temporal mostra um salto
de default rate de 18,5 % para 22,9 %; a calibração mostra o modelo subestimando por causa
disso; o vintage mostra a deterioração começando em 2014–2015. A quebra estrutural não é um
problema a contornar — é um dos achados."

**P9. "Por que tratar `wedding` como protetor (−6,2 p.p.) — não é amostra pequena?"**
R: "É um efeito de composição: quem toma crédito para casamento tende a ter perfil de renda e
emprego mais estável. Eu o reporto como **associação**, não causa, e não construo recomendação
sobre ele justamente porque o N e a representatividade são frágeis. Os fatores que sustentam
recomendação são term, DTI, grade e purpose de capital de giro — todos com N robusto."

**P10. "Qual é, em uma frase, a contribuição desta versão sobre a canônica?"**
R: "A canônica mostra que a combinação term+DTI aparece como o principal padrão observado de
risco. Esta versão **mostra que essa conclusão sobrevive** a três testes mais duros — tempo,
calibração e o eixo temporal do default — e a quantifica em pontos percentuais que um comitê
pode transformar em política."

---

## Parte 4 — Limitações para admitir você mesmo (antes de perguntarem)

1. **Viés de resolução nas safras 2016–2018** da análise de sobrevivência — já detalhado em P2.
   Diga isto de forma proativa.
2. **Proporcionalidade de riscos do Cox não testada formalmente** (Schoenfeld) — P4.
3. **`last_pymnt_d` é pós-originação** — legítima como eixo do tempo, jamais como feature
   preditiva. Deixe a distinção explícita.
4. **Causalidade.** Tudo aqui é **associação ajustada**, não efeito causal. Geografia, purpose e
   verificação especialmente — a Seção 2.8 (versão canônica) já mostra `verification_status`
   como variável endógena.
5. **Premissas de P&L (Seção 7.4)** — LGD, custo de funding e duration são premissas
   documentadas para *ranking relativo*, não projeção de lucro real.
6. **AME de variáveis dummy.** O efeito marginal de uma dummy é, a rigor, uma diferença
   discreta; `get_margeff` a aproxima como contínua. A ordem de grandeza não muda, mas vale
   citar se perguntarem com precisão estatística.

> Regra de ouro da defesa: **quem nomeia a própria limitação controla a conversa.** Quem é
> pego nela, perde.

---

## Parte 5 — O fio condutor (não perca isto de vista)

Tudo na versão avançada orbita a **tese central do CREDENCE**:

> *"O grade é um proxy imperfeito de risco. O principal padrão observado de default não está no
> grade isoladamente, mas na combinação de term longo + DTI elevado + purpose de alto risco."*

Como cada técnica reforça a tese:

- **5.4 / 5.5** — o modelo que carrega essa tese **sobrevive** ao teste temporal (ranking
  estável) e revela honestamente onde para de valer (nível subestimado).
- **5.6** — quantifica a combinação: term (+6,7 p.p.) e DTI (+1,7 p.p./10 pts) são alavancas
  **acionáveis**, e empilhadas levam um Grade C ao território de risco de um Grade E.
- **6.2 / 6.3** — confirma, por um método **independente** (tempo-até-evento), que term e DTI
  aceleram o default — não é artefato da regressão logística.
- **6.4** — confirma a deterioração temporal das safras 2014–2015 também sob a ótica de
  sobrevivência.

**Frase de encerramento sugerida:** "A versão canônica encontrou o padrão. A versão avançada o
**estressou** — temporal, probabilístico e no tempo-até-evento — e ele não quebrou. É essa
robustez que dá ao comitê de crédito confiança para transformar a análise em política."

---

## Glossário de bolso

| Termo | Em uma frase |
|---|---|
| **AUC** | Probabilidade de o modelo dar score maior a um mau pagador que a um bom — mede *ordenação*. |
| **Brier score** | Erro quadrático médio da probabilidade prevista — mede *calibração*; menor é melhor. |
| **Calibração** | P(default)=0,30 corresponde a 30 % de default observado. |
| **Censura à direita** | Loan acompanhado sem o evento até certo ponto — informação parcial, não ausência de evento. |
| **Kaplan-Meier** | Estimador não-paramétrico da curva de sobrevivência S(t). |
| **Log-rank** | Teste de hipótese para diferença entre curvas de sobrevivência. |
| **Hazard ratio** | Efeito multiplicativo de um fator sobre o risco *instantâneo* do evento. |
| **Riscos proporcionais** | Suposição do Cox: o hazard ratio é constante ao longo do tempo. |
| **Efeito marginal médio (AME)** | Variação em p.p. da probabilidade de default por +1 unidade do fator. |
| **Elasticidade** | A leitura de negócio do AME: "+10 p.p. de DTI ⇒ +1,7 p.p. de default". |
| **Drift** | O regime de risco muda no tempo; o modelo treinado no passado descalibra. |
| **Viés de resolução** | Restringir a base a loans já encerrados super-representa quem resolveu rápido. |