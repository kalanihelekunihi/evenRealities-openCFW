/* SPDX-License-Identifier: MIT
 * Native CASE 0x0800afcc ordered free-list insertion and coalescing.
 */
#include <stdint.h>
static uint32_t rd(uint32_t a){return *(volatile uint32_t *)(uintptr_t)a;}
static void wr(uint32_t a,uint32_t v){*(volatile uint32_t *)(uintptr_t)a=v;}
void case_boot_heap_insert(uint32_t block)
{
    uint32_t prior=0x20000194u;
    uint32_t next=rd(prior);
    while(next<block){prior=next;next=rd(prior);}
    uint32_t prior_size=rd(prior+4u);
    if(prior+prior_size==block){
        wr(prior+4u,prior_size+rd(block+4u));
        block=prior;
    }
    uint32_t block_size=rd(block+4u);
    if(block+block_size==rd(prior)){
        uint32_t heap_start=rd(0x2000017cu);
        if(next==heap_start)wr(block,heap_start);
        else{
            wr(block+4u,block_size+rd(next+4u));
            wr(block,rd(next));
        }
    }else wr(block,next);
    if(prior!=block)wr(prior,block);
}
