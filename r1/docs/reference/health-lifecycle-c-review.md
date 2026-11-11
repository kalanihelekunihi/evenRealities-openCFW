# Health lifecycle coordinator in C

Current memory-map update: the coordinator now owns relocatable C storage for
the 14,816-byte engine, five 100-byte output records and 264-byte descriptor.
The fixed stock addresses mentioned in the historical reconstruction review
below no longer appear in the source. See the
[engine bridge review](health-engine-initialize-bridge-review.md) and the
current strict linker map for placement. The earlier stock/C replay predates
this relocation and does not by itself validate the new addresses.

`runtime/native_health_lifecycle.c` now supplies stock entry `0x4bd98`, closing the coordinator import from `native_health_startup.c`. The source uses no inline assembly or executable byte arrays. Startup includes the new header. The function has a void C contract: the existing caller discards its result, and this review makes no raw-R0 promise for the stock void routine.

The REA dossier in `build/goal-r1-touch-request-pure-c/rea-lifecycle-next.json` groups this 768-byte range (`0x4bd98..0x4c097`) with the separate wrapper `0x4c37c..0x4c3a9`. Its pseudocode describes the latter entry and prunes recovery branches reachable from `0x4bd98`. Implementation follows the complete instructions for the requested local entry. It does not claim implementation of the entire merged Ghidra body or the separate force-reinitialization wrapper.

The C coordinator retains size-query and log order, authorization pending/retry byte stores, retry-once behavior, previous-state restore/defaulting, profile fallback, fixed engine/output coordinates, activation order and subscription truncation. Raw mode 0 probes retained recovery; raw mode 1 clears previous data before initialization; other words do neither. A failed engine initialization retries only for raw status -5, clearing previous data and reusing the same timestamp. Success initializes the output descriptor's five pointer fields and subscribes only when its state byte is zero. The default seven-float profile is source data and matches all 28 locked stock bytes.

Logging remains observable: both short-circuit flag reads and structured/Nordic messages, values, severity/module words and order are preserved. The compiled source strings relocate; replay compares their contents and descriptor/format pointer equality within each call rather than requiring stock text addresses.

Production-object replay passes 376 pairs against stock. It covers four raw modes; authorization success, retry success and retry failure; initialization success, -5 retry success/failure and other failure; constant and changing log masks; previous/profile availability; existing subscriptions; and full-word registration results truncated to a byte. Provider snapshots compare zeroed header/profile data and complete profile/previous-state inputs. Final retained state, health flags, shared descriptor/context regions, caller bytes, masks, SP and callee-preserved registers agree. Nested stack addresses are excluded, and raw R0 is excluded for the void boundary.

Normal retained accessors advertise 896 bytes, which the coordinator rejects against its distinct 736-byte requirement. Controlled accessor responses additionally exercise the native copy/clear branch for exactly 736 bytes; those responses are explicitly modeled, not claimed as normal recovery behavior. Native instruction hooks record 88 recovery-probe entries, 87 length checks, three accepted copies, 72 forced-default clears and 96 initialization retries. The actual shared C recovery/CRC/clear subset executes where called. Other engine, time, subscription and log boundaries are modeled or native-bound in this fixture. This is not a source-only coordinator link or physical sensor initialization proof.

All three compiled defects are rejected: accepting 896-byte recovery, retrying the wrong status, and clearing previous data for every nonzero mode. The normal build passes 722 units (648 application / 74 bootloader), without failures or duplicate strong symbols. All 721 preexisting object bytes are unchanged; only the startup source declaration changes alongside the new unit. Both source manifests pass.

Application imports change from 177 to 183: the coordinator resolves and seven real lower dependencies become explicit. They are six native engine boundaries (authorization, previous restore, profile loading, engine initialization, profile activation and state mode) plus the time-transition event adapter. Their addresses and symbols are recorded in the receipt; implementations remain unfinished. Bootloader imports remain 34. Shared fixed RAM regions also still require complete firmware memory-map integration. No complete firmware closure, instruction-identity selection, device timing, concurrency/invalid-pointer equivalence, flashing, commit or publication is claimed.

[The receipt](health-lifecycle-c-review.json) binds source and object identities, replay, defect controls, profile audit and the normal build. The source plan is unchanged; paid compilers and byte identity are not completion gates.

The subsequent [time/reset review](health-time-reset-c-review.md) adds the C event adapter and force entry and replays the updated shared unit.
