    .text
    .global irq_fpu_semantic_probe
irq_fpu_semantic_probe:
    fstms vr0-vr7, (r14)
    fldms vr0-vr7, (r14)
    jmp r15
