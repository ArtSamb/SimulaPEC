# SimulaPEC
Programa computacional, baseado em Python, desenvolvido como parte de uma pesquisa de pós-doutorado que possui como objetivo gerar gráficos e tabelas de aceitação e rejeição de mapeamentos com escalas grandes (1:1000 ; 1:2000; 1:5000; 1:10000) analisando seus pontos de controles e seus respectivos erros nos eixos X e Y (ou Leste e Norte).

## Introdução teórica
Na atual norma brasileira (Brasil - 1984), o decreto nº 89.817 de 20 de Junho de 1984 estabelece as Instruções Reguladoras das Normas Técnicas da Cartografia Nacional. No entanto, este foi elaborado para produtos analógicos em escalas pequenas (1:25000 ou menores), os quais são de competência do IBGE (Instituto Brasileiro de Geografia e Estatística). Neste trabalho, têm-se em conta os produtos em meio digital e procura-se a implementação de uma norma nos moldes da ABNT (Associação Brasileira de Normas Técnicas) que visam escalas grandes.

Antes de darmos continuidade, é necessário explicar algumas nomeclaturas que utilizadas muitas vezes nesse trabalho:
- Pontos de Controles (PCs) = São pontos fixos de um mapeamento (pontos bem definidos e identificáveis, como cantos de boca de lobo) que são utilizados para a aplicação do controle de qualidade posicional.
- Padrão de Exatidão Cartográfica (PEC) = Também chamado de 'Erro Admissível', corresponde ao valor máximo (normalmente em metros) aceitável que um erro possa assumir num mapeamento. Esse valor varia a depender da classe que se está analisando e qual a escala utilizada.
- Aceitação / Rejeição = Esse valor, dado em porcentagem, corresponde a quantidade de pontos que está dentro (ou fora) do determinado pela norma.
- Teste da Norma Brasileira = Também podendo ser chamado de teste direto, corresponde a norma vigente em relação a análise dos PCs. É estabelecido que o valor de aceitação de um mapeamento tem que ser no mínimo de 90% (ou ter uma rejeição máxima de 10%).
- Teste de Precisão = Um tipo de teste proposto pela pesquisa de pós-doutorado utilizando a Estatística para a análise dos PCs. O teste em questão se resume ao teste do Qui quadrado. A aceitação / rejeição utilizado também foi de 90% / 10%.

Para mais detalhes sobre a pesquisa, recomenda-se a leitura do documento "PosDocV3" disponível acima.


# SimulaPEC - O aplicativo
Esta parte será destinada a falar sobre o aplicativo em si. Recomendamos que ao testar, opte para as versões mais recentes, visto que elas sempre apresentarão melhoras em relação as antigas, seja comesticamente ou conceitualmente; sempre será informado qual mudança foi feita. Todas as versões até o presente momento apresentaram "teste" no nome (junto com a data de modificação), devido ao fato que ainda não temos certeza de como o produto final será vizualmente falando. Qualquer alteração feita na interface será atualizada nessa parte.

<img width="336" height="440" alt="Simulapec_interface_inicial" src="https://github.com/user-attachments/assets/fd45ca45-0af8-4725-b7a2-44405234d8e8" />

Na imagem acima, tem-se a interface inicial do SimulaPEC. Para começar o processo, é necessário preencher os 6 parâmetros acima. Estes são:
- "Número de PCs" = Bem direto, é o número de Pontos de Controles do mapeamento em análise.
- "Erro admissível (PEC)" = É o valor máximo do erro permitido em metros. Este valor varia a depender da classe e da escala utilizada.
- "%PCs acima do PEC" = Basicamente, qual o nível de rejeição admitido. A Norma Brasileira estabelece que seja 10% (não é necessário colocar o '%').
- "Valor Máximo (%)" = Para análise de gráficos e tabelas, utilizamos porcentagens além do estabelecido pela Norma, ou seja, valores maiores e menores que 10% (de rejeição). Esse parâmetro é para determinar qual o valor de rejeição é satisfatório para análise.
- "Intervalo (%)" = Simular ao parâmetro anterior, estabelece por qual valor de rejeição começa e vai aumentando conforme o valor escolhido.
- "Nº de iterações" = Quantidade de vezes que cada grupo de pontos formados serão análises entre si. Mais a frente, será explicado melhor essa parte.

## Processamento
Após colocado os parâmetros para a análise que será feita, aperta o botão "Confirmar" e a seguinte mensagem aparecerá:

