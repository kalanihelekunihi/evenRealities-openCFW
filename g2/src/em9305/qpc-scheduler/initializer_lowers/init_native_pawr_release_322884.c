#include <stdint.h>

/* Native 0x322884..0x3228a6: detach and release the two PAwR event buffers
 * held at record+300 and record+308; each slot is cleared before release. */
extern uint32_t opencfw_em9305_wsf_event_release(uintptr_t);

void opencfw_em9305_pawr_release_322884(uintptr_t record)
{
    uintptr_t event=*(volatile uint32_t *)(record+300u);
    *(volatile uint32_t *)(record+300u)=0u;
    if(event!=0u) (void)opencfw_em9305_wsf_event_release(event);
    event=*(volatile uint32_t *)(record+308u);
    *(volatile uint32_t *)(record+308u)=0u;
    if(event!=0u) (void)opencfw_em9305_wsf_event_release(event);
}
