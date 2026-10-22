/* Pair-manager protobuf service, stock
 * D:\01_workspace\s200_ap510b_iar_git\platform\protocols\pb_service_dev_config\pb_service_pair_mgr.c.
 * Native 0x4bb3dc..0x4bcf9c (PB_RxSecAuth .. PB_TxEncodeUnpairInfo), literal pools
 * 0x4bbd98.., 0x4bc188.., 0x4bc414.., 0x4bc5a8.., 0x4bc788.., 0x4bcb04.., 0x4bcde0.., 0x4bcf9c..0x4bd054.
 * Neighbours already in g2/src: PB_TxEncodeNotifySecAuthImpl 0x4bb73a (ble/ble-security),
 * PB_TxEncodeNotifySecAuth 0x4bb92c (ble/ble-comm), pairMgrSecAuthFlagSet/Get 0x4bb9b4/0x4bb9bc
 * and PB_LastTxEncodeRingConnectInfoTimeSet 0x4bbf44 (ble/ble-pair),
 * PB_TxEncodeNotifyRingConnectInfo[Impl] 0x4bc1b4/0x4bc418 (ble/ble-ring).
 *
 * All messages share the nanopb descriptor at ROM 0x7766dc. Encoders fill the
 * top-level header (command_id, magic_random, which_payload), clear one
 * trailing payload byte, encode into the caller's buffer and send it with
 * type 1 / command 0x80. command_id / oneof tag: SecAuth 4/3, PipeRoleChange 5/4,
 * RingConnectInfo 6/5, BleConnectParams 7/6, DisconnectInfo 8/7, UnpairInfo 9/8. */
#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

/* Top-level pair-manager message header; the payload union starts at +8. */
typedef struct {
    uint8_t command_id;     /* +0 */
    uint8_t reserved1;
    uint16_t magic_random;  /* +2 */
    uint16_t which_payload; /* +4 oneof tag */
    uint16_t reserved6;
    uint8_t payload[];      /* +8 */
} g2_pair_mgr_msg_t;

/* Decoded submessages as the Rx handlers read them. */
typedef struct {
    uint8_t sec_auth;      /* +0 */
    uint8_t phone_type;    /* +1 3 = iOS */
} g2_pair_sec_auth_t;

typedef struct {
    uint8_t connect_ring;  /* +0 */
    uint8_t reserved1;
    uint16_t mac_size;     /* +2 */
    uint8_t mac[6];        /* +4 */
    uint16_t name_size;    /* +10 */
    uint8_t name[];        /* +12 */
} g2_pair_ring_connect_info_t;

typedef struct {
    uint8_t dev;           /* +0 Disconnect: 1 glasses, 2 ring. Unpair: 0 ring, 2 ring+glasses */
    uint8_t reserved1;
    uint16_t mac_size;     /* +2 */
    uint8_t mac[6];        /* +4 */
} g2_pair_device_info_t;

typedef struct {
    uint8_t reserved[4];
    uint8_t set_speed;     /* +4 0 SLOW, else FAST */
} g2_pair_conn_params_t;

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
    uint32_t type;      /* +0x00 */
    uint16_t code;      /* +0x04 */
    uint16_t reserved;
    const char *path;   /* +0x08 */
    const char *function; /* +0x0c */
    uint32_t line;      /* +0x10 */
} g2_fault_record_t;
_Static_assert(sizeof(g2_fault_record_t) == 20u, "fault record");

extern uint8_t audio_ble_pair_auth_flag_20074ffc;          /* RAM 0x20074ffc */
extern const uint8_t audio_ble_ring_connect_pb_descriptor[]; /* ROM 0x7766dc pb_msgdesc_t */

extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */
extern void audio_uart_buffer_zero(void *dst, uint32_t len, uint32_t fill);                /* 0x43c0e4 */
extern void *audio_uart_display_area_copy_439c04(void *dst, const void *src, uint32_t len); /* word copy */
extern void audio_dump_hex(const char *label, uint32_t width, const uint8_t *data, uint32_t length); /* 0x43dacc */
extern void audio_pb_ostream_from_buffer(g2_pb_ostream_t *out, void *buf, uint32_t size);   /* 0x4905f4 */
extern uint32_t audio_pb_encode(void *stream, const void *fields, const void *src);          /* pb_encode 0x490c32 */
extern void audio_ring_pb_assert_509b48(const g2_fault_record_t *record);  /* APP_errorFaultHandler */
extern uint32_t Thread_MsgPbTxByBleDirect(uint8_t type, uint8_t command, const void *payload, uint16_t length); /* 0x475a38 */
extern uint32_t audio_ring_pb_tx_ble_475b14(uint32_t type, uint32_t command, const void *payload, uint32_t length); /* Thread_MsgPbTxByBle */
extern void audio_event_loop_push_delayed(void (*callback)(void), uint32_t argument, uint32_t delay); /* 0x47697e */
extern uint32_t audio_event_loop_remove_delayed(void (*callback)(void));                         /* 0x476ace */
extern void pairMgrSecAuthFlagSet(uint8_t value);                       /* 0x4bb9b4 */
extern uint32_t audio_ble_comm_recovery_delayed(uint16_t notification); /* PB_TxEncodeNotifySecAuth 0x4bb92c */
extern void audio_ble_slave_disconnect_followup(uint32_t trusted);      /* 0x46effc */
extern void audio_ble_slave_open_followup(void);                        /* 0x46f098 */
extern void app_ble_connect_phone_type_set_4b8140(uint8_t phone_type);  /* APP_BleConnectPhoneTypeSet */
extern uint8_t app_ble_phone_type_get_4b8128(void);                     /* APP_BleConnectPhoneTypeGet */
extern void APP_BleSlaveAsCmdRole(uint8_t cmd_pipe);                    /* 0x46f164 */
extern void ble_ota_mode_set(uint8_t value);                            /* 0x46efe4 */
extern void APP_BleSlaveDisconnect(void);                               /* 0x46f0ec, stock passes r0 = 0 */
extern uint8_t audio_uart_device_role_get(void);                        /* 0x45a568, 1 = right */
extern uint32_t audio_uart_ring_active(void);                           /* central_is_ring_owner_side 0x4a2914 */
extern void audio_ble_master_set_target(const uint8_t *address, const char *name, uint8_t name_length); /* APP_MasterSetTargetAddrName 0x4a2068 */
extern uint32_t audio_ble_master_auth_mode_set(uint8_t mode);           /* auth_mode_set 0x4a2168 */
extern uint32_t audio_ble_master_link_matches_target(const uint8_t *target); /* 0x4a2864 */
extern void audio_ble_master_reset_retry_count(void);                   /* APP_MasterResetRetryConnectCnt 0x4a2300 */
extern void audio_ble_master_begin_failure_notify_4a1546(void);         /* APP_MasterBeginRingConnectFailureNotifyAfterRetry */
extern void audio_ble_master_clear_failure_notify(void);                /* APP_MasterClearRingConnectFailureNotifyAfterRetry 0x4a15c0 */
extern void audio_ble_master_connect_event(void);                       /* APP_MasterConnectEvent 0x4a1b60, delayed callback */
extern void audio_ble_master_start_try_connect_ring(void);              /* APP_MasterSysStartTryConnectRing 0x4a23ac */
extern void audio_ble_master_cleanup_ring_unpair_4a2c9c(const uint8_t *remove_record); /* APP_MasterCleanupRingUnpair */
extern bool RING_ConnectPolicyShouldBlockRingConnectInfo(bool is_ring_connect_info); /* 0x49f326 */
extern void RING_ConnectPolicyMarkRingConnectInfoProcessed(bool processed);         /* 0x49f438 */
extern void audio_ble_ring_policy_schedule_connect_timeout_49f4a8(void);  /* RING_ConnectPolicyScheduleConnectTimeout */
extern void audio_ble_ring_policy_cancel_connect_timeout_49f5f8(void);    /* RING_ConnectPolicyCancelConnectTimeout */
extern void audio_ble_ring_policy_notify_success_49f646(void);            /* RING_ConnectPolicyNotifyConnectSuccessSoon */
extern void RING_ConnectPolicyResetRingConnectInfoThrottle(void);         /* 0x49f702 */
extern void audio_ble_ring_connect_policy_reset(void);                    /* RING_ConnectPolicyReset 0x49f6ae */
extern void audio_ble_param_reset_delayed_event(uint32_t delay);          /* ble_param_reset_delayed_event 0x478252 */
extern void ble_state_skip_manual_start(uint8_t value);                   /* 0x478110 */

