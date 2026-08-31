# Apollo-main liblc3 encoder build component

This component compiles and section-GC links the admitted Google liblc3
v1.1.3-compatible encoder source boundary for Cortex-M55. It is intentionally
**build-only and unplaced**: it emits no OTA image, assigns no runtime address,
patches no stock callsite, and does not route `service_audio.c`.

The output directory contains:

- `liblc3_encoder.text.bin` — retained, unrelocated executable bytes;
- `liblc3_encoder.rodata.bin` — retained, unrelocated constant tables;
- `liblc3_encoder.data.bin` — retained, unrelocated writable pointer tables;
- `liblc3_encoder.relocatable.o` — the authoritative relocation-bearing ARM
  object for a future placement/link layer; and
- `build-report.json` — source, toolchain, object, section, root-symbol,
  relocation, import, and non-routing receipts.

The local linker roots only the four bounded-provider entries. It proves that
decoder and PLC sections are absent, discards 87 individually authenticated
canonical CANTUNWIND rows, and rejects any import outside the exact allowlist
in `components/shared/liblc3/encoder_source_admission.json`. The raw section
artifacts are not loadable by themselves because their 567 relocations remain
unresolved until placement is authorized.

Build the reviewed Apple Clang/LLD profile with:

```sh
python3 g2/components/apollo_main/liblc3_encoder/build_component.py
```

Run the deterministic build qualification with:

```sh
python3 -m unittest -v g2.tests.test_apollo_liblc3_encoder_component
```

The maintained finalizer now closes the admitted memory/math imports and
applies all 484 retained text, rodata, and immutable-table relocations in a
synthetic placement. The five immutable pointer tables occupy 404 XIP bytes
with no runtime copy and no table RAM. The compact `service_audio` adapter also
fits the four authenticated 2,628-byte stock contexts exactly (10,512 writable
bytes total) with no additional runtime-writable allocation. These receipts do
not authorize production routing: the specialized closure still has a
30,516-byte authenticated flash-placement shortfall before service routing.
The exact two-entry stock ABI shim is now source-closed and synthetically
finalized, but raises the canonical Apple closure shortfall to 34,084 bytes.
No stock patch is emitted. Hardware cadence, acoustic, BLE interoperability,
stack, and WCET evidence remain unavailable.

The current placement investigation is machine-readable in
`placement_routing_proposal.json`. It authenticates the five stock
`service_audio.c` calls and proves that the 128,752-byte aligned closure cannot
fit in the 71,100-byte Apple append interval. Even counting all reserved PT
padding and removing the existing LTPF component leaves a 34,784-byte
aggregate shortfall, so no placement or routing patch is emitted. Reproduce
that fail-closed result with:

```sh
python3 g2/tools/analyze_g2_liblc3_encoder_placement.py --pretty
python3 -m unittest -v g2.tests.test_analyze_g2_liblc3_encoder_placement
```

The separate `specialization_experiment.json` records the only reduction the
current service evidence permits: disabling LC3-Plus HR while retaining every
runtime-selectable non-HR duration, rate, bitrate, stride, and PCM format. It
reduces the aligned span from 128,752 to 101,616 bytes but still exceeds
authenticated headroom by 30,516 bytes. A smaller build which also disables
LC3-Plus durations is emitted only as an explicitly rejected counterfactual.
Run the deterministic experiment and its evidence audit with:

```sh
python3 g2/components/apollo_main/liblc3_encoder/build_specialization_experiment.py
python3 g2/tools/analyze_g2_liblc3_encoder_specialization.py --pretty
python3 -m unittest -v g2.tests.test_apollo_liblc3_encoder_specialization
```

The follow-on `capacity_rebalancing_proposal.json` audits source-owned stock
patch spans as possible containers for already admitted closures. A minimal
82-slot prefix would save 30,676 append bytes and leave 172 bytes before the
protected update record after the specialized encoder, but that result is
conditional: a stable-order repack would still move 206 leaves whose relocation
contracts are not marked strict, while the minimum unavoidable suffix itself
now has no non-strict member.
The proposal still changes no placement and does not authorize routing because
the required production repack would displace existing live closures and has
not been admitted into the canonical final image.

