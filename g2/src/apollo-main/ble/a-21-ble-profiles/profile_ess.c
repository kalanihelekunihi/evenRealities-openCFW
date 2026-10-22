/* ESS (echo/self-test GATT service) profile, stock
 * D:\01_workspace\s200_ap510b_iar_git\platform\ble\profiles\ess\profile_ess.c.
 * Native 0x4be2b4..0x4be2d6 (essWriteCallback) and 0x4be2f6..0x4be384
 * (APP_BleEssSendDataMsg); inline string "ESS" at 0x4be388, literal pool
 * 0x4be38c..0x4be3a4. The other ESS entries live in ble/ble-profile and
 * ble/ble-slave.
 *
 * A write is hex-dumped and echoed straight back as a notification. Every
 * path that does not post a message signals tx-complete so the BLE msgtx
 * thread is not left waiting. */
#include <stdint.h>
#include <stddef.h>

typedef struct {
    uint16_t param;      /* +0 connId */
    uint8_t event;       /* +2 0xa9 ESS send */
    uint8_t status;      /* +3 */
    const uint8_t *data; /* +4 */
    uint16_t length;     /* +8 */
} g2_profile_send_msg_t;
_Static_assert(sizeof(g2_profile_send_msg_t) == 12u, "WsfMsgAlloc(12)");

extern uint8_t audio_ble_ess_handler_state[4]; /* RAM 0x200748a8 essCb */

extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */
extern void audio_dump_hex(const char *label, uint32_t width, const uint8_t *data, uint32_t length); /* 0x43dacc elog hexdump */
extern uint8_t profile_get_conn_state_byte(void); /* 0x46efd8 */
extern uint32_t semantic_OtaTransferActive(void); /* 0x4487ac */
extern void thread_ble_wsf_tx_complete_notify(void); /* 0x4d0c36 */
extern void *WsfMsgAlloc(uint16_t length); /* 0x4bf99e */
extern void WsfMsgSend(uint8_t handler, void *message); /* 0x4bf9ba */

static const char dump_label[] = "ESS"; /* ROM 0x4be388 */
static const char module_tag[] = "profile.ess"; /* ROM 0x78b7f8 */
static const char source_file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\ble\\profiles\\ess\\profile_ess.c"; /* ROM 0x6f5444 */
static const char send_fn[] = "APP_BleEssSendDataMsg"; /* ROM 0x77a7a4 */
static const char alloc_fail[] = "APP_BleEssSendDataMsg WsfMsgAlloc failed"; /* ROM 0x741998 */
static const char alloc_fail_short[] = "[profile.ess]APP_BleEssSendDataMsg WsfMsgAlloc failed"; /* ROM 0x721710 */

uint32_t APP_BleEssSendDataMsg(const uint8_t *data, uint16_t length);

uint8_t essWriteCallback(uint8_t conn_id, uint16_t handle, uint8_t operation,
                         uint16_t offset, uint16_t length, uint8_t *value, void *attr)
{
    (void)conn_id; (void)handle; (void)operation; (void)offset; (void)attr;
    audio_dump_hex(dump_label, 16u, value, length);
    (void)APP_BleEssSendDataMsg(value, length);
    return 0u;
}

uint32_t APP_BleEssSendDataMsg(const uint8_t *data, uint16_t length)
{
    uint8_t *cb = audio_ble_ess_handler_state;
    (void)profile_get_conn_state_byte(); /* result unused in stock */
    if (semantic_OtaTransferActive() != 0u) {
        thread_ble_wsf_tx_complete_notify();
        return 0u;
    }
    if (cb[0] == 0u || cb[2] != 1u) {
        thread_ble_wsf_tx_complete_notify();
        return 0u;
    }
    g2_profile_send_msg_t *msg = (g2_profile_send_msg_t *)WsfMsgAlloc(12u);
    if (msg == NULL) {
        if ((audio_log_flags() & 2u) != 0u)
            audio_log_extended(1u, module_tag, source_file, send_fn, 0xe2u, alloc_fail);
        if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
            (void)compress_log_output(0x04000000u, alloc_fail_short, alloc_fail_short);
        thread_ble_wsf_tx_complete_notify();
        return 0u;
    }
    msg->event = 0xa9u;
    msg->param = cb[0];
    msg->data = data;
    msg->length = length;
    WsfMsgSend(cb[1], msg);
    return 0u;
}
