/* Charger common layer, stock D:\01_workspace\s200_ap510b_iar_git\platform\service\charger\charger_common.c.
 * Native 0x4ace10..0x4ad907; literal pools 0x4ad7c8..0x4ad7db, 0x4ad86c..0x4ad87f
 * and 0x4ad908..0x4ad9b7.
 *
 * Keeps the local battery reading (0x20074104), the peer reading and the
 * aggregate SOC/charging state shown to the user (0x20073b30), synchronised
 * with the other temple over sync service 0x105. Aggregate SOC = min(local,
 * peer); both start at -1, so the aggregate stays invalid until both sides
 * reported. At startup a bounded retry (polls 2/4/6/8, give up at poll 16)
 * re-sends while the aggregate SOC is still invalid.
 *
 * CHG_InitBatterySync 0x4acf7c (audio_device_manager_battery_sync_init in
 * drivers/power/charge-battery), CHG_GetSoc 0x4ad8fa and CHG_GetIsCharging
 * 0x4ad900 (app/settings-charge) are already defined elsewhere and are not
 * repeated here. */
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include "g2_charger.h"

/* Aggregate state, RAM 0x20073b30 (zeroed as 24 bytes by CHG_InitBatterySync). */
typedef struct {
    uint8_t reserved[8];    /* +0x00 zeroed, not read by this file */
    g2_battery_info_t peer; /* +0x08 last record received from the peer */
    int32_t soc;            /* +0x10 aggregate SOC, -1 until valid */
    int8_t is_charging;     /* +0x14 aggregate charging flag */
    uint8_t pad[3];
} g2_charger_sync_state_t;
_Static_assert(sizeof(g2_charger_sync_state_t) == 24u, "charger sync state is 24 bytes");

/* View of the charger telemetry record at RAM 0x20073b18 (g2_charger_telemetry,
 * written by the bq27427 gauge and bq25180 charger drivers); this file reads
 * +0x04, +0x0c and +0x15. +0x15 is a charger-side byte of unknown meaning. */
typedef struct {
    uint32_t charge_status; /* +0x00 BQ25180 CHG_STAT */
    int32_t soc;            /* +0x04 gauge SOC percent */
    int32_t voltage_mv;     /* +0x08 */
    int32_t current_ma;     /* +0x0c AverageCurrent, negative while charging */
    int32_t temperature;    /* +0x10 */
    uint8_t unknown_14;
    uint8_t soc_boost;      /* +0x15 ==1 selects the faster 93..95 % compensation */
} g2_charger_telemetry_view_t;
_Static_assert(offsetof(g2_charger_telemetry_view_t, current_ma) == 0x0c, "current at +0xc");
_Static_assert(offsetof(g2_charger_telemetry_view_t, soc_boost) == 0x15, "flag at +0x15");

/* Existing definitions: audio/master-dispatch/charge_sync_*.c. */
extern void *audio_charge_sync_mutex;                    /* RAM 0x20074370 */
extern uint8_t audio_charge_sync_record[24u];            /* RAM 0x20073b30 */
extern uint8_t audio_charge_sync_peer_record[8u];        /* RAM 0x20074104, local reading cache */
extern volatile uint8_t audio_charge_sync_flag_20074f97; /* charging-change debounce count */
extern volatile uint8_t audio_charge_sync_flag_20074f98; /* startup sync pending */
extern volatile uint8_t audio_charge_sync_flag_20074f99; /* startup retries done */
extern volatile uint16_t audio_charge_sync_mode_20074f1a;  /* startup poll count */
extern volatile uint16_t audio_charge_sync_phase_20074f1c; /* poll of next retry */
extern const g2_charger_telemetry_view_t g2_charger_telemetry; /* RAM 0x20073b18 */

#define STATE ((g2_charger_sync_state_t *)(void *)audio_charge_sync_record)
#define LOCAL ((g2_battery_info_t *)(void *)audio_charge_sync_peer_record)
#define DEBOUNCE audio_charge_sync_flag_20074f97
#define INIT_PENDING audio_charge_sync_flag_20074f98
#define RETRY_COUNT audio_charge_sync_flag_20074f99
#define POLL_COUNT audio_charge_sync_mode_20074f1a
#define NEXT_RETRY_POLL audio_charge_sync_phase_20074f1c

#define INIT_SYNC_MAX_POLLS 16u
#define INIT_SYNC_MAX_RETRIES 4u
#define INIT_SYNC_RETRY_INTERVAL 2u
#define NEAR_FULL_SOC 98
#define CHARGING_DEBOUNCE 4u
#define ROLE_PRIMARY 1u

