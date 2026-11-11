/* Reconstructed codec UART3 ring-drain providers; valid mask/storage only. */
#include "drain.h"
/* Stock-RAM literals rewritten to named objects (sim-test wave 2026-10-26,
 * .waves/sim-fix/apply.py): g2ref_X is the linker symbol X. */
#include <stdint.h>
extern unsigned char g2ref_g2_stock_ram_20073ed0[] __asm__("g2_stock_ram_20073ed0");
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
/* Stock 0x58FB2A (codec UART3 RX ring read) */
uint32_t codec_uart_read(uint8_t *dst,uint32_t capacity){return codec_ring_read((uart3_ring_t *)((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20073ed0+0x4u),dst,capacity);}
