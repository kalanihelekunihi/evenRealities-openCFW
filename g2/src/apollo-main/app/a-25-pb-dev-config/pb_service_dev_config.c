/* Device-config protobuf service, stock
 * D:\01_workspace\s200_ap510b_iar_git\platform\protocols\pb_service_dev_config\pb_service_dev_config.c.
 * Native 0x4d83d8..0x4d8eaa (APP_PbRxDevCfgFrameDataProcess, APP_PbRxErrorCode,
 * APP_PbTxEncodeErrorCode), literal pools 0x4d8b7c..0x4d8bdc, 0x4d8da0..0x4d8db4,
 * 0x4d8eac..0x4d8f48.
 *
 * Phone frames for BLE service 0x80 decode with the nanopb descriptor at ROM
 * 0x7766dc (shared with pb_service_pair_mgr.c and pb_service_dev_setting.c)
 * into a 0xd0-byte stack message. Every handled command calls its PB_Rx*
 * handler with the request's magic_random and the payload at +8, and on 0
 * answers through the matching PB_TxEncode* with the 256-byte packet at RAM
 * 0x2037c3a0 and the 0xd0-byte tx message at RAM 0x200f57b4. Unknown
 * commands are answered with a COMMAND_EXCEPTION (10) carrying
 * eErrorCode_NOT_SUPPORT (8). */
#include <stdint.h>
#include <stddef.h>

/* Top-level dev-config message header; the payload union starts at +8. */
typedef struct {
    uint8_t command_id;     /* +0 eDevCfgCommandId */
    uint8_t reserved1;
    uint16_t magic_random;  /* +2 */
    uint16_t which_payload; /* +4 oneof tag */
    uint16_t reserved6;
    uint8_t payload[0xc8];  /* +8 */
} g2_devcfg_msg_t;
_Static_assert(sizeof(g2_devcfg_msg_t) == 0xd0u, "dev-config message");

/* COMMAND_EXCEPTION payload (oneof tag 9). */
typedef struct {
    uint8_t command;    /* +0 command the error refers to */
    uint8_t error_code; /* +1 eErrorCode */
} g2_devcfg_error_code_t;

/* nanopb 0.4 pb_istream_t / pb_ostream_t. */
typedef struct {
    void *callback;
    void *state;
    uint32_t bytes_left;
    const char *errmsg;
} g2_pb_istream_t;
typedef struct {
    void *callback;
    void *state;
    uint32_t max_size;
    uint32_t bytes_written;
    const char *errmsg;
} g2_pb_ostream_t;
_Static_assert(sizeof(g2_pb_istream_t) == 16u, "nanopb istream");
_Static_assert(sizeof(g2_pb_ostream_t) == 20u, "nanopb ostream");

/* APP_errorFaultHandler record; the ROM template carries code 0, the caller sets 1. */
typedef struct {
    uint32_t type;        /* +0x00 */
    uint16_t code;        /* +0x04 */
    uint16_t reserved;
    const char *path;     /* +0x08 */
    const char *function; /* +0x0c */
    uint32_t line;        /* +0x10 */
} g2_fault_record_t;
_Static_assert(sizeof(g2_fault_record_t) == 20u, "fault record");

