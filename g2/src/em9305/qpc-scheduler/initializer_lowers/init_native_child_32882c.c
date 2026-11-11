#include <stdint.h>

/* Native 0x32882c..0x3288b0: complete a sync establishment. When native
 * 0x328a74 reports a status, send message 4 and finish with that status.
 * Otherwise request common resource 1 and, for a train (+180) in state 1,
 * mark it (+369, +378 unless +2785 is set), seed its CRC state (+1442) from
 * a random value, the length +2250 and the data at *(+1424), and set +2786;
 * then post event 2 and count up the command state. */
extern uint32_t opencfw_em9305_child_328a74(uintptr_t);
extern uint32_t opencfw_em9305_child_32909c(uintptr_t,uint32_t);
extern uint32_t opencfw_em9305_child_3230e0(uintptr_t,uint32_t);
extern uint32_t opencfw_em9305_common_request_30455c(uint32_t);
extern uint32_t opencfw_em9305_scan_random_30c478(void);
extern uint32_t opencfw_em9305_crc_update_304678(uint32_t,uint32_t,uintptr_t);
extern uint32_t opencfw_em9305_child_329064(uintptr_t,uint32_t);
extern uint32_t opencfw_em9305_command_count_30e4bc(void);

uint32_t opencfw_em9305_child_32882c(uintptr_t record)
{
    uint32_t status = opencfw_em9305_child_328a74(record);
    if (status != 0u) {
        (void)opencfw_em9305_child_32909c(record, 4u);
        return opencfw_em9305_child_3230e0(record, status);
    }
    (void)opencfw_em9305_common_request_30455c(1u);
    uintptr_t train = *(volatile uint32_t *)(record + 180u);
    if (train != 0u) {
        uint32_t state = *(volatile uint8_t *)(train + 2u);
        *(volatile uint8_t *)(train + 369u) = 1u;
        if (state == 1u) {
            if (*(volatile uint8_t *)(train + 2785u) == 0u)
                *(volatile uint8_t *)(train + 378u) = 1u;
            uint32_t length = *(volatile uint16_t *)(train + 2250u);
            uintptr_t data = *(volatile uint32_t *)(train + 1424u);
            uint32_t seed = opencfw_em9305_scan_random_30c478();
            uint32_t crc = opencfw_em9305_crc_update_304678(seed, length, data);
            *(volatile uint8_t *)(train + 2786u) = 1u;
            *(volatile uint16_t *)(train + 1442u) = (uint16_t)crc;
        }
    }
    (void)opencfw_em9305_child_329064(record, 2u);
    return opencfw_em9305_command_count_30e4bc();
}
