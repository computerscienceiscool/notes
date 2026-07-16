# Ex2 Demo

`ex2-grid-editor` is the local-first grid editor example.

## Quick Local Run

Start the relay:

```bash
cd /home/jj/lab/cswg/grid-examples/ex2-grid-editor
go run ./cmd/grid-relay --listen 127.0.0.1:7015
```

Open the browser:

```text
http://127.0.0.1:7015/?doc=demo
```

Optional Neovim client:

```bash
cd /home/jj/lab/cswg/grid-examples/ex2-grid-editor
./scripts/grid-editor-nvim demo
```

## Two-Relay Local Demo

Relay A:

```bash
cd /home/jj/lab/cswg/grid-examples/ex2-grid-editor
go run ./cmd/grid-relay --listen 127.0.0.1:7015
```

Relay B:

```bash
cd /home/jj/lab/cswg/grid-examples/ex2-grid-editor
go run ./cmd/grid-relay --listen 127.0.0.1:7016 --peer http://127.0.0.1:7015
```

Browser URLs:

```text
http://127.0.0.1:7015/?doc=demo
http://127.0.0.1:7016/?doc=demo
```

## Docker Demo

```bash
cd /home/jj/lab/cswg/grid-examples/ex2-grid-editor
docker-compose up --build
```

Then open the same two URLs above.
