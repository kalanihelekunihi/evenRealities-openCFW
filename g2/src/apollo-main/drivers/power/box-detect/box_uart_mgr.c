/* Charging-case UART manager, stock
 * D:\01_workspace\s200_ap510b_iar_git\platform\device_mgr\box_uart_mgr.c.
 * Native 0x539e92..0x53a3a3; literal pool 0x53a3a4..0x53a413.
 *
 * The case talks to the glasses over product UART 2 (the pogo-pin link).
 * Received chunks of 3..1024 bytes are copied into a five-slot ring of
 * 1 KiB buffers and posted to the device manager; DEV_BoxRevcMsgProcess then
 * pauses the UART, unpacks the frame, runs it through the product-test
 * protocol, answers, restarts the UART and lets the production-mode
 * orchestrator act on the command.
 *
 * Frames: leading 0x00 bytes are skipped. A frame starting with 'T' is taken
 * verbatim (text command); otherwise its last byte must equal
 * (len + 0x7d + sum of the preceding bytes) & 0xff. */
#include <stddef.h>
#include <stdint.h>

#define BOX_UART            2u
#define BOX_RX_SLOTS        5u
#define BOX_RX_SLOT_SIZE    0x400u
#define BOX_RSP_SIZE        0x100u
#define BOX_MSG_RX          1u

/* Device-manager message (8 bytes); also the shape DEV_BoxRevcMsgProcess
 * receives back. */
typedef struct {
    uint16_t type;       /* +0 1 = box UART data */
    uint16_t length;     /* +2 */
    const uint8_t *data; /* +4 */
} g2_box_uart_msg_t;
_Static_assert(sizeof(g2_box_uart_msg_t) == 8, "device-manager message is 8 bytes");

extern uint8_t g2_box_uart_rx_slot;                                  /* RAM 0x20074f96 */
extern uint8_t g2_box_uart_rx_buffers[BOX_RX_SLOTS][BOX_RX_SLOT_SIZE]; /* RAM 0x2005ba68 */

extern uint32_t hal_uart_power_on_55e5bc(uint8_t uart);
extern uint32_t hal_uart_start_55e68e(uint8_t uart);
extern uint32_t hal_uart_stop_55e75a(uint8_t uart);
extern uint32_t hal_uart_send_55e7fa(uint8_t uart, const uint8_t *data, uint8_t len);
extern void hal_uart_rx_callback_set_55e8f0(uint8_t uart, void (*callback)(const uint8_t *, uint32_t));
extern uint32_t uart_channel_rx_flush_55e90c(uint8_t uart);
extern uint32_t hal_uart_tx_flush_55e956(uint8_t uart);
extern void audio_ble_device_manager_send(const uint8_t *message); /* Stock 0x4c659a DEV_SendMessage */
extern uint32_t pt_protocol_dispatch(const uint8_t *payload, uint8_t length, uint8_t *response,
                                     uint8_t *response_length);
extern uint32_t pt_production_mode_orchestrate(const uint8_t *payload, uint8_t length,
                                               uint8_t *response, uint8_t response_length);
extern int32_t osDelay(uint32_t ticks);
extern void *audio_queue_copy_bytes(void *dst, const void *src, uint32_t len); /* 0x439be4 memcpy */
extern void audio_uart_buffer_zero(void *dst, uint32_t len, uint32_t fill);  /* 0x43c0e4 */
extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */

static const char module_tag[] = "box_uart_mgr"; /* ROM 0x7856a0 */
static const char source_file[] = "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\device_mgr\\box_uart_mgr.c"; /* ROM 0x6f890c */
static const char fn_comm_read[] = "comm_read"; /* ROM 0x78a55c */
static const char fn_process[] = "DEV_BoxRevcMsgProcess"; /* ROM 0x77586c */
static const char s_msg_err[] = "box rcv msg err\n"; /* ROM 0x77e7e4 */
static const char c_msg_err[] = "[box_uart_mgr]box rcv msg err\n"; /* ROM 0x75e4d0 */
static const char s_crc[] = "crc check failed, data len = %d, tmp_crc: 0x%x, tmp_buf[idx + tmp_len - 1]: 0x%x"; /* ROM 0x6e661c */
static const char c_crc[] = "[box_uart_mgr]crc check failed, data len = %d, tmp_crc: 0x%x, tmp_buf[idx + tmp_len - 1]: 0x%x"; /* ROM 0x6dcb14 */
static const char s_stop[] = "uart stop failed: %d\n"; /* ROM 0x775884 */
static const char c_stop[] = "[box_uart_mgr]uart stop failed: %d\n"; /* ROM 0x75261c */
static const char s_clear[] = "uart clear buffer failed: %d\n"; /* ROM 0x75e4f0 */
static const char c_clear[] = "[box_uart_mgr]uart clear buffer failed: %d\n"; /* ROM 0x73c770 */
static const char s_unpack[] = "box uart unpack err:%d\n"; /* ROM 0x77589c */
static const char c_unpack[] = "[box_uart_mgr]box uart unpack err:%d\n"; /* ROM 0x747ef4 */
static const char s_pack[] = "box uart pack err:%d\n"; /* ROM 0x7758b4 */
static const char c_pack[] = "[box_uart_mgr]box uart pack err:%d\n"; /* ROM 0x752640 */
static const char s_send[] = "box uart send err:%d\n"; /* ROM 0x7758cc */
static const char c_send[] = "[box_uart_mgr]box uart send err:%d\n"; /* ROM 0x752664 */
static const char s_flush[] = "uart tx flush failed: %d\n"; /* ROM 0x769f04 */
static const char c_flush[] = "[box_uart_mgr]uart tx flush failed: %d\n"; /* ROM 0x747f1c */
static const char s_start[] = "uart start failed: %d\n"; /* ROM 0x7758e4 */
static const char c_start[] = "[box_uart_mgr]uart start failed: %d\n"; /* ROM 0x747f44 */
static const char s_pt[] = "pt cmd execute err:%d\n"; /* ROM 0x7758fc */
static const char c_pt[] = "[box_uart_mgr]pt cmd execute err:%d\n"; /* ROM 0x747f6c */

static const g2_box_uart_msg_t box_msg_template = {0u, 0u, NULL}; /* ROM 0x78d10c */

#define BOX_UART_ERR(fn, line, plain, compact, value)                                         \
    do {                                                                                      \
        if (audio_log_flags() & 2u)                                                           \
            audio_log_extended(1u, module_tag, source_file, (fn), (line), (plain), (value));  \
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))                             \
            (void)compress_log_output(0x04400000u, (compact), (compact), (value));            \
    } while (0)

/* Returns 0 (frame copied, or nothing but padding), -1 bad message, -3
 * checksum mismatch. */
int32_t comm_read_539e92(const g2_box_uart_msg_t *msg, uint8_t *out, uint8_t *out_len) {
    if (msg == NULL || msg->length == 0u) {
        if (audio_log_flags() & 2u)
            audio_log_extended(1u, module_tag, source_file, fn_comm_read, 0x1au, s_msg_err);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compress_log_output(0x04000000u, c_msg_err, c_msg_err);
        return -1;
    }
    const uint8_t *buf = msg->data;
    for (uint16_t idx = 0u; idx < msg->length; idx++) {
        if (buf[idx] == 0u)
            continue;
        uint16_t len = (uint16_t)(msg->length - idx);
        if (buf[idx] == 'T') {
            (void)audio_queue_copy_bytes(out, &buf[idx], len);
            *out_len = (uint8_t)len;
        } else {
            uint16_t crc = (uint16_t)(len + 0x7du);
            for (uint16_t i = 0u; (int32_t)i < (int32_t)len - 1; i++)
                crc = (uint16_t)(crc + buf[(uint16_t)(i + idx)]);
            if ((crc & 0xffu) != buf[(uint32_t)len + idx - 1u]) {
                if (audio_log_flags() & 2u)
                    audio_log_extended(1u, module_tag, source_file, fn_comm_read, 0x40u, s_crc,
                                       len, crc & 0xffu, buf[(uint32_t)len + idx - 1u]);
                if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
                    (void)compress_log_output(0x04c00000u, c_crc, c_crc, len, crc & 0xffu,
                                              buf[(uint32_t)idx + len - 1u]);
                return -3;
            }
            (void)audio_queue_copy_bytes(out, &buf[idx], len);
            *out_len = (uint8_t)len;
        }
        break;
    }
    return 0;
}

