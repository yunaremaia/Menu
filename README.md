# Menu

**Menu** é uma plataforma open source auto-hospedada para criação, gestão e disponibilização de cardápios digitais interativos para restaurantes, bares, cafeterias, food trucks e qualquer estabelecimento do setor alimentício. Os clientes acessam o cardápio pelo próprio celular escaneando um QR Code na mesa — sem necessidade de app, sem tocar em cardápio físico, sem depender de serviços terceiros que cobram assinatura mensal.

---

## Problema

Restaurantes e estabelecimentos alimentícios gastam dinheiro recorrente com impressão de cardápios físicos que desatualizam rapidamente — preços mudam, pratos saem de circulação, promoções começam e terminam. Cada alteração exige reimpressão ou uso de etiquetas sobrepostas que passam uma imagem amadora.

As soluções digitais disponíveis se dividem em dois grupos igualmente problemáticos:

- **SaaS fechados** (CardápioWeb, Menu.Digital, iMenu) — cobram assinatura mensal, armazenam os dados do estabelecimento em servidores alheios, exibem anúncios de concorrentes em muitos casos, e criam dependência tecnológica. Se o restaurante parar de pagar, o cardápio simplesmente some.
- **Soluções genéricas** (linktree, Google Sites, PDF hospedado no Drive) — não são feitas para cardápios: não têm busca, organização por categoria, fotos em galeria, cálculo de total do pedido, ou detecção de idioma do cliente.

Nenhuma solução open source madura atende especificamente o nicho de cardápios digitais com foco em simplicidade de operação para o dono do estabelecimento e boa experiência para o cliente.

---

## O que o Menu oferece

### Para o estabelecimento (painel de administração)

- **Cardápios ilimitados** — Crie quantos cardápios precisar: cardápio do dia, cardápio da noite, happy hour, brunch, cardápio sazonal de fim de ano. Cada um com suas próprias categorias, itens, fotos e preços.
- **Categorias e itens** — Organize por categorias (entradas, principais, sobremesas, bebidas, vinhos, etc.) com ordenação por arrastar e soltar. Cada item suporta: nome, descrição, preço, foto (upload ou URL), tags (vegano, sem glúten, apimentado, mais vendido), destaque, e disponibilidade (disponível/esgotado).
- **Múltiplos preços** — Um mesmo item pode ter preços diferentes por cardápio. Ex.: o mesmo hambúrguer custa R\$ 29 no cardápio do dia e R\$ 35 no cardápio da noite. Sem duplicar o item.
- **QR Code por mesa** — Gere QR Codes únicos por mesa ou área do salão. O cliente escaneia e cai direto no cardápio da mesa dele. O estabelecimento imprime uma vez e nunca mais precisa reimprimir.
- **Visualização ao vivo** — O administrador vê exatamente como o cardápio está aparecendo para o cliente antes de publicar alterações.
- **Histórico de versões** — Cada alteração publicada gera um snapshot. Se algo der errado, o dono pode reverter para uma versão anterior em um clique.
- **Dashboard de audiência** — Quantas pessoas visualizaram o cardápio hoje, nesta semana, neste mês. Quais itens foram mais vistos. Em qual horário o cardápio é mais acessado.
- **Idiomas** — Cadastre o cardápio em múltiplos idiomas (português, inglês, espanhol, francês). O sistema detecta o idioma do navegador do cliente e exibe a versão correspondente automaticamente.
- **Modo offline** — Uma vez carregado, o cardápio fica acessível no celular do cliente mesmo se a internet do estabelecimento cair. Usa Service Worker para cache.

### Para o cliente (interface pública)

