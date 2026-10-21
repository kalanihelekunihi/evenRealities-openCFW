/* Native init_thread_pool 0x49137a backing storage. Absolute placement
 * remains a linker/product contract; sizes follow ROM pointer cells and
 * the CMSIS attributes at 0x77ccac. */
#include <stdint.h>

void *audio_uart_pool_threads[8];          /* native 0x200739dc, 0x20 bytes */
char audio_uart_pool_names[8][20];         /* native 0x20071710, 0xa0 bytes */
_Alignas(8) uint8_t audio_uart_pool_stacks[8][0x1000];
_Alignas(4) uint8_t audio_uart_pool_controls[8][0x70];
_Alignas(4) uint8_t audio_uart_pool_queue_control_mem[0x50];
_Alignas(8) uint8_t audio_uart_pool_queue_storage[0xbb8];

_Static_assert(sizeof(audio_uart_pool_threads)==0x20u,"thread handles");
_Static_assert(sizeof(audio_uart_pool_names)==0xa0u,"thread names");
_Static_assert(sizeof(audio_uart_pool_stacks)==0x8000u,"thread stacks");
_Static_assert(sizeof(audio_uart_pool_controls)==0x380u,"thread controls");
