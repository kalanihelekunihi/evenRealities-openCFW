/* Cordio AttsSetAttr, stock 0x5353e8..0x535440. */
#include <stdint.h>

extern void WsfTaskLock(void);
extern void WsfTaskUnlock(void);
extern uint8_t *attsFindByHandle(uint16_t handle, void **group);
extern void *memcpy(void *destination, const void *source, unsigned length);

uint8_t AttsSetAttr(uint16_t handle, uint16_t value_length, uint8_t *value)
{
    void *group = 0;
    uint8_t error = 0u;
    WsfTaskLock();
    uint8_t *const attribute = attsFindByHandle(handle, &group);
    if (attribute == 0) {
        error = 0x0au;
    } else if (value_length > *(uint16_t *)(void *)(attribute + 0x0cu)) {
        error = 0x0du;
    } else {
        uint8_t *const destination =
            (uint8_t *)(uintptr_t)*(uint32_t *)(void *)(attribute + 4u);
        memcpy(destination, value, value_length);
        if ((attribute[0x0eu] & 0x08u) != 0u) {
            uint16_t *const length =
                (uint16_t *)(uintptr_t)*(uint32_t *)(void *)(attribute + 8u);
            *length = value_length;
        }
    }
    WsfTaskUnlock();
    return error;
}