enum {
    DEVCFG_CMD_AUTHENTICATION = 4u,
    DEVCFG_CMD_PIPE_ROLE_CHANGE = 5u,
    DEVCFG_CMD_RING_CONNECT_INFO = 6u,
    DEVCFG_CMD_BLE_CONNECT_PARAM = 7u,
    DEVCFG_CMD_DISCONNECT_INFO = 8u,
    DEVCFG_CMD_UNPAIR_INFO = 9u,
    DEVCFG_CMD_COMMAND_EXCEPTION = 10u,
    DEVCFG_CMD_SET_DEVICE_INFO = 11u,
    DEVCFG_CMD_GET_DEVICE_INFO = 12u,
    DEVCFG_CMD_RESTORE_TO_FACTORY_SETTINGS = 13u,
    DEVCFG_CMD_BASE_CONNECT_HEART_BEAT = 14u,
    DEVCFG_CMD_QUICK_RESTART = 15u,
    DEVCFG_CMD_TIME_SYNC = 0x80u,
    DEVCFG_CMD_AUD_CONTROL = 0x81u,
};
enum {
    DEVCFG_ERR_CRC = 1u,
    DEVCFG_ERR_PB_ERROR = 5u,
    DEVCFG_ERR_FAIL = 7u,
    DEVCFG_ERR_NOT_SUPPORT = 8u,
    DEVCFG_ERR_SUPPORT = 9u,
};
#define DEVCFG_TAG_ERROR_CODE 9u
#define DEVCFG_SERVICE_ID     0x80u
#define DEVCFG_TX_BUFFER_SIZE 256u
#define DEVCFG_HEARTBEAT_TIMEOUT_MS 30000u

extern uint8_t g2_devcfg_tx_buffer_2037c3a0[DEVCFG_TX_BUFFER_SIZE]; /* RAM 0x2037c3a0 */
extern g2_devcfg_msg_t g2_devcfg_tx_msg_200f57b4;                    /* RAM 0x200f57b4 */
extern const uint8_t audio_ble_ring_connect_pb_descriptor[];         /* ROM 0x7766dc pb_msgdesc_t */

extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */
extern void audio_uart_buffer_zero(void *dst, uint32_t len, uint32_t fill);                /* 0x43c0e4 */
extern void audio_uart_lv_memzero_48949c(void *dst, uint32_t len);                          /* 0x48949c */
extern void *audio_uart_display_area_copy_439c04(void *dst, const void *src, uint32_t len); /* word copy */
extern void audio_uart_pb_stream_init(g2_pb_istream_t *out, const void *buf, uint32_t size); /* pb_istream_from_buffer 0x48f49c */
extern uint32_t audio_uart_pb_decode(void *stream, const void *fields, void *dest);          /* pb_decode 0x490120 */
extern void audio_pb_ostream_from_buffer(g2_pb_ostream_t *out, void *buf, uint32_t size);   /* 0x4905f4 */
extern uint32_t audio_pb_encode(void *stream, const void *fields, const void *src);          /* pb_encode 0x490c32 */
extern void APP_errorFaultHandler(const g2_fault_record_t *record);                          /* 0x509b48 */
extern uint32_t Thread_MsgPbTxByBle(uint8_t type, uint8_t command, const void *payload, uint16_t length); /* 0x475b14 */
extern uint32_t fw_event_loop_remove_delayed(void (*callback)(void));                        /* 0x476ace */
extern void fw_event_loop_push_delayed(void (*callback)(void), uint32_t argument, uint32_t delay_ms); /* 0x47697e */
extern void audio_ble_comm_link_delayed(void); /* APP_BleConnectTimeoutCheckEvt 0x4b81b8 */

