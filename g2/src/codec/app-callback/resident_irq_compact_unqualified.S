/* Native IRQ entry 0x10025574. The exact stock FPU pair f4ee3400 /
 * f4ee3000 is fstms/fldms fr0-fr7 on the selected ck804ef assembler.
 * Earlier fr16-fr19 disassembly was a decoder error. */
    .text
    .align 2
    .global gx8002_resident_irq_compact_entry_25574
    .type gx8002_resident_irq_compact_entry_25574, %function
/* Stock 0x10025574 (gx8002_irq_compact_entry) */
gx8002_resident_irq_compact_entry_25574:
    nie
    ipush
    subi r14, r14, 56
    stm r18-r31, (r14)
    subi r14, r14, 32
    fstms fr0-fr7, (r14)
    push r15
    lrw r3, 0xe000e100
    ld.w r0, (r3, 0xb00)
    andi r0, r0, 511
    subi r0, r0, 32
    lrw r3, 0x20026ef4
    ldr.w r2, (r3, r0 << 3)
    bez r2, 3f
    lsli r1, r0, 3
    addu r3, r1
    ld.w r1, (r3, 4)
    jsr r2
3:  ld.w r15, (r14, 0)
    addi r14, r14, 4
    fldms fr0-fr7, (r14)
    addi r14, r14, 32
    ldm r18-r31, (r14)
    addi r14, r14, 56
    ipop
    nir
    .size gx8002_resident_irq_compact_entry_25574, .-gx8002_resident_irq_compact_entry_25574
