/* SPDX-License-Identifier: MIT
 * Stock 0x42dd98..0x42dd9a (s200 bootloader thread_dfu orchestrator leaf).
 * The DFU orchestrator 0x42dd14 calls this bare `bx lr` between the runtime
 * context setup 0x42dd68 and the manager start-done wrapper 0x42dda4. It has
 * no arguments, state, or return value (the caller ignores r0).
 */

void noop_callback_0042dd98(void);

/* Stock 0x42dd98 (noop_callback_0042dd98) */
void noop_callback_0042dd98(void)
{
}
