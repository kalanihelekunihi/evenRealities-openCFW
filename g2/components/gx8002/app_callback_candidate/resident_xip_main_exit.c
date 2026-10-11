/* SPDX-License-Identifier: MIT
 * Authenticated native XIP 0x10207a7c is one `jmp r15` instruction.
 * This exact exit hook has no side effects; it is not a synthetic stub.
 * The retained seed list omits this two-byte body.
 */
void gx8002_xip_main_exit_10207a7c(void)
{
}
