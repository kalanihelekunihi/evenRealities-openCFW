# FreeRTOS scheduler cluster production-promotion plan

Status: promoted and reproducibly verified for canonical Apple and exact-root
Linux profiles; no hardware operation performed

Scope: Even Realities G2 firmware `2.2.6.10`, Apollo-main component, offline
source/build analysis only; no signing, flashing, debugger, serial, or hardware
operation

## Decision

Promote the following six authenticated FreeRTOS-Kernel V10.5.1 functions as
one fail-closed production tranche, in dependency order:

1. `open_cfw_freertos_port_yield`;
2. `open_cfw_freertos_port_enter_critical`;
3. `open_cfw_freertos_port_exit_critical`;
4. `open_cfw_freertos_task_reset_next_task_unblock_time`;
5. `open_cfw_freertos_task_increment_tick`; and
6. `open_cfw_freertos_task_resume_all`.

All six should be registered as **relocated leaves at the current overlay
tail**, even when a leaf has no relocation. That keeps every current function
offset stable, limits profile-dependent pin churn to the new tail, lets the
builder resolve the cluster by named providers, and avoids inserting new
isolated leaves before the already pinned relocated-leaf sequence.

There is no unresolved target-code, topology, relocation, branch-range, or
overlay-capacity blocker. The earlier host differential crash was diagnosed as
a host-only strict-aliasing issue in the FreeRTOS `MiniListItem_t`/
`ListItem_t` common-prefix oracle. Both host translation units now compile with
`-fno-strict-aliasing`; target sources and target objects did not change. The
current Apple suite passes 33/33, the current `/workspace` Linux suite passes
33/33, and an independent exact-root Linux run at
`/Users/kalani/Repo/SybilSightABCD/openCFW` passes 33/33.

The original remaining gates were normal promotion actions: register and
record the leaves, verify the computed placement/relocations, refresh artifact
pins and aggregate assertions, and pass both complete profile builds. Those
gates are now complete; final recorded hashes appear at the end of this
document.

## Authenticated inputs

The stock provider remains the 3,523,396-byte official Apollo-main package,
SHA-256
`36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863`,
with a 32-byte preamble and runtime base `0x00438000`. The source comparator is
FreeRTOS-Kernel V10.5.1 commit
`def7d2df2b0506d3d249334974f51e427c17a41c`, authenticated by the vendored
snapshot verifier.

| Boundary | Current source file | Bytes | SHA-256 |
|---|---|---:|---|
| scheduler-port trio | `research/candidates/freertos_scheduler_port_trio.c` | 5,437 | `8fdefac8d8219c25b9a7a5424b6469b2882f9ae0331bfe33e69720b804a9a24e` |
| scheduler-port interface | `research/candidates/freertos_scheduler_port_trio.h` | 814 | `8b5e6fb78ae1c3211e7bf0925ede8c04c1bc8d7dd2102a1b11814c545a40c0f4` |
| reset-next helper | `components/shared/freertos/runtime_freertos_reset_next_task_unblock_time.c` | 2,544 | `afaf50d27bf7fc9a106e15b9318d36f0afa6ff6ba35619269297f41e3ce867b8` |
| reset-next interface | `components/shared/freertos/runtime_freertos_reset_next_task_unblock_time.h` | 4,721 | `33d825bc20a59592935908a88a061062707fc5e81590f077a7adb2324ef07073` |
| tick increment | `components/shared/freertos/runtime_freertos_task_increment_tick.c` | 6,927 | `0fb59aba7fb8b8ab1f7fc2b2cc5095f9bb05334770d44790a42b33ad80369cb2` |
| tick interface | `components/shared/freertos/runtime_freertos_task_increment_tick.h` | 11,502 | `0e7990ad52bc620fd9529b350baab42c22b06cb6ad916e6bcf535f12f560d906` |
| resume-all | `components/shared/freertos/runtime_freertos_task_resume_all.c` | 6,119 | `72d617c82f5f5650e8e08a4ba4ac112eb42cbd576b483c3aaaf774dc88f3010f` |
| resume-all interface | `components/shared/freertos/runtime_freertos_task_resume_all.h` | 10,646 | `54bc1f998021817aabf566b260de6028912caf07fdc38f8aa91ab7adb4b749ff` |