- **Acesso instantâneo** — Escaneia o QR Code e o cardápio abre no navegador. Sem download, sem cadastro, sem notificações push.
- **Navegação por categorias** — Abas ou menu lateral para pular entre categorias rapidamente.
- **Busca** — Digite "hambúrguer" ou "sem glúten" e veja só os itens relevantes.
- **Filtros** — Filtre por tipo (vegano, sem lactose, apimentado), faixa de preço, ou disponibilidade.
- **Visualização do item** — Ao clicar em um item, abre um modal com foto ampliada, descrição detalhada, preço, informações nutricionais (se cadastradas) e selos (vegano, sem glúten, etc.).
- **Cálculo total** — O cliente pode selecionar itens e quantidades e ver o total parcial do pedido — útil para grupos que dividem a conta.
- **Modo escuro** — Respeita a preferência de tema do sistema do cliente.
- **Acessibilidade** — Navegação por teclado, suporte a leitores de tela, contraste adequado e fontes redimensionáveis.

### Técnico

- **API REST completa** — Crie, leia, atualize e remova cardápios, categorias, itens e mesas programaticamente. Perfeito para integrar com sistemas de PDV (Point of Sale) existentes.
- **Exportação e importação** — Exporte todo o cardápio em JSON ou CSV. Importe de volta para migrar entre instalações ou fazer backup.
- **Self-hosted** — Roda em qualquer lugar: um Raspberry Pi na rede do restaurante, um VPS de 5 dólares, ou o notebook velho no escritório. Sem dependência de serviço externo.
- **Docker opcional** — Imagem Docker pronta para quem prefere containerização.
- **CLI companion** — Gerencie cardápios do terminal: `menu import cardapio.json`, `menu publish`, `menu stats`.

---

## Status do desenvolvimento

### Implementado

- [x] **Modelos de domínio** — Cardapio, Categoria, Item e Mesa com validação Pydantic (nomes não vazios, preços não negativos, timezone-aware)
- [x] **Repositório SQLite** — CRUD completo para cardápios, categorias, itens e mesas com suporte a filtros (ativos, disponíveis) e ordenação
- [x] **API REST** — 27 endpoints que expõem toda a funcionalidade via HTTP com FastAPI e documentação automática (Swagger UI em `/docs`)
- [x] **Geração de QR Code** — Serviço standalone e endpoint REST para gerar QR Codes PNG por mesa, prontos para impressão
- [x] **Interface web do cardápio** — Página HTML responsiva que exibe o cardápio com categorias, itens, preços, fotos e tags; acessível via `/cardapio/{id}?mesa={id}`
- [x] **Upload de imagens** — Serviço de armazenamento local e endpoint REST para upload de fotos dos itens (PNG, JPG, GIF, WebP) com substituição automática
- [x] **Exportação e importação** — Exporte cardápios completos (com categorias, itens e mesas) em JSON ou CSV e importe de volta em JSON

### Interface web do cardápio

| Método | Rota | Descrição |
|---|---|---|
| `GET` | `/cardapio/{id}` | Página pública do cardápio (`?mesa={id}` opcional) |

### API REST

#### Cardápios

| Método | Rota | Descrição |
|---|---|---|
| `POST` | `/api/cardapios` | Criar cardápio |
| `GET` | `/api/cardapios` | Listar cardápios (`?apenas_ativos=true`) |
| `GET` | `/api/cardapios/{id}` | Obter cardápio |
| `GET` | `/api/cardapios/{id}/exportar` | Exportar cardápio completo (`?formato=json` ou `csv`) |
| `POST` | `/api/cardapios/importar` | Importar cardápio completo (JSON) |
| `PUT` | `/api/cardapios/{id}` | Atualizar cardápio |
| `DELETE` | `/api/cardapios/{id}` | Deletar cardápio |

#### Categorias

| Método | Rota | Descrição |
|---|---|---|
| `POST` | `/api/categorias` | Criar categoria |
| `GET` | `/api/cardapios/{id}/categorias` | Listar categorias de um cardápio |
| `GET` | `/api/categorias/{id}` | Obter categoria |
| `PUT` | `/api/categorias/{id}` | Atualizar categoria |
| `DELETE` | `/api/categorias/{id}` | Deletar categoria |

#### Itens

