/* SPDX-License-Identifier: MIT */
/* CK804EF nested IRQ context, preserving stock state plus r16/r17.
 * Instructions are assembled from source; no encoded instruction data.
 * The ordinary C body uses the ABI while this wrapper protects interrupted
 * extended GPR/FPU state from arbitrary registered handler calls. */
.section .text.open_cfw_gx8002_irq_entry,"ax",@progbits
.balign 4
.global open_cfw_gx8002_irq_entry
.type open_cfw_gx8002_irq_entry,@function
open_cfw_gx8002_irq_entry:
    nie
    ipush
    subi sp, 68
    stm r15-r31, (sp)
    subi sp, 32
    fstms fr0-fr7, (sp)
    bsr open_cfw_gx8002_irq_dispatch_body
    fldms fr0-fr7, (sp)
    addi sp, 32
    ldm r15-r31, (sp)
    addi sp, 68
    ipop
    nir
.size open_cfw_gx8002_irq_entry, .-open_cfw_gx8002_irq_entry
