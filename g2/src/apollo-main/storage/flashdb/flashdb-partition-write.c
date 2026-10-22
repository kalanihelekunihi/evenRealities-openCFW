/* FAL partition write, with logging compiled out as in the stock body.
 * Lower device selection and flash write remain external contracts. */
#include <stdint.h>

extern uint32_t g2_fal_device_for_partition(uint32_t partition);

/* Stock 0x597D72 (fal_partition_write) */
int32_t g2_flashdb_partition_write(uint32_t partition, uint32_t address,
                                   uint32_t buffer, uint32_t size)
{
    const uint32_t length = *(const uint32_t *)(uintptr_t)(partition + 0x38u);
    if (address + size > length) return -1;
    const uint32_t device = g2_fal_device_for_partition(partition);
    if (device == 0u) return -1;
    const uint32_t callback = *(const uint32_t *)(uintptr_t)(device + 0x2cu);
    int32_t (*write_fn)(uint32_t, uint32_t, uint32_t) =
        (int32_t (*)(uint32_t, uint32_t, uint32_t))(uintptr_t)callback;
    const uint32_t offset = *(const uint32_t *)(uintptr_t)(partition + 0x34u);
    return write_fn(offset + address, buffer, size);
}
