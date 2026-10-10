# G2 third-party shortcut frontier refresh — 2026-10-10

This pass checked whether the completed fourth frontier can be reopened with a changed public input or tool revision. It did not change the campaign ledger, firmware source, or any submodule pin.

## Current evidence

- The fourth frontier's retained scan reports 2,557 registered binary artifacts, 34,282 source files, 287,285 ELF members, and 570,457 sized functions across ARM, older ARC, ARCv2, and C-SKY. Its 545 exact occurrences, 462 relocation-mask candidates, and 168 natively validated unique provider functions remain *candidate evidence*, not accepted P2 coverage. See `../shortcut-theory-fourth-frontier-20261009/REPORT.md` and `../shortcut-cross-corpus-20261009-agent3/final-summary.json`.
- The three requested tool submodules remain at Ghidra-MCP `9cc29c0f1efb6c63a7d6898c9a23aff39397f992`, Ablation `97e051b44d1ac8129b35556fe533e6e8b5338db2`, and REA `7aa4d768eb15317a63a476431ed75bafec086033`. The working tree and index have no changes to those gitlinks or `.gitmodules`.
- Live `git ls-remote HEAD` on 2026-10-10 found NationalChip `lvp_kws` at `8bf9ee5cb6eeb226011e61c15fa4981b83b93bd5`, `lvp_sed` at `28439b899f395b546f578bfe459dc4226428f0f0`, and Ghidra-MCP at `9cc29c0f1efb6c63a7d6898c9a23aff39397f992`. These match the previously inspected heads. No changed repository content was identified to download or pin.
- `g2/workflow/state.json` still says `P2_EXECUTING`; G2 pseudocode completion through G6 exact build are `not_run`.

The three GPT-6.1 Sol Low worker starts were rejected by the model service with HTTP 403, `Daybreak isn't available for this model`. A retry of two lanes returned the same error. This is a model entitlement/routing failure, not a cybersecurity classifier decision or a reverse-engineering result. No agent report or acquisition came from those failed starts.

## Boundary and next evidence

The previously completed fourth frontier remains the finite exhaustion boundary for the *currently registered* third-party and dependency corpus. A new authenticated producer input, a concrete stock body discriminator, or independent P2 review of the ten saved IAR exact occurrences would reopen a bounded investigation. Private historical `lvp_tws`, EM9305 v4.2, producing IAR DLIB/MetaWare inputs, target CapSense generator configuration, resident ROM, and hardware behavior remain unavailable or separate evidence classes. Public similarity matches alone cannot advance the G2/G3 gates or establish a custom-compilable image.

No new public Git source met the threshold for a submodule in this refresh. Ghidra-MCP and REA remain useful analysis transports; the registered exact-byte, native extraction, relocation, and controlled-execution oracles are the stronger evidence for the existing candidate identities.
