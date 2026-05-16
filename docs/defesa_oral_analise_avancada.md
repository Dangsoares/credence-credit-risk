# Defesa Oral - Analise Avancada CREDENCE

Documento de apoio para sustentar a analise do notebook `notebooks/credence_analise_avancado.ipynb`.

## 1. Abertura sugerida

Esta analise avalia risco de credito no Lending Club entre 2007 e 2018, usando uma base modelavel de 1.306.387 emprestimos com desfecho conhecido. A tese central e que o grade e um bom proxy inicial de risco, mas e insuficiente para tomada de decisao. O risco mais acionavel aparece na combinacao entre grade, prazo, DTI, finalidade, geografia e precificacao.

O resultado principal nao e "cortar os piores grades". A leitura mais madura e: alguns segmentos de alto default podem ser rentaveis se a taxa compensa o risco, enquanto segmentos intermediarios podem destruir valor por estarem mal precificados. Por isso, a recomendacao e reprecificar ou restringir combinacoes especificas com P&L risco-ajustado negativo, e nao aplicar uma politica cega por grade.

## 2. Mensagem central para defender

A inadimplencia nao aparece concentrada em um unico fator isolado. O padrao observado e multidimensional:

- Grades D/E possuem risco estruturalmente maior: 33,0% de default contra 16,4% nos demais grades.
- Prazo de 60 meses esta associado a default praticamente duas vezes maior que 36 meses: 32,6% contra 16,1%.
- DTI elevado aparece associado a maior risco mesmo dentro do mesmo grade.
- Grade C com 60 meses e DTI acima de 20 chega a 31,0% de default, contra 22,5% do Grade C geral.
- A simulacao direcional de P&L mostra que alto default nao significa necessariamente destruicao de valor.

Frase de defesa:

> "A analise mostra que risco de credito nao deve ser lido apenas pela etiqueta do grade. A decisao boa e a que combina probabilidade de default, prazo, capacidade de pagamento e retorno ajustado ao risco."

## 3. O que a versao avancada adiciona

O notebook avancado nao e apenas uma EDA. Ele adiciona quatro camadas de maturidade analitica:

1. Validacao temporal: treina em 2007-2015 e testa em 2016-2018.
2. Calibracao probabilistica: verifica se as probabilidades previstas batem com o default observado.
3. Efeitos marginais: traduz coeficientes estatisticos para pontos percentuais de default.
4. Analise de sobrevivencia: avalia quando o default ocorre, nao apenas se ocorre.

Como defender:

> "Eu parti de uma analise descritiva, mas avancei para uma leitura de comite de credito: estabilidade fora do tempo, calibracao, interpretabilidade economica e risco ao longo da vida do contrato."

## 4. Base e definicao de inadimplencia

A base bruta possui 2.260.668 linhas. A base modelavel possui 1.306.387 emprestimos, equivalente a 57,8% do total. Foram excluidos 954.281 registros com desfecho ainda desconhecido ou nao terminal.

Regra usada:

- Default: `Charged Off`, `Default` e variantes de charge-off.
- Non-default: `Fully Paid` e variantes.
- Excluidos da analise principal: `Current`, `In Grace Period`, `Late (16-30 days)`, `Late (31-120 days)` e `Issued`.

Por que isso importa:

Taxa de inadimplencia depende diretamente da definicao do denominador. Incluir `Current` como bom pagador reduziria artificialmente a taxa de default, porque muitos contratos ainda nao tiveram tempo de maturar. Por isso, a analise principal usa apenas contratos com desfecho conhecido.

Resposta se perguntarem sobre `Late (31-120 days)`:

> "Na analise principal eu preservei uma definicao conservadora e terminal de default. `Late (31-120 days)` foi deixado fora porque ainda pode curar ou migrar para charge-off. Para self-service BI, eu deixei essa categoria disponivel no export como definicao alternativa, desde que o dashboard declare a regra."

## 5. Principais achados quantitativos

### 5.1 Grade e risco

Default por grade:

