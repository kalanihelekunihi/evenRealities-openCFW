/* Native BLE ring client entries 0x4c46c0, 0x4c46d0, 0x4c48ac,
 * and APP_BleRingProcMsg 0x4c4910. */
#include <stdint.h>
#include <stddef.h>

struct audio_ble_ring_handler_state {
    uint8_t active;
    uint8_t handler;
    uint16_t reserved;
    uint16_t *service_handles;
    uint16_t initialized;
};
_Static_assert(sizeof(struct audio_ble_ring_handler_state) == 12u,
               "ring state ABI");
_Static_assert(offsetof(struct audio_ble_ring_handler_state, initialized) == 8u,
               "ring epoch ABI");
extern struct audio_ble_ring_handler_state audio_ble_ring_handler_state;
extern uint8_t DmConnRole(uint8_t);
extern uint8_t DmConnInUse(uint8_t);
extern void audio_ble_attc_write_request(uint8_t, uint16_t, uint16_t,
                                         const uint8_t *);
extern uint32_t audio_ble_attc_write_command_539dea(uint8_t, uint16_t,
                                                     uint16_t, const uint8_t *);
extern void audio_event_loop_push_delayed(void (*)(uint32_t), uint32_t, uint32_t);
extern uint32_t audio_event_loop_remove_delayed(void (*)(uint32_t));
extern uint32_t Thread_SendEvtToRingTask(uint32_t);
extern void audio_uart_registry_child_4c548c(uint32_t, uint16_t);
extern void audio_ble_tx_complete_notify(void);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t, const char *, const char *,
                               const char *, uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);

static const char module[] = "ble.ring";
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\ble\\profiles\\ring\\profile_ring.c";
static const char enable_fn[] = "_ringEnableCccd";
static const char proc_fn[] = "APP_BleRingProcMsg";
static const char receive_fn[] = "_bleRingReceiveData";
static const char skipped[] = "_ringEnableCccd skipped: stale connId=%d epoch=%u cur=%d/%u";
static const char skipped_short[] =
    "[ble.ring]_ringEnableCccd skipped: stale connId=%d epoch=%u cur=%d/%u";
static const char enabling[] =
    "_ringEnableCccd: connId=%d, CCCD handle=0x%04X, value=0x0001 (NOTIFY), flag=%d";
static const char enabling_short[] =
    "[ble.ring]_ringEnableCccd: connId=%d, CCCD handle=0x%04X, value=0x0001 (NOTIFY), flag=%d";
static const char receive_text[] = "ring rx data:";
static const char receive_short[] = "[ble.ring]ring rx data:";
static const char cccd_text[] = "ringCb.pRingHdlList[RING_RX_CH_CCC_HDL_IDX] = 0x%04X";
static const char cccd_short[] =
    "[ble.ring]ringCb.pRingHdlList[RING_RX_CH_CCC_HDL_IDX] = 0x%04X";
static const char sending[] = "EVEN_RING_SEND";
static const char sending_short[] = "[ble.ring]EVEN_RING_SEND";
static const char dropped[] = "EVEN_RING_SEND dropped: sendId=%d, curId=%d, txHdl=0x%04X";
static const char dropped_short[] =
    "[ble.ring]EVEN_RING_SEND dropped: sendId=%d, curId=%d, txHdl=0x%04X";
static const char handle_text[] = "ringCb.pRingHdlList[%d] = 0x%04X";
static const char handle_short[] = "[ble.ring]ringCb.pRingHdlList[%d] = 0x%04X";

uint32_t audio_ble_ring_cccd_epoch_token(uint8_t connection, uint8_t final,
                                          uint16_t epoch)
{
    return ((uint32_t)epoch << 16) | ((uint32_t)final << 8) | connection;
}

void audio_ble_ring_cccd_enable(uint32_t token)
{
    struct audio_ble_ring_handler_state *state = &audio_ble_ring_handler_state;
    uint8_t connection = (uint8_t)token;
    uint16_t epoch = (uint16_t)(token >> 16);
    uint16_t handle = 0u;
    if (connection != 0u && connection == state->active &&
        epoch == state->initialized && DmConnInUse(connection) != 0u &&
        state->service_handles != 0)
        handle = state->service_handles[2];
    if (handle == 0u) {
        if ((audio_log_flags() & 2u) != 0u)
            audio_log_extended(2u, module, path, enable_fn, 0x76u, skipped,
                               connection, epoch, state->active,
                               state->initialized);
        if ((audio_log_flags() & 1u) != 0u ||
            (audio_log_flags() & 4u) != 0u)
            (void)compressed_log_output(0x09000000u, skipped_short,
                                        skipped_short, connection, epoch,
                                        state->active, state->initialized);
        return;
    }
    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(3u, module, path, enable_fn, 0x7eu, enabling,
                           connection, handle, (token >> 8) & 0xffu);
    if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
        (void)compressed_log_output(0x0cc00000u, enabling_short,
                                    enabling_short, connection, handle,
                                    (token >> 8) & 0xffu);
    uint16_t value = 1u;
    audio_ble_attc_write_request(connection, handle, 2u,
                                  (const uint8_t *)(const void *)&value);
    if (((token >> 8) & 0xffu) == 1u)
        (void)Thread_SendEvtToRingTask(4u);
}

