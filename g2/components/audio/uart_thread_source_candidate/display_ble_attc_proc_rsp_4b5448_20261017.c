/* Cordio attcProcRsp at stock Main 0x4b5448. */
#include <stdint.h>

extern uint8_t audio_ble_att_common_state[];
extern uint8_t audio_ble_attc_state[];
extern void WsfTimerStop(void *);
extern void audio_ble_attc_free_pkt_531ac0(void *);
extern void audio_ble_attc_send_req_531144(void *);
extern void audio_ble_attc_setup_req_531160(void *, void *);

typedef struct {
    uint16_t param;
    uint8_t event;
    uint8_t status;
    const uint8_t *value;
    uint16_t value_length;
    uint16_t handle;
    uint8_t continuing;
} audio_attc_rsp_event_t;

typedef void (*audio_attc_rsp_handler_t)(uint8_t *, uint16_t,
                                         const uint8_t *, audio_attc_rsp_event_t *);
extern void audio_attc_rsp_error_4b5230(uint8_t *, uint16_t, const uint8_t *, audio_attc_rsp_event_t *);
extern void audio_attc_rsp_mtu_4b527a(uint8_t *, uint16_t, const uint8_t *, audio_attc_rsp_event_t *);
extern void audio_attc_rsp_find_read_4b52c2(uint8_t *, uint16_t, const uint8_t *, audio_attc_rsp_event_t *);
extern void audio_attc_rsp_find_type_56c3b0(uint8_t *, uint16_t, const uint8_t *, audio_attc_rsp_event_t *);
extern void audio_attc_rsp_read_4b53da(uint8_t *, uint16_t, const uint8_t *, audio_attc_rsp_event_t *);
extern void audio_attc_rsp_read_long_56c454(uint8_t *, uint16_t, const uint8_t *, audio_attc_rsp_event_t *);
extern void audio_attc_rsp_write_4b53dc(uint8_t *, uint16_t, const uint8_t *, audio_attc_rsp_event_t *);
extern void audio_attc_rsp_prepare_write_539dcc(uint8_t *, uint16_t, const uint8_t *, audio_attc_rsp_event_t *);
extern void audio_attc_rsp_read_multi_var_4b53e2(uint8_t *, uint16_t, const uint8_t *, audio_attc_rsp_event_t *);

static const audio_attc_rsp_handler_t handlers[18] = {
    audio_attc_rsp_error_4b5230, audio_attc_rsp_mtu_4b527a,
    audio_attc_rsp_find_read_4b52c2, audio_attc_rsp_find_type_56c3b0,
    audio_attc_rsp_find_read_4b52c2, audio_attc_rsp_read_4b53da,
    audio_attc_rsp_read_long_56c454, audio_attc_rsp_read_4b53da,
    audio_attc_rsp_find_read_4b52c2, audio_attc_rsp_write_4b53dc,
    0, audio_attc_rsp_prepare_write_539dcc, audio_attc_rsp_write_4b53dc,
    0, 0, 0, audio_attc_rsp_read_multi_var_4b53e2, 0,
};

/* Stock minimum-length bytes at 0x785270; 0x61 at index 16 is the
 * adjacent source string byte read by the native lookup. */
static const uint8_t min_length[18] = {
    5, 3, 2, 1, 2, 1, 1, 1, 2, 1, 3, 5, 1, 0, 0, 0, 0x61, 0x74,
};

static uint16_t read16(const uint8_t *data)
{
    return (uint16_t)data[0] | ((uint16_t)data[1] << 8);
}

void audio_ble_attc_proc_rsp_4b5448(uint8_t *ccb, uint16_t length,
                                     const uint8_t *packet)
{
    if (ccb[6u] == 0u)
        return;
    const uint8_t method = (uint8_t)((packet[8u] & (uint8_t)~1u) / 2u);
    if (method >= 18u || (method != 0u && method != ccb[6u]))
        return;

    WsfTimerStop(ccb + 0x18u);
    audio_attc_rsp_event_t event = {0};
    event.event = method;
    event.value = packet + 9u;
    event.value_length = (uint16_t)(length - 1u);
    event.handle = read16(ccb + 0x0cu);
    /* Stock index 17 resolves into adjacent constant bytes rather than a
     * valid handler. Short packets return; reject the malformed long case. */
    if (method == 17u)
        return;
    const audio_attc_rsp_handler_t handler = handlers[method];
    if (handler != 0) {
        if (length < min_length[method])
            return;
        handler(ccb, length, packet, &event);
    }
    if (ccb[7u] == 0u || event.status != 0u) {
        ccb[6u] = 0u;
        audio_ble_attc_free_pkt_531ac0(ccb + 4u);
    }
    if (method != 1u) {
        void (*callback)(const audio_attc_rsp_event_t *) =
            *(void (**)(const audio_attc_rsp_event_t *))(audio_ble_att_common_state + 0x58u);
        if (callback != 0) {
            event.continuing = ccb[7u];
            event.param = read16(ccb + 4u);
            callback(&event);
        }
    }
    uint8_t *main_ccb = *(uint8_t **)ccb;
    if ((main_ccb[(uint32_t)ccb[0x28u] * 4u + 2u] & 2u) != 0u)
        return;
    if (*(uint32_t *)(ccb + 8u) != 0u) {
        audio_ble_attc_send_req_531144(ccb);
    } else if (ccb[0x28u] == 0u) {
        uint8_t *on_deck = audio_ble_attc_state + 0x180u + (uint32_t)ccb[0x29u] * 12u;
        if (on_deck[2u] != 0u) {
            audio_ble_attc_setup_req_531160(ccb, on_deck);
            on_deck[2u] = 0u;
        }
    }
}