uint32_t box_uart_send_53a010(uint8_t uart, const uint8_t *data, uint8_t len) {
    return hal_uart_send_55e7fa(uart, data, len);
}

/* UART 2 receive callback (interrupt context). */
void box_uart_rx_callback_53a01c(const uint8_t *data, uint32_t len) {
    if (len - 3u >= BOX_RX_SLOT_SIZE - 2u)
        return;
    uint8_t slot = g2_box_uart_rx_slot;
    (void)audio_queue_copy_bytes(g2_box_uart_rx_buffers[slot], data, len);
    audio_uart_buffer_zero(&g2_box_uart_rx_buffers[slot][len], BOX_RX_SLOT_SIZE - len, 0u);
    g2_box_uart_rx_slot = (uint8_t)((int32_t)(g2_box_uart_rx_slot + 1u) % (int32_t)BOX_RX_SLOTS);
    g2_box_uart_msg_t msg = box_msg_template;
    msg.type = BOX_MSG_RX;
    msg.length = (uint16_t)len;
    msg.data = g2_box_uart_rx_buffers[slot];
    audio_ble_device_manager_send((const uint8_t *)&msg);
}

void box_uart_init_53a09c(void) {
    hal_uart_rx_callback_set_55e8f0(BOX_UART, box_uart_rx_callback_53a01c);
    (void)hal_uart_power_on_55e5bc(BOX_UART);
    (void)hal_uart_start_55e68e(BOX_UART);
}

/* The UART is stopped while the frame is handled and always restarted; the
 * production-mode step only runs when the restart succeeded. */
void DEV_BoxRevcMsgProcess_53a0b6(const g2_box_uart_msg_t *msg) {
    if (msg == NULL || msg->length == 0u) {
        if (audio_log_flags() & 2u)
            audio_log_extended(1u, module_tag, source_file, fn_process, 0x7cu, s_msg_err);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compress_log_output(0x04000000u, c_msg_err, c_msg_err);
        return;
    }
    uint8_t rx_len;
    uint8_t rsp_len;
    uint8_t rsp[BOX_RSP_SIZE];
    uint8_t rx[BOX_RX_SLOT_SIZE];
    uint32_t err;

    rsp_len = 0u;
    rx_len = 0u;
    audio_uart_buffer_zero(rx, sizeof(rx), 0u);
    audio_uart_buffer_zero(rsp, sizeof(rsp), 0u);
    err = hal_uart_stop_55e75a(BOX_UART);
    if (err == 0u) {
        uint32_t flush = uart_channel_rx_flush_55e90c(BOX_UART);
        if (flush != 0u)
            BOX_UART_ERR(fn_process, 0x92u, s_clear, c_clear, flush);
        int32_t read = comm_read_539e92(msg, rx, &rx_len);
        if (read == 0) {
            err = pt_protocol_dispatch(rx, rx_len, rsp, &rsp_len);
            if (err == 0u) {
                (void)osDelay(2u);
                err = box_uart_send_53a010(BOX_UART, rsp, rsp_len);
                if (err == 0u) {
                    err = hal_uart_tx_flush_55e956(BOX_UART);
                    if (err != 0u)
                        BOX_UART_ERR(fn_process, 0xb1u, s_flush, c_flush, err);
                } else {
                    BOX_UART_ERR(fn_process, 0xa9u, s_send, c_send, err);
                }
            } else {
                BOX_UART_ERR(fn_process, 0x9fu, s_pack, c_pack, err);
            }
        } else {
            BOX_UART_ERR(fn_process, 0x98u, s_unpack, c_unpack, read);
        }
    } else {
        BOX_UART_ERR(fn_process, 0x8au, s_stop, c_stop, err);
    }
    err = hal_uart_start_55e68e(BOX_UART);
    if (err != 0u)
        BOX_UART_ERR(fn_process, 0xbau, s_start, c_start, err);
    if (err == 0u) {
        err = pt_production_mode_orchestrate(rx, rx_len, rsp, rsp_len);
        if (err != 0u)
            BOX_UART_ERR(fn_process, 0xc3u, s_pt, c_pt, err);
    }
}
