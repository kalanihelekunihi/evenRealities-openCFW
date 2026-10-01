.section .firmware,"ax"
.global boundary_context_entry
boundary_context_entry:
.incbin "boundary-context.bin"
