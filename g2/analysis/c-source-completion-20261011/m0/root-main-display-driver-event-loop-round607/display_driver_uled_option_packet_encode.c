/* Apollo S200 24-byte packet descriptor encoder at 0x59cafc. */
#include <stdint.h>

extern void audio_uart_buffer_zero(void *,uint32_t,uint32_t);

void display_driver_uled_packet_encode_59cafc(const void *source,void *output,
                                              uint32_t direction) {
    if (source == 0 || output == 0) return;
    const uint8_t *s=(const uint8_t *)source;
    uint8_t *d=(uint8_t *)output;
    audio_uart_buffer_zero(d,24u,0u);
    for (uint32_t i=0;i<4u;i++) d[i]=s[12u+i];
    d[16]=s[16];
    for (uint32_t i=0;i<4u;i++) d[20u+i]=s[20u+i];
    d[5]=0u;
    d[17]=0u;
    d[6]=(uint8_t)direction;
    d[7]=s[0];
    for (uint32_t i=0;i<4u;i++) d[8u+i]=s[4u+i];
    d[12]=s[8];
    d[14]=s[9];
    d[15]=0u;
}