extern uint8_t audio_uart_device_role_get(void);                          /* 0x45a568 */
extern void audio_uart_buffer_zero(void *dst, uint32_t len, uint32_t fill); /* 0x43c0e4 */
extern void *audio_queue_copy_bytes(void *dst, const void *src, uint32_t len); /* 0x439be4 */
extern uint32_t audio_uart_request_send(uint32_t app, const void *data, uint32_t len,
                                        uint32_t flags); /* SendDataToPeer 0x4651e0 */
extern void *osMutexNew(const void *attr);
extern int32_t osMutexAcquire(void *mutex, uint32_t timeout);
extern int32_t osMutexRelease(void *mutex);
extern int32_t osMutexDelete(void *mutex);
extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */

static const char module_tag[] = "charger_common"; /* ROM 0x785720 */
static const char source_file[] = "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\service\\charger\\charger_common.c"; /* ROM 0x6eb9e8 */

static const char fn_init_sync[] = "_CHG_HandleInitSync"; /* ROM 0x77e884 */
static const char sync_done_stop[] = "init sync done: sync soc valid, stop startup timeout retry"; /* ROM 0x712ab4 */
static const char sync_done_stop_short[] = "[charger_common]init sync done: sync soc valid, stop startup timeout retry"; /* ROM 0x6f1d0c */
static const char sync_timeout[] = "init sync timeout: sync soc still invalid, stop startup timeout retry"; /* ROM 0x6f8954 */
static const char sync_timeout_short[] = "[charger_common]init sync timeout: sync soc still invalid, stop startup timeout retry"; /* ROM 0x6e27a8 */
static const char sync_retry[] = "init sync retry %d/%d, next in %d poll"; /* ROM 0x748124 */
static const char sync_retry_short[] = "[charger_common]init sync retry %d/%d, next in %d poll"; /* ROM 0x71c620 */

static const char fn_deinit[] = "CHG_DeinitBatterySync"; /* ROM 0x7759bc */
static const char deinit_text[] = "CHG_DeinitBatterySync"; /* ROM 0x7759d4 */
static const char deinit_short[] = "[charger_common]CHG_DeinitBatterySync"; /* ROM 0x74814c */

static const char local_fail[] = "Failed to get local battery data"; /* ROM 0x7527f0 */
static const char local_fail_short[] = "[charger_common]Failed to get local battery data"; /* ROM 0x72743c */
static const char no_mutex[] = "Sync battery mutex not initialized"; /* ROM 0x752814 */
static const char no_mutex_short[] = "[charger_common]Sync battery mutex not initialized"; /* ROM 0x727470 */
static const char lock_fail[] = "Failed to acquire sync battery mutex"; /* ROM 0x748174 */
static const char lock_fail_short[] = "[charger_common]Failed to acquire sync battery mutex"; /* ROM 0x71c658 */

static const char fn_update_soc[] = "CHG_CompareAndUpdateSoc"; /* ROM 0x7759ec */
static const char soc_changed[] = "soc changed from %d to %d"; /* ROM 0x76a01c */
static const char soc_changed_short[] = "[charger_common]soc changed from %d to %d"; /* ROM 0x73c84c */
static const char sync_done[] = "init sync done: sync soc valid"; /* ROM 0x75e5d0 */
static const char sync_done_short[] = "[charger_common]init sync done: sync soc valid"; /* ROM 0x731e44 */

static const char fn_update_charging[] = "CHG_CompareAndUpdateIsCharging"; /* ROM 0x75e5f0 */
static const char charging_changed[] = "charging state changed from %d to %d"; /* ROM 0x74819c */
static const char charging_changed_short[] = "[charger_common]charging state changed from %d to %d"; /* ROM 0x71c690 */

static const char fn_level_changed[] = "CHG_OnBatteryLevelChanged"; /* ROM 0x76a038 */
static const char level_changed[] = "Battery level changed (role=%d), sending NOTIFY to peer"; /* ROM 0x71c6c8 */
static const char level_changed_short[] = "[charger_common]Battery level changed (role=%d), sending NOTIFY to peer"; /* ROM 0x6f899c */

static const char fn_send[] = "CHG_SendBatteryInfoToPeer"; /* ROM 0x76a054 */
static const char sending[] = "Sending battery sync message: msg_id=%d, soc=%d, is_charging=%d"; /* ROM 0x709964 */
static const char sending_short[] = "[charger_common]Sending battery sync message: msg_id=%d, soc=%d, is_charging=%d"; /* ROM 0x6eba38 */

