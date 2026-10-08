.syntax unified
.thumb
.section .text.native_termination_alias,"ax",%progbits
.global opencfw_provider_416200
.global opencfw_boot_dfu_thread_terminate
.thumb_func
opencfw_provider_416200:
.thumb_func
opencfw_boot_dfu_thread_terminate:
 b.w opencfw_boot_runtime_action
.section .note.GNU-stack,"",%progbits
