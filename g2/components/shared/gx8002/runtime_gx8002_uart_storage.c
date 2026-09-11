/* SPDX-License-Identifier: MIT */
#include <stdint.h>
#include <base_addr.h>
#include <soc.h>

/* Descriptor offsets are consumed by the recovered UART routines. Fields 7
 * and 8 are normalized to 8 and 1 by configuration; their original names are
 * not established. Remaining fields start at zero and hold runtime state. */
enum { UART_PORT=0, UART_DEVICE=1, UART_BAUD=4,
       UART_DEFAULT_7=7, UART_DEFAULT_8=8, UART_IRQ=15 };
volatile uint32_t open_cfw_gx8002_uart_descriptors[2][32] = {
    { [UART_PORT]=0, [UART_DEVICE]=GX_REG_BASE_UART0, [UART_BAUD]=115200,
      [UART_DEFAULT_7]=8, [UART_DEFAULT_8]=1, [UART_IRQ]=IRQ_NUM_DW_UART1 },
    { [UART_PORT]=1, [UART_DEVICE]=GX_REG_BASE_UART1, [UART_BAUD]=115200,
      [UART_DEFAULT_7]=8, [UART_DEFAULT_8]=1, [UART_IRQ]=IRQ_NUM_DW_UART2 }
};
_Static_assert(sizeof(open_cfw_gx8002_uart_descriptors[0])==128,"UART descriptor stride");
