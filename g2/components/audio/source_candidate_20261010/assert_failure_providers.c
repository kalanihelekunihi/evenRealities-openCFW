/* Apollo MAIN 0x441800 and 0x45537e: fatal assert boundaries.
 * Each writes zero to the invalid word address, then spins if that write returns.
 * Kept as separate entry symbols because the original functions have distinct
 * addresses even though their complete instruction bodies are identical.
 */
__attribute__((naked, noreturn, used)) void audio_queue_bad_argument(void) {
    __asm volatile("movs r0, #0\n"
                   "movs.w r1, #-1\n"
                   "str r0, [r1]\n"
                   "1: b 1b\n");
}

__attribute__((naked, noreturn, used)) void opencfw_event_group_assert_failure(void) {
    __asm volatile("movs r0, #0\n"
                   "movs.w r1, #-1\n"
                   "str r0, [r1]\n"
                   "1: b 1b\n");
}

/* Distinct original entry 0x4420f6, used by the critical-exit boundary. */
__attribute__((naked, noreturn, used)) void stock_bad_critical_exit(void) {
    __asm volatile("movs r0, #0\n"
                   "movs.w r1, #-1\n"
                   "str r0, [r1]\n"
                   "1: b 1b\n");
}