static const char module_tag[] = "pb.devc"; /* ROM 0x78defc */
static const char source_file[] = "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\protocols\\pb_service_dev_config\\pb_service_pair_mgr.c"; /* ROM 0x6db290 */
static const char fn_rx_sec_auth[] = "PB_RxSecAuth";                 /* ROM 0x787e50 */
static const char fn_tx_sec_auth[] = "PB_TxEncodeSecAuth";           /* ROM 0x7820b0 */
static const char fn_rx_role[] = "PB_RxPipeRoleChange";              /* ROM 0x7820d8 */
static const char fn_tx_role[] = "PB_TxEncodePipeRoleChange";        /* ROM 0x76f828 */
static const char fn_owner_execute[] = "_PB_RxRingConnectInfoOwnerExecute"; /* ROM 0x757c08 */
static const char fn_ring_common[] = "_PB_RxRingConnectInfoCommon";  /* ROM 0x76f844 */
static const char fn_tx_ring[] = "PB_TxEncodeRingConnectInfo";       /* ROM 0x76f87c */
static const char fn_rx_params[] = "PB_RxBleConnectParams";          /* ROM 0x77a51c */
static const char fn_tx_params[] = "PB_TxEncodeBleConnectParams";    /* ROM 0x76f898 */
static const char fn_rx_disconnect[] = "PB_RxDisconnectInfo";        /* ROM 0x782100 */
static const char fn_tx_disconnect[] = "PB_TxEncodeDisconnectInfo";  /* ROM 0x76f8ec */
static const char fn_rx_unpair[] = "PB_RxUnpairInfo";                /* ROM 0x787e60 */
static const char fn_tx_unpair[] = "PB_TxEncodeUnpairInfo";          /* ROM 0x77a564 */
static const char none_text[] = "(none)";                            /* ROM 0x78df04 */
static const char text_right[] = "RIGHT";                            /* ROM 0x78df0c */
static const char text_left[] = "LEFT";                              /* ROM 0x78df14 */
static const char text_connect[] = "CONNECT";                        /* ROM 0x78df1c */
static const char text_disconnect[] = "DISCONNECT";                  /* ROM 0x78b78c */
static const char text_fast[] = "FAST";                              /* ROM 0x78df2c */
static const char text_slow[] = "SLOW";                              /* ROM 0x78df34 */
static const char label_ring_mac[] = "ringMac";                      /* ROM 0x78df24 */
static const char label_disconnect_mac[] = "disconnect ringMac";     /* ROM 0x782114 */
static const char label_unpair_mac[] = "unpair ringMac";             /* ROM 0x787e80 */

/* ROM 0x78213c..0x782307: one fault template per NULL check. */
static const g2_fault_record_t fault_rx_sec_auth = {0u, 0u, 0u, source_file, fn_rx_sec_auth, 0x3eu};
static const g2_fault_record_t fault_tx_sec_auth[3] = {
    {0u, 0u, 0u, source_file, fn_tx_sec_auth, 0x5fu},
    {0u, 0u, 0u, source_file, fn_tx_sec_auth, 0x60u},
    {0u, 0u, 0u, source_file, fn_tx_sec_auth, 0x61u}};
static const g2_fault_record_t fault_rx_role = {0u, 0u, 0u, source_file, fn_rx_role, 0xd2u};
static const g2_fault_record_t fault_tx_role[3] = {
    {0u, 0u, 0u, source_file, fn_tx_role, 0xe3u},
    {0u, 0u, 0u, source_file, fn_tx_role, 0xe4u},
    {0u, 0u, 0u, source_file, fn_tx_role, 0xe5u}};
static const g2_fault_record_t fault_tx_ring[3] = {
    {0u, 0u, 0u, source_file, fn_tx_ring, 0x173u},
    {0u, 0u, 0u, source_file, fn_tx_ring, 0x174u},
    {0u, 0u, 0u, source_file, fn_tx_ring, 0x175u}};
static const g2_fault_record_t fault_rx_params = {0u, 0u, 0u, source_file, fn_rx_params, 0x1e5u};
static const g2_fault_record_t fault_tx_params[3] = {
    {0u, 0u, 0u, source_file, fn_tx_params, 0x1fau},
    {0u, 0u, 0u, source_file, fn_tx_params, 0x1fbu},
    {0u, 0u, 0u, source_file, fn_tx_params, 0x1fcu}};
