# Google Local Lead Scraper

Uma ferramenta simples e eficiente em Python desenvolvida para automatizar a busca e organização de dados públicos de empresas no Google Local / Maps. 

O objetivo principal deste projeto é demonstrar a aplicação prática de automação web e raspagem de dados para **prospecção B2B (Business to Business)** e inteligência de mercado.



## O que o projeto faz?

**Multitask em abas:** Realiza buscas simultâneas em até 3 abas para otimizar o tempo de execução.
**Padronização de Telefones:** Formata automaticamente os números encontrados para o padrão brasileiro (`DDI + DDD + Número`, ex: `5567991709231`), ajustando números locais sem DDD.
**Tratamento de Dados:** Remove números duplicados automaticamente e exporta os resultados limpos em uma planilha Excel (`.xlsx`).
**Navegação Fluida:** Utiliza o `undetected-chromedriver` para evitar bloqueios simples de automação e gerencia a paginação até o fim dos resultados.



## Tecnologias Utilizadas

**Python 3.10+**
**Selenium** & **undetected-chromedriver** (Automação de navegação)
**Pandas** & **openpyxl** (Tratamento e exportação de dados)
**Expressões Regulares (Re)** (Extração e validação de padrões)


