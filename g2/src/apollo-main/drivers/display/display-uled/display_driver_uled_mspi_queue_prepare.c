/* Apollo S200 MSPI queue preparation at 0x4bfcc0. */
#include <stdint.h>

extern uint64_t g2_main_cq_reserve_538ece(uint32_t, uint32_t, uint32_t,
                                            uint32_t);
extern uint32_t display_driver_uled_mspi_descriptor_4bfa3c(
    uint32_t, uint32_t, uint32_t, const void *);
extern void g2_main_cq_rollback_538f82(uint32_t);

uint32_t display_driver_uled_mspi_queue_prepare_4bfcc0(
    uint32_t handle, const void *transfer, uint32_t priority,
    uint32_t callback, uint32_t context) {
    uint8_t *const h = (uint8_t *)(uintptr_t)handle;
    uint32_t descriptor = callback;
    uint32_t index = priority;
    uint32_t words = 0;
    if ((priority & 0xffu) == 0u) words = 3u;
    else if ((priority & 0xffu) == 1u) words = 8u;

    if (*(uint32_t *)(void *)(h + 32) == 0x100u) return 5u;
    const uint32_t queue = *(uint32_t *)(void *)(h + 0x828);
    uint32_t result = (uint32_t)g2_main_cq_reserve_538ece(
        queue, words, (uint32_t)(uintptr_t)&descriptor,
        (uint32_t)(uintptr_t)&index);
    if (result != 0) return result;
    result = display_driver_uled_mspi_descriptor_4bfa3c(
        handle, priority & 0xffu, descriptor, transfer);
    if (result != 0) {
        g2_main_cq_rollback_538f82(queue);
        return result;
    }
    const uint32_t slot = index & 0xffu;
    *(uint32_t *)(void *)(h + 0x28 + slot * 4u) = callback;
    *(uint32_t *)(void *)(h + 0x428 + slot * 4u) = context;
    return 0u;
}