static const g2_fault_record_t fault_rx_disconnect = {0u, 0u, 0u, source_file, fn_rx_disconnect, 0x24du};
static const g2_fault_record_t fault_tx_disconnect[3] = {
    {0u, 0u, 0u, source_file, fn_tx_disconnect, 0x26au},
    {0u, 0u, 0u, source_file, fn_tx_disconnect, 0x26bu},
    {0u, 0u, 0u, source_file, fn_tx_disconnect, 0x26cu}};
static const g2_fault_record_t fault_rx_unpair = {0u, 0u, 0u, source_file, fn_rx_unpair, 0x299u};
static const g2_fault_record_t fault_tx_unpair[3] = {
    {0u, 0u, 0u, source_file, fn_tx_unpair, 0x2c6u},
    {0u, 0u, 0u, source_file, fn_tx_unpair, 0x2c7u},
    {0u, 0u, 0u, source_file, fn_tx_unpair, 0x2c8u}};

#define PAIR_LOG(level, fn, line, mask, fmt, ...) do { \
    if (audio_log_flags() & 2u) \
        audio_log_extended((level), module_tag, source_file, (fn), (line), fmt, ##__VA_ARGS__); \
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u)) \
        (void)compress_log_output((mask), "[pb.devc]" fmt, "[pb.devc]" fmt, ##__VA_ARGS__); \
} while (0)

static void raise_fault(const g2_fault_record_t *record)
{
    g2_fault_record_t fault;
    (void)audio_uart_display_area_copy_439c04(&fault, record, sizeof fault);
    fault.code = 1u;
    audio_ring_pb_assert_509b48(&fault);
}

static const char *role_text(void)
{
    return audio_uart_device_role_get() == 1u ? text_right : text_left;
}

/* Shared body of the six PB_TxEncode* functions (stock repeats it inline).
 * Returns 0 sent, 2 NULL argument, 0x2b encode failure; the send result is ignored. */
static uint32_t pair_tx_encode(uint8_t magic, uint8_t *buffer, uint16_t size,
                               g2_pair_mgr_msg_t *msg, const void *payload,
                               const g2_fault_record_t faults[3], const char *fn,
                               uint32_t null_line, uint8_t command_id, uint16_t tag,
                               uint32_t clear_offset, uint32_t length_line, bool direct)
{
    if (buffer == NULL)
        raise_fault(&faults[0]);
    if (msg == NULL)
        raise_fault(&faults[1]);
    if (payload == NULL)
        raise_fault(&faults[2]);
    if (buffer == NULL || msg == NULL || payload == NULL) {
        PAIR_LOG(1u, fn, null_line, 0x04000000u, "PORINT NULL");
        return 2u;
    }
    audio_uart_buffer_zero(buffer, size, 0u);
    g2_pb_ostream_t initial, stream;
    audio_pb_ostream_from_buffer(&initial, buffer, size);
    (void)audio_uart_display_area_copy_439c04(&stream, &initial, sizeof stream);
    msg->command_id = command_id;
    msg->magic_random = magic;
    msg->which_payload = tag;
    ((uint8_t *)msg)[clear_offset] = 0u;
    uint32_t ok = audio_pb_encode(&stream, audio_ble_ring_connect_pb_descriptor, msg);
    PAIR_LOG(4u, fn, length_line, 0x10400000u, "messageLength = %d", stream.bytes_written);
    if ((uint8_t)ok == 0u) {
        PAIR_LOG(1u, fn, length_line + 3u, 0x04400000u, "Encoding failed: %s\n",
                 stream.errmsg != NULL ? stream.errmsg : none_text);
        return 0x2bu;
    }
    if (direct)
        (void)Thread_MsgPbTxByBleDirect(1u, 0x80u, buffer, (uint16_t)stream.bytes_written);
    else
        (void)audio_ring_pb_tx_ble_475b14(1u, 0x80u, buffer, (uint16_t)stream.bytes_written);
    return 0u;
}