| Grade | Default |
|---|---:|
| A | 6,1% |
| B | 13,4% |
| C | 22,5% |
| D | 30,4% |
| E | 38,6% |
| F | 45,2% |
| G | 49,8% |

Interpretacao:

O grade ordena risco muito bem. A taxa sobe monotonicamente de A para G. Mas o grade nao captura toda a heterogeneidade dentro de cada grupo. Dentro do Grade C, por exemplo, o risco varia bastante quando combinamos prazo e DTI.

Como falar:

> "O grade funciona como ranking geral, mas nao basta para politica. Ele separa A de G, mas esconde combinacoes ruins dentro de grades intermediarios."

### 5.2 Prazo

Default por prazo:

| Prazo | Default |
|---|---:|
| 36 meses | 16,1% |
| 60 meses | 32,6% |

Interpretacao:

O prazo de 60 meses aparece como um dos sinais mais fortes de risco. Ele alonga a exposicao, aumenta incerteza sobre renda futura e amplia a janela em que eventos adversos podem ocorrer.

Importante: a analise mostra associacao, nao causalidade. A formulacao correta e:

> "Prazo de 60 meses esta associado a maior inadimplencia, mesmo controlando por outras variaveis no modelo explicativo."

### 5.3 Renda, DTI e capacidade de pagamento

Default por renda cai de 23,8% em clientes abaixo de US$ 40 mil para 14,7% em clientes acima de US$ 150 mil. Ainda assim, renda isolada nao resolve o problema. O DTI e mais util para risco porque captura comprometimento da renda.

Na regressao, cada aumento de 10 pontos percentuais em DTI esta associado a +1,66 p.p. na probabilidade de default. Ja US$ 10 mil adicionais de renda reduzem a probabilidade em apenas 0,43 p.p.

Como defender:

> "Renda alta ajuda, mas nao compensa automaticamente endividamento alto. Para politica de credito, DTI e mais acionavel do que renda bruta isolada."

### 5.4 Verificacao de renda

Resultado observado: `Not Verified` tem menor inadimplencia em todas as faixas de renda, enquanto `Verified` tem maior inadimplencia.

Interpretacao senior:

Isso nao significa que verificar renda aumenta risco. Significa que `verification_status` e endogeno. O Lending Club provavelmente verificava mais os pedidos que ja pareciam suspeitos. Logo, `Verified` e um marcador de selecao previa, nao uma causa.

Como defender:

> "Eu nao uso verification_status como alavanca de politica porque ele carrega vies de selecao. A pergunta correta nao e se verificar renda causa default, mas por que certos clientes foram selecionados para verificacao."

### 5.5 Geografia

A analise separa default bruto de residual geografico controlado pelo mix de grades.

Estados com maior residual:

| Estado | Residual |
|---|---:|
| MS | +5,00 p.p. |
| NE | +4,63 p.p. |
| AR | +3,55 p.p. |
| OK | +3,21 p.p. |
| LA | +3,06 p.p. |

Estados com menor residual:

| Estado | Residual |
|---|---:|
| DC | -5,70 p.p. |
| ME | -5,36 p.p. |
| VT | -5,30 p.p. |
| OR | -5,23 p.p. |
| NH | -4,67 p.p. |

Interpretacao:

A geografia aparece associada a risco residual mesmo apos controlar por composicao de grade. Isso pode refletir fatores macro locais, como mercado de trabalho, custo de vida ou ciclos economicos regionais.

Ressalva regulatoria:

Geografia nao deve ser usada como hard cutoff de underwriting. Pode apoiar monitoramento, caps de exposicao e pricing documentado, com cuidado de fair lending.

## 6. Hipotese D/E

Comparacao:

- D/E: 288.089 loans, 33,0% default.
- Demais grades: 1.018.298 loans, 16,4% default.
- Diferenca: 16,6 p.p.
- IC 95%: [16,42; 16,79] p.p.
- Qui-quadrado: 38.584,79, p aproximadamente zero.
- V de Cramer: 0,1719, efeito medio.

Como interpretar:

