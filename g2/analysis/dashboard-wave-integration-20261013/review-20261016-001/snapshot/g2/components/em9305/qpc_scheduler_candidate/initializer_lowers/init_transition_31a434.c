#include <stdint.h>

extern uintptr_t opencfw_em9305_wsf_event_allocate(uint32_t);
extern void *opencfw_em9305_memcpy(void *,const void *,uint32_t);
extern uint32_t opencfw_em9305_wsf_task_message_send(uint32_t,uintptr_t);
extern uint32_t opencfw_em9305_associated_schedule_insert_312da4(
    uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_init_schedule_compare_318b78(
    uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_init_transition_count_down_320068(void);

static uint32_t native_mpywhl_31a518(uint32_t left)
{
#ifdef __arc__
    uint32_t result;
    __asm__ volatile("mpywhl %0,%1,1250":"=r"(result):"r"(left):"r58","r59","memory");
    return result;
#else
    return left*1250u; /* Host fixture model only. */
#endif
}

/* Full native 0x31a434..0x31a536. The first schedule pointer is captured
 * in BL delay slot before the insert call and reused on retries. */
uint32_t opencfw_em9305_init_transition_31a434(uintptr_t request)
{
    uintptr_t slot=request+0xafcu;
    uintptr_t initial_nested=*(volatile uint32_t *)slot;
    uintptr_t base=*(volatile uint32_t *)(uintptr_t)0x805c70u;
    uint16_t initial_id=*(volatile uint16_t *)(initial_nested+94u);
    uintptr_t event=opencfw_em9305_wsf_event_allocate(88u);
    uintptr_t connection;
    if(event!=0u) {
        *(volatile uint16_t *)(event+2u)=0x3f01u;
        uintptr_t nested=*(volatile uint32_t *)slot;
        base=*(volatile uint32_t *)(uintptr_t)0x805c70u;
        uint16_t id=*(volatile uint16_t *)(nested+94u);
        *(volatile uint16_t *)event=(uint8_t)id;
        connection=base+(uint32_t)id*912u;
        *(volatile uint8_t *)(connection+2u)=0u; /* Copy call delay slot. */
        (void)opencfw_em9305_memcpy((void *)(event+4u),
            (const void *)(nested+100u),44u);
        nested=*(volatile uint32_t *)slot;
        uint8_t request_flag=*(volatile uint8_t *)(request+2261u);
        uint8_t request_option=*(volatile uint8_t *)(request+63u);
        uint8_t request_id=*(volatile uint8_t *)(request+1u);
        uint32_t high=*(volatile uint32_t *)(nested+112u);
        uint32_t low=*(volatile uint32_t *)(nested+108u);
        uint8_t handler=*(volatile uint8_t *)(uintptr_t)0x805b18u;
        uint8_t selected=((high&0xc000u)==0x4000u);
        *(volatile uint8_t *)(event+52u)=selected;
        *(volatile uint32_t *)(event+60u)=low;
        uint32_t shared_high=*(volatile uint32_t *)(uintptr_t)0x805be8u;
        uint32_t shared_low=*(volatile uint32_t *)(uintptr_t)0x805be4u;
        *(volatile uint8_t *)(event+84u)=request_id;
        *(volatile uint32_t *)(event+72u)=0u;
        *(volatile uint32_t *)(event+76u)=shared_low;
        *(volatile uint32_t *)(event+68u)=0u;
        *(volatile uint16_t *)(event+86u)=0xffffu;
        *(volatile uint8_t *)(event+53u)=request_flag;
        *(volatile uint8_t *)(event+54u)=request_option;
        *(volatile uint32_t *)(event+80u)=shared_high;
        *(volatile uint32_t *)(event+64u)=high; /* Send delay slot. */
        (void)opencfw_em9305_wsf_task_message_send(handler,event);
    } else {
        connection=base+(uint32_t)initial_id*912u;
    }
    uint32_t initial_time=*(volatile uint32_t *)(connection+24u);
    uintptr_t object=connection+16u;
    uintptr_t compare=(uintptr_t)opencfw_em9305_init_schedule_compare_318b78;
    uint32_t inserted=opencfw_em9305_associated_schedule_insert_312da4(
        object,compare);
    if(inserted==0u) {
        uint32_t repeat=1u;
        do {
            uint16_t interval=*(volatile uint16_t *)(connection+266u);
            /* Native MPYUW consumes the low 16 bits of both operands. */
            uint32_t product=(uint32_t)(uint16_t)repeat*(uint32_t)interval;
            uint16_t offset=*(volatile uint16_t *)(connection+262u);
            uint32_t advance=native_mpywhl_31a518(product);
            *(volatile uint16_t *)(connection+262u)=(uint16_t)(offset+1u);
            *(volatile uint32_t *)(connection+24u)=initial_time+advance;
            inserted=opencfw_em9305_associated_schedule_insert_312da4(
                object,compare);
            repeat++;
        } while(inserted==0u);
    }
    return opencfw_em9305_init_transition_count_down_320068();
}