<img width="252" height="190" alt="Simulapec_tempo_estimado" src="https://github.com/user-attachments/assets/18593679-e378-42bd-828b-302fac361abe" />

Essa mensagem apresenta o tempo estimado que cada curva dos gráficos levará para ser plotada. Clicando em "Yes", começará a simulação. Clicando em "No", não começará e será apresentada essa mensagem:

<img width="306" height="190" alt="Simulapec_cancelado" src="https://github.com/user-attachments/assets/7a93b290-e644-4dcc-9fc0-0de3cd45a3a6" />

Começando a simulação, as duas barras logo abaixo dos parâmetros irão ser preenchidas. A barra "Progesso" representa o progresso realizado por cada curva, enquanto a barra "Progresso total" representa o progresso da simulação inteira. Logo abaixo está um exemplo:

<img width="336" height="440" alt="Simulapec_exemplo" src="https://github.com/user-attachments/assets/b4b77d66-fcd9-4dd6-b88b-e34daf894b53" />

Um ponto importante citar é o botão de "Cancelar". Quando não tem nenhuma simulação sendo feita, esse botão fica desativado. Quando começa uma, esse botão fica ativado e pode ser clicado a qualquer momento, até o final da simulção. Clicando nele, a mensagem de "A simulação foi interrompida" aparece novamente.

Terminado a simulação, aparecerá um gráfico mostrando o resultado processado. Logo abaixo está um exemplo de um gráfico processado:

<img width="1400" height="600" alt="Figure_1" src="https://github.com/user-attachments/assets/07c37728-a9bd-49e1-87b8-d03b9e869a02" />

Nesse gráfico está presente o resultado das curvas de rejeição tanto do Teste de Precisão quanto do Teste da Norma Brasileira. No eixo das abcissas temos o tamanho da amostra que varia de 0 até 60% dos PCs indo de 5 em 5, ou seja, (0, 5, 10, 15, ... , 60%*PCs). E no eixo das ordenadas temos o Percentual de Rejeição do Mapeamento (PRM%). No tópico seguinte iremos explicar o cada um significa.
Também vale citar, o tempo total de processamento localizado no topo.

Esse gráfico pode ser salvo ou diretamente na imagem ou então apertando o botão "Salvar Gráfico" localizado na Interface inicial. Também pode ser salvo uma panilha contendo todos os dados processados para uma análise mais profunda; basta clicar no botão "Salvar Planilha" também localizado na Interface inicial. Vale a pena citar que nenhum desses botões funcionaram antes de uma simulação ser feita, aparecendo uma mensagem pedindo para ser feita uma simulação antes.

## Teste de Precisão e Norma Brasileira
Vamos começar pelo Teste de Precisão. Como citado anteriormente, o teste é baseado no teste do Qui quadrado.

Logo no começo, uma tabela de pontos é criada, contendo a mesma quantidade de PCs fornecido pelo usuário. Esses pontos são chamados de "Dados Fictícios". Esses dados seguem uma distribuição normal.

Em seguida, grupos de PCs de tamanho n são formados. O tamanho desses grupos variam de 5 em 5 até 60% dos PCs totais, com reposição. Utilizando o grau de liberdade (n-1), é calculado o desvio padrão de cada grupo e depois o Qui quadrado, sendo, para o cálculo deste, utilizado o desvio padrão, o grau de liberdade e o PEC. Tendo esse valor, é comparado com o Qui tabelado, e decidido se foi aceito ou não essa amostragem. Cada grupo passa por esse processo repetidas vezes, decide pelo usuário na parte de "Nº de iterações". O resultado final resulta no PRM%, em outras palavras, qual é a média de vezes que o mapeamento não foi aceito para cada quantidade de PCs em cada nível de rejeição determinada.

Agora, para o Teste da Norma Brasileira.

A norma determina que para cada amostragem, é permitido que até 10% dos PCs tenha um erro acima do PEC. Por isso também é chamado de teste direto. Similar ao Teste de Precisão de Precisão, grupos de tamanho n são formados, o processo é repetido pela quantidade determinada pelo usuário e por fim temos o PRM% para cada nível de rejeição.

A razão de serem utilizados "Dados Fictícios" foi com a intenção de evitar riscos e prejuízos ao consumidor e ao técnico ao analisar um mapeamento. No entanto, caso já tenha sido feito a análise, é possível adicionar esses dados a simulação também. Esses dados são chamados de "Dados Reais".

## Teste de Precisão e Norma Brasileira - Dados Reais