| Método | Rota | Descrição |
|---|---|---|
| `POST` | `/api/itens` | Criar item |
| `GET` | `/api/categorias/{id}/itens` | Listar itens de uma categoria (`?apenas_disponiveis=true`) |
| `GET` | `/api/itens/{id}` | Obter item |
| `PUT` | `/api/itens/{id}` | Atualizar item |
| `POST` | `/api/itens/{id}/foto` | Upload de foto do item (multipart) |
| `DELETE` | `/api/itens/{id}` | Deletar item |

#### Mesas

| Método | Rota | Descrição |
|---|---|---|
| `POST` | `/api/mesas` | Criar mesa |
| `GET` | `/api/cardapios/{id}/mesas` | Listar mesas de um cardápio (`?apenas_ativas=true`) |
| `GET` | `/api/mesas/{id}` | Obter mesa |
| `PUT` | `/api/mesas/{id}` | Atualizar mesa |
| `DELETE` | `/api/mesas/{id}` | Deletar mesa |
| `GET` | `/api/mesas/{id}/qrcode` | Obter QR Code da mesa (PNG) |

### Testes

```bash
pytest -v           # Todos os testes (162 atualmente)
pytest -k "api"     # Testes de API
pytest -k "repo"    # Testes de repositório
pytest -k "modelos" # Testes de modelos
pytest -k "qrcode"  # Testes de QR Code (serviço + API)
pytest -k "web"     # Testes da interface web
```

### Próximos passos

- [ ] Painel de administração web
- [ ] Cache com Service Worker para modo offline
- [ ] Suporte a múltiplos idiomas

---

## Público-alvo

- **Restaurantes, bares e cafeterias** de pequeno e médio porte que querem modernizar o cardápio sem pagar assinatura mensal.
- **Food trucks e pop-ups** que mudam de local frequentemente e precisam de um cardápio digital sempre atualizado.
- **Hamburguerias e pizzarias** que têm cardápios sazonais ou promocionais e cansam de reimprimir.
- **Hotéis e pousadas** que querem oferecer room service com cardápio digital nos quartos.
- **Eventos gastronômicos** (feiras, festivais, exposições) onde cada expositor precisa de um cardápio temporário.
- **Desenvolvedores** que querem uma solução para um amigo ou parente que tem um restaurante e não quer depender de plataformas fechadas.

---

## Stack sugerida

### Backend

| Camada | Tecnologia | Motivo |
|---|---|---|
| Linguagem | Python 3.12+ | Mesma stack dos projetos existentes, facilita manutenção |
| Framework web | FastAPI | Performance, validação com Pydantic, documentação automática |
| Banco de dados | SQLite (padrão), PostgreSQL (escala) | SQLite para instalações single-usuário; PostgreSQL para redes com muitos acessos simultâneos |
| Cache | Redis (opcional) | Para cache de cardápios públicos e sessões de admin |
| Processamento de imagens | Pillow + tinypng ou libvips | Redimensionamento e compressão automática de fotos dos itens |
| QR Code | qrcode (Python) | Geração de QR Codes por mesa no servidor |

### Frontend (painel admin)

| Camada | Tecnologia |
|---|---|
| Framework | React com Vite ou SvelteKit |
| UI Kit | shadcn/ui ou Radix UI |
| Upload de imagens | Upload com preview e crop (react-easy-crop) |
| Drag and drop | dnd-kit (React) ou nativo sortable (Svelte) |
| QR Code | Geração via API, exibição com biblioteca própria |

### Frontend (cardápio público)

| Camada | Tecnologia |
|---|---|
| Framework | Nenhum — HTML + CSS + JS vanilla (performance máxima, sem framework) |
| Build | Vite (para bundling mínimo) |
| Cache offline | Service Worker (Workbox) |
| Imagens | Lazy loading com Intersection Observer, WebP com fallback JPEG |
| Ícones | Lucide ou Phosphor Icons (leves, MIT) |

### Infraestrutura

- Empacotamento via `pip install menu` ou Docker (`docker run -p 8000:8000 menu`)
- CLI em Python com `click` ou `typer`
- Extensão opcional para WordPress (plugin que embute o cardápio no site do restaurante)

---

## Possíveis desafios e aprendizados