The port trio may be registered from its currently authenticated research path
without changing its bytes. Moving it to `components/shared/freertos` is a
reasonable repository-hygiene follow-up, but any rename/include edit changes
the source pin and must precede the record build. It is not a technical
promotion blocker.

## Exact stock ownership and redirect coverage

| Stock function | Complete stock range | Bytes | Stock SHA-256 |
|---|---|---:|---|
| `vPortYield` | `[0x004420BC,0x004420D0)` | 20 | `dd981b3e9196c6fd87bb79719c94628c89e564d5728b3fdd1ff08c397eccb397` |
| `vPortEnterCritical` | `[0x004420D0,0x004420E8)` | 24 | `5809638c22f928d2b32cd21cc9b92a292fad24cd8b8008de4ad92b9faeaba0d4` |
| `vPortExitCritical` | `[0x004420E8,0x00442114)` | 44 | `bfd3ddb76c61ad634a3f58ed203260da3834895b646c9dffada546f9dc9d2a31` |
| `xTaskResumeAll` | `[0x00454DCC,0x00454EFE)` | 306 | `548e05e1f8a2f498372dd1f4eb7c6536e093dbbfdb82fbe8f9b54231cedc8a09` |
| `xTaskIncrementTick` | `[0x0045504C,0x0045519E)` | 338 | `438ad4e9e1a7b439671463b2bbfd13616ebb6de32bd2aad53b802d31f11cc050` |
| `prvResetNextTaskUnblockTime` | `[0x00455876,0x0045589C)` | 38 | `a789916ee424c824c5c5f2302e62e4a861f0fa1289917d9c0e095947bce82598` |

The complete replacement owns 770 stock bytes. Each patch site must use one
four-byte Thumb `B.W` followed by `0xBF00` NOPs through the end of the exact
authenticated span. No old instruction, literal, alignment halfword, or
alternate entry remains executable inside a replaced range.

The following replacement pins are determined by the proposed tail placement.
They are not whole-artifact hashes.

| Function | Apple target / branch bytes / replacement SHA-256 | Linux target / branch bytes / replacement SHA-256 |
|---|---|---|
| `vPortYield` | `0x007B0868` / `6ef3d4bb` / `18d191d67d45cf2fd730db9dd1a218ec37bda727a3806dc50f34cf1ff3b4effa` | `0x007B0FA0` / `6ef370bf` / `b81e181780ee375a71c104ce812f97a763ff9c7a26e8b83b7991d4ab0eb2a569` |
| `vPortEnterCritical` | `0x007B0880` / `6ef3d6bb` / `147a84cc4e3adc172e0f25f9ce0d20805d4decb4257ce95eab88ff0a2dd99aac` | `0x007B0FB8` / `6ef372bf` / `9724000f0bd958bf5830c3e42dd8ff99ee83a27fb0a3154ee97d7ed5a8e0ffb6` |
| `vPortExitCritical` | `0x007B08A0` / `6ef3dabb` / `7833c0cfe8a87b8af156ec1e2204b10dfb1b17654dfa0b6e5d63c1e61222ea11` | `0x007B0FD8` / `6ef376bf` / `f42a12137c8886c08c53d29b1387342ab03b6250c778ceb338ae4585301b7929` |
| reset-next | `0x007B08D8` / `5bf32fb8` / `cb08f56dbf3a1f8d53d5c33c6c391e1ff0b6e9eb336cfe7fd3a47d6d8d5551d6` | `0x007B1010` / `5bf3cbbb` / `b5b0b4dd174125dc7e426baf3017af9920ed4ce468a6429b82147b69fdeff14b` |
| increment-tick | `0x007B08F8` / `5bf354bc` / `af1aaf8e1cbc881b331f23c76e6d611b06a523e3fde7c7a78afbb73dfa81dde8` | `0x007B1030` / `5bf3f0bf` / `c0bd7cb134c2a6287213251f4e1905e3789392b93da30ebee50160cbfc029f95` |
| resume-all | `0x007B0A50` / `5bf340be` / `0eacb13f66c5169738678544788c152babe81275c890d85fd0f69b5fb4c538ac` | `0x007B1184` / `5cf3dab9` / `da5c39aba7bc5bcadc00ffd61333e07c3fbbc40e80dc84fe2798407e69f93e56` |

