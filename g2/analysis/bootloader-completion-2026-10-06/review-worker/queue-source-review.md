# Independent bootloader queue-source review

Date: 2026-10-06. Scope: inspect the candidate queue wrapper and source runtime-mode helper against the locked original instructions and review the external provider cuts. No firmware or device was written; no hardware was used.

## Findings

The runtime-state helper source matches the observed stock control flow:

- `0x418B56` loads `*(uint32_t *)0x20027150`; returns 1 when it is zero.
- Only if that first word is nonzero, it loads `*(uint32_t *)0x2002716c`; returns 2 when it is zero.
- Otherwise it returns 0.

The stock listing at `0x41602A` reads IPSR; exception mode returns 1. In thread mode it calls `0x418B56`, returns 0 immediately for helper result 1, otherwise reads PRIMASK then BASEPRI and returns whether either mask is nonzero. The C candidate retains that ordering and the nonintuitive helper-result-1 branch. The stock wrappers at `0x416816`, `0x4168A2`, and `0x416920` match the source's checks, 32-bit wrapped count-times-item-size arithmetic, static/dynamic storage selection, timeout-dependent failure returns, ignored priority argument, and PendSV set write. In particular, the underlying queue-kernel behavior is outside this source implementation.

The default `module.ld` makes the runtime-state query and six kernel queue functions explicit linked dependencies at their stock Thumb entry addresses. The alternate `runtime_module.ld` compiles the source runtime-mode query but still maps all six kernel functions to stock addresses. `queue_runtime_task_module.ld` likewise marks the runtime query source-defined while retaining explicit stock kernel boundaries. This is accurate scoping: the state query is source-backed in the alternate/integrated profile; the RTOS queue core is not reconstructed.

## Independent run

I independently ran the current verifier with the installed offline Unicorn environment and `--real-runtime` against `g2/build/bootloader-completion/queue-runtime/queue-runtime.elf`. Result: PASS, 45 cases (6 context, 11 create, 14 put, 14 get), and 450 distinct original instruction bytes. The result is saved at [queue-runtime-independent.json](downloaded-tools/queue-runtime-independent.json), SHA-256 `65d6b61aed64ef0dd8be469c28a4d2ec62e5970a36274963510fbb7ba8bc762b`.

The comparison is bound to original firmware SHA-256 `f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5`, ELF SHA-256 `e433ed46e19973a8aacaaf0c8743eecaaf520e9215859bdf4a5cd4ebd14c0dc7`, and the current source hashes recorded in the result. `real_source_runtime_query` is true. Test fixture sets the two RAM words to cover helper results 0, 1 and 2; PRIMASK/BASEPRI and the wrapper behavior are exercised. Nonzero IPSR is not injected. Kernel provider results and ISR wake values remain synthetic exact-entry interceptions; no scheduler/queue-storage mutation or actual interrupt behavior is verified. The comparison proves only these tested paths for this compiled ELF and tested fixtures, not all compiler profiles or full bootloader behavior.

## Documentation discrepancy

`g2/components/bootloader/queue/README.md` currently says the component comparison uses 418 instruction bytes and that both runtime-mode and kernel providers are synthetic. That description is stale for the current `comparison-first.json`/`--real-runtime` result (45 cases, 450 bytes, source runtime query); update that documentation when the owning integration pass is finalized. The older worker evidence note still accurately describes its historical synthetic-query run but does not describe the current source-runtime comparison.

## Source identities checked

- `runtime_mode.c`: `dd97dc30a02adc443beeb3b96f1df0c4a2ea830ec5ea7e4f144603e1664ea83e`
- `queue_wrappers.c`: `e7c168579d68b36f4406c194fd460eaaf041fa2f75f328e1e01444522308d5b3`
- `queue_wrappers.h`: `5ae09065df69edd0c4cc92ceb2393c2a7fe7e43912ddf14f33d63dd390cc1b42`
- `module.ld`: `3193dcbec08e79b900849be89fee5d5cfe01a6e8037f747e6780e22ea0350e59`
- `runtime_module.ld`: `e1d99c17cafab54d2fc59e6809a055e593a9ce90f07ac890c026bcf9f2fb3e1f`
- `verify_queue.py`: `1a877111f29bd6ffeb5ec20d582be56928f85c12dd7989304d5e9e2872a446cb`
