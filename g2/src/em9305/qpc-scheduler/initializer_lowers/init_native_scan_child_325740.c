#include <stdint.h>

/* Native 0x325740..0x3257a4: finish a scan context (0x804fd8 or the
 * other scanner): count the command down, clear its busy byte (0x805a73
 * or 0x805a74), count the init state down when bit 0 of +66 is set,
 * release its PAwR state and free every event queued at +40 and +48.
 * Always returns 0. */
extern uint32_t opencfw_em9305_command_count_down_30e48c(void);
extern uint32_t opencfw_em9305_init_state_count_down_30e49c(void);
extern uint32_t opencfw_em9305_pawr_release_322884(uintptr_t scan);
extern uintptr_t opencfw_em9305_wsf_event_remove(uintptr_t queue, uintptr_t handler_out);
extern uint32_t opencfw_em9305_wsf_event_release(uintptr_t event);

uint32_t opencfw_em9305_scan_finish_325740(uintptr_t scan)
{
    uint8_t handler;
    uintptr_t event;
    (void)opencfw_em9305_command_count_down_30e48c();
    if(scan==0x804fd8u)*(volatile uint8_t *)(uintptr_t)0x805a73u=0u;
    else *(volatile uint8_t *)(uintptr_t)0x805a74u=0u;
    if((*(volatile uint8_t *)(scan+66u)&1u)!=0u)
        (void)opencfw_em9305_init_state_count_down_30e49c();
    (void)opencfw_em9305_pawr_release_322884(scan);
    while((event=opencfw_em9305_wsf_event_remove(scan+40u,(uintptr_t)&handler))!=0u)
        (void)opencfw_em9305_wsf_event_release(event);
    while((event=opencfw_em9305_wsf_event_remove(scan+48u,(uintptr_t)&handler))!=0u)
        (void)opencfw_em9305_wsf_event_release(event);
    return 0u;
}
