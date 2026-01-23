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
