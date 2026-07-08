# Robo CNPJ - Casa dos Dados

Robo em Python que pesquisa CNPJs na [Casa dos Dados](https://casadosdados.com.br/solucao/cnpj/pesquisa-avancada), obtem o detalhe de cada resultado e salva em arquivo `.txt` separado por virgula (pronto para abrir no Excel).

## Requisitos

- Python 3.8+
- Windows / Linux

## Instalacao

```powershell
cd RoboCnpjCasaDados
py -m venv .venv
.\.venv\Scripts\pip.exe install -r requirements.txt
copy .env.example .env
```

> **PowerShell:** se `Activate.ps1` for bloqueado, use `.\iniciar.bat` ou `.\.venv\Scripts\python.exe main.py`.

## Configuracao

Edite `config/filtros.json` para definir os filtros da pesquisa (termo, UF, municipio, bairro, situacao, etc.).

Opcionalmente, edite `.env`:

| Variavel | Descricao |
|---|---|
| `FONTE` | `gratuita` (padrao), `plataforma` (login + pesquisa salva) ou `oficial` |
| `PORTAL_EMAIL` | E-mail da conta na plataforma (quando `FONTE=plataforma`) |
| `PORTAL_SENHA` | Senha da conta na plataforma |
| `PESQUISA_ID` | UUID da pesquisa salva (campo `pesquisaId` na URL do portal) |
| `LIMITE_PAGINA_PLATAFORMA` | Resultados por pagina na plataforma (padrao: **1000**) |
| `API_KEY` | Chave da API paga (necessaria quando `FONTE=oficial`) |
| `CF_CLEARANCE` | Cookie do Cloudflare (fallback se houver bloqueio 403) |
| `USER_AGENT` | User-Agent do navegador (usar junto com `CF_CLEARANCE`) |
| `DELAY_ENTRE_REQUISICOES` | Segundos entre requisicoes (padrao: **4.0**) |
| `MAX_PAGINAS` | Numero maximo de paginas da pesquisa (padrao: 100) |
| `MAX_RESULTADOS` | Para apos N CNPJs encontrados (0 = ilimitado) |
| `MAX_ERROS_CONSECUTIVOS` | Interrompe apos N erros seguidos de Cloudflare (padrao: 5) |
| `DELIMITADOR` | Separador do arquivo de saida (padrao: `,`) |

### Configurar CF_CLEARANCE (Cloudflare)

Se aparecer no log: `Bloqueio Cloudflare ao acessar pagina de detalhe`, configure o cookie no `.env`:

**Passo a passo (Chrome):**

1. Abra https://casadosdados.com.br/solucao/cnpj/pesquisa-avancada no **Google Chrome**
2. Aguarde a pagina carregar por completo (sem mensagem "Just a moment...")
3. Pressione **F12** para abrir as Ferramentas do Desenvolvedor
4. Va em **Application** (Aplicativo) → **Storage** → **Cookies** → `https://casadosdados.com.br`
5. Localize a linha **`cf_clearance`** e copie o **Value** (valor completo)
6. Cole no `.env`:

```env
CF_CLEARANCE=valor_copiado_aqui
USER_AGENT=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36
```

**Importante:**

- O `USER_AGENT` deve ser o **mesmo navegador** onde voce copiou o cookie. Para ver o seu:
  - No Chrome, abra o Console (F12) e digite: `navigator.userAgent`
  - Copie o texto exibido e cole em `USER_AGENT` no `.env`
- O cookie `cf_clearance` **expira** (geralmente em algumas horas). Se o bloqueio voltar, repita os passos acima.
- Mantenha `DELAY_ENTRE_REQUISICOES=4.0` (ou maior) para reduzir novos bloqueios.

**Exemplo de `.env` configurado:**

```env
FONTE=gratuita
DELAY_ENTRE_REQUISICOES=4.0
CF_CLEARANCE=AbCdEf1234567890_exemplo...
USER_AGENT=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36
IMPERSONATE=chrome120
```

## Como funciona (fonte gratuita)

1. **Pesquisa avancada** via `POST /v5/public/cnpj/pesquisa` com o **mesmo payload do site**, incluindo `data_abertura.inicio` (ex.: `2022-01-01` ou `01/01/2022` no `filtros.json`).
2. O plano gratuito retorna **no maximo 20 CNPJs** (pagina 1), ja filtrados pela API.
3. Para cada CNPJ encontrado, o robo **abre a pagina de detalhe** e extrai os dados do bloco `__NUXT_DATA__`.
4. **Salva** em `saida/pesquisa.txt` (1 linha por CNPJ, separado por virgula).

## Como funciona (fonte plataforma)

Para extrair **todos** os resultados de uma pesquisa salva (ex.: 4000+ registros):

1. Crie a pesquisa no [portal](https://portal.casadosdados.com.br/plataforma/pesquisa) e salve.
2. Copie o UUID da URL (`pesquisaId=5407171b-ecec-43fd-89e6-...`).
3. Configure o `.env`:

```env
FONTE=plataforma
PORTAL_EMAIL=seu@email.com
PORTAL_SENHA=sua_senha
PESQUISA_ID=5407171b-ecec-43fd-89e6-bd574612fb4a
LIMITE_PAGINA_PLATAFORMA=1000
DELAY_ENTRE_REQUISICOES=1.0
```

4. O robo faz **login**, carrega a pesquisa salva, pagina em lotes de 1000 e busca o detalhe de cada CNPJ via API JSON (`GET /v4/cnpj/{cnpj}`).
5. A saida e o mesmo `saida/pesquisa.txt` (CSV com BOM UTF-8).

**Estimativa:** ~4043 CNPJs com delay de 1s ≈ 67 minutos. Use `--max-resultados 5` para testar antes.

```powershell
.\iniciar.bat --max-resultados 5
.\iniciar.bat
```

Tambem aceita URL completa:

```powershell
.\iniciar.bat --fonte plataforma --pesquisa-id "https://portal.casadosdados.com.br/plataforma/pesquisa?pesquisaId=5407171b-ecec-43fd-89e6-bd574612fb4a"
```

## Uso

Com os filtros padrao do `config/filtros.json` (condominio / SP / SAO PAULO / VILA CARRAO / ATIVA):

```powershell
.\iniciar.bat
```

O resultado e gravado em **`saida/pesquisa.txt`** (padrao).

Sobrescrever filtros pela linha de comando:

```powershell
.\iniciar.bat --termo condominio --uf SP --municipio "SAO PAULO" --bairro "VILA CARRAO" --situacao ATIVA
```

Definir arquivo de saida:

```powershell
.\iniciar.bat --saida saida\meus_cnpjs.txt
```

Buscar detalhes de CNPJs especificos (pula a pesquisa):

```powershell
.\iniciar.bat --cnpjs "96512355000139,68478437000179" --saida saida\detalhes.txt
```

Limitar paginas e resultados (util para testes):

```powershell
.\iniciar.bat --max-paginas 20 --max-resultados 5
```

Usar API oficial (futuro, com api-key):

```powershell
.\iniciar.bat --fonte oficial
```

## Saida

Por padrao, o arquivo e gerado em **`saida/pesquisa.txt`**:

- 1 linha por CNPJ
- Campos separados por virgula
- Cabecalho na primeira linha
- Encoding UTF-8 com BOM (abre corretamente no Excel)

Para usar outro caminho: `.\iniciar.bat --saida saida\outro_nome.txt`

## Estrutura do projeto

```
RoboCnpjCasaDados/
├── config/          # settings, filtros.json
├── controllers/     # orquestracao do robo
├── models/          # FiltroPesquisa, EmpresaCnpj
├── services/        # cliente HTTP (gratuita/oficial)
├── views/           # gravacao do .txt
├── saida/           # arquivos gerados
├── logs/            # logs de execucao
├── main.py          # ponto de entrada
└── requirements.txt
```