O resultado sustenta que D/E sao estruturalmente mais arriscados. Mas o V de Cramer mostra que grade group sozinho nao captura tudo. Existe risco relevante fora de D/E e existe heterogeneidade dentro de cada grade.

Frase boa:

> "A hipotese D/E e estatisticamente forte, mas gerencialmente incompleta. Ela identifica onde ha risco estrutural, mas nao onde esta a maior oportunidade economica."

## 7. Validacao temporal

O modelo foi treinado em 2007-2015 e testado em 2016-2018.

| Recorte | Default | AUC | Brier |
|---|---:|---:|---:|
| Treino 2007-2015 | 18,5% | 0,7060 | 0,1378 |
| Teste 2016-2018 | 22,9% | 0,6841 | 0,1660 |

Interpretacao:

O AUC cai pouco, de 0,706 para 0,684. Isso significa que o modelo ainda ordena risco razoavelmente bem fora do tempo. Mas o Brier piora, porque o nivel de inadimplencia das safras recentes e maior. O modelo aprendeu um regime mais brando e subestima o risco em 2016-2018.

Como defender:

> "O modelo rankeia razoavelmente bem fora do tempo, mas suas probabilidades absolutas nao devem ser usadas sem recalibracao."

## 8. Calibracao

No teste 2016-2018, o modelo subestima o default em todos os decis de score. O gap chega a cerca de +7 p.p. em decis intermediarios. Exemplo: loans previstos perto de 20% de risco observam default perto de 28%.

A recalibracao isotonica melhora o Brier de 0,1660 para 0,1632. A melhora e real, mas limitada.

Interpretacao:

O problema nao e apenas ranking. Para provisao, capital e pricing, a probabilidade precisa estar calibrada. Um AUC aceitavel nao basta.

Frase de defesa:

> "AUC responde se eu consigo ordenar quem e mais arriscado. Calibracao responde se 30% previsto realmente vira 30% observado. Para credito, as duas coisas importam."

## 9. Efeitos marginais

Principais efeitos marginais medios:

| Variavel | Efeito |
|---|---:|
| Grade G vs A | +33,5 p.p. |
| Grade F vs A | +31,2 p.p. |
| Grade E vs A | +28,1 p.p. |
| Grade D vs A | +24,4 p.p. |
| Grade C vs A | +19,2 p.p. |
| Grade B vs A | +11,5 p.p. |
| Small business | +8,1 p.p. |
| Term 60 | +6,7 p.p. |
| DTI +10 p.p. | +1,66 p.p. |
| Renda +US$ 10 mil | -0,43 p.p. |

Como interpretar:

Grade domina em magnitude, mas grade e atribuido pelo sistema de score. As alavancas de politica sao term, DTI, limites de exposicao e precificacao.

Resposta se perguntarem por que nao usar apenas odds ratio:

> "Odds ratio e estatisticamente correto, mas pouco intuitivo para comite. Efeito marginal traduz a leitura para pontos percentuais de default, que e a unidade de decisao de risco."

## 10. Analise de sobrevivencia

A sobrevivencia responde uma pergunta que a regressao logistica nao responde: quando o default ocorre.

Achados:

- Log-rank 36m x 60m: qui-quadrado de 25.335,2, p aproximadamente zero.
- Cox:
  - Cada passo de grade multiplica o hazard por 1,44.
  - Prazo de 60 meses multiplica o hazard por 1,19.
  - Cada ponto de DTI multiplica o hazard por 1,003.
  - Log-renda tem HR 0,85, indicando associacao protetora.

Interpretacao:

Emprestimos de 60 meses nao apenas inadimplem mais. Eles tambem carregam risco por mais tempo. Isso importa para capital, provisionamento e desenho de politica.

Ressalva importante:

A analise de vintage por sobrevivencia e confiavel para safras maduras ate 2015. Para 2016-2018, a base com desfechos resolvidos super-representa defaults precoces, pois muitos `Current` foram excluidos. Em producao, os `Current` deveriam entrar como observacoes censuradas na data do snapshot.

Frase de defesa:

