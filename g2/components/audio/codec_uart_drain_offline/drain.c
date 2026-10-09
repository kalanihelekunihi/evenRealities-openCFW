/* Reconstructed codec UART3 ring-drain providers; valid mask/storage only. */
#include "drain.h"
uint32_t codec_ring_empty(const uart3_ring_t *q){return q->write==q->read;}
uint32_t codec_ring_get(uart3_ring_t *q,uint8_t *out){
    if(codec_ring_empty(q))return 0;
    *out=q->storage[q->read];q->read=(q->read+1)&q->mask;return 1;
}
uint32_t codec_ring_read(uart3_ring_t *q,uint8_t *dst,uint32_t capacity){
    if(codec_ring_empty(q))return 0;
    uint32_t n=0;
    while(n<capacity && codec_ring_get(q,dst)){n++;dst++;}
    return n;
}
uint32_t codec_uart_read(uint8_t *dst,uint32_t capacity){return codec_ring_read((uart3_ring_t *)0x20073ed4,dst,capacity);}
