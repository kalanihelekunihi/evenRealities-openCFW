/* Device-setting protobuf handlers, stock
 * D:\01_workspace\s200_ap510b_iar_git\platform\protocols\pb_service_dev_config\pb_service_dev_setting.c
 * (path ROM 0x6d94fc, module tag "pb.devc" ROM 0x78de9c).
 * Native 0x542dc4..0x543b87 (PB_RxRestoreFactory .. PB_TxEncodeAudControl),
 * literal pools 0x5436d0..0x5436ef, 0x543908..0x543917, 0x5439bc..0x5439e3,
 * 0x543b88..0x543c47; fault templates ROM 0x7819f8..0x781b87.
 *
 * Called from APP_PbRxDevCfgFrameDataProcess (app/a-25-pb-dev-config) with the
 * decoded request's magic_random and payload; on Rx 0 it answers through the
 * matching PB_TxEncode* into the shared 256-byte packet. All messages use the
 * nanopb descriptor at ROM 0x7766dc. command_id / oneof tag of the replies:
 * RestoreFactory 13/12, QuickRestart 15/14, BaseConnHeartBeat 14/13,
 * TimeSync 0x80/0x80, AudControl 0x81/0x81. The static helper 0x542d4c (alert
 * close + KVDB/bond cleanup without format/reset) sits just before this file. */
#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

/* Top-level dev-config message header; the payload union starts at +8. */
typedef struct {
    uint8_t command_id;     /* +0 */
    uint8_t reserved1;
    uint16_t magic_random;  /* +2 */
    uint16_t which_payload; /* +4 oneof tag */
    uint16_t reserved6;
    uint8_t payload[];      /* +8 */
} g2_devset_msg_t;

/* TIME_SYNC payload, also the RAM copy at 0x20004394. */
typedef struct {
    uint32_t utc_second; /* +0 */
    int8_t time_zone;    /* +4 */
} g2_devset_time_sync_t;

/* nanopb 0.4 pb_ostream_t. */
typedef struct {
    void *callback;
    void *state;
    uint32_t max_size;
    uint32_t bytes_written;
    const char *errmsg;
} g2_pb_ostream_t;
_Static_assert(sizeof(g2_pb_ostream_t) == 20u, "nanopb ostream");

/* APP_errorFaultHandler record; the ROM templates carry code 0, the caller sets 1. */
typedef struct {
    uint32_t type;        /* +0x00 */
    uint16_t code;        /* +0x04 */
    uint16_t reserved;
    const char *path;     /* +0x08 */
    const char *function; /* +0x0c */
    uint32_t line;        /* +0x10 */
} g2_fault_record_t;
_Static_assert(sizeof(g2_fault_record_t) == 20u, "fault record");

#define DEVSET_SERVICE_ID 0x80u
#define DEVSET_ALERT_DELAY_MS 500u

extern g2_devset_time_sync_t g2_pb_time_sync_info_20004394;   /* RAM 0x20004394 */
extern const uint8_t audio_ble_ring_connect_pb_descriptor[];   /* ROM 0x7766dc pb_msgdesc_t */

extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */
extern void audio_uart_buffer_zero(void *dst, uint32_t len, uint32_t fill);                /* 0x43c0e4 */
extern void *audio_uart_display_area_copy_439c04(void *dst, const void *src, uint32_t len); /* word copy */
extern void audio_pb_ostream_from_buffer(g2_pb_ostream_t *out, void *buf, uint32_t size);   /* 0x4905f4 */
extern uint32_t audio_pb_encode(void *stream, const void *fields, const void *src);          /* pb_encode 0x490c32 */
extern void APP_errorFaultHandler(const g2_fault_record_t *record);                          /* 0x509b48 */
extern uint32_t Thread_MsgPbTxByBle(uint8_t type, uint8_t command, const void *payload, uint16_t length);       /* 0x475b14 */
extern uint32_t Thread_MsgPbTxByBleDirect(uint8_t type, uint8_t command, const void *payload, uint16_t length); /* 0x475a38 */
extern uint32_t fw_event_loop_remove_delayed(void (*callback)(void));                        /* 0x476ace */
extern uint8_t audio_uart_device_role_get(void);            /* 0x45a568, 1 = right (master) */
extern uint32_t audio_log_wake_allowed(void);               /* 0x443484 */
extern uint32_t display_background_app_running_44349c(void);
extern uint32_t display_foreground_app_running_4434b4(void);
extern void audio_system_alert_close_464c36(uint32_t app, uint32_t payload, uint32_t len, uint32_t context);
extern int32_t osDelay(uint32_t ticks);                     /* 0x449376 */
extern int32_t SVC_KvdbInvalidateMagic(void);               /* 0x4d9a84 */
extern void kvdbOnboardingConfigUpdateAndPersist(uint8_t index, const uint8_t *value); /* 0x4a7820 */
extern int32_t file_remove(const char *path);               /* 0x47498c */
extern void app_clear_all_bonding_info_4b46ce(void);
extern int littlefs_format_4761d2(void);                    /* 0 = ok */
extern void audio_ble_radio_ready_44b0ae(void);             /* system reset via 0x44ab24 */
extern void audio_ble_slave_security_state(uint8_t state);  /* 0x4b82e8 */
extern void SVC_SystemTimeSync(uint32_t epoch, int8_t zone); /* 0x44a1fe */
extern void RPC_SystemTimeSync(void);                       /* 0x44a2b2; stock passes r0 = 0 */
extern int32_t SVC_KvdbWriteTime(uint32_t timestamp, int8_t timezone); /* 0x585758 */
extern uint32_t audio_ble_comm_recovery_delayed(uint16_t notification); /* PB_TxEncodeNotifySecAuth 0x4bb92c */

static const char module_tag[] = "pb.devc"; /* ROM 0x78de9c */
static const char source_file[] = "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\protocols\\pb_service_dev_config\\pb_service_dev_setting.c"; /* ROM 0x6d94fc */
static const char fn_rx_restore[] = "PB_RxRestoreFactory";            /* ROM 0x781980 */
static const char fn_tx_restore[] = "PB_TxEncodeRestoreFactory";      /* ROM 0x76f534 */
static const char fn_rx_restart[] = "PB_RxQuickRestart";              /* ROM 0x7819a8 */
static const char fn_tx_restart[] = "PB_TxEncodeQuickRestart";        /* ROM 0x77a0fc */
static const char fn_rx_heartbeat[] = "PB_RxBaseConnHeartBeat";       /* ROM 0x77a114 */
static const char fn_tx_heartbeat[] = "PB_TxEncodeBaseConnHeartBeat"; /* ROM 0x763190 */
static const char fn_rx_time[] = "PB_RxTimeSyncInfo";                 /* ROM 0x7819bc */
static const char fn_tx_time[] = "PB_TxEncodeTimeSyncInfo";           /* ROM 0x77a144 */
static const char fn_rx_aud[] = "PB_RxAudControl";                    /* ROM 0x787d60 */
static const char fn_tx_aud[] = "PB_TxEncodeAudControl";              /* ROM 0x77a15c */
static const char none_text[] = "(none)";                             /* ROM 0x78dea4 */
static const char whitelist_path[] = "user/notify_whitelist.json";    /* ROM 0x76f518 */

/* ROM 0x7819f8..0x781b87: one template per NULL check. */
static const g2_fault_record_t fault_rx_restore = {0u, 0u, 0u, source_file, fn_rx_restore, 0x5au};
static const g2_fault_record_t fault_tx_restore[3] = {
    {0u, 0u, 0u, source_file, fn_tx_restore, 0x89u},
    {0u, 0u, 0u, source_file, fn_tx_restore, 0x8au},
    {0u, 0u, 0u, source_file, fn_tx_restore, 0x8bu}};
static const g2_fault_record_t fault_rx_restart = {0u, 0u, 0u, source_file, fn_rx_restart, 0xacu};
static const g2_fault_record_t fault_tx_restart[3] = {
    {0u, 0u, 0u, source_file, fn_tx_restart, 0xbdu},
    {0u, 0u, 0u, source_file, fn_tx_restart, 0xbeu},
    {0u, 0u, 0u, source_file, fn_tx_restart, 0xbfu}};
static const g2_fault_record_t fault_rx_heartbeat = {0u, 0u, 0u, source_file, fn_rx_heartbeat, 0xe0u};
static const g2_fault_record_t fault_tx_heartbeat[3] = {
    {0u, 0u, 0u, source_file, fn_tx_heartbeat, 0xf0u},
    {0u, 0u, 0u, source_file, fn_tx_heartbeat, 0xf1u},
    {0u, 0u, 0u, source_file, fn_tx_heartbeat, 0xf2u}};