Every branch round-trips through the overlay builder's Thumb decoder. The
largest displacement is well inside the signed Thumb-2 wide-branch range.

## Whole-image entry, interior, and stored-pointer closure

Entry redirects are sufficient because every recoverable external control-flow
edge reaches a public start and no authenticated alternate owner enters an
interior instruction.

| Entry | Direct `BL` callers | Caller-address SHA-256 | Address+encoding SHA-256 | Stored-pointer result |
|---|---:|---|---|---|
| port yield | 21 | `a3e06a6ce5af90723601814b9ab099b79ec4240fcfb185ae287630f5b2ab90a7` | `82bf0d7ac31cb2985e55ebbe5e31791d74e3c826be25da010fd121d281bd7001` | no aligned entry/interior pointer; 20 odd unaligned false hits into port-exit interior are pinned |
| port enter | 45 | `65bc28cb458bf50bb2b30160bf661f686d8ce2d9fcdae800244ed901933f3993` | `8365ac4db9e8d5531c7791a7462440c5999ce30de0ef75c43e004233c3295792` | no aligned entry/interior pointer |
| port exit | 51 | `61250f3aa182674a0ee06462d2efaf5308511f36178f58561040dac2c1d5b631` | `605cbb784ec11f6d07fbf7e4f26d16d8b6c51263be5d10e88f46a76f81a0cafd` | no aligned entry/interior pointer |
| resume-all | 21 | `0376e19f832cae16a06c7f82772d8447c7b0ba259829731b5f2d9fd459bbcbbf` | `b6a64bf2fc5277484f9ec220ae171f77a520adb1bcf03c9b57f56360a9a769f2` | no entry pointer; 22 incidental interior-valued byte patterns, digest `3bbc8c32bcc73d9275d5a486a5f909a19718991b19f668ff857ee80e49e280a8` |
| increment-tick | 3 | `1a3ea5d9db1d906a1f91d344c8e6228b55ed15522fc8ca7186f50e5846f25d7d` | `2102130f9d20f69f316b7e41d3d36c9e142ab1c323c19647b815347364fa9cfb` | six odd/unaligned false positives only, record digest `a62e912b15215e33f75cb097bcf6575df948fb0ee4d5ca7a1a2192f4e75d7c6c` |
| reset-next | 6 | `e849e824765de1654a2c5cca71758a37bce2729459dc5f3b7cb71b9854082c56` | `012189a12f316609470b8801612f6365db31ce8510ec46a218c3044a02a86fd3` | no entry or interior pointer |

The scans also prove no external `B.W`, narrow `B`/conditional branch,
`CBZ`/`CBNZ`, or wide conditional branch reaches a cluster entry or interior.
Some listed callers are inside stock cluster bodies and disappear into NOP
fill during promotion; their new equivalents are explicit named relocations.
All remaining stock callers continue to reach the complete entry redirect.

## Proposed placement, alignment, and capacity

The current overlay runtime base is `0x00794324`. Canonical Apple currently
ends at offset 116,034 (`0x007B0866`); Linux currently ends at offset 117,882
(`0x007B0F9E`). Each new function requires four-byte alignment.

| Function | Size Apple | Apple offset / runtime | Size Linux | Linux offset / runtime |
|---|---:|---|---:|---|
| alignment before yield | 2 | `116034..116036` | 2 | `117882..117884` |
| port yield | 24 | `116036` / `0x007B0868` | 24 | `117884` / `0x007B0FA0` |
| port enter | 30 | `116060` / `0x007B0880` | 30 | `117908` / `0x007B0FB8` |
| alignment before port exit | 2 | `116090..116092` | 2 | `117938..117940` |
| port exit | 54 | `116092` / `0x007B08A0` | 54 | `117940` / `0x007B0FD8` |
| alignment before reset-next | 2 | `116146..116148` | 2 | `117994..117996` |
| reset-next | 32 | `116148` / `0x007B08D8` | 32 | `117996` / `0x007B1010` |
| increment-tick | 344 | `116180` / `0x007B08F8` | 338 | `118028` / `0x007B1030` |
| Linux-only alignment before resume | 0 | n/a | 2 | `118366..118368` |
| resume-all | 292 | `116524` / `0x007B0A50` | 292 | `118368` / `0x007B1184` |
| new overlay end |  | `116816` / `0x007B0B74` |  | `118660` / `0x007B12A8` |