/* Pair manager (pb_service_pair_mgr.c) and dev-setting handlers. */
extern uint32_t PB_RxSecAuth(uint8_t magic, const void *payload);              /* 0x4bb3dc */
extern uint32_t PB_TxEncodeSecAuth(uint8_t magic, uint8_t *buffer, uint16_t size, void *msg, const void *payload); /* 0x4bb576 */
extern uint32_t PB_RxPipeRoleChange(uint8_t magic, const void *payload);       /* 0x4bb9c4 */
extern uint32_t PB_TxEncodePipeRoleChange(uint8_t magic, uint8_t *buffer, uint16_t size, void *msg, const void *payload); /* 0x4bbaa0 */
extern uint32_t PB_RxRingConnectInfo(uint8_t magic, const void *payload);      /* 0x4bbf38 */
extern uint32_t PB_TxEncodeRingConnectInfo(uint8_t magic, uint8_t *buffer, uint16_t size, void *msg, const void *payload); /* 0x4bbfbc */
extern uint32_t PB_RxBleConnectParams(uint8_t magic, const void *payload);     /* 0x4bc4bc */
extern uint32_t PB_TxEncodeBleConnectParams(uint8_t magic, uint8_t *buffer, uint16_t size, void *msg, const void *payload); /* 0x4bc5c8 */
extern uint32_t PB_RxDisconnectInfo(uint8_t magic, const void *payload);       /* 0x4bc7d4 */
extern uint32_t PB_TxEncodeDisconnectInfo(uint8_t magic, uint8_t *buffer, uint16_t size, void *msg, const void *payload); /* 0x4bc93c */
extern uint32_t PB_RxUnpairInfo(uint8_t magic, const void *payload);           /* 0x4bcb28 */
extern uint32_t PB_TxEncodeUnpairInfo(uint8_t magic, uint8_t *buffer, uint16_t size, void *msg, const void *payload); /* 0x4bcdfc */
extern uint32_t PB_RxRestoreFactory(uint8_t magic, const void *payload);       /* 0x542dc4 */
extern uint32_t PB_TxEncodeRestoreFactory(uint8_t magic, uint8_t *buffer, uint16_t size, void *msg, const void *payload); /* 0x542f38 */
extern uint32_t PB_RxQuickRestart(uint8_t magic, const void *payload);         /* 0x5430fc */
extern uint32_t PB_TxEncodeQuickRestart(uint8_t magic, uint8_t *buffer, uint16_t size, void *msg, const void *payload); /* 0x5431b4 */
extern uint32_t PB_RxBaseConnHeartBeat(uint8_t magic, const void *payload);    /* 0x543378 */
extern uint32_t PB_TxEncodeBaseConnHeartBeat(uint8_t magic, uint8_t *buffer, uint16_t size, void *msg, const void *payload); /* 0x543426 */
extern uint32_t PB_RxTimeSyncInfo(uint8_t magic, const void *payload);         /* 0x5435de */
extern uint32_t PB_TxEncodeTimeSyncInfo(uint8_t magic, uint8_t *buffer, uint16_t size, void *msg, const void *payload); /* 0x5436f0 */
extern uint32_t PB_RxAudControl(uint8_t magic, const void *payload);           /* 0x543918 */
extern uint32_t PB_TxEncodeAudControl(uint8_t magic, uint8_t *buffer, uint16_t size, void *msg, const void *payload); /* 0x5439e4 */

static const char module_tag[] = "pb.ser"; /* ROM 0x78de8c */
static const char source_file[] = "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\protocols\\pb_service_dev_config\\pb_service_dev_config.c"; /* ROM 0x6d9494 */
static const char fn_frame[] = "APP_PbRxDevCfgFrameDataProcess"; /* ROM 0x762fb0 */
static const char fn_rx_error[] = "APP_PbRxErrorCode";           /* ROM 0x781958 */
static const char fn_tx_error[] = "APP_PbTxEncodeErrorCode";     /* ROM 0x77a054 */
static const char none_text[] = "(none)";                        /* ROM 0x78de94 */

/* ROM 0x78196c: NULL-frame fault template (line 0x2d). */
static const g2_fault_record_t fault_frame_null = {0u, 0u, 0u, source_file, fn_frame, 0x2du};

#define DEVCFG_LOG(level, fn, line, mask, fmt, ...) do { \
    if (audio_log_flags() & 2u) \
        audio_log_extended((level), module_tag, source_file, (fn), (line), fmt, ##__VA_ARGS__); \
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u)) \
        (void)compress_log_output((mask), "[pb.ser]" fmt, "[pb.ser]" fmt, ##__VA_ARGS__); \
} while (0)

uint32_t APP_PbRxErrorCode(uint8_t magic, const g2_devcfg_error_code_t *error);
uint32_t APP_PbTxEncodeErrorCode(uint32_t type, uint32_t command, uint8_t magic, uint8_t error_command,
                                 uint8_t error_code);