The admitted `-Oz` closure enables a smaller capacity proof that does not move
those 206 leaves. `service_audio_suffix_pack_proposal.json` moves only the
final 84 strict leaves (9,252 contiguous bytes) into seven authenticated
stock-slot NOP tails. Exact replay leaves 96 bytes before `0x007FE000`. This is
capacity authority, not routing authority. A dedicated production-order replay
now closes exact ownership/bindings for all 11 runtime imports, consumes all
485 Apple relocations, and verifies the 78 immutable initializers and six table
references at this placement. Atomic package/OTA integration remains
fail-closed, so no stock image is emitted.

Reproduce the fail-closed capacity and branch-reach audit with:

```sh
python3 g2/tools/analyze_g2_liblc3_encoder_capacity.py --pretty
python3 -m unittest -v g2.tests.test_analyze_g2_liblc3_encoder_capacity
```

The seven-function suffix is audited separately in
`suffix_strict_contracts.json`. All seven closures now satisfy strict symbol
and relocation replay at both current and proposed addresses: 8,910 bytes and
44 relocations in total. The 3,508-byte formatter engine uses a reviewed
same-section `R_ARM_THM_CALL` to its own runtime entry, with no embedded
placement-specific pointer. Capacity rebalancing nevertheless remains blocked
on production repack integration and exact final-image ingress routing.
Synthetic LC3 relocation, runtime binding, immutable-data policy, and the
bounded service-audio adapter are separately closed and tested, but do not
supply missing flash capacity. Reproduce the fail-closed routing audit with:

```sh
python3 g2/tools/analyze_g2_liblc3_encoder_suffix_contracts.py --pretty
python3 -m unittest -v \
  g2.tests.test_analyze_g2_liblc3_encoder_suffix_contracts
```

`service_audio_route_experiment.json` admits the exact stock setup and encode
ABIs at `0x0057A926` and `0x0057A940`, all nine whole-image ingress sites, and
their complete four-context literal provenance. The dedicated builder links
the shim, compact-state adapter, specialized encoder, and immutable tables,
then uses the component finalizer to apply every relocation at synthetic
addresses. The proposed entry veneers are Thumb-2 `B.W` tail branches, so the
callers' original link registers are preserved. Reproduce the route boundary
with:

```sh
python3 g2/tools/analyze_g2_liblc3_service_audio_route.py --pretty
python3 -m unittest -v \
  g2.tests.test_runtime_liblc3_service_audio_stock_shim \
  g2.tests.test_analyze_g2_liblc3_service_audio_route
```

`service_audio_capacity_experiment.json` additionally tests the complete route
with `-Oz`, section GC, LTO, and constant merging against the package-verified
whole Apollo address space. The accepted Apple `-Oz` closure is 19,360 text +
60,480 rodata + 404 table bytes and retains the same 11 external imports. It
still misses the only unowned append interval by 9,152 bytes after considering
all six section orders. LTO and no-GC violate the admitted table/writable-data
policy; constant merging saves no bytes. No production placement is emitted.
Reproduce the audit with:

```sh
python3 g2/tools/analyze_g2_liblc3_service_audio_capacity.py --pretty
python3 -m unittest -v \
  g2.tests.test_analyze_g2_liblc3_service_audio_capacity
```

`service_audio_production_replay.json` pins the LC3-owned ten-symbol scalar
runtime plus the source-owned `sqrtf` leaf, then repeats the exact final link
under Apple Clang 21 and LLVM 22. The Apple replay emits 19,360 text + 60,480
rodata + 404 immutable-table bytes, consumes 485 relocations with zero output
relocations/imports, and ends 96 bytes below `0x007FE000`. It only writes
temporary build evidence and keeps routing, image emission, and hardware
operations false. Reproduce it with:

```sh
python3 -m unittest -v \
  g2.tests.test_runtime_liblc3_target_runtime \
  g2.tests.test_apollo_liblc3_service_audio_production_replay
```
