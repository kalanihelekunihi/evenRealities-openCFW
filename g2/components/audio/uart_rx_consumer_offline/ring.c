/* Reconstructed UART3 staging ring helpers, authenticated stock bytes.
 * No concurrency/ISR atomicity claim; caller supplies valid power-of-two mask. */
#include <stdint.h>
#include "ring.h"
uint32_t uart3_ring_full(const uart3_ring_t *q){return ((q->write-q->read)&q->mask)==q->mask;}
void uart3_ring_put(uart3_ring_t *q,uint32_t byte){
    if(uart3_ring_full(q))q->read=(q->read+1)&q->mask;
    q->storage[q->write]=(uint8_t)byte;
    q->write=(q->write+1)&q->mask;
}
void uart3_ring_write(uart3_ring_t *q,const uint8_t *src,uint32_t n){for(uint32_t i=0;i<n;i++)uart3_ring_put(q,src[i]);}