/* Returns 0 handled (whatever the handler returned), 2 NULL frame, 0x2b decode failure. */
uint32_t APP_PbRxDevCfgFrameDataProcess(const uint8_t *data, uint16_t length)
{
    DEVCFG_LOG(4u, fn_frame, 0x2cu, 0x10400000u, "4 len=%d:", length);
    if (data == NULL) {
        g2_fault_record_t fault;
        (void)audio_uart_display_area_copy_439c04(&fault, &fault_frame_null, sizeof fault);
        fault.code = 1u;
        APP_errorFaultHandler(&fault);
    }
    if (data == NULL) {
        DEVCFG_LOG(1u, fn_frame, 0x2fu, 0x04000000u, "PORINT NULL");
        return 2u;
    }

    g2_devcfg_msg_t msg;
    audio_uart_lv_memzero_48949c(&msg, sizeof msg);
    g2_pb_istream_t initial, stream;
    audio_uart_pb_stream_init(&initial, data, length);
    (void)audio_uart_display_area_copy_439c04(&stream, &initial, sizeof stream);
    if ((uint8_t)audio_uart_pb_decode(&stream, audio_ble_ring_connect_pb_descriptor, &msg) == 0u) {
        DEVCFG_LOG(1u, fn_frame, 0x3bu, 0x04400000u, "Decoding failed: %s\n",
                   stream.errmsg != NULL ? stream.errmsg : none_text);
        return 0x2bu;
    }

    g2_devcfg_msg_t *tx = &g2_devcfg_tx_msg_200f57b4;
    uint8_t *buffer = g2_devcfg_tx_buffer_2037c3a0;
    audio_uart_buffer_zero(tx, sizeof *tx, 0u);
    DEVCFG_LOG(4u, fn_frame, 0x42u, 0x10400000u, "p_msg->commandId: %d", msg.command_id);

    uint8_t magic = (uint8_t)msg.magic_random;
    const void *payload = msg.payload;
    switch (msg.command_id) {
    case DEVCFG_CMD_AUTHENTICATION:
        DEVCFG_LOG(4u, fn_frame, 0x4du, 0x10000000u, "eDevCfgCommandId_AUTHENTICATION");
        if (PB_RxSecAuth(magic, payload) == 0u)
            (void)PB_TxEncodeSecAuth(magic, buffer, DEVCFG_TX_BUFFER_SIZE, tx, payload);
        break;
    case DEVCFG_CMD_PIPE_ROLE_CHANGE:
        DEVCFG_LOG(4u, fn_frame, 0x55u, 0x10000000u, "eDevCfgCommandId_PIPE_ROLE_CHANGE");
        if (PB_RxPipeRoleChange(magic, payload) == 0u)
            (void)PB_TxEncodePipeRoleChange(magic, buffer, DEVCFG_TX_BUFFER_SIZE, tx, payload);
        break;
    case DEVCFG_CMD_RING_CONNECT_INFO:
        DEVCFG_LOG(4u, fn_frame, 0x5du, 0x10000000u, "eDevCfgCommandId_RING_CONNECT_INFO");
        if (PB_RxRingConnectInfo(magic, payload) == 0u)
            (void)PB_TxEncodeRingConnectInfo(magic, buffer, DEVCFG_TX_BUFFER_SIZE, tx, payload);
        break;
    case DEVCFG_CMD_BLE_CONNECT_PARAM:
        DEVCFG_LOG(4u, fn_frame, 0x65u, 0x10000000u, "eDevCfgCommandId_BLE_CONNECT_PARAM");
        if (PB_RxBleConnectParams(magic, payload) == 0u)
            (void)PB_TxEncodeBleConnectParams(magic, buffer, DEVCFG_TX_BUFFER_SIZE, tx, payload);
        break;
    case DEVCFG_CMD_DISCONNECT_INFO:
        DEVCFG_LOG(4u, fn_frame, 0x6du, 0x10000000u, "eDevCfgCommandId_DISCONNECT_INFO");
        if (PB_RxDisconnectInfo(magic, payload) == 0u)
            (void)PB_TxEncodeDisconnectInfo(magic, buffer, DEVCFG_TX_BUFFER_SIZE, tx, payload);
        break;
    case DEVCFG_CMD_UNPAIR_INFO:
        DEVCFG_LOG(4u, fn_frame, 0x75u, 0x10000000u, "eDevCfgCommandId_UNPAIR_INFO");
        if (PB_RxUnpairInfo(magic, payload) == 0u)
            (void)PB_TxEncodeUnpairInfo(magic, buffer, DEVCFG_TX_BUFFER_SIZE, tx, payload);
        break;
    case DEVCFG_CMD_COMMAND_EXCEPTION:
        DEVCFG_LOG(4u, fn_frame, 0x7du, 0x10000000u, "eDevCfgCommandId_COMMAND_EXCEPTION");
        (void)APP_PbRxErrorCode(magic, (const g2_devcfg_error_code_t *)payload);
        break;
    case DEVCFG_CMD_GET_DEVICE_INFO:
        /* Logged only; no handler in 2.2.6.10. */
        DEVCFG_LOG(4u, fn_frame, 0x83u, 0x10000000u, "eDevCfgCommandId_GET_DEVICE_INFO");
        break;
    case DEVCFG_CMD_SET_DEVICE_INFO:
        DEVCFG_LOG(4u, fn_frame, 0x89u, 0x10000000u, "eDevCfgCommandId_SET_DEVICE_INFO");
        break;
    case DEVCFG_CMD_RESTORE_TO_FACTORY_SETTINGS:
        DEVCFG_LOG(4u, fn_frame, 0x8fu, 0x10000000u, "eDevCfgCommandId_RESTORE_TO_FACTORY_SETTINGS");
        if (PB_RxRestoreFactory(magic, payload) == 0u)
            (void)PB_TxEncodeRestoreFactory(magic, buffer, DEVCFG_TX_BUFFER_SIZE, tx, payload);
        break;
    case DEVCFG_CMD_BASE_CONNECT_HEART_BEAT:
        DEVCFG_LOG(4u, fn_frame, 0x97u, 0x10000000u, "eDevCfgCommandId_BASE_CONNECT_HEART_BEAT");
        if (PB_RxBaseConnHeartBeat(magic, payload) == 0u) {
            /* Re-arm the 30 s connection watchdog on every phone heartbeat. */
            (void)fw_event_loop_remove_delayed(audio_ble_comm_link_delayed);
            fw_event_loop_push_delayed(audio_ble_comm_link_delayed, 0u, DEVCFG_HEARTBEAT_TIMEOUT_MS);
            (void)PB_TxEncodeBaseConnHeartBeat(magic, buffer, DEVCFG_TX_BUFFER_SIZE, tx, payload);
        }
        break;
    case DEVCFG_CMD_QUICK_RESTART:
        DEVCFG_LOG(4u, fn_frame, 0xa1u, 0x10000000u, "eDevCfgCommandId_QUICK_RESTART");
        if (PB_RxQuickRestart(magic, payload) == 0u)
            (void)PB_TxEncodeQuickRestart(magic, buffer, DEVCFG_TX_BUFFER_SIZE, tx, payload);
        break;
    case DEVCFG_CMD_TIME_SYNC:
        DEVCFG_LOG(4u, fn_frame, 0xa9u, 0x10000000u, "eDevCfgCommandId_TIME_SYNC");
        if (PB_RxTimeSyncInfo(magic, payload) == 0u)
            (void)PB_TxEncodeTimeSyncInfo(magic, buffer, DEVCFG_TX_BUFFER_SIZE, tx, payload);
        break;
    case DEVCFG_CMD_AUD_CONTROL:
        DEVCFG_LOG(4u, fn_frame, 0xb1u, 0x10000000u, "eDevCfgCommandId_AUD_CONTROL");
        if (PB_RxAudControl(magic, payload) == 0u)
            (void)PB_TxEncodeAudControl(magic, buffer, DEVCFG_TX_BUFFER_SIZE, tx, payload);
        break;
    default:
        DEVCFG_LOG(4u, fn_frame, 0xb9u, 0x10400000u, "p_msg->commandId = %d", msg.command_id);
        (void)APP_PbTxEncodeErrorCode(1u, DEVCFG_SERVICE_ID, magic, msg.command_id, DEVCFG_ERR_NOT_SUPPORT);
        break;
    }
    return 0u;
}