static const char fn_receive[] = "CHG_ReceiveBatteryInfoFromPeer"; /* ROM 0x75e610 */
static const char invalid_msg[] = "Invalid battery sync message"; /* ROM 0x75e630 */
static const char invalid_msg_short[] = "[charger_common]Invalid battery sync message"; /* ROM 0x731e74 */
static const char received[] = "Receive battery sync from peer: msg_id=%d, soc=%d, is_charging=%d"; /* ROM 0x700a74 */
static const char received_short[] = "[charger_common]Receive battery sync from peer: msg_id=%d, soc=%d, is_charging=%d"; /* ROM 0x6e676c */

static const char fn_request[] = "CHG_RequestNotifyBatteryInfoFromPeer"; /* ROM 0x7481c4 */
static const char requesting[] = "Requesting battery info from peer (role=%d)"; /* ROM 0x73c878 */
static const char requesting_short[] = "[charger_common]Requesting battery info from peer (role=%d)"; /* ROM 0x712af0 */

/* Stock log macro expansion: extended log when flag bit 1 is set, compressed
 * log when bit 0 or bit 2 is set. LOGF needs at least one format argument. */
#define LOG(level, line, mask, fn, text, short_text)                                  \
    do {                                                                              \
        if (audio_log_flags() & 2u)                                                   \
            audio_log_extended((level), module_tag, source_file, (fn), (line), (text)); \
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))                     \
            (void)compress_log_output((mask), (short_text), (short_text));            \
    } while (0)
#define LOGF(level, line, mask, fn, text, short_text, ...)                                         \
    do {                                                                                           \
        if (audio_log_flags() & 2u)                                                                \
            audio_log_extended((level), module_tag, source_file, (fn), (line), (text), __VA_ARGS__); \
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))                                  \
            (void)compress_log_output((mask), (short_text), (short_text), __VA_ARGS__);            \
    } while (0)

bool charger_soc_is_valid(uint32_t soc) {
    return soc < 101u;
}

bool charger_aggregate_soc_is_valid(void) {
    return charger_soc_is_valid((uint32_t)STATE->soc);
}

/* Startup retry step, run from CHG_OnBatteryLevelChanged when nothing changed.
 * Returns 1 when a resend is due now. */
uint32_t _CHG_HandleInitSync(void) {
    if (INIT_PENDING == 0u)
        return 0u;
    if (charger_aggregate_soc_is_valid()) {
        INIT_PENDING = 0u;
        LOG(3u, 0x44u, 0x0c000000u, fn_init_sync, sync_done_stop, sync_done_stop_short);
        return 0u;
    }
    if (POLL_COUNT != 0xffffu)
        POLL_COUNT = (uint16_t)(POLL_COUNT + 1u);
    if (POLL_COUNT >= INIT_SYNC_MAX_POLLS) {
        INIT_PENDING = 0u;
        LOG(2u, 0x4fu, 0x08000000u, fn_init_sync, sync_timeout, sync_timeout_short);
        return 0u;
    }
    if (RETRY_COUNT >= INIT_SYNC_MAX_RETRIES)
        return 0u;
    if (POLL_COUNT < NEXT_RETRY_POLL)
        return 0u;
    RETRY_COUNT = (uint8_t)(RETRY_COUNT + 1u);
    NEXT_RETRY_POLL = (uint16_t)(POLL_COUNT + INIT_SYNC_RETRY_INTERVAL);
    LOGF(3u, 0x5du, 0x0cc00000u, fn_init_sync, sync_retry, sync_retry_short,
         RETRY_COUNT, INIT_SYNC_MAX_RETRIES, INIT_SYNC_RETRY_INTERVAL);
    return 1u;
}

void CHG_DeinitBatterySync(void) {
    LOG(4u, 0x84u, 0x10000000u, fn_deinit, deinit_text, deinit_short);
    if (audio_charge_sync_mutex != NULL) {
        (void)osMutexDelete(audio_charge_sync_mutex);
        audio_charge_sync_mutex = NULL;
    }
    CB_CHG_DeinitBatInfoCallbacks();
}

/* The fresh reading only gates the update; the aggregate uses the cached local
 * reading. Logs and notifies event 0 even when the value is unchanged. */
