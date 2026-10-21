/* FreeRTOS unordered event-list placement, stock 0x4552ae. */
#include <stdint.h>
extern void audio_block_ticks(uint32_t ticks,uint32_t can_block_indefinitely);
extern void g2_event_place_assert(void) __attribute__((noreturn));
void g2_event_place_unordered(void *raw_list,uint32_t value,uint32_t ticks) {
    if(!raw_list || *(volatile uint32_t *)(uintptr_t)0x20074a58u==0u)
        g2_event_place_assert();
    uint8_t *list=(uint8_t *)raw_list;
    uint8_t *tcb=*(uint8_t *volatile *)(uintptr_t)0x20074a20u;
    *(uint32_t *)(void *)(tcb+0x18u)=value|0x80000000u;
    uint8_t *index=*(uint8_t **)(void *)(list+4u);
    *(void **)(void *)(tcb+0x1cu)=index;
    uint8_t *prev=*(uint8_t **)(void *)(index+8u);
    *(void **)(void *)(tcb+0x20u)=prev;
    *(void **)(void *)(prev+4u)=tcb+0x18u;
    *(void **)(void *)(index+8u)=tcb+0x18u;
    *(void **)(void *)(tcb+0x28u)=list;
    *(uint32_t *)(void *)list+=1u;
    audio_block_ticks(ticks,1u);
}