/* Phone-reported command exception: logged only, always returns 0. */
uint32_t APP_PbRxErrorCode(uint8_t magic, const g2_devcfg_error_code_t *error)
{
    DEVCFG_LOG(4u, fn_rx_error, 0x114u, 0x10800000u, "error command = %d magic = %d\n", error->command, magic);
    switch (error->error_code) {
    case DEVCFG_ERR_CRC:
        DEVCFG_LOG(4u, fn_rx_error, 0x117u, 0x10400000u, "eErrorCode_CRC = %d\n", error->error_code);
        break;
    case DEVCFG_ERR_PB_ERROR:
        DEVCFG_LOG(4u, fn_rx_error, 0x11cu, 0x10400000u, "eErrorCode_PB_ERROR = %d\n", error->error_code);
        break;
    case DEVCFG_ERR_FAIL:
        DEVCFG_LOG(4u, fn_rx_error, 0x121u, 0x10400000u, "eErrorCode_FAIL = %d\n", error->error_code);
        break;
    case DEVCFG_ERR_NOT_SUPPORT:
        DEVCFG_LOG(4u, fn_rx_error, 0x126u, 0x10400000u, "eErrorCode_NOT_SUPPORT = %d\n", error->error_code);
        break;
    case DEVCFG_ERR_SUPPORT:
        DEVCFG_LOG(4u, fn_rx_error, 0x12bu, 0x10400000u, "eErrorCode_SUPPORT = %d\n", error->error_code);
        break;
    default:
        break;
    }
    return 0u;
}