The Apple tail grows by 782 bytes: 776 function bytes and six alignment bytes.
The Linux tail grows by 778 bytes: 770 function bytes and eight alignment
bytes. The builder limit is `0x007F0000`, leaving 259,212 bytes after the Apple
placement and 257,368 bytes after the Linux placement. Capacity is not a
blocker.

The canonical manifest gains eight stock-region records: four from splitting
the one opaque port region, one each for the resume and reset tail splits, and
two for the tick interior split. It also gains six appended source-leaf records
and three Apple alignment records. The Apollo-main region count therefore moves
from 788 to **805** if the proposed order and source paths are retained.

## Per-profile object and relocation contract

| Function | Apple unrelocated size / SHA-256 | Linux unrelocated size / SHA-256 | Relocations |
|---|---|---|---|
| port yield | 24 / `105148e84e8d81859d7c85803d553503d05745bd56d807495d62f3bf9da68235` | identical | none |
| port enter | 30 / `18797972899b42b6333a1353a25820dc720a5e477d0275b3fb4f039cbc0ef158` | identical | `+0x02 R_ARM_THM_CALL -> ulSetInterruptMask` |
| port exit | 54 / `1106c10ba143e84c0335da8c09658f88594e4578a8dfece201e73ee36f00900f` | identical | `+0x1C R_ARM_THM_JUMP24 -> vClearInterruptMask`; `+0x22 R_ARM_THM_CALL -> ulSetInterruptMask` |
| reset-next | 32 / `249e6dafc8adc7286fbf5b96db744f902a04c7a38709a4344f766e01ec264a5f` | identical | none |
| increment-tick | 344 / `453dd5addafa0fade84729e0f215668b067055eea7daf43cc089b9ee98e02888` | 338 / `889ae62e4116bbd1bd8c8db65612b779372dfe8a4f26e5c78e3a0828e1671c5a` | Apple `+0x3C/+0x64`; Linux `+0x38/+0x60`; calls mask/reset respectively |
| resume-all | 292 / `8b8a8bde3a875d1b4f6b28d3aa0e4bedf2c80f80d0c0c380614e3e1a8c4216a3` | 292 / `7fb0e6bab36ed324d800362e1d1f85e29b8b7924e6cbe994600ebe998fe025a6` | six calls at `+0x12/+0x22/+0x2E/+0xEE/+0xFC/+0x11C` to enter/exit/mask/reset/tick/yield |

With current production providers and the proposed placements, the required
relocated function hashes are:

| Function | Apple relocated SHA-256 | Linux relocated SHA-256 |
|---|---|---|
| port yield | `105148e84e8d81859d7c85803d553503d05745bd56d807495d62f3bf9da68235` | same |
| port enter | `c382397165ed32cec367e2ceb68f6af24ce748937cef326d825270741bafab7f` | `5b83770b60d27de697acae48b58eba3b27d55ab668c775c9d858c73f395877e4` |
| port exit | `da3e6da9d2363ba358f7b6bbbd098a7cd7483807ec37477497db2d31632e4e9c` | `1e97f6015a84574113451a4da90c9bd1e22dbc2570f7b1db11ba9c0f6d9b5228` |
| reset-next | `249e6dafc8adc7286fbf5b96db744f902a04c7a38709a4344f766e01ec264a5f` | same |
| increment-tick | `1aec337b980ad1a9719f7bed519894ea3b7a8d2a0cecc239309a55729b40ecef` | `6fabcf5492fe4171cf7b27c225fc7a65730906cb9b57ca003c0539a4ddda3ea1` |
| resume-all | `e608ef2a9725d183beb19220d7c864691b2affa85e64372cf62350d671badcdd` | `43b18067bfa208746aff747013f4daf4d16f198474cc8891aebf4a0fedfc24d5` |

These hashes assume the current mask-provider offsets remain unchanged. The
record build must still compare rather than trust the plan.

## Dependency-provider bindings

The production graph must use named source providers, never an implicit fixed
address:

```text
ulSetInterruptMask (already source-owned)
  -> port enter
  -> port exit assertion
  -> increment-tick assertion
  -> resume-all assertion

vClearInterruptMask (already source-owned)
  -> port exit

port enter/exit/yield + reset-next + increment-tick
  -> resume-all

ulSetInterruptMask + reset-next
  -> increment-tick
```