void audio_ble_ring_receive_data_4c48ac(const uint8_t *message)
{
    struct audio_ble_ring_handler_state *state = &audio_ble_ring_handler_state;
    if (message[3] != 0u || state->service_handles == 0)
        return;
    uint16_t handle = (uint16_t)message[10] | ((uint16_t)message[11] << 8);
    if (handle != state->service_handles[1])
        return;
    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(3u, module, path, receive_fn, 0xccu, receive_text);
    if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
        (void)compressed_log_output(0x0c000000u, receive_short, receive_short);
    uint32_t data = (uint32_t)message[4] | ((uint32_t)message[5] << 8) |
                    ((uint32_t)message[6] << 16) | ((uint32_t)message[7] << 24);
    uint16_t length = (uint16_t)message[8] | ((uint16_t)message[9] << 8);
    audio_uart_registry_child_4c548c(data, length);
}

void audio_ble_master_message(uint8_t handler, void *raw)
{
    (void)handler;
    if (raw == 0)
        return;
    const uint8_t *message = (const uint8_t *)raw;
    struct audio_ble_ring_handler_state *state = &audio_ble_ring_handler_state;
    uint8_t connection = message[0];
    uint8_t event = message[2];
    if (event == 5u || event == 13u || event == 14u) {
        if (DmConnRole(state->active) == 0u)
            audio_ble_ring_receive_data_4c48ac(message);
    } else if (event == 0x27u) {
        if (DmConnRole(connection) != 0u)
            return;
        state->active = connection;
        state->initialized = (uint16_t)(state->initialized + 1u);
        uint16_t *handles = state->service_handles;
        handles[0] = 0x10u;
        handles[1] = 0x12u;
        handles[2] = 0x13u;
        if ((audio_log_flags() & 2u) != 0u)
            audio_log_extended(3u, module, path, proc_fn, 0x110u,
                               cccd_text, handles[2]);
        if ((audio_log_flags() & 1u) != 0u ||
            (audio_log_flags() & 4u) != 0u)
            (void)compressed_log_output(0x0c400000u, cccd_short,
                                        cccd_short, handles[2]);
        if (handles[2] != 0u) {
            (void)audio_event_loop_remove_delayed(audio_ble_ring_cccd_enable);
            uint32_t token = audio_ble_ring_cccd_epoch_token(
                state->active, 0u, state->initialized);
            audio_event_loop_push_delayed(audio_ble_ring_cccd_enable,
                                           token, 500u);
            audio_event_loop_push_delayed(audio_ble_ring_cccd_enable,
                                           token, 700u);
            token = audio_ble_ring_cccd_epoch_token(state->active, 1u,
                                                     state->initialized);
            audio_event_loop_push_delayed(audio_ble_ring_cccd_enable,
                                           token, 900u);
        }
    } else if (event == 0x28u) {
        if (DmConnRole(connection) != 0u)
            return;
        state->active = 0u;
        state->initialized = (uint16_t)(state->initialized + 1u);
        uint16_t *handles = state->service_handles;
        if (handles != 0) {
            handles[0] = 0u;
            handles[1] = 0u;
            handles[2] = 0u;
        }
        (void)audio_event_loop_remove_delayed(audio_ble_ring_cccd_enable);
        (void)Thread_SendEvtToRingTask(8u);
    } else if (event == 0xacu) {
        if ((audio_log_flags() & 2u) != 0u)
            audio_log_extended(4u, module, path, proc_fn, 0xe7u, sending);
        if ((audio_log_flags() & 1u) != 0u ||
            (audio_log_flags() & 4u) != 0u)
            (void)compressed_log_output(0x10000000u, sending_short,
                                        sending_short);
        uint16_t handle = state->service_handles != 0 ?
                          state->service_handles[0] : 0u;
        if (connection == 0u || connection != state->active || handle == 0u) {
            if ((audio_log_flags() & 2u) != 0u)
                audio_log_extended(2u, module, path, proc_fn, 0xf6u,
                                   dropped, connection, state->active, handle);
            if ((audio_log_flags() & 1u) != 0u ||
                (audio_log_flags() & 4u) != 0u)
                (void)compressed_log_output(0x08c00000u, dropped_short,
                                            dropped_short, connection,
                                            state->active, handle);
            audio_ble_tx_complete_notify();
        } else {
            if ((audio_log_flags() & 2u) != 0u)
                audio_log_extended(4u, module, path, proc_fn, 0xfau,
                                   handle_text, 0u, handle);
            if ((audio_log_flags() & 1u) != 0u ||
                (audio_log_flags() & 4u) != 0u)
                (void)compressed_log_output(0x10800000u, handle_short,
                                            handle_short, 0u, handle);
            uint32_t data = (uint32_t)message[4] | ((uint32_t)message[5] << 8) |
                            ((uint32_t)message[6] << 16) |
                            ((uint32_t)message[7] << 24);
            uint16_t length = (uint16_t)message[8] |
                              ((uint16_t)message[9] << 8);
            (void)audio_ble_attc_write_command_539dea(connection, handle,
                                                        length,
                                                        (const uint8_t *)(uintptr_t)data);
        }
    }
}
