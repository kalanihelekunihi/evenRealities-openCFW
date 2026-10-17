/* Cordio attsProcessDatabaseHashUpdate, stock 0x534d46..0x534dd0. */
#include <stdint.h>

extern void WsfBufFree(void *);
extern void WStrReverse(uint8_t *, uint8_t);
extern uint16_t attsFindUuidInRange(uint16_t, uint16_t, uint8_t,
                                    const uint8_t *, void **, void **);
extern void AttsSetAttr(uint16_t, uint16_t, uint8_t *);
extern void attsCsfSetHashUpdateStatus(uint8_t);
extern uint8_t audio_ble_att_common_state[];

static const uint8_t audio_ble_att_gatt_db_hash_uuid[2] = {0x2au, 0x2bu};

void audio_ble_atts_database_hash_update_534d46(void *message)
{
    uint8_t *const msg = (uint8_t *)message;
    uint8_t event[24] = {0};
    event[2] = 0x15u;
    event[8] = 0x10u;
    void *const cipher = (void *)(uintptr_t)*(uint32_t *)(void *)(msg + 4u);
    *(uint32_t *)(void *)(event + 4u) = (uint32_t)(uintptr_t)cipher;
    void *plain = (void *)(uintptr_t)*(uint32_t *)(void *)(msg + 8u);
    if (plain != 0) {
        WsfBufFree(plain);
        *(uint32_t *)(void *)(msg + 8u) = 0u;
    }
    WStrReverse((uint8_t *)cipher, 0x10u);
    void *attribute = 0;
    void *group = 0;
    const uint16_t handle = attsFindUuidInRange(1u, 0xffffu, 2u,
                                                 audio_ble_att_gatt_db_hash_uuid,
                                                 &attribute, &group);
    if (handle != 0u)
        AttsSetAttr(handle, 0x10u, (uint8_t *)cipher);
    attsCsfSetHashUpdateStatus(0u);
    const uintptr_t callback = *(const uint32_t *)(const void *)
        (audio_ble_att_common_state + 0x58u);
    ((void (*)(void *))callback)(event);
}