Canonical Apple resolves `ulSetInterruptMask` to `0x007B0158` and
`vClearInterruptMask` to `0x007B016E`; Linux resolves them to `0x007B07AC`
and `0x007B07C2`. Both are the existing appended source-owned copies. Their
exact fixed-address source copies remain at `[0x005FA0A4,0x005FA0BA)` and
`[0x005FA0BA,0x005FA0C8)`, preserving all stock callers. Cluster relocations
must bind to the appended named providers, matching current relocated-leaf
policy.

No function section has any other undefined symbol. Fixed G2 RAM/MMIO seams
are materialized in the code and produce no linker relocation. Normal
`.ARM.exidx` `R_ARM_PREL31` records are extractor metadata, not runtime
providers, and are not appended with the isolated function section.

## Expected accounting transition

### Canonical Apple component

| Metric | Before | Delta | Expected after record build |
|---|---:|---:|---:|
| source-owned bytes | 116,216 | +782 | **116,998** |
| source-owned in place | 182 | 0 | **182** |
| generated patch-site bytes | 81,708 | +770 | **82,478** |
| replaced stock bytes | 81,890 | +770 | **82,660** |
| opaque base bytes | 3,441,474 | -770 | **3,440,704** |
| generated wrapper bytes | 32 | 0 | **32** |
| overlay bytes | 116,034 | +782 | **116,816** |
| component bytes | 3,639,430 | +782 | **3,640,212** |
| filtered functions / patch sites | 596 / 563 | +6 / +6 | **602 / 569** |
| raw configured functions / patch sites | 600 / 567 | +6 / +6 | **606 / 573** |

### Linux component

Linux production includes four profile-only leaves filtered from Apple. Their
four stock replacement spans total 166 bytes. Linux pre-promotion accounting
is therefore 118,064 source-owned bytes, 81,874 generated patch bytes, 82,056
replaced stock bytes, and 3,441,308 opaque base bytes.

| Metric | Before | Delta | Expected after record build |
|---|---:|---:|---:|
| source-owned bytes | 118,064 | +778 | **118,842** |
| source-owned in place | 182 | 0 | **182** |
| generated patch-site bytes | 81,874 | +770 | **82,644** |
| replaced stock bytes | 82,056 | +770 | **82,826** |
| opaque base bytes | 3,441,308 | -770 | **3,440,538** |
| overlay bytes | 117,882 | +778 | **118,660** |
| component bytes | 3,641,278 | +778 | **3,642,056** |
| functions / patch sites | 600 / 567 | +6 / +6 | **606 / 573** |

At package level the canonical source/generated/opaque/controlled ownership
transition is expected to be
`116,836/83,501/4,217,547/200,337` to
**`117,612/84,277/4,216,777/200,337`**. The six-byte adjustment from the
original prediction classifies the three new explicit alignment regions as
generated in the manifest while component accounting owns the complete
overlay tail as source. Canonical package size should grow
from 4,417,884 to **4,418,666 bytes** because only the appended source tail
changes size. The flash-plan JSON size and every artifact hash/checksum remain
record-build outputs and are intentionally not predicted here.

## Exact production edit set

### Configuration and manifest

- `components/apollo_main/core_overlay/overlay.json`: add six relocated-leaf
  records in the order above, their source and toolchain pins, both profile
  output/offset/relocation pins, six function names, and six complete `b_w`
  patch sites; refresh overlay/component pins only after record builds.
- `manifests/g2-2.2.6.10-core-source.json`: split the three stock opaque areas,
  add six generated source-entry regions, append six source-leaf and three
  Apple alignment regions, update source/opaque ownership descriptions,
  component/package pins and region totals.

No change is required to `tools/apollo_overlay.py`: it already validates the
needed `R_ARM_THM_CALL`, `R_ARM_THM_JUMP24`, four-byte alignment, named
provider resolution, entry `B.W` plus NOP fill, branch round-trip, and capacity
limit.

### Focused and production tests

The four focused files must stop asserting non-registration and instead prove
the recorded production entries, redirects, placement, providers, profile
pins, manifest regions, accounting, and rollback on any drift:

