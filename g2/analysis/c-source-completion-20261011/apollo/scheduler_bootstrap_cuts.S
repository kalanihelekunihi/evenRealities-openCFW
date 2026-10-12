.syntax unified
.thumb
.macro lower name
.global \name
.type \name,%function
.thumb_func
\name:
    bx lr
.endm
lower idle_entry
lower opencfw_bl_kernel_static_thread
lower opencfw_bl_timer_service_start
lower opencfw_bl_mask_interrupts
lower opencfw_bl_port_start
.section .note.GNU-stack,"",%progbits
