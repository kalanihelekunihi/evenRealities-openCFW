/* BLE peripheral (slave) application helpers, stock
 * D:\01_workspace\s200_ap510b_iar_git\platform\ble\app_ble_peripheral.c
 * (module tag "ble.Slave"). Native 0x46ed08..0x46ed5a, 0x46eeec..0x46ef56,
 * 0x46efe4..0x46efec, 0x46f0ec..0x46f1c2, 0x46f2c6..0x46f328; literal pool
 * 0x46f3c0..0x46f4a3 (shared with the rest of the object).
 *
 * The slave state lives behind two pointer cells bound by APP_SlaveHanderInit:
 *   profile context (0x2007432c): +0x54 connection id, +0x56 WSF handler id
 *   slave context   (0x20074330): +0x1f cmdPipe (LEFT = 2 | RIGHT = 1),
 *                                 +0x20 trusted-device flag,
 *                                 +0x22 negotiated ATT MTU (u16)
 * Application events are 12-byte WSF messages: +0 u16 param (conn id or 0xff),
 * +2 event, +8 u16 status. */
#include <stdint.h>
#include <stddef.h>

extern uint8_t *audio_ble_profile_connection_context; /* RAM pointer cell 0x2007432c */
extern uint8_t *audio_ble_slave_mode_context;         /* RAM pointer cell 0x20074330 */
extern uint8_t audio_ble_adv_name_buffer[];           /* RAM 0x200003ec, advertised name */
extern uint8_t audio_ble_slave_unpair_flag_20074f8b;  /* RAM 0x20074f8b, _g_unpairGlassesFlag */
extern uint8_t audio_ble_slave_link_flags_20074f8c;   /* RAM 0x20074f8c, keep-connect flags */

extern void *WsfMsgAlloc(uint16_t length);                /* 0x4bf99e */
extern void WsfMsgSend(uint8_t handler, void *message);   /* 0x4bf9ba */
extern uint8_t audio_uart_device_role_get(void);          /* 0x45a568 */
extern uint32_t audio_log_flags(void);                    /* 0x43d0ce */
extern void audio_log_extended(uint8_t level, const char *module, const char *file,
                               const char *function, uint32_t line,
                               const char *format, ...);  /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t mask, const char *format,
                                    const char *copy, ...); /* 0x43ce9e */

#define EVEN_SLAVE_DISCONNECT_EVT 0xadu
#define EVEN_SLAVE_ADV_STOP_EVT 0xb7u

static const char module[] = "ble.Slave"; /* ROM 0x78a070 */
static const char file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\ble\\app_ble_peripheral.c"; /* ROM 0x6f809c */

static const char fn_name_get[] = "APP_BleNameGet";                 /* ROM 0x784e40 */
static const char adv_name[] = "adv name = %s";                     /* ROM 0x784e50 */
static const char adv_name_s[] = "[ble.Slave]adv name = %s";        /* ROM 0x769104 */
static const char fn_adv_stop[] = "APP_BleSlaveAdvStopEvent";       /* ROM 0x76913c */
static const char adv_stop[] = "EVEN_SLAVE_ADV_STOP_EVT sent";      /* ROM 0x75dbf0 */
static const char adv_stop_s[] = "[ble.Slave]EVEN_SLAVE_ADV_STOP_EVT sent"; /* ROM 0x74751c */
static const char fn_disconnect[] = "APP_BleSlaveDisconnect";       /* ROM 0x774f24 */
static const char disconnect[] = "pMsg->hdr.event = EVEN_SLAVE_DISCONNECT_EVT"; /* ROM 0x73bf5c */
static const char disconnect_s[] =
    "[ble.Slave]pMsg->hdr.event = EVEN_SLAVE_DISCONNECT_EVT";      /* ROM 0x71bdd0 */
static const char fn_cmd_role[] = "APP_BleSlaveAsCmdRole";          /* ROM 0x774f3c */
static const char cmd_pipe_fmt[] = "pEvenSlaveConnInfo->cmdPipe = %d(%d)"; /* ROM 0x747544 */
static const char cmd_pipe_s[] = "[ble.Slave]pEvenSlaveConnInfo->cmdPipe = %d(%d)"; /* ROM 0x731544 */
static const char fn_keep[] = "APP_BleSlaveSetKeepConnectFlag";     /* ROM 0x75dc30 */
static const char keep[] = "APP_BleSlaveSetKeepConnectFlag %d";     /* ROM 0x751c44 */
static const char keep_s[] = "[ble.Slave]APP_BleSlaveSetKeepConnectFlag %d"; /* ROM 0x731574 */

