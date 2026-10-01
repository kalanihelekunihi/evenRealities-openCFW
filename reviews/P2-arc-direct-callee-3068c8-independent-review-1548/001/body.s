.section .firmware,"ax"
.global body_entry
body_entry:
.incbin "body.bin"
