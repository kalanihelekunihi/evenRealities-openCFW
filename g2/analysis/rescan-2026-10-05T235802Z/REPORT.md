# Checkout rescan

Compared with the 23:13 UTC snapshot, foundation C/header files increased from 71 to 77 (+6). Changed prior source hashes: 0; removed: 0.

New source files:

- `g2/components/foundation/radio_iom_power_prepare/power_prepare.c`
- `g2/components/foundation/radio_iom_power_prepare/power_prepare.h`
- `g2/components/foundation/radio_iom_release/iom_release.c`
- `g2/components/foundation/radio_iom_release/iom_release.h`
- `g2/components/foundation/radio_transport_pads/transport_pads.c`
- `g2/components/foundation/radio_transport_pads/transport_pads.h`

Saved comparisons bind to current source manifests and ELF files: transport-pad selection 5760 cases/700 traced bytes; IOM release 336/348; power preparation 812/708. All are PASS, with no current manifest mismatch. No comparisons/builds/tests were rerun for this scan.

The cumulative traces were independently deduplicated from all saved comparison inputs: 6290 distinct payload/address bytes, with overlapping values agreeing: {'touch': 234, 'apollo_main': 6056}. Compared with the previous 5,174 total, this adds 1,116: pads570, release190, preparation356. The cumulative inventory total agrees, but its per-payload breakdown is stale (touch234/apollo4940); its script calculates that breakdown before adding these three batches. Use the independently recomputed breakdown above. Original evidence remains unchanged. These counts are bounded execution evidence, not whole-firmware coverage or source-built byte equality.

New behavior: pad dispatch recovers instance/operation-selected pin configurations. IOM release terminates the local queue and clears enable/init state, but does not establish callback draining or asynchronous ownership. Power preparation validates the handle/ready/pending state, optionally snapshots 13 registers and pauses the queue, then clears two submodule-enable bits. Its successful original path stops at 0x55ca72 before physical power callbacks; source success means prepared, not powered down. The existing wrapped-index intermediate RAM-store difference remains an unclosed asynchronous-observer contract.

Saved aggregate: 224 method tests, 218 passed, six method skips and one setup skip, zero failures/errors; affected Ambiq log records 22 passing tests. Independent power review records 11 representative reruns. Power preparation still lacks a top-level narrative/provenance closeout, although source, comparison and review artifacts exist.

New sources are untracked and not ignored. Simulator ELF is ignored by the build/ rule (exact git check-ignore output in snapshot.json). Git committed/staged-only views miss new sources; ignore rules hide build evidence, not these C/header additions.

Optimized tick remains blocked by the preserved Unicorn instrumentation-sensitive limitation. Full power timing, physical shutdown and DMA/ISR quiescence remain unproven. No fully source-complete payload or source-built byte-identical bundle is established.

This scan wrote only its report/snapshot, without changing source, staging, committing or running generators.