/* Phone reports secure authentication; returns 0, or 2 for NULL. */
uint32_t PB_RxSecAuth(uint8_t magic, const g2_pair_sec_auth_t *sec_auth)
{
    (void)magic;
    if (sec_auth == NULL) {
        raise_fault(&fault_rx_sec_auth);
        PAIR_LOG(1u, fn_rx_sec_auth, 0x40u, 0x04000000u, "PORINT NULL");
        return 2u;
    }
    PAIR_LOG(4u, fn_rx_sec_auth, 0x44u, 0x10400000u, "pSecAuth->secAuth = %d", sec_auth->sec_auth);
    if (sec_auth->sec_auth != 0u) {
        (void)audio_event_loop_remove_delayed((void (*)(void))audio_ble_slave_disconnect_followup);
        audio_event_loop_push_delayed((void (*)(void))audio_ble_slave_disconnect_followup, 1u, 500u);
    }
    app_ble_connect_phone_type_set_4b8140(sec_auth->phone_type);
    (void)audio_event_loop_remove_delayed(audio_ble_slave_open_followup);
    if (audio_ble_pair_auth_flag_20074ffc == 0u) {
        /* Not yet encrypted: arm the flag, the encryption event sends the notify. */
        pairMgrSecAuthFlagSet(1u);
        PAIR_LOG(4u, fn_rx_sec_auth, 0x55u, 0x10000000u, "PB_TxEncodeNotifySecAuth wait encrypted");
    } else {
        PAIR_LOG(4u, fn_rx_sec_auth, 0x4fu, 0x10000000u,
                 "encrypted auth success, PB_TxEncodeNotifySecAuth 200ms auth flag notify");
        void (*notify)(void) = (void (*)(void))audio_ble_comm_recovery_delayed;
        (void)audio_event_loop_remove_delayed(notify);
        audio_event_loop_push_delayed(notify, 1u, 100u);
        audio_event_loop_push_delayed(notify, 1u, 2000u);
    }
    return 0u;
}

uint32_t PB_TxEncodeSecAuth(uint8_t magic, uint8_t *buffer, uint16_t size,
                            g2_pair_mgr_msg_t *msg, const void *payload)
{
    return pair_tx_encode(magic, buffer, size, msg, payload, fault_tx_sec_auth, fn_tx_sec_auth,
                          0x63u, 4u, 3u, 10u, 0x73u, true);
}

/* asCmdRole 1 = right glasses own the command pipe. */
uint32_t PB_RxPipeRoleChange(uint8_t magic, const uint8_t *role_change)
{
    (void)magic;
    if (role_change == NULL) {
        raise_fault(&fault_rx_role);
        PAIR_LOG(1u, fn_rx_role, 0xd4u, 0x04000000u, "PORINT NULL");
        return 2u;
    }
    PAIR_LOG(4u, fn_rx_role, 0xd8u, 0x10400000u, "pRoleChange->asCmdRole = %s",
             role_change[0] == 1u ? text_right : text_left);
    APP_BleSlaveAsCmdRole(role_change[0]);
    return 0u;
}

uint32_t PB_TxEncodePipeRoleChange(uint8_t magic, uint8_t *buffer, uint16_t size,
                                   g2_pair_mgr_msg_t *msg, const void *payload)
{
    return pair_tx_encode(magic, buffer, size, msg, payload, fault_tx_role, fn_tx_role,
                          0xe7u, 5u, 4u, 10u, 0xf7u, false);
}

/* Owner side: retarget the central link and (re)start or stop ring connect. */
uint32_t _PB_RxRingConnectInfoOwnerExecute(uint8_t magic, const g2_pair_ring_connect_info_t *info)
{
    (void)magic;
    audio_ble_master_set_target(info->mac, (const char *)info->name, (uint8_t)info->name_size);
    (void)audio_ble_master_auth_mode_set(info->connect_ring);
    PAIR_LOG(4u, fn_owner_execute, 0x10fu, 0x10400000u, "TO %s RING",
             info->connect_ring != 0u ? text_connect : text_disconnect);
    if (info->connect_ring != 0u && audio_ble_master_link_matches_target(info->mac) != 0u) {
        PAIR_LOG(3u, fn_owner_execute, 0x115u, 0x0c000000u,
                 "PB_RxRingConnectInfo: already connected to target ring (state=CONNECTED), notify success");
        RING_ConnectPolicyMarkRingConnectInfoProcessed(info->connect_ring != 0u);
        audio_ble_master_clear_failure_notify();
        audio_ble_ring_policy_notify_success_49f646();
        (void)audio_event_loop_remove_delayed(audio_ble_master_connect_event);
        (void)audio_event_loop_remove_delayed(audio_ble_master_start_try_connect_ring);
        return 0u;
    }
    (void)audio_event_loop_remove_delayed(audio_ble_master_connect_event);
    (void)audio_event_loop_remove_delayed(audio_ble_master_start_try_connect_ring);
    audio_ble_master_reset_retry_count();
    if (info->connect_ring != 0u)
        audio_ble_master_begin_failure_notify_4a1546();
    else
        audio_ble_master_clear_failure_notify();
    /* Event argument 1 = connect, 0x102 = disconnect. */
    audio_event_loop_push_delayed(audio_ble_master_connect_event,
                                  info->connect_ring != 0u ? 1u : 0x102u, 0u);
    RING_ConnectPolicyMarkRingConnectInfoProcessed(info->connect_ring != 0u);
    if (info->connect_ring != 0u)
        audio_ble_ring_policy_schedule_connect_timeout_49f4a8();
    else
        audio_ble_ring_policy_cancel_connect_timeout_49f5f8();
    return 0u;
}

