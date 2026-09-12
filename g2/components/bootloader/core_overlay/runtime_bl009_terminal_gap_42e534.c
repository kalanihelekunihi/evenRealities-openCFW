/* SPDX-License-Identifier: MIT */
/* Clean-room in-place data: eight-byte MMIO-target cell at 0x0042E534
 * between the terminal-mode control primitive (ends 0x0042E534) and the
 * event-object/task initialisation service (starts 0x0042E53C).
 *
 * The original terminal-mode primitive writes a mode byte to one of two
 * memory-mapped control registers selected by the mode argument:
 * - 0x0042E534: 0x40000008. Original consumer 0x0042E522
 *   (`ldr r1, [pc, #0x10]`) loads it and executes `str r0, [r1]` with
 *   r0 = 0xD4 on the mode-0 path.
 * - 0x0042E538: 0x40000004. Original consumer 0x0042E52A
 *   (`ldr r1, [pc, #0xc]`) loads it and executes `str r0, [r1]` with
 *   r0 = 0x1B on the mode-1 path; any other mode falls through to a
 *   no-op return.
 * The routed successor encodes equivalent store targets in its own
 * body, so these cells are original-layout residue reproduced here to
 * preserve the authenticated image bytes from named constants.
 */
typedef __UINT32_TYPE__ open_cfw_bl009_u32;

struct open_cfw_bl009_gap_42e534 {
    open_cfw_bl009_u32 mode0_register;
    open_cfw_bl009_u32 mode1_register;
};

__attribute__((used))
const struct open_cfw_bl009_gap_42e534
open_cfw_bootloader_bl009_gap_42e534 = { 0x40000008u, 0x40000004u };
