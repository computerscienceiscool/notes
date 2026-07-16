# Ex3 Demo

`ex3-grid-editor-websocket` is the websocket-capable grid editor example.

## Quick Local Run

Start the relay:

```bash
cd /home/jj/lab/cswg/grid-examples/ex3-grid-editor-websocket
go run ./cmd/grid-relay --listen 127.0.0.1:7025
```

Open the browser:

```text
http://127.0.0.1:7025/?doc=demo
```

Optional Neovim client:

```bash
cd /home/jj/lab/cswg/grid-examples/ex3-grid-editor-websocket
./scripts/grid-editor-nvim demo
```

## Remote / Multi-Machine Demo

Start the relay with the demo access token:

```bash
cd /home/jj/lab/cswg/grid-examples/ex3-grid-editor-websocket
go run ./cmd/grid-relay --listen 0.0.0.0:7025 --remote-access-token ex3-demo-access
```

Browser URL:

```text
http://127.0.0.1:7025/?doc=demo&access_token=ex3-demo-access
```

Neovim client with token:

```bash
cd /home/jj/lab/cswg/grid-examples/ex3-grid-editor-websocket
GRID_EDITOR_RELAY_URL=http://127.0.0.1:7025 GRID_EDITOR_ACCESS_TOKEN=ex3-demo-access ./scripts/grid-editor-nvim demo
```

## Two-Relay Local Demo

Relay A:

```bash
cd /home/jj/lab/cswg/grid-examples/ex3-grid-editor-websocket
go run ./cmd/grid-relay --listen 127.0.0.1:7025 --remote-access-token ex3-demo-access
```

Relay B:

```bash
cd /home/jj/lab/cswg/grid-examples/ex3-grid-editor-websocket
go run ./cmd/grid-relay --listen 127.0.0.1:7026 --peer http://127.0.0.1:7025 --remote-access-token ex3-demo-access
```

Browser URLs:

```text
http://127.0.0.1:7025/?doc=demo&access_token=ex3-demo-access
http://127.0.0.1:7026/?doc=demo&access_token=ex3-demo-access
```

## Docker Demo

```bash
cd /home/jj/lab/cswg/grid-examples/ex3-grid-editor-websocket
docker-compose up --build
```

Then open the same two tokenized browser URLs above.