> "A sobrevivencia mostra que risco de credito e tempo-dependente. Dois loans com mesmo default final podem ter severidade economica diferente se um quebra no mes 10 e outro no mes 55."

## 11. Combinacoes toxicas

Benchmark:

- Grade F geral: 45,2% default.
- Grade C geral: 22,5% default.
- Grade C + 60 meses + DTI > 20: 31,0% default.

Leitura:

A tese e parcialmente confirmada. Grade C + 60m + DTI > 20 nao chega ao default medio do Grade F, ficando 14,3 p.p. abaixo. Mas e 1,4 vez mais arriscado que o Grade C medio. Portanto, o grade e um proxy imperfeito: ha bolsos de risco elevado dentro de grades intermediarios.

Frase de defesa:

> "Eu nao afirmo que todo Grade C vira Grade F. O ponto e mais preciso: certas combinacoes dentro do Grade C se comportam muito pior que o Grade C medio, e a politica precisa enxergar essa heterogeneidade."

## 12. Simulacao direcional de P&L

A secao de P&L deve ser defendida como simulacao direcional de rentabilidade risco-ajustada, nao como lucro real da carteira.

Premissas:

- LGD: 60%.
- Custo de funding: 4% a.a.
- Duration aproximada: term / 24 anos.
- Juros coletados em default: 50% dos juros esperados.

Resultado mais importante:

Cortar as 15 combinacoes com maior default seria uma estrategia ingenua. Essas combinacoes somam P&L estimado positivo de US$ 33,1 milhoes. Corta-las destruiria valor na simulacao.

Estrategia risco-ajustada:

- Cortar ou reprecificar 32 combinacoes com P&L negativo.
- 251.825 loans, 19,3% da carteira.
- Volume de US$ 3,14 bi.
- Ganho liquido estimado de US$ 36,8 milhoes.
- Default da carteira cairia de 20,09% para 18,87%, reducao de 122 bps.

Interpretacao senior:

A destruicao de valor nao esta concentrada apenas em F/G. Ela aparece muito no meio mal precificado, especialmente combinacoes com prazo, DTI e geografia de risco. Isso e uma leitura mais sofisticada do que simplesmente cortar os piores grades.

Frase de defesa:

> "Default alto e risco. P&L negativo e problema economico. A melhor politica nao e a que minimiza default a qualquer custo, mas a que melhora retorno ajustado ao risco."

## 13. Looker e self-service BI

A base de exportacao para Looker tem 1.328.284 linhas e 26 colunas. Ela inclui `Late (31-120 days)` para permitir definicao alternativa de default no dashboard. Por limite de upload, foi gerada uma amostra estratificada por grade e default_flag com 500.001 linhas e 81,8 MB.

Ponto de governanca:

Toda taxa no dashboard deve mostrar percentual e N absoluto. Exemplo: "32,2% (N = 295.300)". Isso evita conclusoes baseadas em celulas pequenas ou visualmente chamativas, mas estatisticamente frageis.

## 14. Perguntas dificeis e respostas

### A analise prova causalidade?

Nao. A analise estima associacoes controladas e padroes consistentes. Termos como "causa" e "prova" devem ser evitados. Para causalidade seria necessario desenho causal, experimento, variavel instrumental, diff-in-diff ou outra estrategia apropriada.

Resposta curta:

> "Eu trato como evidencia observacional para decisao de risco, nao como prova causal."

### Por que excluir `Current`?

Porque `Current` ainda nao tem desfecho final. Classificar como bom pagador contaminaria a taxa de inadimplencia, principalmente em safras recentes.

Resposta curta:

> "Eu exclui `Current` da analise principal para nao misturar contratos maduros com contratos ainda em observacao."

### Por que o periodo completo inclui 2018, mas voce fala de vies em 2016-2018?

Porque a analise principal usa todo o periodo disponivel com desfecho conhecido. Mas, para vintage/sobrevivencia, safras recentes exigem cautela porque muitos contratos ainda estavam em andamento e foram excluidos da base terminal.

Resposta curta:

> "Uso o periodo completo para coerencia da base oficial, mas qualifico a leitura temporal quando a maturacao da safra afeta a interpretacao."

