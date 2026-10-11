# Kernel tick getters and context discriminator

`tick.c` provides five bounded source functions corresponding to stock addresses 0x4558a4, 0x44900e, 0x454efe, 0x454f06 and 0x4490cc. The two FreeRTOS getters both read volatile tick word 0x20074a34. The CMSIS wrapper selects by the recovered `IS_IRQ` rule, which reads ARM IPSR, PRIMASK and BASEPRI with explicit `mrs` inline assembly. The scheduler-state provider reads authenticated 0x20074a3c/0x20074a58 words. The source contains no retained executable bytes or provider stubs.

`g2_flashdb_candidate_tick` is a sixth exported adapter with the flash database wrapper's no-argument tick contract. It calls the source-defined CMSIS getter and is compared directly against stock 0x4490cc.

This complements existing `g2/components/foundation/freertos_tick/tasks_tick.c`, which implements `xTaskIncrementTick` and separate tick advance/unblock behavior. It does not define the SysTick interrupt, clock frequency, scheduler initialization, state writers, or firmware link placement. The optimized C wrapper may collapse two identical getter branches; that is semantically equivalent but not byte identical to stock.

Run `g2/analysis/kernel-tick-candidate-20261010/verify.py` with Python packages `unicorn` and `pyelftools`, Clang and ARM binutils. It compiles a Cortex-M55 candidate and a Cortex-M4 emulator object, then compares bounded source and authenticated original functions in Unicorn.
