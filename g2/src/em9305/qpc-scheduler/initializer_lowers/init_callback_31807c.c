#include <stdint.h>

/* Native 0x31807c..0x31810a. The two ROM transition tables at 0x334e80
 * (words) and 0x334ec0 (bytes) remain typed data contracts. Each row has
 * four event selectors and each selector has four transition states. */
extern const uintptr_t opencfw_em9305_init_transition_callbacks_334e80[16];
extern const uint8_t opencfw_em9305_init_transition_states_334ec0[16];
extern uintptr_t opencfw_em9305_radio_record_find_31aa64(uint32_t);

static uint32_t opencfw_em9305_init_callback_step_3180d4(uintptr_t record,
                                                          uint32_t selector)
{
    uintptr_t slot=record+0xafcu;
    uintptr_t nested=*(volatile uint32_t *)slot;
    uint32_t state=*(volatile uint8_t *)(nested+80u);
    uint32_t index=state*4u+selector;
    uintptr_t callback=opencfw_em9305_init_transition_callbacks_334e80[index];
    if(callback!=0u) {
        (void)((uint32_t (*)(uintptr_t,uintptr_t,uint32_t,uintptr_t))callback)
            (record,callback,state,nested);
        nested=*(volatile uint32_t *)slot;
        state=*(volatile uint8_t *)(nested+80u);
    }
    uint32_t next=opencfw_em9305_init_transition_states_334ec0[state*4u+selector];
    *(volatile uint8_t *)(nested+80u)=(uint8_t)next;
    return next;
}

uint32_t opencfw_em9305_init_callback_31807c(uintptr_t event)
{
    uint32_t kind=*(volatile uint8_t *)(event+2u);
    uint32_t selector=*(volatile uint8_t *)(event+3u);
    if(kind!=255u) {
        uintptr_t record=opencfw_em9305_radio_record_find_31aa64(
            *(volatile uint8_t *)event);
        if(record==0u) return 0u;
        if(*(volatile uint32_t *)(record+0xafcu)==0u)return (uint32_t)record;
        return opencfw_em9305_init_callback_step_3180d4(record,selector);
    }
    for(uint32_t index=0u,id=0u;;++index,++id) {
        uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
        uint32_t count=*(volatile uint8_t *)(config+13u);
        if(index>=count)return (uint8_t)id;
        uintptr_t record=opencfw_em9305_radio_record_find_31aa64((uint8_t)id);
        if(record!=0u&&*(volatile uint32_t *)(record+0xafcu)!=0u)
            (void)opencfw_em9305_init_callback_step_3180d4(record,selector);
    }
}
