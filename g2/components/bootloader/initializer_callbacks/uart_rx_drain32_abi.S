/* SPDX-License-Identifier: MIT
 * Native UART FIFO drain adapter 0x423342. Preserve the saved-r7 high return
 * register while the selected C FIFO implementation drains up to 32 bytes.
 */
.syntax unified
.thumb
.section .text.opencfw_boot_uart_rx_drain32_abi,"ax",%progbits
.global opencfw_boot_uart_rx_drain32_abi
.type opencfw_boot_uart_rx_drain32_abi,%function
.thumb_func
opencfw_boot_uart_rx_drain32_abi:
    push {r7,lr}
    movs r3, #0
    movs r2, #32
    movs r1, #0
    bl opencfw_boot_uart_rx_fifo
    pop {r1,pc}
.size opencfw_boot_uart_rx_drain32_abi, .-opencfw_boot_uart_rx_drain32_abi
