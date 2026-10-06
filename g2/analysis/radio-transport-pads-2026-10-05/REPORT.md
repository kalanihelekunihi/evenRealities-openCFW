# Transport pad release prerequisite

Implemented `g2/components/foundation/radio_transport_pads/transport_pads.c` and its header: complete570-byte dispatcher0x4c2e30 called by release0x52df12 before later HAL helpers. It links the unchanged pinned GPIO configuration source and actual PRIMASK provider. It does pad configuration, not IRQ/NVIC control. See pseudocode.md for ordered groups, reconstructed interface and static release call chain.

The selector is `(uint8_t)operation | (instance<<2)` after instance<8 validation. Four-pad and two-pad groups are ordered; unmatched selectors are no-op. Higher command bits can select another group. Instance8 passes release's separate<9 guard but does no pad work here. Every pad call reloads configurationword78ee48=3 and ignores its status. Masking is per GPIO call; no broad atomic section was added. Void residualR0 is not interpreted as status.

Fresh original/source/independent-model comparison PASS5760cases,700 distinct original instruction bytes, all570 dispatcherbytes executed. No executable stubs. Coverage includes every commandbyte, invalid instances, both masks, highbyte truncation, and synthetic per-pin validation failures. The new disjoint ledger adds570bytes,5174→5744. Source and ELF hashes match current disk. Independent reviewer ran10 representative cases; see review/ for final disposition.

Fresh affectedAmbiq22 tests pass. Aggregate43modules224methodtests218pass6methodskips+1setupskip,zero fail/error. Build is Cortex-M4 Thumb2 O2 callable semantic profile, not production compiler or byte equality. build-provenance.json binds source/header/providers/objects/ELF and results. Discarded inefficient and crossing-page fixture attempts are recorded in fixture-diagnostics.md and not credited.

Release-wrapper ordering and tracking-byte clearing are static observations only. Later disable-like0x55c430, power-like0x55c7e8 and uninitialize-like0x55c286 attribution remains inferred/unverified. Command-queue release0x53909a, DMA/buffer ownership, callbacks, pendingIRQ/NVIC and live instance identity are outside this provider. No full shutdown success/safety claim. The next necessary bounded provider is command-queue release and its allocator/ownership effects needed by the disable-like helper.

The old59 source identities, packer, manifest, workflow state and timer ELF remain unchanged. Optimized tick remains BLOCKED. Zero source-complete payloads and no source-built byte-identical bundle are established. No commit, staging, flashing or deployment.
