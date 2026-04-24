# SimulaPEC
Programa computacional, baseado em Python, desenvolvido como parte de uma pesquisa de atualização de pós-doutorado que teve como objetivo gerar gráficos e tabelas de aceitação e rejeição de mapeamentos em qualquer escala (1:1.000 ; 1:2.000; 1:5.000; 1:10.000; 1:25.000; 1:50.000; 1:100.000, entre outras) analisando seus pontos de controle e respectivos erros nos eixos X, Y e Z (Leste, Norte, Altimetria).

## Introdução teórica
Na atual norma brasileira (Brasil - 1984), o decreto nº 89.817 de 20 de Junho de 1984 estabelece as Instruções Reguladoras das Normas Técnicas da Cartografia Nacional. No entanto, este foi elaborado para produtos analógicos em escalas pequenas (1:25000 ou menores), os quais são de competência do IBGE (Instituto Brasileiro de Geografia e Estatística). Neste trabalho, têm-se em conta os produtos em meio digital e procura-se a implementação de uma norma nos moldes da ABNT (Associação Brasileira de Normas Técnicas) que visam escalas grandes.

Antes de darmos continuidade, é necessário explicar algumas nomeclaturas que utilizadas muitas vezes nesse trabalho:
- Pontos de Controle (PCs) = São pontos fixos de um mapeamento (pontos bem definidos e identificáveis, como cantos de boca de lobo) que são utilizados para a aplicação do controle de qualidade posicional.
- Padrão de Exatidão Cartográfica (PEC) = Também chamado de 'Erro Admissível', corresponde ao valor máximo (normalmente em metros) aceitável que um erro possa assumir num mapeamento. Esse valor varia a depender da classe que se está analisando e qual a escala utilizada. Atualmente, podes er definido como o PEC-PCD.
- Aceitação / Rejeição = Esse valor, dado em porcentagem, corresponde ao percentual da quantidade de pontos de controle que está dentro (ou fora) do determinado pela norma.
- Teste da Norma do País = Também podendo ser chamado de teste direto, corresponde a norma vigente em relação a análise dos PCs. É estabelecido que o valor de aceitação de um mapeamento tem que ser no mínimo de 90% (ou ter uma rejeição máxima de 10%).
- Teste de Precisão = Um tipo de teste proposto pela pesquisa de pós-doutorado utilizando a Estatística para a análise dos PCs. O teste em questão se resume ao teste do Qui quadrado. A aceitação / rejeição utilizado também foi de 90% / 10%, no caso do Brasil.

Para mais detalhes sobre a pesquisa, recomenda-se a leitura do documento "PosDocV3.doc" disponível acima.

