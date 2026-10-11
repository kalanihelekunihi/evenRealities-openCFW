/* Native compiler byte-copy helper 0x439be4..0x439c85. The retained UART
 * caller ignores r0; native r0 after copy varies with the alignment path. */
#include <stdint.h>
void audio_uart_checksum_copy(void *destination,const void *source,uint32_t length)
{
    volatile uint8_t *d=(volatile uint8_t *)destination;
    const volatile uint8_t *s=(const volatile uint8_t *)source;
    for (uint32_t i=0;i<length;i++) d[i]=s[i];
}
