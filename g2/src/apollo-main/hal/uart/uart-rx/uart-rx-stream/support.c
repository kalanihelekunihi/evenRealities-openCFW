/* Bounded offline support. Byte loops reconstructed for non-overlapping SRAM
 * memcpy/memset calls, independently compared through original providers.
 * BASEPRI operations reuse the already explained main port contract. */
#include "compat.h"
/* offline_copy (stock 0x439be4 copy) is an alias of audio_uart_checksum_copy
 * in app/byte-copy/byte_copy.c. */
/* offline_fill is an alias of memset in runtime/freestanding-memory/freestanding_memory.c. */
UBaseType_t offline_mask_set(void){uint32_t old;const uint32_t threshold=0x30;__asm volatile("mrs %0,basepri\nmsr basepri,%1\ndsb\nisb":"=&r"(old):"r"(threshold):"memory");return old;}
void offline_mask_restore(UBaseType_t old){__asm volatile("msr basepri,%0"::"r"(old):"memory");}
