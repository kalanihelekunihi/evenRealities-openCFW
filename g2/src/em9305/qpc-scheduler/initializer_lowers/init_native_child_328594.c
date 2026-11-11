#include <stdint.h>

/* Native 0x328594..0x3286e4: initialise the periodic-advertising train of an
 * advertising set. Clear the 312-byte train object (+2468) and fill its
 * header (kinds 2/1/7, owner, data pointers +2248/+2516, completion callback
 * 0x3280e8, sync-info byte +2784); set the sync packet parameters: TX power
 * (+60, 0x7f -> default 0x805a9c), SID (+63), PHY code (1/2/1/2 for PHY +69
 * 1..4, else 0), access address 0x8e89bed6, CRC init 0x555555 and length 8
 * (also +2594 for a coded, chained set). Encode the first PDU (native
 * 0x3239fc) into +945 / +2616, allocate the 18-byte sync message (failure
 * reports status 31, event 4) and install the train callbacks (0x32be78,
 * 0x32bdfc, 0x32c5a4), then start the train (native 0x328270). */
extern void *opencfw_em9305_memset(void *,uint32_t,uint32_t);
extern uint32_t opencfw_em9305_child_3239fc(uintptr_t,uintptr_t,uintptr_t,uint32_t);
extern uintptr_t opencfw_em9305_wsf_event_allocate(uint32_t);
extern uint32_t opencfw_em9305_child_325a40(uintptr_t,uint32_t);
extern uint32_t opencfw_em9305_child_328270(uintptr_t,uintptr_t);
extern void opencfw_em9305_child_3280e8(uintptr_t);
extern uint32_t opencfw_em9305_child_32be78(uintptr_t);
extern uint32_t opencfw_em9305_child_32bdfc(uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_child_32c5a4(uintptr_t,uint32_t);

uint32_t opencfw_em9305_child_328594(uintptr_t set)
{
    uintptr_t train = set + 2468u;
    (void)opencfw_em9305_memset((void *)train, 0u, 312u);
    uint32_t power = (uint32_t)(int32_t)*(volatile int8_t *)(set + 60u);
    uint32_t info = *(volatile uint8_t *)(set + 0xae0u);
    uint32_t complete = (uint32_t)(uintptr_t)opencfw_em9305_child_3280e8;
    *(volatile uint8_t *)(train + 26u) = 1u;
    *(volatile uint8_t *)(train + 24u) = 2u;
    *(volatile uint8_t *)(train + 48u) = 7u;
    *(volatile uint32_t *)(train + 0x24u) = (uint32_t)set;
    *(volatile uint32_t *)(train + 0x2cu) = (uint32_t)(set + 0x9d4u);
    *(volatile uint32_t *)(train + 0x28u) = (uint32_t)(set + 0x8c8u);
    *(volatile uint32_t *)(train + 0x20u) = complete;
    *(volatile uint32_t *)(train + 0x1cu) = complete;
    *(volatile uint8_t *)(train + 49u) = (uint8_t)info;
    if (power == 0x7fu) power = *(volatile uint8_t *)(uintptr_t)0x805a9cu;
    uint32_t sid = *(volatile uint8_t *)(set + 63u);
    uint32_t phy = *(volatile uint8_t *)(set + 69u) - 1u;
    uint32_t properties = *(volatile uint16_t *)(set + 0x20u);
    *(volatile uint8_t *)(set + 2529u) = (uint8_t)sid;
    *(volatile uint8_t *)(set + 2528u) = (uint8_t)sid;
    uint32_t code = phy < 4u ? 0x2010201u >> (((phy & 0xffu) * 8u) & 31u) : 0u;
    *(volatile uint32_t *)(set + 2520u) = 0x8e89bed6u;
    *(volatile uint32_t *)(set + 2524u) = 0x555555u;
    *(volatile uint8_t *)(set + 2518u) = (uint8_t)power;
    *(volatile uint16_t *)(set + 2592u) = 8u;
    *(volatile uint8_t *)(set + 2531u) = (uint8_t)code;
    *(volatile uint8_t *)(set + 2530u) = (uint8_t)code;
    if ((properties & 6u) == 2u && (*(volatile uint8_t *)(set + 59u) & 1u) != 0u)
        *(volatile uint16_t *)(set + 0xa22u) = 8u;
    *(volatile uint16_t *)(set + 1430u) = 0u;
    *(volatile uint32_t *)(set + 0xa3cu) = (uint32_t)(set + 945u);
    uint32_t header = opencfw_em9305_child_3239fc(set, set + 945u, 0u, 0u);
    *(volatile uint16_t *)(set + 0xa38u) = (uint16_t)header;
    uintptr_t message = opencfw_em9305_wsf_event_allocate(0x12u);
    if (message != 0u) {
        *(volatile uint32_t *)(set + 0xa70u) = (uint32_t)(uintptr_t)opencfw_em9305_child_32be78;
        *(volatile uint32_t *)(set + 0xa6cu) = (uint32_t)(uintptr_t)opencfw_em9305_child_32bdfc;
        *(volatile uint32_t *)(set + 0xa48u) = (uint32_t)(message + 4u);
    } else {
        *(volatile uint8_t *)(set + 826u) = 31u;
        (void)opencfw_em9305_child_325a40(set, 4u);
    }
    uint32_t sync_info = *(volatile uint8_t *)(set + 0xa74u + 108u);
    *(volatile uint32_t *)(set + 0xa74u) = (uint32_t)(uintptr_t)opencfw_em9305_child_32c5a4;
    *(volatile uint32_t *)(set + 0xa74u - 36u) = (uint32_t)(set + 1011u);
    *(volatile uint32_t *)(set + 0xa74u - 20u) = (uint32_t)(set + 1011u);
    *(volatile uint8_t *)(set + 0xa74u - 159u) = (uint8_t)sync_info;
    *(volatile uint16_t *)(set + 1706u) = 0u;
    return opencfw_em9305_child_328270(set, train);
}
