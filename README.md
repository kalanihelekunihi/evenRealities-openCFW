# openCFW

Open, source-controlled firmware for Even Realities hardware.

**Goal:** for each device, decompile the official firmware image, recover
reviewed pseudocode for all of it, and then rebuild C source that compiles and
packages into an image **byte-identical** to the official one. Upstream code
that the firmware links (RTOS, BLE stacks, graphics, codecs, vendor SDKs) is
identified, pinned to exact commits, and consumed from those pins. Later
updates can then pick up upstream fixes and keep the devices maintained.

| | [`g2`](g2) | [`r1`](r1) |
| --- | --- | --- |
| Device | G2 smart glasses (and charging case) | R1 smart ring |
| Application MCU | Ambiq Apollo510B (Cortex-M55), one per temple | Nordic nRF52840 (Cortex-M4F) |
| Other programmable parts | EM9305 BLE controller (ARCv2 EM), GX8002 voice codec (C-SKY CK804EF), PSoC 4000T touch, STM32G0 case MCU | S140 7.2.0 SoftDevice, Secure DFU bootloader |
| Locked reference | EVENOTA `s200_v2.2.6.10`, six payloads ([target lock](g2/workflow/target.json)) | application `2.2.6.0009` with its bootloader and UICR ([rebuild oracle](r1/research/decompilation/rebuild)) |
| Original toolchains | IAR EWARM (Apollo), Synopsys MetaWare (EM9305), C-SKY GCC (GX8002), GCC (touch, case) | Arm Compiler 5 (armcc) |
| Process | [pseudocode-first workflow](g2/workflow/README.md) | decompilation corpus and source correlation in [`r1/research`](r1/research) |

Pseudocode coverage, source completeness and byte equality are separate gates.
None of them is complete for either device yet. Equivalent replacements,
retained opcode arrays, stock-byte overlays and clean-room reimplementations
do not satisfy the byte-identity goal. Some are still in the tree as
historical evidence (see [Repository status](#repository-status)).

## Layout

```
openCFW/
├── AGENTS.md             current work instructions and stage gates
├── Makefile, make.sh     unified entry point
├── docs/
│   ├── hardware/         hardware reference: ICs, buses, pins, protocols,
│   │                     FCC/regulatory data, per-component datasheet notes
│   ├── tooling.md        decompilation, byte-matching, emulation and debug tools
│   ├── methodology.md    evidence and attribution rules
│   └── build.md, repository-layout.md
├── tools/bootstrap/      pinned, fail-closed installer for the analysis tools
├── g2/
│   ├── workflow/         active G2 procedure, target lock, gates, prompts
│   ├── docs/reference/   formats, memory map, toolchains, libraries,
│   │                     protocols, capability checklist
│   ├── symbols/          address-keyed naming seeds per payload
│   ├── config-recovered/ recovered upstream configuration and patches
│   ├── blobs/official/   official payload provenance (payloads not tracked)
│   ├── manifests/        EVENOTA reference manifest (+ legacy profiles)
│   ├── research/         Ghidra decompilation corpus and evidence
│   └── tools/            EVENOTA/container tools, Ghidra pipeline, analyzers
├── r1/
│   ├── docs/             memory map, protocol, storage formats, pinout,
│   │                     toolchain/dependencies, security, correlation records
│   ├── config-recovered/ SDK/RTOS/linker configuration seeds for a stock build
│   ├── research/         application/bootloader decompilation, rebuild oracle,
│   │                     source correlation, BSim runs
│   └── tools/            Ghidra export and verification scripts
└── third-party/          dependency registry: submodules, fetched archives,
                          proposed pins, G2 emulator
```

## Where to start

| You want to | Read |
| --- | --- |
| understand the hardware | [`docs/hardware/README.md`](docs/hardware/README.md) |
| set up analysis tools | [`docs/tooling.md`](docs/tooling.md), [`tools/bootstrap/README.md`](tools/bootstrap/README.md) |
| work on G2 | [`g2/workflow/README.md`](g2/workflow/README.md), then [`g2/docs/reference/`](g2/docs/reference) |
| work on R1 | [`r1/docs/memory-map.md`](r1/docs/memory-map.md), [`r1/docs/toolchain-and-dependencies.md`](r1/docs/toolchain-and-dependencies.md), [`r1/research/README.md`](r1/research/README.md) |
| know which upstream is pinned where | [`third-party/README.md`](third-party/README.md) |
| know what "verified" means here | [`docs/methodology.md`](docs/methodology.md) |

## Official inputs

Official Even Realities payloads are vendor-proprietary and are not tracked.
Put locally authorized copies where
[`g2/blobs/official/g2-2.2.6.10/PROVENANCE.md`](g2/blobs/official/g2-2.2.6.10/PROVENANCE.md)
and [`r1/research/decompilation/rebuild/PROVENANCE.md`](r1/research/decompilation/rebuild/PROVENANCE.md)
say. Every tool checks their SHA-256 before use. `./make.sh g2-build`
repacks the six official G2 payloads into the byte-identical reference
EVENOTA. That confirms the container format, not source reconstruction.

> **History warning:** the Git history retains 52 `g2/.tmp-*` paths and
> descendants (108,601,986 bytes), including official-derived firmware variants
> and exact official-payload copies (SHA-256
> `36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863`). Do not
> publish or mirror this history as-is.

## Repository status

On 2026-09-29 the earlier G2 hybrid-overlay campaign, the R1 clean-room
reimplementation, the retired agent launcher and queue, and the duplicate
vendored snapshots were removed. Their durable knowledge was first
consolidated into the reference documents above. Nothing in the tree yet
rebuilds a payload from source byte for byte. The plan is
[`docs/roadmap.md`](docs/roadmap.md). The removed material is in Git history
at commit `832137ec`.

## Community

Contributions must preserve the provenance, upstream-first and mixed-license
rules described in [CONTRIBUTING.md](CONTRIBUTING.md). Community behavior,
private vulnerability reporting, and support expectations are documented in
[CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md), [SECURITY.md](SECURITY.md), and
[SUPPORT.md](SUPPORT.md).

## Licensing

openCFW-authored software and documentation without a more specific license are
available under the [MIT License](LICENSE); see [NOTICE](NOTICE) for the
licensing boundary. Upstream code in `third-party/` keeps its own licence;
the pins and licences are listed in
[`third-party/README.md`](third-party/README.md). QP/C and g2flash remain
GPL-covered. A firmware binary that combines GPL code with MIT components
must be distributed in compliance with the GPL.

Official Even Realities firmware payloads and captured vendor artifacts are not
covered by the MIT grant and are not tracked.
