# Building and verifying openCFW

Every target runs through the root [`Makefile`](../Makefile), or through
`./make.sh` from any directory. Each device keeps its own Makefile, which
`make -C g2` and `make -C r1` run directly. Every gate fails closed: a
hash, size or pin mismatch aborts the build.

```sh
./make.sh help
./make.sh test          # G2 tool tests + R1 corpus check; no vendor inputs needed
```

## Prerequisites

| Need | For |
| --- | --- |
| Python 3.9+, GNU make, a C11 compiler | every target |
| Git with submodule support | `third-party/` pins |
| The tools in [`../tools/bootstrap/`](../tools/bootstrap/README.md) | decompilation and byte matching; see [`tooling.md`](tooling.md) |
| Licensed original compilers (IAR EWARM, Synopsys MetaWare, Arm Compiler 5) | byte-identical C builds; you install and fingerprint them yourself |

## Versioned firmware mirrors

The versioned G2 and R1 release mirrors are tracked under
`g2/blobs/official/g2-<version>/` and `r1/blobs/official/r1-<version>/`.
Each directory includes release metadata and `SHA256SUMS` alongside its
firmware assets. See [`LICENSE`](../LICENSE) and [`NOTICE`](../NOTICE) for
licensing terms and boundaries.

## Inputs that are not tracked

| Input | Where it goes | Identity record |
| --- | --- | --- |
| Additional R1 captured reconstruction images (bootloader, UICR, APPROTECT) | `r1/blobs/official/2.2.6.0009/` | [`PROVENANCE.md`](../r1/blobs/official/2.2.6.0009/PROVENANCE.md) |
| nRF5 SDK 17.1.0 and R1 archive sources | any absolute cache directory | [`../third-party/fetched/`](../third-party/fetched/README.md) |
| Upstream libraries | `third-party/upstream/*` | `git submodule update --init --depth 1 <path>` |

## Targets

| Target | What it does | Needs |
| --- | --- | --- |
| `./make.sh g2-test` | tests for the kept G2 tools; tests that read payloads skip when they are absent | nothing |
| `./make.sh g2-build` | repacks the six official payloads into the byte-identical reference EVENOTA | G2 payloads |
| `./make.sh g2-verify` | reference build, manifest verification and research-corpus authentication | G2 payloads |
| `make -C g2 research-corpus` | authenticates `g2/research/` | nothing |
| `make -C g2 ghidra-harvest` | re-exports Apollo pseudocode from an analyzed Ghidra project | Ghidra, JDK, G2 payloads |
| `./make.sh r1-test` | structural check of the R1 decompilation corpus | nothing |
| `./make.sh r1-verify` | adds the exact-byte R1 image oracle | R1 images |
| `make -C r1 vendor-audit ...` | authenticates the fetched R1 archives and FreeRTOS/CMSIS/CmBacktrace submodules | fetched cache, initialised submodules |
| `./make.sh third-party` | checks every initialised submodule is at its pinned commit | nothing |
| `./make.sh tools` | lists the pinned analysis tools | nothing |

`g2-build` proves the container format and payload identities. It does not
reconstruct source. The byte-identical C builds are defined phase by phase in
[`roadmap.md`](roadmap.md) and gated by
[`../g2/workflow/PROCEDURE.md`](../g2/workflow/PROCEDURE.md).

## When a target fails

- **`cannot read ... provider` or `official payloads not present`:** the
  untracked inputs are missing. Put them where the identity record says.
- **A digest mismatch** means the input is not the pinned artifact. Do not
  re-pin to make it pass. The target identities are fixed.
- **`not at pinned commit`** from `third-party`: a submodule was moved. Run
  `git submodule update <path>`, or record a deliberate upgrade as its own
  change together with the evidence for it.
