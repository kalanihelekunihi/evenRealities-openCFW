/* Provisional C backing for the observed UART configuration prefix.
 * Stock RAM base is 0x20000d9c. This uninitialized object is not a claim
 * that stock startup leaves those bytes zero or that the full extent is 16. */
#include "sync_uart_config_contract.h"
g2_sync_uart_config_prefix_t g2_uart_sync_buffer;
