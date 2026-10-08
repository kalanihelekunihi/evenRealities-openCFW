.syntax unified
.thumb
.section .text.external_boundary,"ax",%progbits
.global opencfw_provider_416200
.global opencfw_boot_dfu_thread_terminate
.thumb_func
opencfw_provider_416200:
.thumb_func
opencfw_boot_dfu_thread_terminate:
 ldr r12, =0x416201
 bx r12
.section .note.GNU-stack,"",%progbits