void CHG_CompareAndUpdateSoc(void) {
    g2_battery_info_t info;
    audio_uart_buffer_zero(&info, sizeof info, 0u);
    if (charger_get_local_battery_info(&info) != 0) {
        LOG(1u, 0x94u, 0x04000000u, fn_update_soc, local_fail, local_fail_short);
        return;
    }
    if (audio_charge_sync_mutex == NULL) {
        LOG(1u, 0x99u, 0x04000000u, fn_update_soc, no_mutex, no_mutex_short);
        return;
    }
    if (osMutexAcquire(audio_charge_sync_mutex, UINT32_MAX) != 0) {
        LOG(1u, 0x9fu, 0x04000000u, fn_update_soc, lock_fail, lock_fail_short);
        return;
    }
    g2_charger_sync_state_t *state = STATE;
    int32_t soc = LOCAL->soc < state->peer.soc ? LOCAL->soc : state->peer.soc;
    LOGF(3u, 0xacu, 0x0c800000u, fn_update_soc, soc_changed, soc_changed_short, state->soc, soc);
    state->soc = soc;
    (void)osMutexRelease(audio_charge_sync_mutex);
    if (INIT_PENDING != 0u && charger_aggregate_soc_is_valid()) {
        INIT_PENDING = 0u;
        LOG(3u, 0xb7u, 0x0c000000u, fn_update_soc, sync_done, sync_done_short);
    }
    (void)CB_CHG_NotifyBatInfo(G2_BAT_INFO_EVENT_SOC, (uint32_t)state->soc);
}

/* Charging is shown when one side charges and the other charges or is full. */
void CHG_CompareAndUpdateIsCharging(void) {
    g2_battery_info_t info;
    audio_uart_buffer_zero(&info, sizeof info, 0u);
    if (charger_get_local_battery_info(&info) != 0) {
        LOG(1u, 0xc5u, 0x04000000u, fn_update_charging, local_fail, local_fail_short);
        return;
    }
    if (audio_charge_sync_mutex == NULL) {
        LOG(1u, 0xcau, 0x04000000u, fn_update_charging, no_mutex, no_mutex_short);
        return;
    }
    if (osMutexAcquire(audio_charge_sync_mutex, UINT32_MAX) != 0) {
        LOG(1u, 0xd0u, 0x04000000u, fn_update_charging, lock_fail, lock_fail_short);
        return;
    }
    g2_charger_sync_state_t *state = STATE;
    bool changed = false;
    int8_t charging = 0;
    if (state->peer.is_charging == 1) {
        if (LOCAL->is_charging == 1 || LOCAL->soc == 100)
            charging = 1;
    } else if (LOCAL->is_charging == 1) {
        if (state->peer.is_charging == 1 || state->peer.soc == 100)
            charging = 1;
    }
    if (charging != state->is_charging) {
        LOGF(3u, 0xe9u, 0x0c800000u, fn_update_charging, charging_changed, charging_changed_short,
             (int32_t)state->is_charging, (int32_t)charging);
        state->is_charging = charging;
        changed = true;
    }
    (void)osMutexRelease(audio_charge_sync_mutex);
    if (changed)
        (void)CB_CHG_NotifyBatInfo(G2_BAT_INFO_EVENT_CHARGING, (uint32_t)(int32_t)state->is_charging);
}

/* Charger poll hook. SOC changes are taken at once; a charging-flag change at
 * gauge SOC >= 98 must persist for 4 polls. Role 1 pushes NOTIFY, the other
 * side asks the peer for one. */
void CHG_OnBatteryLevelChanged(void) {
    uint8_t role = audio_uart_device_role_get();
    g2_battery_info_t info;
    audio_uart_buffer_zero(&info, sizeof info, 0u);
    (void)charger_get_local_battery_info(&info);
    g2_battery_info_t *local = LOCAL;
    bool soc_changed = false;
    bool charging_changed = false;
    if (local->soc != info.soc) {
        local->soc = info.soc;
        soc_changed = true;
    }
    if (local->is_charging != info.is_charging) {
        DEBOUNCE = (uint8_t)(DEBOUNCE + 1u);
        if (g2_charger_telemetry.soc < NEAR_FULL_SOC || DEBOUNCE >= CHARGING_DEBOUNCE) {
            DEBOUNCE = 0u;
            local->is_charging = info.is_charging;
            charging_changed = true;
        }
    } else {
        DEBOUNCE = 0u;
    }
    if (!(soc_changed || charging_changed) && _CHG_HandleInitSync() != 1u)
        return;
    LOGF(4u, 0x118u, 0x10400000u, fn_level_changed, level_changed, level_changed_short, role);
    if (role == ROLE_PRIMARY)
        CHG_SendBatteryInfoToPeer(G2_BAT_SYNC_NOTIFY);
    else
        CHG_RequestNotifyBatteryInfoFromPeer();
}

