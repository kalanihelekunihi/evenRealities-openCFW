/* Image-A SRAM 0x10025e48: pass native ambient r0/r4 to the source C core. */
    .text
    .align 2
    .global gx8002_resident_audio_irq_25e48
    .type gx8002_resident_audio_irq_25e48, @function
gx8002_resident_audio_irq_25e48:
    push r15
    mov r1, r4
    bsr gx8002_resident_audio_irq_core_25e48
    movi r0, 0
    pop r15
    .size gx8002_resident_audio_irq_25e48, .-gx8002_resident_audio_irq_25e48