### Por que a regressao nao e modelo de producao?

Porque ela foi usada como ferramenta explicativa. Um modelo de producao exigiria validacao temporal formal, calibracao, estabilidade, monitoramento de drift, fairness, governanca de features, rejeicao inferida e criterios de aprovacao.

Resposta curta:

> "A regressao aqui ajuda a entender associacoes ajustadas. Nao estou propondo colocar esse logit em producao."

### Por que nao aplicar balanceamento de classe?

Porque o objetivo da regressao em `statsmodels` e inferencial, nao otimizar classificacao. A taxa 80/20 e uma caracteristica real da carteira. Balancear artificialmente poderia alterar a interpretacao dos coeficientes e da taxa base.

Resposta curta:

> "Como a leitura e explicativa, mantive a distribuicao real da carteira e reportei o desbalanceamento como caracteristica da amostra."

### AUC de 0,68 e bom?

Para um modelo simples e explicativo, e razoavel. Mas nao basta para producao. O ponto mais relevante e que o modelo mantem ordenacao fora do tempo, embora precise recalibrar probabilidades.

Resposta curta:

> "O AUC mostra ranking util; a calibracao mostra que a probabilidade crua ainda nao pode ir para provisao ou pricing."

### Por que P&L nao e lucro real?

Porque usa premissas simplificadas de LGD, funding, duration e juros recebidos antes do default. Nao inclui recuperacao real, pre-pagamento, servicing, impostos, custo operacional ou curva de capital.

Resposta curta:

> "E uma simulacao direcional para comparar segmentos, nao uma contabilidade de lucro realizado."

### Pode usar geografia em credito?

Com muito cuidado. Geografia pode ser usada para monitoramento, pricing documentado ou caps de exposicao, mas nao como hard cutoff automatico sem avaliacao regulatoria e fair lending.

Resposta curta:

> "Eu uso geografia como sinal de monitoramento e segmentacao de risco, nao como regra cega de exclusao."

### Por que verificar renda nao reduz risco?

Porque a verificacao nao parece aleatoria. Clientes verificados provavelmente ja eram mais suspeitos no funil. Logo, o status de verificacao reflete selecao previa.

Resposta curta:

> "Verification_status e endogeno. Ele diz algo sobre a triagem do Lending Club, nao necessariamente sobre o efeito de verificar renda."

## 15. Roteiro de apresentacao de 5 minutos

1. Comece pela tese: grade e util, mas insuficiente.
2. Explique a base: 1,3M contratos com desfecho conhecido, 2007-2018, default terminal.
3. Mostre o padrao basico: default cresce de A para G e 60 meses dobra o risco.
4. Mostre a virada analitica: dentro do Grade C, prazo e DTI criam bolsos de risco muito acima da media.
5. Traga a regressao: efeitos controlados confirmam grade, term, DTI e purpose como sinais relevantes.
6. Traga a validacao temporal: modelo rankeia fora do tempo, mas subestima o risco recente.
7. Traga sobrevivencia: risco tambem depende do tempo ate default.
8. Feche com P&L: default alto nao e sinonimo de valor negativo; decisao correta e risco-ajustada.
9. Recomende: reprecificar ou restringir combinacoes especificas, monitorar calibracao e levar a base para BI governado.

## 16. Roteiro de apresentacao de 2 minutos

> "A analise usa 1,3M emprestimos Lending Club de 2007 a 2018 com desfecho conhecido. O primeiro resultado confirma o esperado: grades piores inadimplem mais, de 6,1% no Grade A para 49,8% no Grade G. Mas o achado principal e que o grade sozinho esconde risco. Prazo de 60 meses tem default de 32,6%, contra 16,1% em 36 meses, e Grade C com 60 meses e DTI acima de 20 chega a 31,0%, bem acima do Grade C medio de 22,5%.
>
> Para sustentar isso, eu uso regressao logistica como ferramenta explicativa, efeitos marginais, validacao temporal, calibracao e sobrevivencia. O modelo treinado em 2007-2015 ainda ordena bem em 2016-2018, com AUC de 0,684, mas subestima o risco, entao probabilidades precisariam de recalibracao antes de pricing ou provisao.
>
> A parte mais importante para negocio e a simulacao direcional de P&L. Ela mostra que cortar os segmentos de maior default nao e necessariamente bom, porque alguns cobram juros suficientes para compensar o risco. A melhor recomendacao e reprecificar ou restringir as 32 combinacoes com P&L negativo, que representam 19,3% da carteira e geram ganho estimado de US$ 36,8 milhoes na simulacao."

