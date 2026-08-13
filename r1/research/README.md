# R1 research evidence

The recovered evidence the R1 implementation and its correlation documents are
built on. Everything the [`../tools/`](../tools) scripts read lives here.

```
research/
├── decompilation/            the stock 2.2.6.0009 images and their decompilation
│   ├── application/          disassembly, decompiler output, call graph, symbols
│   ├── bootloader/           the same for the bootloader
│   └── rebuild/              byte-exact image reconstruction + its verifier
├── bootloader-reconstruction/ a rebuildable bootloader project and its evidence
└── source-correlation/       raw Ghidra BSim comparison runs
```

## `decompilation/`

The analysis subject. `rebuild/` reconstructs the four pinned images —
application, bootloader, UICR, APPROTECT runtime — byte-for-byte from stored
arrays and authenticates them:

```sh
make -C r1/research/decompilation/rebuild verify
```

The reconstructed application hashes to
`0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`, the digest
every R1 correlation document pins against.

The byte arrays themselves are the vendor firmware in another encoding and are
**not** tracked here — the same policy this repository applies to the G2 OTA
payloads. [`decompilation/rebuild/PROVENANCE.md`](decompilation/rebuild/PROVENANCE.md)
records the digests and how to supply your own copy.

`application/` and `bootloader/` hold the decompilation products — disassembly,
decompiler C, call graph, function and symbol tables, memory blocks. Those are
analysis output rather than vendor bytes, so they are tracked.

## `bootloader-reconstruction/`

A rebuildable Nordic-SDK bootloader project correlated against the recovered
image, plus its generated function tables, functional model, SDK overlay, and
the memory-map, security-model, and rebuildability write-ups. The 108 MB build
tree is not tracked; the project rebuilds it.

## `source-correlation/`

Raw Ghidra BSim comparison runs against symbol-bearing references — the
correlation CSVs, run logs, and generated hash records. The reviewed conclusions
are in [`../docs/reference/bsim/`](../docs/reference/bsim); these are the inputs
behind them, kept because `verify_openr1.py` checks their digests and
dimensions.

## Reading the evidence

These are inputs, not conclusions. A BSim similarity of 1.0 is a *candidate*
signal — the R1 review repeatedly found perfect matches among tiny wrappers that
plainly do not implement the suggested symbol. Attribution needs distinctive
constants, complete semantics, source diagnostics, or corroborating call
topology.

The claims themselves live in [`../docs/correlation/`](../docs/correlation) and
[`../docs/boundaries/`](../docs/boundaries), and are gated by:

```sh
make -C r1 verify
```
