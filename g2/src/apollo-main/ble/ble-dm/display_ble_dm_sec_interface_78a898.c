/* Native Cordio dmSecFcnIf at ROM 0x78a898 and dmSecMsgHandler 0x4d2440. */
#include <stdint.h>

extern void audio_ble_dm_dispatch_4d2544(void *);
extern void audio_ble_dm_dispatch_4d2364(void *);
extern uint8_t *dmConnCcbById(uint8_t);
extern void DmConnSetIdle(uint8_t, uint16_t, uint8_t);
extern void HciLeStartEncryptionCmd(uint16_t, const uint8_t *, uint16_t, const uint8_t *);
extern void HciLeLtkReqReplCmd(uint16_t, const uint8_t *);
extern void HciLeLtkReqNegReplCmd(uint16_t);

void audio_ble_dm_sec_msg_handler_4d2440(void *message_ptr)
{
    uint8_t *const message = (uint8_t *)message_ptr;
    uint8_t *const ccb = dmConnCcbById(message[0u]);
    if (ccb == 0) return;
    const uint16_t handle = *(const uint16_t *)(const void *)(ccb + 0x0cu);
    if (message[2u] == 0x28u) {
        DmConnSetIdle(ccb[0x10u], 2u, 1u);
        ccb[0x18u] = message[0x1eu];
        ccb[0x12u] = 1u;
        HciLeStartEncryptionCmd(handle, message + 0x14u,
                                *(const uint16_t *)(const void *)(message + 0x1cu),
                                message + 4u);
    } else if (message[2u] == 0x29u) {
        if (message[0x14u] != 0u) {
            ccb[0x18u] = message[0x15u];
            HciLeLtkReqReplCmd(handle, message + 4u);
        } else {
            DmConnSetIdle(ccb[0x10u], 2u, 0u);
            HciLeLtkReqNegReplCmd(handle);
        }
    }
}

typedef void (*audio_ble_dm_security_fn)(void *);
_Static_assert(sizeof(audio_ble_dm_security_fn) == 4u, "Thumb pointer ABI");
const audio_ble_dm_security_fn audio_ble_dm_security_table[3]
    __attribute__((used, aligned(4))) = {
        audio_ble_dm_dispatch_4d2544,
        audio_ble_dm_dispatch_4d2364,
        audio_ble_dm_sec_msg_handler_4d2440,
    };
