#include <stdint.h>
#include <stddef.h>

/* Native 0x319204..0x319208. Opcode-table default handler. */
uint32_t opencfw_em9305_packet_entry_319204(uint32_t context, uint32_t payload,
                                             uint32_t mode)
{
    (void)context; (void)payload; (void)mode;
    return 25u;
}

/* Native 0x3191ac..0x3191c4. Store at 0x3191c0 is the return delay slot. */
uint32_t opencfw_em9305_packet_entry_3191ac(uint32_t context, uint32_t payload,
                                             uint32_t mode)
{
    (void)mode;
    volatile uint8_t *record = (volatile uint8_t *)(uintptr_t)context;
    record[12] = 255u;
    uint32_t status = record[5] == 2u ? 0u : 25u;
    record[13] = *(volatile const uint8_t *)(uintptr_t)(payload + 1u);
    return status;
}

/* Native 0x3191c4..0x3191dc. Child 0x32e1f4 is still a true provider. */
extern uint32_t opencfw_em9305_child_32e1f4(uint32_t record_fields);
uint32_t opencfw_em9305_packet_entry_3191c4(uint32_t context, uint32_t payload,
                                             uint32_t mode)
{
    (void)payload; (void)mode;
    (void)opencfw_em9305_child_32e1f4(context + 12u);
    return *(volatile const uint8_t *)(uintptr_t)(context + 5u) == 6u ? 0u : 25u;
}
