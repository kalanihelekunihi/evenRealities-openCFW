.syntax unified
.thumb
.macro lower name
.global \name
.type \name,%function
.thumb_func
\name:
    bx lr
.endm
lower opencfw_bl_mask_interrupts
lower opencfw_bl_kernel_enter
lower opencfw_bl_kernel_exit
lower opencfw_bl_remove_event_waiter
lower opencfw_bl_kernel_reschedule
lower opencfw_boot_list_initialize
.section .note.GNU-stack,"",%progbits