## 17. Frases que ajudam na banca

- "Nao estou defendendo corte cego por grade, estou defendendo decisao por combinacao de risco e retorno."
- "AUC mede ranking; calibracao mede se a probabilidade pode ser usada em dinheiro."
- "A regressao e explicativa, nao um modelo final de producao."
- "A simulacao de P&L e direcional, nao lucro contabil."
- "O risco observado e compativel com mix, prazo, DTI e precificacao, mas nao afirmo causalidade sem desenho causal."
- "Self-service BI sem definicao de default e sem N absoluto vira risco de governanca."

## 18. Frases a evitar

- "O prazo causou default."
- "A regressao prova que..."
- "O P&L real da carteira e..."
- "Basta cortar F e G."
- "Geografia pode ser usada para negar credito."
- "Verified e pior porque verificar renda aumenta risco."

Substitua por:

- "Esta associado a..."
- "E compativel com..."
- "A simulacao sugere..."
- "Aparece como principal vetor observado..."
- "Requer avaliacao regulatoria e fairness..."
- "E um marcador endogeno de triagem..."

## 19. Limitacoes reconhecidas

1. A base e observacional, portanto as conclusoes sao associativas.
2. A definicao principal exclui contratos em andamento, adequada para default terminal, mas exige cuidado em safras recentes.
3. A analise de sobrevivencia seria mais robusta em producao incluindo `Current` como censura a direita.
4. A simulacao de P&L usa premissas simplificadas e serve para ranking relativo.
5. O dataset publico nao traz todas as variaveis que uma fintech real teria, como score interno, historico bancario completo, recuperacao real, pre-pagamento e custos operacionais.
6. Variaveis como geografia e verificacao exigem cuidado de governanca, vies e regulacao.

## 20. Recomendacoes executivas

1. Manter grade como eixo de risco, mas nao como unica regra de politica.
2. Criar matriz de politica por grade, prazo, DTI, purpose e geo_tier.
3. Reprecificar ou restringir combinacoes com P&L risco-ajustado negativo.
4. Evitar corte cego de alto default sem avaliar spread e perda esperada.
5. Monitorar calibracao por safra, especialmente quando o regime de default muda.
6. Usar survival/vintage para acompanhar maturacao das safras.
7. Documentar definicao de default em todo dashboard e relatorio.
8. Exibir sempre percentual e N absoluto no Looker.
9. Tratar `verification_status` como variavel descritiva/endogena, nao como alavanca causal.
10. Submeter qualquer uso de geografia a revisao de fair lending.

## 21. Conclusao para encerramento

A analise avancada mostra maturidade porque nao para na taxa de inadimplencia. Ela conecta risco estatistico, estabilidade temporal, calibracao, sobrevivencia e retorno ajustado ao risco.

A principal conclusao e que a FinLend nao deveria gerir credito apenas por grade. O grade ordena risco, mas a oportunidade economica esta em identificar combinacoes mal precificadas: prazo longo, DTI elevado, finalidade mais arriscada e geografia residual. A recomendacao nao e reduzir risco a qualquer custo, e melhorar retorno ajustado ao risco com politica segmentada, governanca de metricas e monitoramento recorrente.

Fechamento sugerido:

> "Se eu tivesse que transformar esta analise em uma decisao de negocio, eu nao levaria uma regra unica de aprovacao. Eu levaria uma matriz de acoes: aprovar, reprecificar, limitar prazo, reduzir ticket ou revisar manualmente, de acordo com o P&L risco-ajustado e a estabilidade do segmento."
