/*
 * SPDX-License-Identifier: MIT
 *
 * Source-owned replacement for the single capacity comparison in the stock
 * FreeRTOS+CLI console collector.  The stock collector owns a 128-byte input
 * buffer and later passes it to FreeRTOS_CLIProcessCommand as a C string.  Its
 * original ``cmp r0, #128`` permits byte 128 to replace the final NUL.  This
 * fragment changes only that bound to 127; it deliberately has no return
 * instruction because the production overlay copies these two instruction
 * bytes into the interior stock control-flow site at 0x00541708.
 */

    .syntax unified
    .cpu cortex-m55
    .thumb

    .section .text.open_cfw_freertos_cli_collector_capacity_patch, "ax", %progbits
    .p2align 1
    .global open_cfw_freertos_cli_collector_capacity_patch
    .type open_cfw_freertos_cli_collector_capacity_patch, %function
    .thumb_func
open_cfw_freertos_cli_collector_capacity_patch:
    cmp     r0, #127
    .size open_cfw_freertos_cli_collector_capacity_patch, . - open_cfw_freertos_cli_collector_capacity_patch

    .section .note.GNU-stack, "", %progbits
