#include <stdint.h>
/* Apollo MAIN 0x441800 and 0x45537e: fatal assert boundaries.
 * Each writes zero to the invalid word address, then spins if that write returns.
 * Kept as separate entry symbols because the original functions have distinct
 * addresses even though their complete instruction bodies are identical.
 */
__attribute__((noreturn, used)) void audio_queue_bad_argument(void) {
    /* Write to the unmapped top word to raise a bus fault, then spin. */
    *(volatile uint32_t *)UINT32_C(0xffffffff) = 0u;
    for (;;) {
    }
}

__attribute__((noreturn, used)) void opencfw_event_group_assert_failure(void) {
    /* Write to the unmapped top word to raise a bus fault, then spin. */
    *(volatile uint32_t *)UINT32_C(0xffffffff) = 0u;
    for (;;) {
    }
}

/* Distinct original entry 0x4420f6, used by the critical-exit boundary. */
__attribute__((noreturn, used)) void stock_bad_critical_exit(void) {
    /* Write to the unmapped top word to raise a bus fault, then spin. */
    *(volatile uint32_t *)UINT32_C(0xffffffff) = 0u;
    for (;;) {
    }
}
