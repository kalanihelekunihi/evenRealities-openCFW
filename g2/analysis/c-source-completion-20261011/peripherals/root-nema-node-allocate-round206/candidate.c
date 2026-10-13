#include <stdint.h>
extern void *audio_uart_lv_pool_allocate_484180(void *,uint32_t);
/* Native51416c..514178, same source pool contract as node-release514178. */
void *audio_uart_nema_node_allocate_51416c(uint32_t size) { return audio_uart_lv_pool_allocate_484180((void *)(uintptr_t)0x20000338u,size); }