- `tests/test_freertos_scheduler_port_trio_candidate.py`;
- `tests/test_runtime_freertos_reset_next_task_unblock_time.py`;
- `tests/test_runtime_freertos_task_increment_tick.py`; and
- `tests/test_runtime_freertos_task_resume_all.py`.

Add `tests/test_runtime_freertos_scheduler_cluster.py` as the cluster-level
contract: build all six entries together, assert the complete dependency graph
and resolved calls for both profiles, authenticate all six stock spans and
redirect fills, and verify the pre/post accounting equations.

The aggregate pin assertions currently repeated in these production tests
must be refreshed as one mechanical set after the canonical build:

- `tests/test_core_overlay.py`;
- `tests/test_runtime_cmsis_message_queue_new.py`;
- `tests/test_runtime_cmsis_mutex_new.py`;
- `tests/test_runtime_cmsis_semaphore_new.py`;
- `tests/test_runtime_easylogger_helpers_main.py`;
- `tests/test_runtime_freertos_heap4.py`;
- `tests/test_runtime_freertos_interrupt_mask.py`;
- `tests/test_runtime_freertos_missed_yield.py`;
- `tests/test_runtime_freertos_mutex_held.py`;
- `tests/test_runtime_freertos_ntz_port.py`;
- `tests/test_runtime_freertos_pc_task_get_name.py`;
- `tests/test_runtime_freertos_queue.py`;
- `tests/test_runtime_freertos_queue_delete.py`;
- `tests/test_runtime_freertos_reset_event_item_value.py`;
- `tests/test_runtime_freertos_suspend_all.py`;
- `tests/test_runtime_freertos_task_count.py`;
- `tests/test_runtime_freertos_tick_count.py`;
- `tests/test_runtime_freertos_timeout_state.py`;
- `tests/test_runtime_littlefs_alloc_lookahead.py`;
- `tests/test_runtime_littlefs_disk_version_parts.py`;
- `tests/test_runtime_littlefs_util.py`;
- `tests/test_runtime_littlefs_util_bitops.py`; and
- `tests/test_runtime_tlsf.py`.

`tests/test_toolchain_profiles.py` must qualify the final exact-root Linux
aggregate, while `tests/test_open_cfw.py` must qualify the refreshed package,
flash plan, checksum, and deterministic rebuild. They consume manifest/config
pins and may not need literal edits, but they are mandatory promotion gates.

### Documentation and notices

Change the four isolated audits to include a subsequent-production-status
section with final artifact evidence:

- `docs/research/freertos-scheduler-port-trio-source-boundary-audit.md`;
- `docs/research/freertos-reset-next-task-unblock-time-source-boundary-audit.md`;
- `docs/research/freertos-task-increment-tick-source-boundary-audit.md`; and
- `docs/research/freertos-task-resume-all-source-boundary-audit.md`.

Refresh the current production summary/pin surfaces together:

- `README.md`;
- `components/README.md`;
- `components/apollo_main/core_overlay/EVIDENCE.md`;
- `components/apollo_main/core_overlay/NOTICE.md`;
- `docs/linux-reproducible-build.md`;
- `docs/memory-map.md`;
- `docs/source-coverage.md`;
- `docs/upstream-inventory.md`;
- `docs/research/freertos-g2-config-port-audit.md`;
- `docs/research/freertos-assert-port-seam-source-boundary-audit.md`;
- `docs/research/upstream-library-source-reuse-audit.md`;
- `docs/research/freertos-missed-yield-source-boundary-audit.md`;
- `docs/research/freertos-reset-event-item-value-source-boundary-audit.md`;
- `docs/research/freertos-mutex-held-source-boundary-audit.md`;
- `docs/research/freertos-suspend-all-source-boundary-audit.md`; and
- `docs/research/freertos-timeout-state-source-boundary-audit.md`.

The existing `LICENSE-FreeRTOS-MIT` already supplies the applicable license;
the notice still needs to enumerate the newly admitted source boundaries.

## Fail-closed integration checklist

1. Freeze the four source/header pairs and all focused fixture/test hashes. If
   the port trio is moved out of `research/candidates`, re-run both target
   profiles before using any pin in this document.
2. Re-run the four focused scheduler modules and the interrupt-mask provider
   test on Apple. Require 38/38 total: scheduler 33 plus mask pair 5.