uint32_t _PB_RxRingConnectInfoCommon(uint8_t magic, const g2_pair_ring_connect_info_t *info,
                                     uint8_t from_peer_forward)
{
    if (info == NULL) {
        PAIR_LOG(1u, fn_ring_common, 0x143u, 0x04000000u, "PB_RxRingConnectInfo: NULL");
        return 2u;
    }
    if (audio_log_flags() & 2u) {
        uint8_t owner = (uint8_t)audio_uart_ring_active();
        audio_log_extended(3u, module_tag, source_file, fn_ring_common, 0x14bu,
                           "PB_RxRingConnectInfo: connectRing=%d fromPeerForward=%d role=%s owner=%d",
                           info->connect_ring, from_peer_forward, role_text(), owner);
    }
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u)) {
        uint8_t owner = (uint8_t)audio_uart_ring_active();
        static const char compact[] =
            "[pb.devc]PB_RxRingConnectInfo: connectRing=%d fromPeerForward=%d role=%s owner=%d";
        (void)compress_log_output(0x0d000000u, compact, compact, info->connect_ring,
                                  from_peer_forward, role_text(), owner);
    }
    audio_dump_hex(label_ring_mac, 16u, info->mac, info->mac_size);
    if (from_peer_forward == 0u &&
        RING_ConnectPolicyShouldBlockRingConnectInfo(info->connect_ring != 0u))
        return 0u;
    if (info->connect_ring == 0u || audio_uart_ring_active() != 0u)
        return _PB_RxRingConnectInfoOwnerExecute(magic, info);
    PAIR_LOG(2u, fn_ring_common, 0x157u, 0x08000000u,
             "PB_RxRingConnectInfo: not owner, ignore connect (dominant_hand drives connect now)");
    return 0u;
}

uint32_t PB_RxRingConnectInfo(uint8_t magic, const g2_pair_ring_connect_info_t *info)
{
    return _PB_RxRingConnectInfoCommon(magic, info, 0u);
}

uint32_t PB_TxEncodeRingConnectInfo(uint8_t magic, uint8_t *buffer, uint16_t size,
                                    g2_pair_mgr_msg_t *msg, const void *payload)
{
    return pair_tx_encode(magic, buffer, size, msg, payload, fault_tx_ring, fn_tx_ring,
                          0x177u, 6u, 5u, 0x25u, 0x187u, true);
}

uint32_t PB_RxBleConnectParams(uint8_t magic, const g2_pair_conn_params_t *params)
{
    (void)magic;
    if (params == NULL) {
        raise_fault(&fault_rx_params);
        PAIR_LOG(1u, fn_rx_params, 0x1e7u, 0x04000000u, "PORINT NULL");
        return 2u;
    }
    PAIR_LOG(4u, fn_rx_params, 0x1ebu, 0x10400000u, "pConnParams->setSpeed = eConnParamState_%s",
             params->set_speed != 0u ? text_fast : text_slow);
    if (params->set_speed == 0u)
        audio_ble_param_reset_delayed_event(0u);
    else
        ble_state_skip_manual_start(0u);
    return 0u;
}

uint32_t PB_TxEncodeBleConnectParams(uint8_t magic, uint8_t *buffer, uint16_t size,
                                     g2_pair_mgr_msg_t *msg, const void *payload)
{
    return pair_tx_encode(magic, buffer, size, msg, payload, fault_tx_params, fn_tx_params,
                          0x1feu, 7u, 6u, 14u, 0x20eu, false);
}

