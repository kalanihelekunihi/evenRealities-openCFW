/* Native Cordio dmSecHciHandler 0x4d2364, with dm_sec.c control flow. */
#include <stdint.h>

extern uint8_t *audio_ble_dm_conn_ccb_by_handle_4b601c(uint16_t);
extern int32_t g2_lfs_memcmp(const void *, const void *, uint32_t);
extern uint8_t *audio_ble_smp_get_stk_537c4c(uint8_t, uint8_t *);
extern uint8_t audio_ble_smp_lesc_enabled_537c30(uint8_t);
extern void HciLeLtkReqReplCmd(uint16_t, const uint8_t *);
extern void HciLeLtkReqNegReplCmd(uint16_t);
extern void DmConnSetIdle(uint8_t, uint16_t, uint8_t);
extern void DmSmpCbackExec(void *);
extern void audio_ble_smp_encrypt_ind_537be6(void *);
extern uint8_t audio_ble_dm_handler_state[];

void audio_ble_dm_dispatch_4d2364(void *event_ptr)
{
    uint8_t *const event = (uint8_t *)event_ptr;
    const uint16_t handle = *(const uint16_t *)(const void *)event;
    uint8_t *const ccb = audio_ble_dm_conn_ccb_by_handle_4b601c(handle);
    if (ccb == 0) return;

    if (event[2u] == 0x10u) {
        static const uint8_t zero_rand[8] = {0};
        const uint16_t ediv = *(const uint16_t *)(const void *)(event + 0x0eu);
        if (ediv == 0u && g2_lfs_memcmp(event + 6u, zero_rand, 8u) == 0) {
            uint8_t level = 0u;
            const uint8_t *const key = audio_ble_smp_get_stk_537c4c(ccb[0x10u], &level);
            if (key != 0) {
                ccb[0x18u] = level;
                ccb[0x12u] = 0u;
                HciLeLtkReqReplCmd(handle, key);
                return;
            }
        } else if (audio_ble_smp_lesc_enabled_537c30(ccb[0x10u]) == 1u) {
            HciLeLtkReqNegReplCmd(handle);
            return;
        }
        DmConnSetIdle(ccb[0x10u], 2u, 1u);
        ccb[0x12u] = 1u;
        *(uint16_t *)(void *)event = ccb[0x10u];
        event[2u] = 0x30u;
        void (*callback)(void *) = *(void (**)(void *))(audio_ble_dm_handler_state + 8u);
        callback(event);
        return;
    }

    if (event[2u] == 0x0eu || event[2u] == 0x0fu) {
        DmConnSetIdle(ccb[0x10u], 2u, 0u);
        uint8_t indication[8] = {0};
        *(uint16_t *)(void *)indication = ccb[0x10u];
        indication[3u] = event[3u];
        if (indication[3u] == 0u) {
            indication[2u] = 0x2cu;
            ccb[0x17u] = ccb[0x18u];
            indication[4u] = ccb[0x12u];
        } else {
            indication[2u] = 0x2du;
        }
        DmSmpCbackExec(indication);
        audio_ble_smp_encrypt_ind_537be6(indication);
    }
}
