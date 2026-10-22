/* APP_BleHwErrorReset, stock
 * D:\01_workspace\s200_ap510b_iar_git\platform\ble\app_ble.c (module "ble.comm").
 * Stock range 0x4b8224..0x4b82d3 (literal pool entries 0x4b8488, 0x4b87c0..0x4b87db).
 *
 * Posts EVEN_HW_ERROR_IND_EVT (0xa6) to the BLE comm WSF handler, whose id is
 * the byte at +0x56 of the comm state (RAM 0x200727f0). Called from the
 * "AT+BLE" CLI command (system/x-02-cli-commands/prvCommand_ble_at.c). */
#include <stdint.h>

#define EVEN_HW_ERROR_IND_EVT 0xa6u

/* Cordio wsfMsgHdr_t. */
typedef struct {
    uint16_t param;  /* +0 */
    uint8_t event;   /* +2 */
    uint8_t status;  /* +3 */
} wsf_msg_hdr_t;

extern uint8_t audio_ble_comm_state[0x57];   /* RAM 0x200727f0, +0x56 WSF handler id */

extern void *WsfMsgAlloc(uint16_t len);       /* 0x4bf99e */
extern void WsfMsgSend(uint8_t handler_id, void *msg); /* 0x4bf9ba */
extern uint32_t audio_log_flags(void);        /* 0x43d0ce */
extern void elog_output(uint8_t level, const char *tag, const char *file, const char *func,
                        const long line, const char *format, ...); /* 0x43d574 */
extern uint32_t compressed_log_output(uint32_t code, const char *fmt, const char *text,
                                      ...);   /* 0x43ce9e */

static const char module_tag[] = "ble.comm"; /* ROM 0x789ff8 */
static const char source_file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\ble\\app_ble.c"; /* ROM 0x711d94 */
static const char function_name[] = "APP_BleHwErrorReset"; /* ROM 0x77d948 */
static const char sent_msg[] = "APP_BleHwErrorReset: EVEN_HW_ERROR_IND_EVT sent"; /* ROM 0x731094 */
static const char sent_short[] =
    "[ble.comm]APP_BleHwErrorReset: EVEN_HW_ERROR_IND_EVT sent"; /* ROM 0x711e84 */
static const char alloc_msg[] = "APP_BleHwErrorReset: Failed to allocate message"; /* ROM 0x7310c4 */
static const char alloc_short[] =
    "[ble.comm]APP_BleHwErrorReset: Failed to allocate message"; /* ROM 0x711ec0 */

/* Stock 0x004B8224 (APP_BleHwErrorReset) */
void app_ble_hw_error_reset_4b8224(void)
{
    wsf_msg_hdr_t *msg = (wsf_msg_hdr_t *)WsfMsgAlloc(12u);

    if (msg != 0) {
        msg->event = EVEN_HW_ERROR_IND_EVT;
        msg->param = 0u;
        msg->status = 0u;
        WsfMsgSend(audio_ble_comm_state[0x56u], msg);
        if ((audio_log_flags() & 2u) != 0u)
            elog_output(3u, module_tag, source_file, function_name, 0x3ae, sent_msg);
        if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
            (void)compressed_log_output(0x0c000000u, sent_short, sent_short);
    } else {
        if ((audio_log_flags() & 2u) != 0u)
            elog_output(1u, module_tag, source_file, function_name, 0x3b2, alloc_msg);
        if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
            (void)compressed_log_output(0x04000000u, alloc_short, alloc_short);
    }
}