/* The ring-connect throttle is reset even for a NULL message. */
uint32_t PB_RxDisconnectInfo(uint8_t magic, const g2_pair_device_info_t *info)
{
    (void)magic;
    if (info == NULL)
        raise_fault(&fault_rx_disconnect);
    RING_ConnectPolicyResetRingConnectInfoThrottle();
    if (info == NULL) {
        PAIR_LOG(1u, fn_rx_disconnect, 0x253u, 0x04000000u, "PORINT NULL");
        return 2u;
    }
    PAIR_LOG(4u, fn_rx_disconnect, 0x256u, 0x10400000u, "pDisconnectInfo->dev = %d", info->dev);
    if (info->dev == 2u)
        audio_dump_hex(label_disconnect_mac, 16u, info->mac, info->mac_size);
    else if (info->dev == 1u)
        PAIR_LOG(4u, fn_rx_disconnect, 0x25au, 0x10000000u, "disconnect glasses");
    audio_ble_master_reset_retry_count();
    (void)audio_event_loop_remove_delayed(audio_ble_master_connect_event);
    audio_event_loop_push_delayed(audio_ble_master_connect_event, 0x102u, 0u);
    return 0u;
}

uint32_t PB_TxEncodeDisconnectInfo(uint8_t magic, uint8_t *buffer, uint16_t size,
                                   g2_pair_mgr_msg_t *msg, const void *payload)
{
    return pair_tx_encode(magic, buffer, size, msg, payload, fault_tx_disconnect, fn_tx_disconnect,
                          0x26eu, 8u, 7u, 18u, 0x27eu, false);
}

uint32_t PB_RxUnpairInfo(uint8_t magic, const g2_pair_device_info_t *info)
{
    (void)magic;
    if (info == NULL) {
        raise_fault(&fault_rx_unpair);
        PAIR_LOG(1u, fn_rx_unpair, 0x29bu, 0x04000000u, "POINTER NULL");
        return 2u;
    }
    if (audio_log_flags() & 2u) {
        uint8_t owner = (uint8_t)audio_uart_ring_active();
        audio_log_extended(4u, module_tag, source_file, fn_rx_unpair, 0x2a1u,
                           "PB_RxUnpairInfo: dev=%d role=%s owner=%d", info->dev, role_text(), owner);
    }
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u)) {
        uint8_t owner = (uint8_t)audio_uart_ring_active();
        static const char compact[] = "[pb.devc]PB_RxUnpairInfo: dev=%d role=%s owner=%d";
        (void)compress_log_output(0x10c00000u, compact, compact, info->dev, role_text(), owner);
    }
    if (info->dev == 0u || info->dev == 2u) {
        /* The MAC is printed most-significant byte first (wire bytes 9..4). */
        PAIR_LOG(4u, fn_rx_unpair, 0x2a7u, 0x11800000u,
                 "unpair ringAddr = %02X:%02X:%02X:%02X:%02X:%02X",
                 info->mac[5], info->mac[4], info->mac[3], info->mac[2], info->mac[1], info->mac[0]);
        if (info->mac_size == 6u) {
            audio_dump_hex(label_unpair_mac, 16u, info->mac, info->mac_size);
            PAIR_LOG(2u, fn_rx_unpair, 0x2abu, 0x08000000u,
                     "PB_RxUnpairInfo: global ring cleanup, ignore owner/window state");
            audio_ble_master_cleanup_ring_unpair_4a2c9c(info->mac);
        } else {
            PAIR_LOG(2u, fn_rx_unpair, 0x2afu, 0x08400000u,
                     "PB_RxUnpairInfo: invalid ring mac size=%d, cleanup ring binding anyway",
                     info->mac_size);
            audio_ble_master_cleanup_ring_unpair_4a2c9c(NULL);
        }
    }
    if (info->dev == 2u) {
        PAIR_LOG(4u, fn_rx_unpair, 0x2b4u, 0x10000000u, "unpair glasses");
        ble_ota_mode_set(1u);
        if (app_ble_phone_type_get_4b8128() == 3u) {
            PAIR_LOG(4u, fn_rx_unpair, 0x2b7u, 0x10000000u,
                     "APP_BleConnectPhoneTypeGet() == eDevice_PHONE_IOS");
            APP_BleSlaveDisconnect();
        }
        audio_ble_ring_connect_policy_reset();
    }
    return 0u;
}

uint32_t PB_TxEncodeUnpairInfo(uint8_t magic, uint8_t *buffer, uint16_t size,
                               g2_pair_mgr_msg_t *msg, const void *payload)
{
    return pair_tx_encode(magic, buffer, size, msg, payload, fault_tx_unpair, fn_tx_unpair,
                          0x2cau, 9u, 8u, 18u, 0x2dau, false);
}