### Outras referências:
- Nero, M. A., 2005. Propostas para o controle de qualidade de bases cartográficas com ênfase na componente posicional Ph.D. Thesis, Escola Politécnica da Universidade de São Paulo, São Paulo, São Paulo, Brazil, 187pp. ([link](https://teses.usp.br/teses/disponiveis/3/3138/tde-04112005-110341/pt-br.html))
- Nero, M. A., 2006. Metodologias avançadas para o controle de qualidade posicional de bases cartográficas. Relatório de Pós-doutorado, Escola Politécnica da Universidade de São Paulo, São Paulo, São Paulo, Brazil, 198p.
- NERO, M. A.; CINTRA, Jorge Pimentel ; FERREIRA, G. F. ; PEREIRA, T. A. J. ; FARIA, T. S. . A COMPUTATIONAL TOOL TO EVALUATE THE SAMPLE SIZE IN MAP POSITIONAL ACCURACY. Boletim de Ciências Geodésicas, v. 23, p. 445-460, 2017. ([link](http://dx.doi.org/10.1590/s1982-21702017000300030))


# SimulaPEC - O aplicativo
Esta parte será destinada a falar sobre o aplicativo em si. Recomendamos que ao testar, opte para as versões mais recentes, visto que elas sempre apresentarão melhoras em relação as antigas, seja comesticamente ou conceitualmente; sempre será informado qual mudança foi feita. Todas as versões até o presente momento apresentaram "teste" no nome (junto com a data de modificação), devido ao fato que ainda não temos certeza de como o produto final será vizualmente falando. Qualquer alteração feita na interface será atualizada nessa parte.

<img width="502" height="290" alt="2026-04-22 20_10_15-SimulaPEC - Selecione o idioma _ Select Language" src="https://github.com/user-attachments/assets/f8235f2f-1cf1-422c-a950-f849d1ef6cbe" />

Até o presente momento, estamos trabalhando com uma versão "dual", em que o aplicativo funciona em dois idiomas: Português (Original) e Inglês. Nessa parte, é para selecionar qual idioma quer utilizar.

<img width="344" height="485" alt="2026-04-22 20_10_43-SimulaPEC Teste 22_04_2026" src="https://github.com/user-attachments/assets/03da5e21-01e6-49aa-94b3-0038cbc732be" />

Na imagem acima está a versão em português.

<img width="333" height="484" alt="2026-04-22 20_21_31-SimulaPEC Test 22_04_2026" src="https://github.com/user-attachments/assets/267723f5-71ea-4975-ac50-6be563498cc0" />

E na imagem acima está a versão em inglês.

Nas imagens acima, tem-se a interface inicial do SimulaPEC. Para começar o processo, é necessário preencher os 6 parâmetros acima. Estes são:
- "Número de PCs" = Bem direto, é o número de Pontos de Controles do mapeamento em análise.
- "Erro admissível (PEC)" = É o valor máximo do erro permitido em metros. Este valor varia a depender da classe e da escala utilizada.
- "%PCs acima do PEC" = Basicamente, qual o nível de rejeição admitido. A Norma Brasileira estabelece que seja 10% (não é necessário colocar o '%').
- "Intervalo acima (%)" = É a distância entre as curvas superiores a da curva linear (i.e. o valor fornecido pelo usuário no parâmetro "%PCs acima do PEC"). O maior que uma curva pode assumir é 40%.
- "Intervalo abaixo (%)" = É a distância entre as curvas inferiores a da curva linear (bem similar ao parâmetro acima). O menor valor que pode assumir é qualquer um maior que zero.
- "Nº de iterações" = Quantidade de vezes que cada grupo de pontos formados serão análises entre si. Mais a frente, será explicado melhor essa parte.
#### Observação: Valores negativos ou nulos em qualquer um desses parâmetros não serão aceitados.

## Processamento
Após colocado os parâmetros para a análise que será feita, aperta o botão "Confirmar" e a seguinte mensagem aparecerá:

<img width="272" height="190" alt="2026-04-22 20_11_22-Tempo estimado" src="https://github.com/user-attachments/assets/42f9bc2b-6548-4ef0-af03-14c9302bc764" />

Essa mensagem apresenta o tempo estimado que cada curva dos gráficos levará para ser plotada. Clicando em "Yes", começará a simulação. Clicando em "No", não começará e será apresentada essa mensagem:

<img width="306" height="190" alt="Simulapec_cancelado" src="https://github.com/user-attachments/assets/7a93b290-e644-4dcc-9fc0-0de3cd45a3a6" />

Começando a simulação, as duas barras logo abaixo dos parâmetros irão ser preenchidas. A barra "Progesso" representa o progresso realizado por cada curva, enquanto a barra "Progresso total" representa o progresso da simulação inteira. Logo abaixo está um exemplo:

<img width="342" height="484" alt="2026-04-22 20_55_01-SimulaPEC Teste 22_04_2026" src="https://github.com/user-attachments/assets/1929fa62-c134-4bf5-95e4-3c75aa45783a" />

Um ponto importante citar é o botão de "Cancelar". Quando não tem nenhuma simulação sendo feita, esse botão fica desativado. Quando começa uma, esse botão fica ativado e pode ser clicado a qualquer momento, até o final da simulção. Clicando nele, a mensagem de "A simulação foi interrompida" aparece novamente.

Terminado a simulação, aparecerá um gráfico mostrando o resultado processado. Logo abaixo está um exemplo de um gráfico processado:

<img width="4170" height="1779" alt="teste" src="https://github.com/user-attachments/assets/d1bbcc76-cd3d-41b5-9a44-98ccc9882a2f" />

Nesse gráfico está presente o resultado das curvas de rejeição tanto do Teste de Precisão quanto do Teste da Norma do País. No eixo das abcissas temos o tamanho da amostra que varia de 0 até 60% dos PCs indo de 5 em 5, ou seja, (0, 5, 10, 15, ... , 60%*PCs). E no eixo das ordenadas temos o Percentual de Rejeição do Mapeamento (PRM%). No tópico seguinte iremos explicar o cada um significa.
Também vale citar, o tempo total de processamento e o PEC utilizado localizado no topo.

A curva em azul é a curva linear, ou seja, o valor fornecido pelo usuário no "%PCs acima do PEC". As curvas em verde são as inferiores e as curvas em vermelho são as superiores.

Esse gráfico pode ser salvo ou diretamente na imagem ou então apertando o botão "Salvar Gráfico" localizado na Interface inicial. Também pode ser salvo uma panilha contendo todos os dados processados para uma análise mais profunda; basta clicar no botão "Salvar Planilha" também localizado na Interface inicial. E também, é possível salvar um gráfico em formato .html para poder fazer uma análise mais detalhada; basta clicar no botão "Salvar Gráfico Dinâmico". Vale a pena citar que nenhum desses botões funcionaram antes de uma simulação ser feita, aparecendo uma mensagem pedindo para ser feita uma simulação antes.

## Teste de Precisão e Norma do País
Vamos começar pelo Teste de Precisão. Como citado anteriormente, o teste é baseado no teste do Qui quadrado.

Logo no começo, uma tabela de pontos é criada, contendo a mesma quantidade de PCs fornecido pelo usuário. Esses pontos são chamados de "Dados Fictícios". Esses dados seguem uma distribuição normal.

Em seguida, grupos de PCs de tamanho n são formados. O tamanho desses grupos variam de 5 em 5 até 60% dos PCs totais, com reposição. Utilizando o grau de liberdade (n-1), é calculado o desvio padrão de cada grupo e depois o Qui quadrado, sendo, para o cálculo deste, utilizado o desvio padrão, o grau de liberdade e o PEC. Tendo esse valor, é comparado com o Qui tabelado, e decidido se foi aceito ou não essa amostragem. Cada grupo passa por esse processo repetidas vezes, decide pelo usuário na parte de "Nº de iterações". O resultado final resulta no PRM%, em outras palavras, qual é a média de vezes que o mapeamento não foi aceito para cada quantidade de PCs em cada nível de rejeição determinada.

Agora, para o Teste da Norma do País.

A norma determina que para cada amostragem, é permitido que até 10% dos PCs tenha um erro acima do PEC. Por isso também é chamado de teste direto. Similar ao Teste de Precisão de Precisão, grupos de tamanho n são formados, o processo é repetido pela quantidade determinada pelo usuário e por fim temos o PRM% para cada nível de rejeição.

A razão de serem utilizados "Dados Fictícios" foi com a intenção de evitar riscos e prejuízos ao consumidor e ao técnico ao analisar um mapeamento. No entanto, caso já tenha sido feito a análise, é possível adicionar esses dados a simulação também. Esses dados são chamados de "Dados Reais".

## Teste de Precisão e Norma do País - Dados Reais
Para casos em que já existam os dados calculados em campo, é possível adiciona-los na simulação também. Para isso, esses dados precisam estar num arquivo .txt e, por questões de compatibilidades, recomendamos que seja substituído as vírgulas (,) por pontos (.) e que a quantidade de PCs seja a mesma que a fornecida pelo usuário.

Clicando no botão "Carregar Dados Reais", selecione o arquivo que esteja os dados e já pode começar a simulação. O progresso e os testes realizados com esses são exatamente os mesmos que foram realizados nos "Dados Fictícios". A principal diferença vai ser que os resultados vão ter um destaque maior tanto no gráfico quanto na planilha. Na imagem abaixo, temos um exemplo de um gráfico produzido com os dados reais:

<img width="4170" height="1779" alt="teste_real" src="https://github.com/user-attachments/assets/13c504af-1140-4ae0-a8b5-e93ce81aa63d" />

Em que os dados reais são representados pela linha preta tracejada "R".

## Considerações finais
Vale a pena relembrar que esse aplicativo ainda está em fase de teste, e como tal, está sujeito a possíveis erros ou inconsistências. Pedimmos aos usuários que testarem e notarem algum problema, ou queiram dar alguma sugestão de como melhora-lo esteticamente, possam comentar na parte de "issues" do repositório. Faremos o que pudermos para torna-lo mais atrativo.

### Aviso
Por questões de ética e transparência, temos que informar que foram utilizadas duas IAs generativas (ChatGPT e Lumo) para verificação e identificação de algum possível erro. Todas as respostas geradas por elas são analisadas e decidimos se devemos implantar ao não.