static const g2_fault_record_t fault_rx_time = {0u, 0u, 0u, source_file, fn_rx_time, 0x114u};
static const g2_fault_record_t fault_tx_time[3] = {
    {0u, 0u, 0u, source_file, fn_tx_time, 0x12bu},
    {0u, 0u, 0u, source_file, fn_tx_time, 0x12cu},
    {0u, 0u, 0u, source_file, fn_tx_time, 0x12du}};
static const g2_fault_record_t fault_rx_aud = {0u, 0u, 0u, source_file, fn_rx_aud, 0x152u};
static const g2_fault_record_t fault_tx_aud[3] = {
    {0u, 0u, 0u, source_file, fn_tx_aud, 0x162u},
    {0u, 0u, 0u, source_file, fn_tx_aud, 0x163u},
    {0u, 0u, 0u, source_file, fn_tx_aud, 0x164u}};

#define DEVSET_LOG(level, fn, line, mask, fmt, ...) do { \
    if (audio_log_flags() & 2u) \
        audio_log_extended((level), module_tag, source_file, (fn), (line), fmt, ##__VA_ARGS__); \
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u)) \
        (void)compress_log_output((mask), "[pb.devc]" fmt, "[pb.devc]" fmt, ##__VA_ARGS__); \
} while (0)

/* Per-encoder constants of the shared PB_TxEncode* body (stock repeats it inline). */
typedef struct {
    const g2_fault_record_t *faults; /* buffer, msg, payload NULL templates */
    const char *fn;
    uint16_t null_line;
    uint16_t length_line;            /* "Encoding failed" is logged at length_line + 3 */
    uint8_t command_id;
    uint8_t tag;
    bool aud;                        /* AudControl: "POINT NULL", no '\n', clears +0xc word and +0x10 */
    bool direct;                     /* Thread_MsgPbTxByBleDirect instead of Thread_MsgPbTxByBle */
    uint8_t clear_offset;            /* trailing payload byte cleared before encoding */
} g2_devset_tx_t;

static const g2_devset_tx_t tx_restore = {fault_tx_restore, fn_tx_restore, 0x8du, 0x9du, 13u, 12u, false, false, 8u};
static const g2_devset_tx_t tx_restart = {fault_tx_restart, fn_tx_restart, 0xc1u, 0xd1u, 15u, 14u, false, false, 8u};
static const g2_devset_tx_t tx_heartbeat = {fault_tx_heartbeat, fn_tx_heartbeat, 0xf4u, 0x104u, 14u, 13u, false, true, 8u};
static const g2_devset_tx_t tx_time = {fault_tx_time, fn_tx_time, 0x12fu, 0x13fu, 0x80u, 0x80u, false, false, 0xdu};
static const g2_devset_tx_t tx_aud = {fault_tx_aud, fn_tx_aud, 0x166u, 0x177u, 0x81u, 0x81u, true, false, 0x10u};

static void raise_fault(const g2_fault_record_t *record)
{
    g2_fault_record_t fault;
    (void)audio_uart_display_area_copy_439c04(&fault, record, sizeof fault);
    fault.code = 1u;
    APP_errorFaultHandler(&fault);
}

static void close_alert_and_wait(uint8_t role)
{
    if (role == 1u)
        audio_system_alert_close_464c36(0u, 0u, 0u, 0u);
    (void)osDelay(DEVSET_ALERT_DELAY_MS);
}

