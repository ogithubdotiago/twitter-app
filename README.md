**Arquitetura**
----
* **Projeto**

  O projeto foi arquitetado em docker-compose afim de facilitar o provisionamento do ambiente:

  | Container | Descrição |
  | ------ | ------ |
  | twitter-app-frontend | Responsável pela api rest e templates |
  | twitter-app-backend | Responsável pela coleta de tweets e persistência do banco de dados  |
  | twitter-app-mongodb | Banco de dados para persistência dos tweets  |
  | twitter-app-grafana | Visualização de dashboard |
  | twitter-app-prometheus | Coleta de métricas do frontend |
  | twitter-app-filebeat | Coleta de logs "file" via disco compartilhado |
  | twitter-app-elastic | Indexação de logs |
  | twitter-app-kibana | Visualização de logs |

  ![](https://github.com/ogithubdotiago/twitter-app/blob/master/pictures/arquitetura.png)

* **Variaveis de ambiente**
  | ENV | Container | Descrição |
  | ------ | ------ | ------ |
  | TWITTER_API_CLIENT_KEY | backend | Key para autenticação na api do twitter |
  | TWITTER_API_CLIENT_SECRET | backend | Secret para autenticação na api do twitter |  
  | MONGODB_USER | frontend, backend | usuário de acesso mongodb |
  | MONGODB_PWD | frontend, backend | Senha de acesso mongodb |
  | MONGODB_HOST | frontend, backend | Host do mongodb |
  | MONGODB_PORT | frontend, backend | Porta do mongodb |
  | METRICS_PORT | frontend | Porta exposição de métricas para o prometheus |
  | LOG_PATH | frontend, backend | Se habilitado, faz logging em arquivo (true, false) |
  | LOG_FILE | frontend, backend | Se LOG_PATH estiver habilitado, path completo para logging |
  | MONGODB_DROP | backend | Se habilitado, backend faz drop do bd a cada consulta na api do twitter (true, false) |
  | MONGO_INITDB_ROOT_USERNAME | database | Definição de usuário para o mongodb |
  | MONGO_INITDB_ROOT_PASSWORD | database | Definição de senha para o mongodb |

* **Log**

  Os logs do frontend e backend são enviados para stdout e habilitando a flag LOG_PATH via variavel de ambiente, o log e disponibilizado via file.

  Formato do log:
  ```json
  {
    "time":"2020-04-23 00:00:00,000",
    "name":"componet",
    "level":"ERROR",
    "message":"error"
  }
  ```
* **Instalação**
  No diretorio corrente do projeto onde se encontra o arquivo docker-compose.yml, executar o docker-compose:

  ```sh
  $ docker-compose -version
  docker-compose version 1.17.1
  ```
  ```sh
  $ docker-compose up -d
  ```
**API**
----
* **Amostras**
  - Todos os tweets coletados;
  - Os 5 usuários, da amostra coletada, que possuem mais seguidores;
  - Total de postagens, agrupadas por hora do dia (independentemente da #hashtag);
  - Total de postagens para cada uma das #tag por idioma/país do usuário que postou;
  - Health check para validação de conexão com o banco de dados.

* **URL**
  - /api/v1/tweets
  - /api/v1/tweets/followers
  - /api/v1/tweets/posts
  - /api/v1/tweets/location
  - /api/v1/tweets/health

* **Autenticação**

  `user: admin`
  `password: admin`

* **Método**

  `GET`

* **Sucesso Resposta:**
    
  /api/v1/tweets/followers
  * **Code:** 200 <br />
    **Content:** `[{"followers": 185259,"name": "Infosecurity Mag"}]`
 
  /api/v1/tweets/posts
  * **Code:** 200 <br />
    **Content:** `[{"count": 35,"hour": 5}]`

  /api/v1/tweets/location
  * **Code:** 200 <br />
    **Content:** `[{"count": 93,"location": "en","tag": "#metrics"}]`

  /api/v1/tweets/health
  * **Code:** 200 <br />
    **Content:** `{"database": "up"}`

* **Erro Resposta:**

  * **Code:** 403 <br />
    **Content:** `{ 'error': 'Unauthorized access' }`

  * **Code:** 400 <br />
    **Content:** `{ 'error': 'Bad Request' }`

  * **Code:** 404 <br />
    **Content:** `{ 'error': 'Not Found' }`

  * **Code:** 500  <br />
    **Content:** `{ 'error': 'Internal Server' }`

**Frontend**
----
  | URL | Descrição |
  | ------ | ------ |
  | http://127.0.0.1/followers | Os 5 usuários que possuem mais seguidores |
  | http://127.0.0.1t/posts | Total de postagens, agrupadas por hora do dia |
  | http://127.0.0.1/location | Total de postagens para cada #tag por localização |
  | http://127.0.0.1:8080 | Dashboard para visualização de métricas do frontend |
    | http://127.0.0.1:8081 | Dashboard para visualização de logs |

**Métricas**
----
  As métricas são enviadas por um exporter do prometheus no flask, gerando os dashboard abaixo:

  ![](https://github.com/ogithubdotiago/twitter-app/blob/master/pictures/dashboard.png)

  | Dashboard | Descrição |
  | ------ | ------ |
  | Total requests per minute | Total de todas as requisições por status code |
  | Request duration [s] - p90 | Calcula o quantil de 90% de duração das requisições |
  | Request duration [s] - p50 | Calcula o quantil de 50% de duração das requisições  |
  | Requests under 250ms | Total de requisições abaixo de 250ms |
  | Average response time [30s] | Media de tempo de resposta de requisições |
  | Requests per second | Quantidade de requisições por segundo |
  | Errors per second | Quantidade de erros por segundo |

**Logs**
----
  Os logs são coletados via filebeat, enviados para o elasticsearch, indexados para visualização via Kibana:

  ![](https://github.com/ogithubdotiago/twitter-app/blob/master/pictures/log.png)