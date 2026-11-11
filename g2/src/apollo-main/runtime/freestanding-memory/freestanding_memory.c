/* Main's freestanding C/ARM EABI byte-copy and clear runtime. */
#include <stddef.h>
#include <stdint.h>

/* memcpy and __aeabi_memcpy are the stock 0x439be4 copy; they are aliases of
 * audio_uart_checksum_copy in app/byte-copy/byte_copy.c. */

/* Stock 0x0043BB00 (memset): reorders (dst,c,n) to the IAR fill core 0x43c0e4
 * as (dst,n,c) and returns dst. The fill has one body, audio_uart_buffer_zero
 * (drivers/peripherals/ring-init/ring_init.c). */
extern void *audio_uart_buffer_zero(void *destination,uint32_t length,uint32_t fill);
void *memset(void *destination,int value,size_t bytes)
{
    (void)audio_uart_buffer_zero(destination,(uint32_t)bytes,(uint32_t)value);
    return destination;
}

/* offline_fill (hal/uart/uart-rx/uart-rx-stream compat memset) is the same
 * routine with the same contract. */
void *offline_fill(void *destination,int value,size_t bytes) __attribute__((alias("memset")));

void __aeabi_memclr(void *destination,size_t bytes)
{
    (void)memset(destination,0,bytes);
}

/* The 4- and 8-byte-aligned EABI clear entries have the same contract; one body. */
void __aeabi_memclr4(void *destination,size_t bytes) __attribute__((alias("__aeabi_memclr")));
void __aeabi_memclr8(void *destination,size_t bytes) __attribute__((alias("__aeabi_memclr")));
