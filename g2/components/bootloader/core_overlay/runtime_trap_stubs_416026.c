/* SPDX-License-Identifier: MIT */
/* Clean-room reconstruction of two trivial G2 bootloader compatibility
 * stubs retained between the authenticated substring-search primitive and
 * the critical-context predicate: a two-byte infinite self-loop trap and a
 * two-byte no-op return. Both are single-instruction Thumb-2 bodies with no
 * observable state; the inline asm is the only way to pin their exact
 * one-instruction encoding for an in-place (non-redirected) admission.
 */

__attribute__((used, noinline, naked))
void open_cfw_bootloader_runtime_trap_416026(void)
{
    __asm__ volatile("b .\n");
}

__attribute__((used, noinline, naked))
void open_cfw_bootloader_runtime_noop_return_416028(void)
{
    __asm__ volatile("bx lr\n");
}