- **Geração eficiente de QR Codes por mesa** — Um restaurante com 40 mesas precisa de 40 QR Codes únicos. O sistema precisa gerar imagens em alta resolução prontas para impressão em papel adesivo, em formato PDF para leitura em gráfica rápida. É um problema de renderização e layout que envolve template engine + biblioteca de PDF (WeasyPrint ou ReportLab).
- **Cache inteligente do cardápio público** — O cardápio público precisa ser extremamente rápido (o cliente não espera mais que 2 segundos para carregar). É preciso implementar cache em múltiplas camadas: Service Worker no navegador, cache HTTP com ETag no servidor, e cache de banco para consultas frequentes. E invalidar tudo instantaneamente quando o dono publicar uma alteração.
- **Upload e processamento de imagens** — Fotos de comida tiradas com celular podem ter 12 MB. O sistema precisa redimensionar para múltiplos tamanhos (thumbnail 150x150, cardápio 800x600, ampliada 1920x1080), converter para WebP, comprimir sem perda visível de qualidade, e extrair metadados (GPS, data) — opcionalmente apagando-os por privacidade do estabelecimento. Tudo isso de forma assíncrona para não travar a resposta da API.
- **Multi-idioma na prática** — Um cardápio em português com 50 itens vira 150 itens se for traduzido para 3 idiomas. O modelo de dados precisa suportar traduções sem duplicar o registro inteiro, e a interface de admin precisa mostrar os campos lado a lado para o dono preencher sem se perder.
- **Modo offline via Service Worker** — O cardápio precisa funcionar sem internet depois do primeiro carregamento. O Service Worker precisa cachear o HTML, CSS, JS, fontes e imagens. E precisa invalidar o cache quando o dono publicar alterações. Gerenciar versões de cache é um problema clássico de PWA.
- **Detecção de idioma do cliente** — Usar `navigator.language` combinado com `Accept-Language` do header HTTP para exibir automaticamente o cardápio no idioma certo. Com fallback para o idioma padrão do estabelecimento.
- **Acessibilidade em cardápio digital** — Leitores de tela precisam navegar por categorias e itens. Contraste de cores precisa ser adequado para clientes com baixa visão. Fontes precisam ser redimensionáveis sem quebrar o layout. O modal de item precisa gerenciar foco corretamente.
- **Dashboard de audiência sem violar privacidade** — Contar visualizações sem usar Google Analytics e sem identificar individualmente os clientes. Armazenar apenas dados agregados: visualizações por hora/dia/mês, itens mais vistos, tempo médio de navegação. Tudo anonimizado.

---

## Por que este projeto é relevante

O setor de alimentação fora do lar movimenta bilhões de reais por ano no Brasil, e a digitalização dos cardápios é uma tendência acelerada pela pandemia que veio para ficar. No entanto, as soluções disponíveis são quase todas SaaS fechados que cobram mensalidade e mantêm os dados dos estabelecimentos reféns.

O Menu resolve um problema real e imediato para um público enorme (mais de 1 milhão de restaurantes só no Brasil), com uma proposta de valor clara: gratuito, auto-hospedado, sem anúncios e sem limite de cardápios ou itens. Qualquer dono de restaurante com conhecimentos básicos de tecnologia pode rodar o Menu em um computador velho ou VPS de baixo custo.

Para o desenvolvedor, o projeto oferece aprendizado em diversas áreas: APIs RESTful, processamento de imagens, cache distribuído, PWAs com Service Worker, internacionalização (i18n), geração de QR Code, design de interfaces acessíveis e responsivas, e engenharia de performance para dispositivos móveis com conexões lentas.

A comunidade de autohosting brasileira é particularmente ativa (r/selfhostedBR, grupos de WhatsApp e Telegram) e tem grande demanda por ferramentas em português que resolvam problemas do dia a dia — o Menu se encaixa perfeitamente nesse perfil e naturalmente atrairá contribuições de donos de restaurante, desenvolvedores free-lancers e entusiastas de privacidade digital.

---

## Licença

**MIT** — Você pode usar, modificar e distribuir livremente.