#define SLAVE_LOG(level, mask, function, line, format, simple, ...)             \
    do {                                                                        \
        if (audio_log_flags() & 2u)                                             \
            audio_log_extended((level), module, file, (function), (line),       \
                               (format), ##__VA_ARGS__);                        \
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))               \
            (void)compress_log_output((mask), (simple), (simple),               \
                                      ##__VA_ARGS__);                           \
    } while (0)

const char *APP_BleNameGet(void);
void APP_BleSlaveAdvStopEvent(void);
void ble_ota_mode_set(uint8_t value);
void APP_BleSlaveDisconnect(void);
void APP_BleSlaveAsCmdRole(uint8_t cmd_pipe);
uint16_t slave_cmd_pipe_get_0046f2c6(void);
void slave_adv_stop_flag_or_0046f2dc(uint8_t flag);

/* WSF message words are naturally aligned (strh in stock). */
static void put_u16(uint8_t *p, uint16_t value)
{
    *(uint16_t *)(void *)p = value;
}

/* 0x46ed08 */
const char *APP_BleNameGet(void)
{
    SLAVE_LOG(4u, 0x10400000u, fn_name_get, 0x254u, adv_name, adv_name_s,
              audio_ble_adv_name_buffer);
    return (const char *)audio_ble_adv_name_buffer;
}

/* 0x46eeec: post EVEN_SLAVE_ADV_STOP_EVT (param 0xff) to the slave handler. */
void APP_BleSlaveAdvStopEvent(void)
{
    uint8_t *msg = (uint8_t *)WsfMsgAlloc(12u);

    if (msg == NULL)
        return;
    msg[2] = EVEN_SLAVE_ADV_STOP_EVT;
    put_u16(msg, 0xffu);
    WsfMsgSend(audio_ble_profile_connection_context[0x56u], msg);
    SLAVE_LOG(3u, 0x0c000000u, fn_adv_stop, 0x297u, adv_stop, adv_stop_s);
}

/* 0x46efe4: stores the shared 0x20074f8b byte, which _bleSlaveProcMsg reads
 * as _g_unpairGlassesFlag on disconnect (TSV name kept). */
void ble_ota_mode_set(uint8_t value)
{
    audio_ble_slave_unpair_flag_20074f8b = value;
}

/* 0x46f0ec: post EVEN_SLAVE_DISCONNECT_EVT for the active connection. */
void APP_BleSlaveDisconnect(void)
{
    uint8_t *msg = (uint8_t *)WsfMsgAlloc(12u);

    if (msg == NULL)
        return;
    SLAVE_LOG(4u, 0x10000000u, fn_disconnect, 0x304u, disconnect, disconnect_s);
    msg[2] = EVEN_SLAVE_DISCONNECT_EVT;
    put_u16(msg, audio_ble_profile_connection_context[0x54u]);
    put_u16(msg + 8, 0u);
    WsfMsgSend(audio_ble_profile_connection_context[0x56u], msg);
}

/* 0x46f164 */
void APP_BleSlaveAsCmdRole(uint8_t cmd_pipe)
{
    audio_ble_slave_mode_context[0x1fu] = cmd_pipe;
    SLAVE_LOG(4u, 0x10800000u, fn_cmd_role, 0x30fu, cmd_pipe_fmt, cmd_pipe_s,
              audio_ble_slave_mode_context[0x1fu], audio_uart_device_role_get());
}

/* 0x46f2c6: slave context +0x22, the negotiated ATT MTU stored by
 * _bleSlaveProcMsg on ATT_MTU_UPDATE_IND (TSV name kept). */
uint16_t slave_cmd_pipe_get_0046f2c6(void)
{
    return *(const uint16_t *)(const void *)(audio_ble_slave_mode_context + 0x22u);
}

/* 0x46f2dc: stock APP_BleSlaveSetKeepConnectFlag; ORs into 0x20074f8c and
 * logs the resulting value. */
void slave_adv_stop_flag_or_0046f2dc(uint8_t flag)
{
    audio_ble_slave_link_flags_20074f8c |= flag;
    SLAVE_LOG(4u, 0x10400000u, fn_keep, 0x327u, keep, keep_s,
              audio_ble_slave_link_flags_20074f8c);
}
