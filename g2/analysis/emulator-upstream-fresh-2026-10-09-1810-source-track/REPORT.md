# Emulator-to-upstream fresh scan after reviewed 17:16 baseline

One newly useful reference/tooling lead was found: **Pigweed HCI Emboss schemas**, already cited by the emulator but absent from inspected OpenCFW registrations, consolidated library/tooling records and previous scan reports. This is newly acquired protocol-schema evidence, not a new G2 SDK family or hardware identification.

## Acquired public reference

Official upstream https://pigweed.googlesource.com/pigweed/pigweed ; current HEAD verified as `de25dbea944d7d6e11353eb5c4a299ae0e3e7117`. Selected immutable emulator-audit pin `e175383a07c5b811a98924fc662d1001f1d220d0` so the source comparison remains reproducible. Acquired `hci_events.emb`, `hci_commands.emb`, imported `hci_common.emb`, and root LICENSE. All schema source notices are Apache-2.0. Exact URLs, byte counts and SHA256 are in `references/pigweed-hci/provenance.json`. No schema compiler or downloaded code executed.

Emulator `docs/connected-r1-frontier.md:193` explicitly cites this source for LE state interpretation. Pinned `hci_events.emb:1210–1253` defines the supported-state bitmap, including bit6 initiating, bit35 central connection plus connectable/scannable advertising, bit41 peripheral connection plus initiating. Its command-complete structure at1256 includes status and an8-byte bitmap. `G2EM9305.cs:855` responds to opcode201C using its supplied leStates fixture. These bindings explain a concrete analysis shortcut: use the schema's field offsets, bit names and packet lengths to review static HCI event consumers/captured packets, instead of manually reinventing standard layouts.

Confidence high for public schema/protocol interpretation, medium for usefulness to specific unreviewed G2 consumer ranges, low for stock source attribution. It cannot establish physical EM9305 simultaneous-role capacity, prove that a fixture's advertised bits are silicon-supported, or supply vendor-specific opcode behavior. It is not the producing Cordio/EM SDK.

Concrete next finite tests: choose authenticated G2 HCI201C command-complete consumer and frozen packet evidence; verify status position/8bytebitmap length and bit6/35/41 consumption against the pinned schema. Compare existing DLE/LE connection event parser lengths using the corresponding schemas. Emboss generation would require its separate compiler/dependencies and authorization as a tooling step; no install/build is needed to inspect the schemas. No complete schema-compilation claim is made.

Registration proposal: retain the four small pinned reference files with provenance, or a reviewed Pigweed reference submodule if further modules become demonstrably useful. Do not add an entire firmware dependency or change existing Cordio registration merely because the schema agrees. No registration was applied.

## Known and excluded candidates

- TDK revision/patch match, IOM6/GPIO cross-version binding, BQ wholebyte28 update, Macronix protocol/error-path findings and OPT300x/Goodix comparators belong to the baseline and subsequent already reported bindings, not this scan's new results.
- nPM1300 comments point to official npmx and Nordic documents; existing registered npmx `e1aaec53f456887a7d7b80d82f684d1ac3cb08c8` already supplies that provider. No duplicate SDK justified.
- EM9305/Ambiq, ICM45608, BQ25180/BQ27427, PSoC and Nema peripheral comments point to already indexed references or known acquired source families. No newly justified vendor download emerged from these comments.
- `pyproject.toml` lists Capstone, Unicorn, Pillow and optional Hypothesis/pytest/cryptography. OpenCFW tooling already covers the relevant static/differential analysis tools. Emulator g2scatter is a local analysis entrypoint, not a newly discovered manufacturer compiler or firmware source. Decoder mapping was already authenticated in baseline follow-ups.
- Emulator lock's g2flash is already registered at `third-party/reference/g2flash`; Faceclaw/other app carriers are community protocol/resource references, not authoritative manufacturer SDKs. No acquisition was justified without a new address-bound discriminator.
- Renode/runtime pins remain emulator build dependencies, not evidence of the firmware's producing compiler. Known exact-producer/private-ROM and physical timing boundaries remain.

Repository AGENTS/workflow were read. Neither repository has an applicable local .agents/.codex skill directory in the inspected root. Buzzer work was excluded under emulator's explicit instruction. No workers spawned, execution/device actions/emulator edits/seal changes/campaign changes/index writes/commits/pushes. This is a finite source-comment/dependency/reference pass, not proof that all public sources are exhausted.
