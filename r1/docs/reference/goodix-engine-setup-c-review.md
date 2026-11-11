# R1 Goodix engine setup in C

The [SpO2 calculation control-flow review](goodix-spo2-calculate-c-review.md) adds native core control in C, including allocation/status flow and calibration semantics. Fourteen deeper processing stages remain explicit imports; this does not complete the SpO2 engine.

The [SpO2 frame execution review](goodix-spo2-execute-c-review.md) adds the C sensor adapter with bounded floating-point rounding validation and reuses the canonical channel map. All five sensor frame adapters now execute in dispatcher comparisons; `goodix_spo2_calc` remains unfinished.

The [soft-ADT execution review](goodix-soft-adt-execute-c-review.md) adds the C sensor adapter and shared green/IR event reporters, reusing the existing selector, timeout counter and capacitor flag. Timeout advancement on core errors is preserved; the `goodix_nadt_calc` computation core remains unfinished.

The [HR frame-execution review](goodix-hr-execute-c-review.md) adds the C HR adapter and disabled report. Dispatcher replays now execute real ADT, HR and HRV adapters, including the HR record consumed by HRV; calculation cores and HR diagnostics remain explicit unfinished providers.

The [NADT initializer review](goodix-nadt-initialize-c-review.md) closes the remaining NADT constructor import with C, preserving the canonical state/workspace and adding the native configuration owner.

The [HRV initializer review](goodix-hrv-initialize-c-review.md) closes `goodix_hrv_init` with C constructor/storage code and the canonical HRV owner. Successful full allocator/teardown replays call no function ports.

The [HR constructor review](goodix-hba-initialize-c-review.md) supersedes the `goodix_hba_init` boundary. Three native entries now use C; the workspace owner covers all four native words. Workspace initialization, graph construction and four table getters remain open.

The [SpO2 initialization review](goodix-spo2-initialize-c-review.md) implements the SpO2 constructor listed below and twelve helpers. Four deeper SpO2 initialization/resource boundaries remain open; the other three algorithm constructors are still unresolved.

`r1/src/application/goodix/native_engine_setup.c` implements HR, HRV, SpO2 and soft-ADT setup, plus native NADT configuration/version and maximum-channel providers. It reuses the existing C version builders, channel-map routines, and six existing configuration getters. The [machine-readable receipt](goodix-engine-setup-c-review.json) pins the sources, objects, REA bytes, fixtures and final build.

All 880 units compile and compose without duplicate strong symbols. The four engine imports are replaced by four lower-level context-constructor imports, leaving 63 application and 22 bootloader imports. This advances the source implementation through the call graph; context construction and physical sensor bring-up remain incomplete.

| Native entry | Newly implemented provider |
| --- | --- |
| `0x6d3c0` | `r1_goodix_hr_engine_init` |
| `0x6df14` | `r1_goodix_hrv_engine_init` |
| `0x6ec28` | `r1_goodix_spo2_engine_init` |
| `0x32788` | `r1_goodix_soft_adt_engine_init` |
| `0x6e540` | `goodix_nadt_config_get_arr` |
| `0x6e548` | `goodix_nadt_config_get_version` |
| `0x2e8c4` | `Gh3x2xGetHrAlgoSupportChnl` |
| `0x2e8c8` | `Gh3x2xGetSpo2AlgoSupportChnl` |

The existing HR/HRV/SpO2 configuration getters at `0x6cc2c`, `0x6da9c`, `0x6eaf8` and their version getters at `0x6cc34`, `0x6daa4`, `0x6eb00` are verified and reused. Their earlier portable symbol hints are superseded by the actual providers. No second implementation is retained.

HR copies 36 configuration bytes, supplies the full sample rate and live channel count, and rejects counts above four. HRV copies 24 bytes and replaces its rate. SpO2 copies 76 bytes, replaces rate and live count, and rejects counts above one. Soft ADT copies 60 bytes and replaces only the low sample-rate halfword, preserving the packed upper halfword. It clears a separate engine flag at `0x20007c14`; the ADT flag array is a different owner. The constructors receive the exact configuration size and a zero-filled 20-byte interface-version record. Constructor statuses propagate through the three returning engines; the soft-ADT boundary is void.

All 4,080 direct comparisons pass, executing all 504 instruction bytes across the fourteen verified entries. Complete configuration records, interface buffers, channel-map state and the engine flag match stock. Independent oracles check configuration fields, channel limits and bounded version behavior. Zero-capacity interface calls preserve the native write to the preceding byte. Sample-rate extremes, channel-count extremes, initialized/default map states, constructor results, buffer seeds and interrupt masks are exercised.

A further 2,567 comparisons execute the actual C initialization controller, adapters, engines, versions, configuration getters and channel-map routines. Controller/frame/init-state read and write traces match; channel maps and engine flag match at constructor snapshots and final state. The four context constructors remain modeled with BX LR returns:

| Native entry | Remaining dependency |
| --- | --- |
| `0x6d204` | `goodix_hba_init` |
| `0x6db5c` | `goodix_hrv_init` |
| `0x6eb94` | `goodix_spo2_init` |
| `0x6e664` | `goodix_nadt_init` |

Thirteen compiled defects are rejected: wrong HR rate, channel count, limit or size; discarded HRV result; wrong SpO2 count; overwritten NADT packed halfword; wrong engine flag; wrong interface version; omitted zero-capacity write; wrong NADT defaults; wrong HR maximum; and omitted HR channel defaults.

Source execution cannot enter stock. Saved integer/FP registers, SP, masks and guards are checked. Numeric addresses of readonly getter results, caller scratch, APSR and private stack bytes are excluded. The previously documented weights-version private overread difference remains; only its terminated text is consumed. Exact channel-map write width and interrupt concurrency are not claimed.

The first full build detected six duplicate providers; the copies were removed and existing providers reused. Only the final clean build and final corpora are admitted. The new object equals the normal build object; all 869 prior nongenerated source/object pairs remain unchanged. Existing generated startup and uecc objects differ. One byte receives native state ownership at `0x20007c14`, and the new 60-byte readonly NADT defaults match stock exactly.

Final executable linking, RAM/startup placement, context allocation/initialization, physical sensors, other hardware dependencies and device boot remain open. Relocatable composition is not bootable firmware. No instruction or image identity is claimed.
