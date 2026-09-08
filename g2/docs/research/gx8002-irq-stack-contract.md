# IRQ stack and compiler ABI contract

A new source audit found that the local compiler's
CALL_REALLY_USED_REGISTERS marks r16 and r17 as callee-preserved. The IRQ frame
stress model intentionally corrupts those registers as well as caller-clobbered
extended registers. Passing that test is stronger than ordinary C ABI
preservation; it does not prove those additional saves are mandatory for
ABI-compliant callbacks. This corrects earlier reasoning that treated arbitrary
r16/r17 clobbers as a general callback requirement. Retained assembly handlers
still need their own compliance evidence.

The same macro marks r15 preserved, but it is the link register: BSR itself
changes it. An IRQ wrapper must protect the interrupted r15, independently of
ordinary callee return-address handling. It must not remove that save merely
because the macro value is zero. The audit records the full first32 metadata
entries and hashes the compiler source used for the conclusion.

Authenticated SDK startup loads CONFIG_STAGE2_STACK. soc_config.h defines that
as stage2 DRAM base plus configured size minus4. The linker independently holds
CONFIG_MCU_MAIN_STACK_SIZE kilobytes after BSS. The SDK example's settings are
not proof of the shipped G2 configuration. Consequently the observed gap from
BSS end to the initial SP is neither an established IRQ stack allocation nor a
callback budget; mainline depth, priority nesting and callback usage remain.

This evidence motivates checking a smaller ABI-compliant IRQ implementation
rather than treating the current100-byte save block as unavoidable. It does
not admit the existing wrapper or establish stack capacity. Compiler metadata,
SDK source hashes and the relevant expressions are recorded in
 gx8002-irq-stack-contract.json. Firmware and package are unchanged.