/* Returns 0 sent, 2 NULL argument, 0x2b encode failure; the send result is ignored. */
static uint32_t devset_tx_encode(const g2_devset_tx_t *d, uint8_t magic, uint8_t *buffer, uint16_t size,
                                 g2_devset_msg_t *msg, const void *payload)
{
    if (buffer == NULL)
        raise_fault(&d->faults[0]);
    if (msg == NULL)
        raise_fault(&d->faults[1]);
    if (payload == NULL)
        raise_fault(&d->faults[2]);
    if (buffer == NULL || msg == NULL || payload == NULL) {
        if (d->aud)
            DEVSET_LOG(1u, d->fn, d->null_line, 0x04000000u, "POINT NULL");
        else
            DEVSET_LOG(1u, d->fn, d->null_line, 0x04000000u, "PORINT NULL");
        return 2u;
    }
    audio_uart_buffer_zero(buffer, size, 0u);
    g2_pb_ostream_t initial, stream;
    audio_pb_ostream_from_buffer(&initial, buffer, size);
    (void)audio_uart_display_area_copy_439c04(&stream, &initial, sizeof stream);
    msg->command_id = d->command_id;
    msg->magic_random = magic;
    msg->which_payload = d->tag;
    if (d->aud) {
        msg->payload[4] = 0u; /* +0xc word */
        msg->payload[5] = 0u;
        msg->payload[6] = 0u;
        msg->payload[7] = 0u;
    }
    ((uint8_t *)msg)[d->clear_offset] = 0u;
    uint8_t ok = (uint8_t)audio_pb_encode(&stream, audio_ble_ring_connect_pb_descriptor, msg);
    DEVSET_LOG(4u, d->fn, d->length_line, 0x10400000u, "messageLength = %d", stream.bytes_written);
    if (ok == 0u) {
        const char *why = stream.errmsg != NULL ? stream.errmsg : none_text;
        if (d->aud)
            DEVSET_LOG(1u, d->fn, d->length_line + 3u, 0x04400000u, "Encoding failed: %s", why);
        else
            DEVSET_LOG(1u, d->fn, d->length_line + 3u, 0x04400000u, "Encoding failed: %s\n", why);
        return 0x2bu;
    }
    if (d->direct)
        (void)Thread_MsgPbTxByBleDirect(1u, DEVSET_SERVICE_ID, buffer, (uint16_t)stream.bytes_written);
    else
        (void)Thread_MsgPbTxByBle(1u, DEVSET_SERVICE_ID, buffer, (uint16_t)stream.bytes_written);
    return 0u;
}

/* Factory reset: dismiss any open app alert (master side), invalidate the KVDB
 * magic, mark onboarding pending, drop the notify whitelist and all bonds,
 * reformat littlefs and reset. Returns 2 for NULL, otherwise does not return
 * in practice (0 after the reset request). */
uint32_t PB_RxRestoreFactory(uint8_t magic, const void *payload)
{
    (void)magic;
    if (payload == NULL) {
        raise_fault(&fault_rx_restore);
        DEVSET_LOG(1u, fn_rx_restore, 0x5cu, 0x04000000u, "PORINT NULL");
        return 2u;
    }
    DEVSET_LOG(4u, fn_rx_restore, 0x60u, 0x10000000u, "RestoreFactory");
    uint8_t role = audio_uart_device_role_get();
    if (audio_log_wake_allowed() == 1u) {
        if (display_background_app_running_44349c() == 1u)
            close_alert_and_wait(role);
        if (display_foreground_app_running_4434b4() == 1u)
            close_alert_and_wait(role);
    }
    (void)SVC_KvdbInvalidateMagic();
    uint8_t onboarding = 1u;
    kvdbOnboardingConfigUpdateAndPersist(0u, &onboarding);
    (void)file_remove(whitelist_path);
    app_clear_all_bonding_info_4b46ce();
    if (littlefs_format_4761d2() != 0)
        DEVSET_LOG(1u, fn_rx_restore, 0x7cu, 0x04000000u, "littlefs_format faild");
    audio_ble_radio_ready_44b0ae();
    return 0u;
}

uint32_t PB_TxEncodeRestoreFactory(uint8_t magic, uint8_t *buffer, uint16_t size, void *msg, const void *payload)
{
    return devset_tx_encode(&tx_restore, magic, buffer, size, (g2_devset_msg_t *)msg, payload);
}

uint32_t PB_RxQuickRestart(uint8_t magic, const void *payload)
{
    (void)magic;
    if (payload == NULL) {
        raise_fault(&fault_rx_restart);
        DEVSET_LOG(1u, fn_rx_restart, 0xaeu, 0x04000000u, "PORINT NULL");
        return 2u;
    }
    DEVSET_LOG(4u, fn_rx_restart, 0xb2u, 0x10000000u, "QuickRestart");
    audio_ble_radio_ready_44b0ae();
    return 0u;
}

