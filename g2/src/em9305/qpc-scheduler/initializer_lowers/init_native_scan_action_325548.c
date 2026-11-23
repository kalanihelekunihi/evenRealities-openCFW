#include <stdint.h>
#include "em9305_ram.h"

/* Native 0x325548..0x3255a6: start scanning. Copy the two scan
 * configuration words (((uintptr_t)&em9305_ram_805af0 + 0x8u)) to ((uintptr_t)&em9305_ram_805010 + 0x4u), initialise the scan ring
 * at ((uintptr_t)&em9305_ram_803d58 + 0x12c4u) for the configured size, issue common request 1, count the
 * command, mark scanning active (((uintptr_t)&em9305_ram_805a6c + 0x7u)) and count the secondary when
 * bit 0 of ((uintptr_t)&em9305_ram_805010 + 0xau) is set, start the scan, set the start flags at
 * ((uintptr_t)&em9305_ram_805160 + 0x6u)/((uintptr_t)&em9305_ram_805160 + 0x8u), clear ((uintptr_t)&em9305_ram_805a6c + 0x9u) and report command status 0. */
extern uint32_t opencfw_em9305_scan_ring_init_316a54(uint32_t a,uint32_t b);
extern uint32_t opencfw_em9305_common_request_30455c(uint32_t index);
extern uint32_t opencfw_em9305_command_count_30e4bc(void);
extern uint32_t opencfw_em9305_init_secondary_count_up_30e4cc(void);
extern uint32_t opencfw_em9305_scan_start_31eac8(void);
extern uint32_t opencfw_em9305_command_status_30e8c0(uint32_t status);

uint32_t opencfw_em9305_scan_action_325548(void)
{
    uint32_t second=*(volatile uint32_t *)((uintptr_t)&em9305_ram_805af0 + 0xcu);
    uint32_t first=*(volatile uint32_t *)((uintptr_t)&em9305_ram_805af0 + 0x8u);
    uintptr_t config=*(volatile uint32_t *)((uintptr_t)&em9305_ram_805c5c + 0x1cu);
    *(volatile uint32_t *)((uintptr_t)&em9305_ram_805010 + 0x8u)=second;
    *(volatile uint32_t *)((uintptr_t)&em9305_ram_805010 + 0x4u)=first;
    (void)opencfw_em9305_scan_ring_init_316a54(((uintptr_t)&em9305_ram_803d58 + 0x12c4u),
                                               *(volatile uint8_t *)(config+4u));
    (void)opencfw_em9305_common_request_30455c(1u);
    (void)opencfw_em9305_command_count_30e4bc();
    uint32_t options=*(volatile uint8_t *)((uintptr_t)&em9305_ram_805010 + 0xau);
    *(volatile uint8_t *)((uintptr_t)&em9305_ram_805a6c + 0x7u)=1u;
    if((options&1u)!=0u)(void)opencfw_em9305_init_secondary_count_up_30e4cc();
    (void)opencfw_em9305_scan_start_31eac8();
    *(volatile uint8_t *)((uintptr_t)&em9305_ram_805160 + 0x8u)=1u;
    *(volatile uint16_t *)((uintptr_t)&em9305_ram_805160 + 0x6u)=1u;
    *(volatile uint8_t *)((uintptr_t)&em9305_ram_805a6c + 0x9u)=0u;
    return opencfw_em9305_command_status_30e8c0(0u);
}