/* Sends the cached local reading; the fresh reading only gates the send. */
void CHG_SendBatteryInfoToPeer(uint8_t msg_id) {
    g2_battery_sync_msg_t msg;
    g2_battery_info_t info;
    audio_uart_buffer_zero(&msg, sizeof msg, 0u);
    audio_uart_buffer_zero(&info, sizeof info, 0u);
    if (charger_get_local_battery_info(&info) != 0) {
        LOG(1u, 300u, 0x04000000u, fn_send, local_fail, local_fail_short);
        return;
    }
    uint8_t role = audio_uart_device_role_get();
    msg.msg_id = msg_id;
    msg.payload_len = G2_BAT_INFO_PAYLOAD_LEN;
    msg.src_role = role;
    msg.dst_role = role == ROLE_PRIMARY ? 2u : 1u;
    const g2_battery_info_t *local = LOCAL;
    (void)audio_queue_copy_bytes(&msg.info, local, sizeof msg.info);
    LOGF(4u, 0x13au, 0x10c00000u, fn_send, sending, sending_short,
         msg_id, local->soc, (int32_t)local->is_charging);
    (void)audio_uart_request_send(G2_BAT_SYNC_SERVICE, &msg, sizeof msg, 0u);
}

/* Called by UX_BatterySyncHandler 0x5f958c for msg_id 2 and 3. */
void CHG_ReceiveBatteryInfoFromPeer(const g2_battery_sync_msg_t *msg) {
    if (msg == NULL) {
        LOG(1u, 0x146u, 0x04000000u, fn_receive, invalid_msg, invalid_msg_short);
        return;
    }
    LOGF(4u, 0x14bu, 0x10c00000u, fn_receive, received, received_short,
         msg->msg_id, msg->info.soc, (int32_t)msg->info.is_charging);
    (void)audio_uart_device_role_get();
    if (audio_charge_sync_mutex == NULL) {
        LOG(1u, 0x151u, 0x04000000u, fn_receive, no_mutex, no_mutex_short);
        return;
    }
    if (osMutexAcquire(audio_charge_sync_mutex, UINT32_MAX) != 0) {
        LOG(1u, 0x157u, 0x04000000u, fn_receive, lock_fail, lock_fail_short);
        return;
    }
    g2_charger_sync_state_t *state = STATE;
    state->peer.soc = msg->info.soc;
    state->peer.is_charging = msg->info.is_charging;
    (void)osMutexRelease(audio_charge_sync_mutex);
    if (msg->msg_id == G2_BAT_SYNC_NOTIFY) {
        CHG_SendBatteryInfoToPeer(G2_BAT_SYNC_RESPONSE);
        CHG_CompareAndUpdateSoc();
        CHG_CompareAndUpdateIsCharging();
    } else if (msg->msg_id == G2_BAT_SYNC_RESPONSE) {
        CHG_CompareAndUpdateSoc();
        CHG_CompareAndUpdateIsCharging();
    }
}

void CHG_RequestNotifyBatteryInfoFromPeer(void) {
    g2_battery_sync_msg_t msg;
    audio_uart_buffer_zero(&msg, sizeof msg, 0u);
    uint8_t role = audio_uart_device_role_get();
    msg.msg_id = G2_BAT_SYNC_REQUEST_NOTIFY;
    msg.payload_len = 0u;
    msg.src_role = role;
    msg.dst_role = role == ROLE_PRIMARY ? 2u : 1u;
    LOGF(4u, 0x18eu, 0x10400000u, fn_request, requesting, requesting_short, role);
    (void)audio_uart_request_send(G2_BAT_SYNC_SERVICE, &msg, sizeof msg, 0u);
}

/* Gauge SOC with the stock top-end compensation:
 * 93->93/94, 94->95/96, 95->97/98 (second value when soc_boost == 1),
 * 96->99, >=97->100. Charging means negative gauge current. */
int32_t charger_get_local_battery_info(g2_battery_info_t *info) {
    const g2_charger_telemetry_view_t *dev = &g2_charger_telemetry;
    if (info == NULL)
        return -1;
    info->soc = dev->soc;
    if (dev->soc == 93) {
        if (dev->soc_boost == 1u)
            info->soc = 94;
    } else if (dev->soc == 94) {
        info->soc = dev->soc_boost == 1u ? 96 : 95;
    } else if (dev->soc == 95) {
        info->soc = dev->soc_boost == 1u ? 98 : 97;
    } else if (dev->soc == 96) {
        info->soc = 99;
    } else if (dev->soc > 96) {
        info->soc = 100;
    }
    info->is_charging = dev->current_ma < 0;
    return 0;
}
