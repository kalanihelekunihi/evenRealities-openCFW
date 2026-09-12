/* SPDX-License-Identifier: MIT */
/* Clean-room in-place data: eight-byte MMIO-target run at 0x0042E8C8,
 * the tail of the fourteen-byte cell at 0x0042E8C2 between the guarded
 * indirect-call cleanup service (ends 0x0042E8C2) and the hardware-context
 * initialiser (starts 0x0042E8D0).
 *
 * Only the two register-address cells are routed here; the head of the
 * span (two zero pad bytes plus the word 0x00433120, an indirect-call
 * pointer loaded by original code at 0x0042E8AA and dereferenced for
 * `blx` into the still-opaque BL-012 range) stays retained stock because
 * a pointer into opaque functionality is not source ownership.
 * - 0x0042E8C8: 0x40014008. Original consumer 0x0042E8B0
 *   (`ldr r1, [pc, #0x14]`) loads it and executes `str r2, [r1]` with
 *   r2 = 0xC3, i.e. a control-register store in the cleanup epilogue.
 * - 0x0042E8CC: 0x40014024. Original consumer 0x0042E8B8
 *   (`ldr r3, [pc, #0x10]`) loads it and executes `str r2, [r3]` with
 *   r2 = 0, i.e. the companion status-clear store.
 * The routed successor encodes equivalent targets in its own body, so
 * these cells are original-layout residue reproduced from named
 * constants.
 */
typedef __UINT32_TYPE__ open_cfw_bl009_u32;

struct open_cfw_bl009_gap_42e8c8 {
    open_cfw_bl009_u32 control_store_register;
    open_cfw_bl009_u32 status_clear_register;
};

__attribute__((used))
const struct open_cfw_bl009_gap_42e8c8
open_cfw_bootloader_bl009_gap_42e8c8 = { 0x40014008u, 0x40014024u };
