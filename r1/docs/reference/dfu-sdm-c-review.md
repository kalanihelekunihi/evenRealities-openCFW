# DFU vector-table handoff through the Nordic C API

`r1/src/application/runtime/native_dfu_vector_restore.c` now includes the pinned
S140 `nrf_sdm.h` and calls `sd_softdevice_vector_table_base_set`. Its bespoke
register-pinned SVC assembly is removed. The SDK's `SVCALL` declaration owns the
service number and architectural ABI for both the bootloader-vector selection
and application-vector restoration paths. The policy source contains ordinary
C; the SDK still emits the necessary SVC instruction and return adapter.
This is not assembly-free firmware.

The dedicated manifest profile extends the existing unit flags with the
nRF52840 device definition and system include paths for pinned S140, MDK and
CMSIS headers. No SDK source or shared profile is modified, and the unit still
builds with Clang. The normal dependency file supplies exact header hashes in
[dfu-sdm-c-review.json](dfu-sdm-c-review.json).

Fresh REA code windows at stock 0x78590 and 0x7876c match the preserved application
image. The latter restore entry was confirmed directly from its instructions,
including its SVC19 and fixed 0x27000 base, rather than inferred from a name.
The set path retains MBR-word selection with UICR fallback only for UINT32_MAX,
snapshots the selected base before logging, and preserves raw SVC status. It
does not add alignment/range validation. The restore path always selects the
application base. Both retain separate live log-mode reads and exact markers,
texts and IDs, including error logging after nonzero service results.

Normal product objects pass **2912 stock/C set pairs** and **672 stock/C restore
pairs**, or **3584 paired cases (7168 executions)**. An independent oracle checks
address-word reads, fallback, base capture across provider mutations, SVC number,
argument/status, log order, full-width status results, SP, callee-saved registers
and interrupt masks. Source execution is prohibited from entering stock code.
Three compiled defect variants are rejected independently in both paths: wrong
service, shifted base and discarded return status. The SDK primitive executes;
SVC handling and logging are modeled boundaries, not bypassed C calls.

The normal build compiles all **801 units (719 application, 82 bootloader)** with
zero failures or duplicate strong symbols. Imports remain 95 application and
22 bootloader linker metadata symbols. Strict GNU bootloader linking succeeds.
All 798 other nongenerated prior object hashes are unchanged; generated boot
crypto/vectors retain identical allocated bytes and relocations. R1 manifest
checks pass, while the global check retains the unrelated unlisted G2
`resident_rom_thumb_set.S` file. Source-plan selections are unchanged.

Provider frame depths are recorded, not equated. Private spills, live temporary
registers, caller-clobbered outputs and APSR are excluded. Tests use mapped
address words and terminating modeled services. Physical SoftDevice dispatch,
vector-table mutation, boot transfer, NVIC/exception frames and full application
final linking remain unverified.
