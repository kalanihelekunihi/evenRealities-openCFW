# G2 research evidence

The raw decompilation evidence retained for the pseudocode-first workflow. It is
stored unpacked and filed by subject.

```
research/
├── MANIFEST.sha256                     index of every file below
└── corpus/
    ├── PROVENANCE.md                   delivery history and pruning record
    ├── SHA256SUMS.lane-bundle          original bundle manifest (partly pruned)
    ├── apollo-main/ghidra/decomp/      Ghidra 12.1.2 pseudocode for all 7,449 Apollo main functions
    ├── apollo-main/ghidra/full64-j64-auth/  the 64-shard authenticated run behind decomp/
    ├── apollo-main/ghidra/pt-protocol/ product-test protocol region decompilation
    ├── case/ghidra/final-frontier/     case function list, call graph and census
    ├── em9305/ghidra/round16-authoritative/, residual-round4/  ARCompact shard logs
    ├── iar/                            IAR DLIB runtime identification evidence
    └── qpc/                            QP/C on EM9305 identification evidence
```

None of this is reviewed pseudocode. The workflow requires identity and scope
validation before any of it seeds a P2 raw export.
[`../symbols/`](../symbols/README.md) holds the naming seeds consolidated from
the pruned records.

Verify the tree:

```sh
make -C g2 research-corpus
```

After adding or removing evidence, regenerate the index. This first checks
every delivery manifest:

```sh
python3 g2/tools/verify_research_corpus.py --write-manifest
```
