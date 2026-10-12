/* Native 0x0041b854: call selected UART log-send body with module 1,
 * then return saved ambient r7 in r0, discarding child's r0 result.
 */
.syntax unified
.thumb
.text
.align 1
.global opencfw_boot_uart_log_send_ambient_abi
.type opencfw_boot_uart_log_send_ambient_abi,%function
.thumb_func
opencfw_boot_uart_log_send_ambient_abi:
    push {r7, lr}
    movs r2, r1
    movs r1, r0
    movs r0, #1
    bl opencfw_boot_uart_log_send
    pop {r0, pc}
.size opencfw_boot_uart_log_send_ambient_abi, .-opencfw_boot_uart_log_send_ambient_abi
.section .note.GNU-stack,"",%progbits
