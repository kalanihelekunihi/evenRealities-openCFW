/* SPDX-License-Identifier: MIT */
/* Mirrors the pinned SDK uart_message_v2.c header parser: its four-byte
 * synchronization prefix has already been consumed on entry. */
enum { UART_HEADER_PREFIX_BYTES = 4 };
unsigned int s_recv_header_data_count[2]
    __attribute__((section(".data.header_counts"))) = {
        UART_HEADER_PREFIX_BYTES, UART_HEADER_PREFIX_BYTES
    };
_Static_assert(sizeof(unsigned int) == 4, "UART counter ABI");
