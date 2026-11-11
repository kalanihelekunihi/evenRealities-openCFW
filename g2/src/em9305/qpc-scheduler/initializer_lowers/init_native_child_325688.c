#include <stdint.h>

/* Native 0x325688..0x3256c8: scan backoff update. Every second call
 * (counter at +102) doubles the backoff window (+98, capped at 256); then
 * clear +101 and pick a random count in 1..window into +100. */
extern uint32_t opencfw_em9305_scan_random_30c478(void);

uint32_t opencfw_em9305_child_325688(uintptr_t record)
{
    uint32_t count=*(volatile uint8_t *)(record+102u)+1u;
    *(volatile uint8_t *)(record+102u)=(uint8_t)count;
    if((uint8_t)count>=2u) {
        uint32_t window=*(volatile uint16_t *)(record+98u);
        *(volatile uint8_t *)(record+102u)=0u;
        window=(uint16_t)(window<<1);
        if(window>256u) window=256u;
        *(volatile uint16_t *)(record+98u)=(uint16_t)window;
    }
    *(volatile uint8_t *)(record+101u)=0u;
    uint32_t random=opencfw_em9305_scan_random_30c478();
    uint32_t pick=(random&(*(volatile uint16_t *)(record+98u)-1u))+1u;
    *(volatile uint8_t *)(record+100u)=(uint8_t)pick;
    return pick;
}
