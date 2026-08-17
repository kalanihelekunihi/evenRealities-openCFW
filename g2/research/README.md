# G2 research evidence

The reverse-engineering evidence the G2 analyzers are built on. Everything here
is stored **unpacked and filed by subject** — no archives, and no trace of which
machine happened to run a given job.

```
research/
├── MANIFEST.sha256    authenticated index of every file below
├── candidates/        recovered source under review, not yet admitted
├── readiness/         per-module compiler/closure matrices, one directory per module
└── corpus/            decompilation and SDK-comparison evidence, filed by subject
```

Verify the whole tree:

```sh
make -C g2 research-corpus
```

That checks two independent layers — every delivered `SHA256SUMS` manifest still
verifies in place, and `MANIFEST.sha256` covers the tree exactly. It fails
closed on an edited, added, or removed file.

## `candidates/`

Recovered source candidates that compile and match recovered bytes, but have not
been promoted into a build. Promotion is a reviewed change with its own audit
under [`../docs/research`](../docs/research); until then a candidate lives here
and is exercised only by its `*_candidate` test.

## `readiness/`

One directory per Cordio/WSF module, each holding the compiler-matrix run that
established what the module's source-level closure looks like: build results,
per-function best sizes, include and provider closures, source identities, and
the exact toolchain configuration.

| Group | Modules |
| --- | --- |
| ATT | `attc-disc`, `atts-ccc`, `atts-csf` |
| DM | `dm-adv`, `dm-adv-leg`, `dm-conn`, `dm-conn-master`, `dm-conn-sm`, `dm-dev`, `dm-dev-priv`, `dm-main`, `dm-phy`, `dm-priv`, `dm-sec`, `dm-sec-lesc`, `dm-sec-master`, `dm-sec-slave` |
| SMP | `smp-db`, `smp-main` |
| WSF | `wsf-assert-trace`, `wsf-buf`, `wsf-efs-inclusion-census`, `wsf-os-queue-stockabi`, `wstr` |

Each directory keeps the `SHA256SUMS` it was delivered with. The matching
analyzer in [`../tools`](../tools) pins that manifest, so tampering with a
readiness result fails the analyzer rather than silently changing a conclusion.
The compact tables the analyzers read row-by-row are also materialized as
`../tools/manifests/readiness-cordio-*.tsv`.

## `corpus/`

Decompilation output, SDK comparisons, and lane transcripts, filed by subject:

| Subject | Contents |
| --- | --- |
| `apollo-main/ghidra/` | the Apollo application 64-chunk Ghidra corpora, including the audit-hardened 64-log / 7,370-function result |
| `apollo-main/ghidra/decomp/` | the decompilation itself — 7,449 functions as C, with bounds, prototypes, callees and per-body hashes; the input to the [transparent-source pipeline](../docs/transparent-source.md) |
| `em9305/ghidra/` | EM9305 Ghidra shard rounds — five `round16-*` passes and three `residual-round*` passes |
| `em9305/sdk-comparison/` | EM9305 SDK function comparison reports across five configurations |
| `em9305/nop-aware/`, `em9305/size-delta/` | link-order and size-delta analyses |
| `wsf/` | the Packetcraft WSF comparator, the eleven-function timer matrices, the OS/queue readiness set, and the stock-module inspection |
| `iar/` | IAR runtime shards and the math-errno and memory-qualification lanes |
| `qpc/` | QP/C full and survivor reports |
| `source-lanes/` | Cordio, LVGL, and path-gap source-lane transcripts |

Origin, the original delivery roots, and every change made while unpacking are
recorded in [`corpus/PROVENANCE.md`](corpus/PROVENANCE.md).

## Reading the evidence

These are inputs, not conclusions. A readiness matrix showing a size match is a
*candidate* signal; admission still requires distinctive constants, complete
semantics, source diagnostics, or corroborating call topology. The audits that
turn evidence into a claim live in [`../docs/research`](../docs/research), and
the claims themselves are recorded in
[`../docs/source-coverage.md`](../docs/source-coverage.md) and
[`../docs/upstream-inventory.md`](../docs/upstream-inventory.md).
