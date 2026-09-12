/* SPDX-License-Identifier: MIT */
/* Clean-room in-place data: six-byte literal/alignment cell at 0x0042E50E
 * between the alignment-gated runtime dispatcher (ends 0x0042E50E) and
 * the terminal-mode control primitive (starts 0x0042E514).
 *
 * Layout: two zero alignment bytes, then the 32-bit fallback dispatch
 * address 0x08000140 (flash-alias address shape). Original consumers
 * 0x0042E4B2 (`ldr r0, [pc, #0x5c]`, misaligned-input path) and
 * 0x0042E504 (`ldr r0, [pc, #8]`, null-context path) load this word
 * into r0 and return it, so it is the dispatcher fallback address
 * produced when the fast runtime-context path is not taken. The routed
 * successor (runtime_alignment_dispatch_42e4f4.c) encodes the same
 * fallback in its own body, so this cell is original-layout residue
 * reproduced here to preserve the authenticated image bytes.
 */
typedef __UINT32_TYPE__ open_cfw_bl009_u32;
typedef __UINT16_TYPE__ open_cfw_bl009_u16;

struct __attribute__((packed)) open_cfw_bl009_gap_42e50e {
    open_cfw_bl009_u16 align_pad;
    open_cfw_bl009_u32 fallback_address;
};

__attribute__((used))
const struct open_cfw_bl009_gap_42e50e
open_cfw_bootloader_bl009_gap_42e50e = { 0x0000u, 0x08000140u };
