#include <stdint.h>

/* Native 0x3228a8..0x3228e2: scan state machine step. The scan state byte
 * at 0x804ffc and the event's selector byte (+3) pick an entry of the 4x5
 * callback/transition tables at 0x3353fc/0x33544c. The callback (if any)
 * sees its own address, the table offset and the state in r0..r2, as in
 * the native call. Returns the new state. */
extern void (*const opencfw_em9305_scan_callbacks_3353fc[20])(void);
extern const uint8_t opencfw_em9305_scan_transitions_33544c[20];

uint32_t opencfw_em9305_callback_3228a8(uintptr_t event)
{
    volatile uint8_t *state=(volatile uint8_t *)(uintptr_t)0x804ffcu;
    uint32_t selector=*(volatile uint8_t *)(event+3u);
    uint32_t current=*state;
    uint32_t offset=current*20u+selector*4u;
    uintptr_t callback=*(const uintptr_t *)((uintptr_t)opencfw_em9305_scan_callbacks_3353fc+offset);
    if(callback!=0u){
        ((void (*)(uintptr_t,uint32_t,uint32_t))callback)(callback,offset,current);
        current=*state;
    }
    uint32_t next=opencfw_em9305_scan_transitions_33544c[current*5u+selector];
    *state=(uint8_t)next;
    return next;
}
