# CREDENCE — Roteiro de Slides para Defesa

**Apresentação da versão avançada** (`notebooks/credence_analise_avancado.ipynb`).
9 slides · ~10–12 min · um bloco por técnica. Cada slide traz **título**, **o que mostrar**,
**fala sugerida** e **gancho** para o próximo.

> Convenção: a *fala sugerida* é o que dizer em voz alta — curta de propósito. Não leia o slide.

---

## Slide 1 — Abertura: por que uma versão avançada

**Mostrar:** a tabela "crítica → resposta" (4 linhas).

**Fala:** "A versão canônica responde *quem* inadimple. Esta versão responde o que um comitê de
crédito pergunta em seguida: o modelo ainda funciona quando o tempo passa? As probabilidades são
confiáveis em nível absoluto? E *quando* o default acontece? Quatro técnicas, quatro respostas."

**Gancho:** "Começo pela mais incômoda — testar o modelo fora do tempo."

---

## Slide 2 — Validação temporal (Seção 5.4)

**Mostrar:** curvas ROC treino × teste + a tabela de 4 métricas.

| | Treino 2007–2015 | Teste 2016–2018 |
|---|---|---|
| Default rate | 18,5 % | 22,9 % |
| AUC | 0,706 | 0,684 |
| Brier | 0,138 | 0,166 |

**Fala:** "Treinei só com 2007–2015 e testei em 2016–2018. O AUC quase não cai — o modelo
**ordena** o risco mesmo fora do tempo. Mas o Brier piora: ele erra o **nível**. A causa está na
primeira linha — a inadimplência subiu de 18,5 % para 22,9 %."

**Gancho:** "Ranking não é o mesmo que calibração. É isso que o próximo slide mede."

---

## Slide 3 — Calibração probabilística (Seção 5.5)

**Mostrar:** diagrama de confiabilidade (curva do logit acima da diagonal).

**Fala:** "Calibração é: quando digo 30 % de risco, 30 % de fato inadimplem? O modelo fica
**acima da diagonal nos dez decis** — subestima o risco em toda a faixa, até 7 pontos
percentuais. Loans que ele pontua em 20 % inadimplem perto de 28 %."

**Ponto de negócio:** "Provisão e pricing dependem do nível absoluto. Usar a probabilidade crua
**subprovisiona** a carteira recente."

**Gancho:** "Isso não se conserta trocando o modelo — conserta-se recalibrando e monitorando."

---

## Slide 4 — Efeitos marginais e elasticidade (Seção 5.6)

**Mostrar:** gráfico de barras dos AMEs (vermelho/verde).

| Fator | Efeito sobre P(default) |
|---|---|
| Grade C (vs A) | +19,2 p.p. |
| Term 60 meses | **+6,7 p.p.** |
| DTI (+10 p.p.) | **+1,7 p.p.** |
| Renda (+US$ 10 mil) | −0,43 p.p. |

**Fala:** "Odds ratio não decide nada num comitê. Efeito marginal, sim: '+10 pontos de DTI ⇒
+1,7 p.p. de default, mantendo o resto constante'. Grade pesa mais, mas é atribuído. **Term e
DTI são as alavancas que o underwriting controla.**"

**Gancho:** "E quando você empilha essas alavancas — é a tese do projeto."

---

## Slide 5 — A tese, quantificada

**Mostrar:** soma visual: Grade C (+19,2) + Term 60 (+6,7) + DTI alto (+3,3) → ≈ Grade E (+28,1).

**Fala:** "Um Grade C que também toma 60 meses e tem DTI elevado acumula um excedente de risco
que o leva ao **território de um Grade E**. A tese do CREDENCE deixa de ser uma frase e vira um
número: a combinação, não o grade isolado, é o principal padrão observado de risco."

**Gancho:** "A logística mostra *se* o default acontece. Falta mostrar *quando*."

---

## Slide 6 — Análise de sobrevivência: o conceito (Seção 6)

**Mostrar:** curvas Kaplan-Meier por term (36 × 60 meses).

**Fala:** "Crédito é tempo-até-evento. Um loan de 60 meses que quebra no mês 10 não é o mesmo
que um que quebra no mês 55 — e a logística não distingue. A sobrevivência modela o *quando* e
trata `Fully Paid` corretamente: não é um 'não-evento', é uma observação **censurada**.
Log-rank entre 36 e 60 meses: p < 0,001 — as curvas são inequivocamente distintas."

**Gancho:** "Isolando o efeito de cada fator no tempo — o modelo de Cox."

---

## Slide 7 — Cox: hazard ratios (Seção 6.3)

**Mostrar:** tabela de HRs.

| Fator | Hazard Ratio |
|---|---|
| Grade (por passo) | 1,44 |
| Term 60 meses | 1,19 |
| DTI (por ponto) | 1,003 |
| log(renda) | 0,85 |

**Fala:** "O Cox confirma, por um método **independente** da logística, as mesmas direções:
grade, term e DTI aceleram o default; renda o retarda. Não é artefato da regressão — é o padrão
real dos dados."

**Antecipar a pergunta:** "Se perguntarem por que o HR de term é só 1,19 — hazard é risco *por
unidade de tempo*; 60 meses espalha o default numa janela mais longa, então o risco mensal é
diluído mesmo com risco total maior."

**Gancho:** "Por fim, o vintage — e aqui eu mesmo aponto um limite."

---

## Slide 8 — Vintage via sobrevivência (Seção 6.4)

**Mostrar:** curvas de default acumulado em 12/24/36 meses por safra.

**Fala:** "Comparar default rate bruto entre safras é injusto — as recentes maturaram menos. A
sobrevivência compara num **horizonte comum**. Para as safras maduras, até 2015, o resultado
confirma a deterioração de 2014–2015 já vista na decomposição. **Sou eu quem aponta o limite:**
as safras 2016–2018 sofrem viés de resolução — a base só tem loans já encerrados — e não devem
ser lidas como taxa final."

**Gancho:** "O que tudo isso significa para a decisão."

---

## Slide 9 — Fechamento

**Mostrar:** os 4 ícones de técnica + a tese central.

**Fala:** "A versão canônica encontrou o padrão. Esta versão o **estressou** — no tempo, na
probabilidade e no tempo-até-evento — e ele não quebrou. O modelo ordena bem fora do tempo,
mas subestima o nível porque o risco piorou; term e DTI são alavancas acionáveis e quantificadas;
e a sobrevivência confirma tudo por um caminho independente. É essa robustez que dá ao comitê
confiança para transformar a análise em política de crédito."

**Encerrar:** "Posso detalhar qualquer uma das técnicas."

---

## Apêndice — slides de reserva (só se perguntarem)

- **R1.** `last_pymnt_d` e leakage — leakage como *feature*; aqui é o *eixo do tempo*. Uso padrão.
- **R2.** Por que statsmodels e não lifelines — não introduzir dependência nova; mesma matemática.
- **R3.** Proporcionalidade do Cox não testada formalmente — HRs lidos como efeito médio; passo
  seguinte seria resíduo de Schoenfeld.
- **R4.** Por que não SMOTE / pesos de classe — objetivo é inferência (odds ratios, AMEs), não
  classificação; reponderar distorceria o intercepto e a calibração.