3. Repeat step 2 in the pinned Linux LLVM 22.1.8 image, using the exact source
   root `/Users/kalani/Repo/SybilSightABCD/openCFW`. Keep
   `-fno-strict-aliasing` on the two resume host/oracle builds; do not add it to
   target flags merely to mask a target-code discrepancy.
4. Register the six relocated leaves, named providers, and six stock patch
   sites in `overlay.json`, retaining the order and four-byte alignment in this
   plan.
5. Run an Apple record build. Require the six observed raw sizes/relocations,
   offsets, resolved provider addresses, relocated hashes, redirect hashes,
   overlay end, accounting, and capacity to equal this plan. Abort on the first
   mismatch; investigate rather than updating pins mechanically.
6. Record the new Apple overlay/component pins, then run a non-record Apple
   build twice. Require byte-identical overlay and component outputs.
7. Run the exact-root Linux record build. Require the Linux sizes, relocation
   offsets, providers, offsets, relocated/redirect hashes, end address, and
   accounting above. Record Linux pins, then require two byte-identical
   non-record builds.
8. Update the manifest stock splits and appended records. Require gap-free,
   overlap-free ownership, exactly 770 newly generated patch bytes, exactly 770
   fewer opaque bytes, 805 canonical Apollo-main regions, and unchanged
   `source_appended_boundary=3523396`.
9. Refresh all tests and documentation listed above from the verified build
   reports. Do not copy provisional whole-artifact values from this plan.
10. Run the focused 38-test cluster/provider group, cluster production test,
    aggregate core-overlay tests, all snapshot verifiers, manifest validation,
    `tests.test_toolchain_profiles`, and `tests.test_open_cfw`.
11. Run `./make.sh source` twice under canonical Apple clang. Require equal
    overlay, component, package, flash-plan, and checksum outputs and a package
    size of 4,418,666 bytes.
12. Run `./make.sh verify`, JSON validation, Python compilation checks, and
    `git diff --check`. Confirm no build-generated file is accidentally staged.
13. Only after every gate is green, label the four audits production-integrated
    and publish the final hashes/checksum. Hardware flashing remains a separate
    explicitly authorized and hardware-qualified operation.

## Validation performed for this plan

The current Apple clang 21.0.0 scheduler chain passes 33/33 focused tests. The
current Linux/Homebrew clang 22.1.8 chain also passes 33/33 in `/workspace`,
and the independently executed exact-root Linux chain passes 33/33. The
interrupt-mask pair passes 5/5 on both reviewed compilers. The placement,
redirect, relocation, accounting, manifest-region, and capacity values above
were computed read-only from the current production pins and the authenticated
isolated object contracts. No production config, source, test, build artifact,
manifest, package, or flash plan was modified by this plan.

## Recorded promotion result

The implementation follows the placement, dependency, and stock-ownership
plan above. The recorded aggregate pins are:

| Profile | Overlay | Apollo-main component | Complete package |
|---|---|---|---|
| Apple clang 21 | 116,816 / `b9cb2b00d4859650d120ff713a8af9a1ca626876b46bac751098abdbca575153` | 3,640,212 / `fcb218fd5d9a33b2398cd046550b26258ca9da90d423c50ae635203535614a58` | 4,418,666 / `5a31772a8a4fb746fa9eff53d618541fd38cf44a93c9d602eb88e15d142cef01` |
| Linux clang 22.1.8 exact root | 118,660 / `77ae17c20117c476596c76544c397516ee561219296db4b7f5dc2d80d0907024` | 3,642,056 / `2c9076f817e28b776bb34538915c18097b1ea24ee1b4cdcfa22aab075797e32f` | 4,420,510 / `2692cc62f39793c3111004bc2d55b65450903b8f6164f9206c43509b7de8462b` |

The canonical 620,534-byte flash plan hashes to
`4c71800d5c33b618ff8cfaf9c0fb4adf06d59b1dcf753b18c56c6bf7f8a2139a`
and contains 861 placed regions. The Linux coarse-region plan is 558,796
bytes, hashes to
`5c3629f259af83752a28e7da1e776fec80d5257f888303ae3effb52b6f00e013`,
and contains 783 placed regions. The production cluster verifier passes 9/9
under both profiles; the combined Apple focused and production chain passes
42/42. No firmware was flashed.
