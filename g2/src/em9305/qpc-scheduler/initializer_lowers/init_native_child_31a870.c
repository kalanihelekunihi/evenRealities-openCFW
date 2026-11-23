#include <stdint.h>
#include "em9305_ram.h"

/* Native 0x31a870..0x31a8ce: start a scan record. Request common resource 1,
 * count up the secondary init state when flag +14 bit 0 is set, clear the
 * request/retry bytes (+1, +2, +56, +241, +242) and run the two start checks
 * (natives 0x31fbb8, 0x31c694). A failing check reports its status as a scan
 * error and sends message 3; otherwise the link count at ((uintptr_t)&em9305_ram_805a6c + 0x7u) grows, the
 * backoff (+98) and count (+100) are reset to 1 and success is reported. */
extern uint32_t opencfw_em9305_common_request_30455c(uint32_t);
extern uint32_t opencfw_em9305_init_secondary_count_up_30e4cc(void);
extern uint32_t opencfw_em9305_child_31fbb8(uintptr_t);
extern uint32_t opencfw_em9305_child_31c694(uintptr_t);
extern uint32_t opencfw_em9305_scan_error_30e7f8(uint32_t);
extern uint32_t opencfw_em9305_child_325edc(uintptr_t,uint32_t);
extern uint32_t opencfw_em9305_command_count_30e4bc(void);

uint32_t opencfw_em9305_child_31a870(uintptr_t record)
{
    (void)opencfw_em9305_common_request_30455c(1u);
    if ((*(volatile uint8_t *)(record + 14u) & 1u) != 0u)
        (void)opencfw_em9305_init_secondary_count_up_30e4cc();
    *(volatile uint8_t *)(record + 242u) = 0u;
    *(volatile uint8_t *)(record + 241u) = 0u;
    *(volatile uint8_t *)(record + 2u) = 0u;
    *(volatile uint8_t *)(record + 1u) = 0u;
    *(volatile uint8_t *)(record + 56u) = 0u;
    uint32_t status = opencfw_em9305_child_31fbb8(record);
    if (status == 0u) status = opencfw_em9305_child_31c694(record);
    if (status != 0u) {
        (void)opencfw_em9305_scan_error_30e7f8(status);
        return opencfw_em9305_child_325edc(record, 3u);
    }
    volatile uint8_t *links = &em9305_ram_805a6c.u8_805a73;
    *links = (uint8_t)(*links + 1u);
    (void)opencfw_em9305_command_count_30e4bc();
    *(volatile uint16_t *)(record + 98u) = 1u;
    *(volatile uint8_t *)(record + 100u) = 1u;
    return opencfw_em9305_scan_error_30e7f8(0u);
}
