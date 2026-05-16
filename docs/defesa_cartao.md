# CREDENCE — Cartão de Defesa (1 página)

*Versão avançada · para levar impresso · números conferidos na execução de referência*

---

### Pitch (decore)
"A canônica responde *quem* inadimple. A avançada responde: o modelo aguenta o tempo? As
probabilidades são confiáveis? E *quando* o default ocorre? Quatro técnicas — e a tese
sobrevive a todas."

### Tese central
Grade é proxy imperfeito. O principal padrão observado é a **combinação** term longo + DTI alto + purpose de risco.
Grade C + 60m + DTI alto ≈ risco de Grade E.

---

### Números-chave

| Técnica | Número | Significado |
|---|---|---|
| **5.4 Temporal** | AUC 0,706 → 0,684 | ranking **aguenta** o tempo |
| | Brier 0,138 → 0,166 | nível **não** aguenta |
| | default 18,5 % → 22,9 % | o regime de risco piorou |
| **5.5 Calibração** | `gap` +3 a +7 p.p., 10/10 decis | modelo **subestima** o risco recente |
| **5.6 Marginais** | Term 60m: **+6,7 p.p.** | alavanca acionável |
| | DTI +10 p.p.: **+1,7 p.p.** | alavanca acionável |
| | Grade C vs A: +19,2 p.p. | grade pesa, mas é atribuído |
| **6 Sobrevivência** | log-rank 36×60m: p < 0,001 | curvas distintas |
| | Cox HR — grade 1,44 · term 1,19 · DTI 1,003 | fatores confirmados, método independente |
| | dataset: 1,24 M loans, 20,9 % eventos | duração mediana 19 meses |

---

### 3 frases que ganham a banca
1. "AUC mede a **ordem**; Brier mede o **número**. O modelo passa no primeiro, falha no segundo
   — e isso é o regime de risco piorando, não um defeito do modelo."
2. "Efeito marginal é a linguagem do comitê: +10 p.p. de DTI ⇒ +1,7 p.p. de default."
3. "A sobrevivência confirma os fatores por um **caminho independente** da logística."

### 3 limitações para admitir primeiro
1. **Viés de resolução** nas safras 2016–2018 (base só tem loans encerrados) → vintage confiável
   só ≤ 2015. Correção: incluir `Current` como censurado no snapshot.
2. **Proporcionalidade do Cox** não testada formalmente (faltou Schoenfeld) → HRs = efeito médio.
3. Tudo é **associação ajustada**, não causalidade.

---

### Perguntas-armadilha → resposta em 1 linha

| Pergunta | Resposta |
|---|---|
| HR de term só 1,19, mas AME +6,7 p.p.? | HR = risco *por mês*; 60m dilui o default numa janela longa. Efeitos consistentes. |
| `last_pymnt_d` não é leakage? | É leakage como *feature*; aqui é o **eixo do tempo**. Uso padrão. |
| AUC 0,68 é baixo? | Normal em *unsecured retail*; o modelo é **explicativo**, não preditivo. |
| Por que não SMOTE? | Objetivo é inferência (OR, AME), não classificação. Reponderar distorce calibração. |
| Por que statsmodels e não lifelines? | Não introduzir dependência nova; mesma matemática. |
| Usou 2007–2018 inteiro — quebra estrutural? | A análise **mostra** a quebra (18,5 %→22,9 %); é um achado, não um problema. |

---

### Fechamento (decore)
"A canônica encontrou o padrão. A avançada o **estressou** — tempo, calibração, tempo-até-evento
— e ele não quebrou. É essa robustez que transforma análise em política de crédito."