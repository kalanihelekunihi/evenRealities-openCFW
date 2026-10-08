# Remaining selected-linker boundaries

Verified `129a6b2f38f145f33e791874f52d722fb1715d5fff5c957a285644312f34a6f9`:17 aliases at17 addresses,10 OTA,4 synthetic,3 external ROM. Same selected scope as761be470:10 OTA, unchanged; new internal callback frontier is separate. No new numeric child dependency. Existing source can be unbound; this is not source completeness.

| Address | Symbol | Kind |
|---|---|---|
| 0x4329c5 | opencfw_boot_platform_terminal | explicit-fixture-provider-or-unexecuted-stock-alias |
| 0x08002101 | opencfw_boot_allocator_log | named-test-provider-or-unrecovered-implementation-cut |
| 0x08002111 | printf | named-test-provider-or-unrecovered-implementation-cut |
| 0x41b391 | opencfw_bl_task_return | explicit-fixture-provider-or-unexecuted-stock-alias |
| 0x41b601 | opencfw_bl_stack_overflow | explicit-fixture-provider-or-unexecuted-stock-alias |
| 0x416201 | opencfw_provider_416200 | explicit-fixture-provider-or-unexecuted-stock-alias |
| 0x08002121 | opencfw_boot_dfu_log | named-test-provider-or-unrecovered-implementation-cut |
| 0x41b5f7 | opencfw_bl_malloc_failed | explicit-fixture-provider-or-unexecuted-stock-alias |
| 0x42e1db | opencfw_boot_dfu_terminal | explicit-fixture-provider-or-unexecuted-stock-alias |
| 0x08002131 | opencfw_boot_control_log | named-test-provider-or-unrecovered-implementation-cut |
| 0x416379 | opencfw_bl_task_delay | explicit-fixture-provider-or-unexecuted-stock-alias |
| 0x0200ff21 | opencfw_boot_rom_mram_program | external-resident-ROM-API-body-absent-from-OTA |
| 0x00000049 | opencfw_boot_rom48 | external-resident-ROM-API-body-absent-from-OTA |
| 0x00000041 | opencfw_boot_rom_delay_cycles | external-resident-ROM-API-body-absent-from-OTA |
| 0x41b219 | opencfw_boot_elog_snprintf | explicit-fixture-provider-or-unexecuted-stock-alias |
| 0x41b25d | opencfw_boot_elog_vsnprintf | explicit-fixture-provider-or-unexecuted-stock-alias |
| 0x41c4b5 | opencfw_boot_startup_power_initialize | explicit-fixture-provider-or-unexecuted-stock-alias |

IAR bounded formatting/backend, startup power/configuration/temperature/runtime children, task restoration/cancellation, vectors/assets/data/layout/compiler equality and external ROM/hardware remain. Integration logger/startup models remain. ITM/debug release is not general task/IRQ drain.

3522 native prerequisites: four init callbacks/timer and four event-family callback entries are component-source;21 unique callback addresses remain explicit contracts. Root41c4b4 unresolved despite bounded clock carry/child proofs. Selected17 alias ledger unchanged.

25a corrects EXTREF-without-PLL pin restore. Root ABI/carry analysis now compares saved registers and stack, but source children and remaining contracts must still be integrated before retiring41c4b4. Selected alias denominator remains unchanged.

129a:11 source-defined callback entries;18 unique target contracts remain. Root4de9 standalone native-children proof passes856 supported-family cases, but544 EM/GX cases remain excluded and selected41c4b4 is not retired. Next actual implementation: GX descendant integration, EM transition/selector closure, then native root variant expansion.
