/* R1 exception-vector glue around Armink's cm_backtrace_fault provider. */
.syntax unified
.thumb
.text

.macro OPENR1_CMB_FAULT_HANDLER name
.global \name
.type \name, %function
.thumb_func
\name:
    mov r0, lr
    mov r1, sp
    bl cm_backtrace_fault
    adr r0, 1f
    mov r1, lr
    bl openr1_reset_trace_fault_and_reset
1:
    b 1b
.size \name, . - \name
.endm

OPENR1_CMB_FAULT_HANDLER NMI_Handler
OPENR1_CMB_FAULT_HANDLER HardFault_Handler
OPENR1_CMB_FAULT_HANDLER MemoryManagement_Handler
OPENR1_CMB_FAULT_HANDLER BusFault_Handler
OPENR1_CMB_FAULT_HANDLER UsageFault_Handler