uint32_t PB_TxEncodeQuickRestart(uint8_t magic, uint8_t *buffer, uint16_t size, void *msg, const void *payload)
{
    return devset_tx_encode(&tx_restart, magic, buffer, size, (g2_devset_msg_t *)msg, payload);
}

/* Phone heartbeat: marks the slave link secure (state 1). The caller re-arms
 * the 30 s connection watchdog. */
uint32_t PB_RxBaseConnHeartBeat(uint8_t magic, const void *payload)
{
    (void)magic;
    if (payload == NULL) {
        raise_fault(&fault_rx_heartbeat);
        DEVSET_LOG(1u, fn_rx_heartbeat, 0xe2u, 0x04000000u, "PORINT NULL");
        return 2u;
    }
    audio_ble_slave_security_state(1u);
    DEVSET_LOG(4u, fn_rx_heartbeat, 0xe6u, 0x10000000u, "pBaseHeartBeat");
    return 0u;
}

uint32_t PB_TxEncodeBaseConnHeartBeat(uint8_t magic, uint8_t *buffer, uint16_t size, void *msg, const void *payload)
{
    return devset_tx_encode(&tx_heartbeat, magic, buffer, size, (g2_devset_msg_t *)msg, payload);
}

/* Phone time sync: cancels the pending security notification first (even for
 * NULL), keeps a copy for the reply, applies it, then pushes it to the peer arm
 * immediately (RPC_SystemTimeSync) and marks the link secure. */
uint32_t PB_RxTimeSyncInfo(uint8_t magic, const void *payload)
{
    (void)magic;
    (void)fw_event_loop_remove_delayed((void (*)(void))(uintptr_t)audio_ble_comm_recovery_delayed);
    g2_devset_time_sync_t *saved = &g2_pb_time_sync_info_20004394;
    const g2_devset_time_sync_t *sync = (const g2_devset_time_sync_t *)payload;
    if (sync == NULL) {
        raise_fault(&fault_rx_time);
        DEVSET_LOG(1u, fn_rx_time, 0x116u, 0x04000000u, "PORINT NULL");
        return 2u;
    }
    saved->utc_second = sync->utc_second;
    saved->time_zone = sync->time_zone;
    SVC_SystemTimeSync(sync->utc_second, sync->time_zone);
    DEVSET_LOG(4u, fn_rx_time, 0x11du, 0x10800000u, "5 sysUtcSecond = %lu time_zone = %d",
               saved->utc_second, (int32_t)saved->time_zone);
    (void)fw_event_loop_remove_delayed(RPC_SystemTimeSync);
    RPC_SystemTimeSync();
    audio_ble_slave_security_state(1u);
    return 0u;
}

/* Echoes the saved time; after a successful send it is persisted to KVDB. */
uint32_t PB_TxEncodeTimeSyncInfo(uint8_t magic, uint8_t *buffer, uint16_t size, void *msg, const void *payload)
{
    uint32_t result = devset_tx_encode(&tx_time, magic, buffer, size, (g2_devset_msg_t *)msg, payload);
    if (result != 0u)
        return result;
    const g2_devset_time_sync_t *saved = &g2_pb_time_sync_info_20004394;
    (void)SVC_KvdbWriteTime(saved->utc_second, saved->time_zone);
    DEVSET_LOG(4u, fn_tx_time, 0x14au, 0x10800000u, "8 sysUtcSecond = %lu time_zone = %d",
               saved->utc_second, (int32_t)saved->time_zone);
    return 0u;
}

/* Not implemented in 2.2.6.10: logs and returns 0 so an empty reply is sent. */
uint32_t PB_RxAudControl(uint8_t magic, const void *payload)
{
    (void)magic;
    if (payload == NULL) {
        raise_fault(&fault_rx_aud);
        DEVSET_LOG(1u, fn_rx_aud, 0x154u, 0x04000000u, "POINT NULL");
        return 2u;
    }
    DEVSET_LOG(2u, fn_rx_aud, 0x158u, 0x08000000u, "PB_RxAudControl not support now");
    return 0u;
}

uint32_t PB_TxEncodeAudControl(uint8_t magic, uint8_t *buffer, uint16_t size, void *msg, const void *payload)
{
    return devset_tx_encode(&tx_aud, magic, buffer, size, (g2_devset_msg_t *)msg, payload);
}
