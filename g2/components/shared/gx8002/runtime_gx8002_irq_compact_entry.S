/* SPDX-License-Identifier: MIT */
/* Architecture entry with the C dispatcher's slot layout and call semantics.
 * IRQ = active_vector[8:0] - 32; slots are {handler, private_data}, 8 bytes.
 * r4-r11/r16-r17 are preserved by ABI-compliant callbacks. Hardware IPUSH
 * protects r0-r3/r12-r13; this entry protects r15/r18-r31 and fr0-fr7.
 * Keep the indirect call inside this frame: no extra C return frame is needed. */
.section .text.open_cfw_gx8002_irq_compact_entry,"ax",@progbits
.balign 4
.global open_cfw_gx8002_irq_compact_entry
.type open_cfw_gx8002_irq_compact_entry,@function
open_cfw_gx8002_irq_compact_entry:
    nie
    ipush
    subi sp, 56
    stm r18-r31, (sp)
    subi sp, 32
    fstms fr0-fr7, (sp)
    push r15
    lrw r3, 0xe000e100
    ld.w r0, (r3, 0xb00)
    andi r0, r0, 511
    subi r0, 32
    lrw r3, open_cfw_gx8002_irq_table
    ldr.w r2, (r3, r0 << 3)
    bez r2, .Lrestore
    lsli r1, r0, 3
    addu r3, r1
    ld.w r1, (r3, 4)
    jsr r2
.Lrestore:
    ld.w r15, (sp, 0)
    addi sp, 4
    fldms fr0-fr7, (sp)
    addi sp, 32
    ldm r18-r31, (sp)
    addi sp, 56
    ipop
    nir
.size open_cfw_gx8002_irq_compact_entry, .-open_cfw_gx8002_irq_compact_entry
