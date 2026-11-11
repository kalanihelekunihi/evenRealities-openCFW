#include <stdint.h>

/* Native 0x325548..0x3255a6: start scanning. Copy the two scan
 * configuration words (0x805af8) to 0x805014, initialise the scan ring
 * at 0x80501c for the configured size, issue common request 1, count the
 * command, mark scanning active (0x805a73) and count the secondary when
 * bit 0 of 0x80501a is set, start the scan, set the start flags at
 * 0x805166/0x805168, clear 0x805a75 and report command status 0. */
extern uint32_t opencfw_em9305_scan_ring_init_316a54(uint32_t a,uint32_t b);
extern uint32_t opencfw_em9305_common_request_30455c(uint32_t index);
extern uint32_t opencfw_em9305_command_count_30e4bc(void);
extern uint32_t opencfw_em9305_init_secondary_count_up_30e4cc(void);
extern uint32_t opencfw_em9305_scan_start_31eac8(void);
extern uint32_t opencfw_em9305_command_status_30e8c0(uint32_t status);

uint32_t opencfw_em9305_scan_action_325548(void)
{
    uint32_t second=*(volatile uint32_t *)0x805afcu;
    uint32_t first=*(volatile uint32_t *)0x805af8u;
    uintptr_t config=*(volatile uint32_t *)0x805c78u;
    *(volatile uint32_t *)0x805018u=second;
    *(volatile uint32_t *)0x805014u=first;
    (void)opencfw_em9305_scan_ring_init_316a54(0x80501cu,
                                               *(volatile uint8_t *)(config+4u));
    (void)opencfw_em9305_common_request_30455c(1u);
    (void)opencfw_em9305_command_count_30e4bc();
    uint32_t options=*(volatile uint8_t *)0x80501au;
    *(volatile uint8_t *)0x805a73u=1u;
    if((options&1u)!=0u)(void)opencfw_em9305_init_secondary_count_up_30e4cc();
    (void)opencfw_em9305_scan_start_31eac8();
    *(volatile uint8_t *)0x805168u=1u;
    *(volatile uint16_t *)0x805166u=1u;
    *(volatile uint8_t *)0x805a75u=0u;
    return opencfw_em9305_command_status_30e8c0(0u);
}