/* Encode a COMMAND_EXCEPTION reply and send it on service 0x80. Stock ignores
 * the type/command arguments (callers pass 1, 0x80) and always sends with
 * type 1 / command 0x80. Returns 0 sent, 0x2b encode failure. */
uint32_t APP_PbTxEncodeErrorCode(uint32_t type, uint32_t command, uint8_t magic, uint8_t error_command,
                                 uint8_t error_code)
{
    (void)type;
    (void)command;
    g2_pb_ostream_t initial, stream;
    audio_pb_ostream_from_buffer(&initial, g2_devcfg_tx_buffer_2037c3a0, DEVCFG_TX_BUFFER_SIZE);
    (void)audio_uart_display_area_copy_439c04(&stream, &initial, sizeof stream);

    g2_devcfg_msg_t *tx = &g2_devcfg_tx_msg_200f57b4;
    tx->command_id = DEVCFG_CMD_COMMAND_EXCEPTION;
    tx->magic_random = magic;
    tx->which_payload = DEVCFG_TAG_ERROR_CODE;
    tx->payload[0] = error_command;
    tx->payload[1] = error_code;
    uint8_t ok = (uint8_t)audio_pb_encode(&stream, audio_ble_ring_connect_pb_descriptor, tx);
    uint32_t written = stream.bytes_written;
    DEVCFG_LOG(4u, fn_tx_error, 0x148u, 0x10400000u, "APP_PbeErrorCodeReply messageLength = %d", written);
    if (ok == 0u) {
        DEVCFG_LOG(1u, fn_tx_error, 0x14bu, 0x04400000u, "Encoding failed: %s\n",
                   stream.errmsg != NULL ? stream.errmsg : none_text);
        return 0x2bu;
    }
    (void)Thread_MsgPbTxByBle(1u, DEVCFG_SERVICE_ID, g2_devcfg_tx_buffer_2037c3a0, (uint16_t)written);
    return 0u;
}
