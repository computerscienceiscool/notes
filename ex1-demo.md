# Ex1 Demo

`ex1-order-flow` is the order-flow / promise-workflow example.

## Run The Demo

```bash
cd /home/jj/lab/cswg/grid-examples/ex1-order-flow/docker
bash run-demo.sh
```

That script runs the default fixture `happy-path.json`.

## Use A Different Fixture

```bash
cd /home/jj/lab/cswg/grid-examples/ex1-order-flow/docker
bash run-demo.sh refund-path.json
```

## Runtime Data

By default the demo preserves runtime data under:

```text
/tmp/grid-examples-ex1-data
```

The script prints the preserved data path when it finishes.

## Notes

- This demo is driven through Docker Compose.
- The fixture files live under `ex1-order-flow/docker/fixtures/`.
