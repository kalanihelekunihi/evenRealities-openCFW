/* ANCC notification store, stock
 * D:\01_workspace\s200_ap510b_iar_git\platform\service\message_notify\service_ancc.c.
 * Native 0x4972a2..0x4972c1 (state byte accessors), 0x4972c2..0x49739d (SVC_ANCC_Init),
 * 0x49758e..0x497937 (Find/Add/Remove notification) and 0x497960..0x497ce9
 * (SVC_ANCC_NotificationMsgTreat); literal pools 0x497938..0x49795f, 0x497cec..0x497db3.
 *
 * Ten 0x304-byte records live at RAM 0x20104c54. Each holds the 0x2fc-byte ANCS
 * notification as received from the BLE ANCC client, an in-use flag at +0x2fc and a
 * next pointer at +0x300; the head of the in-use list is at RAM 0x20074918 and the
 * record count at 0x2007500d, all guarded by the mutex at 0x2007491c. When all ten
 * records are in use, Add recycles the oldest (head) record to the tail.
 * Not here: SVC_ANCC_Clear 0x4973f4 (app/even-ai/even_ai_sync_remote_4973f4.c),
 * SVC_ANCC_GetNotifCount 0x4974d4 (app/settings-unread/display_settings_unread_count.c),
 * service_ancc_state_sync 0x497cf0 (app/even-ai/even_ai_ancc_state_sync_497cf0.c). */
#include <stdint.h>
#include <stddef.h>

/* ANCS notification as cached by the BLE ANCC client (same 0x2fc-byte layout as
 * the Android notification record, app/a-13-android-notify). */
typedef struct {
    uint32_t uid;              /* +0x000 */
    uint8_t category_id;       /* +0x004 ANCS CategoryID (0..11) */
    uint8_t event_id;          /* +0x005 ANCS EventID (0..2) */
    uint8_t event_flags;       /* +0x006 ANCS EventFlags (5 bits) */
    uint8_t reserved_007;
    char app_identifier[64];   /* +0x008 */
    char display_name[32];     /* +0x048 */
    char title[64];            /* +0x068 */
    char subtitle[64];         /* +0x0a8 */
    char message[512];         /* +0x0e8 */
    char date[16];             /* +0x2e8 */
    uint8_t action;            /* +0x2f8 */
    uint8_t reserved_2f9[3];
} g2_ancc_notification_t;
_Static_assert(offsetof(g2_ancc_notification_t, date) == 0x2e8u, "date");
_Static_assert(sizeof(g2_ancc_notification_t) == 0x2fcu, "ANCS notification");

typedef struct g2_ancc_record {
    g2_ancc_notification_t notif;   /* +0x000 */
    uint8_t used;                   /* +0x2fc */
    uint8_t reserved_2fd[3];
    struct g2_ancc_record *next;    /* +0x300 */
} g2_ancc_record_t;
_Static_assert(offsetof(g2_ancc_record_t, next) == 0x300u, "next");
_Static_assert(sizeof(g2_ancc_record_t) == 0x304u, "ANCC record");

#define ANCC_RECORD_COUNT 10

extern uint8_t audio_ble_ancc_service_state[];             /* RAM 0x200036c8 */
extern void *audio_settings_ancc_mutex;                     /* RAM 0x2007491c */
extern uint8_t audio_settings_ancc_count;                   /* RAM 0x2007500d */
extern uint8_t g2_audio_ancc_records_20104c54[0x1e28];      /* RAM 0x20104c54 */
extern uint32_t g2_audio_ancc_sequence_20074918;            /* RAM 0x20074918, list head */

extern void *osMutexNew(const void *attr);                  /* 0x44971c */
extern int32_t osMutexAcquire(void *mutex, uint32_t timeout); /* 0x4497b6 */
extern int32_t osMutexRelease(void *mutex);                 /* 0x44981c */
extern void audio_uart_buffer_zero(void *dst, uint32_t len, uint32_t fill); /* 0x43c0e4 */
extern void *audio_queue_copy_bytes(void *dst, const void *src, uint32_t len); /* 0x439be4 */
extern uint32_t g2_log_module_length(const char *text);     /* 0x44a43c strlen */
extern void CB_ANCC_InitMsgCountCallbacks(void);            /* 0x4e1a48 */
extern void audio_even_ai_ancc_display_clear_4e1af8(uint32_t event, uint32_t count); /* CB_ANCC_NotifyMsgCount */
extern uint8_t onboarding_active_flag_467f08(void);         /* 0x467f08 calibration_ui_status */
extern uint32_t settings_get_terminal_mode(void);           /* 0x46c630 */
extern uint8_t audio_uart_device_role_get(void);            /* 0x45a568, 1 = master */
extern uint32_t audio_log_wake_allowed(void);               /* 0x443484 */
extern uint32_t display_foreground_app_running_4434b4(void);
extern uint32_t audio_quicklist_refresh_enabled_4434d0(uint32_t app);
extern void audio_message_notify_set_startup_4e1b28(uint8_t value);
extern void audio_uart_master_display_refresh(uint32_t app, const void *data, uint16_t len, uint32_t flags); /* 0x464bb2 */
extern void audio_uart_master_display_start(uint32_t app, const void *data, uint16_t len, uint32_t flags);   /* 0x464b2e */
extern uint32_t audio_log_flags(void);                      /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */

static const char module_tag[] = "svc.ancc"; /* ROM 0x78be04 */
static const char source_file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\service\\message_notify\\service_ancc.c"; /* ROM 0x6e9a9c */
static const char init_fn[] = "SVC_ANCC_Init"; /* ROM 0x788690 */
static const char find_fn[] = "SVC_ANCC_FindNotification"; /* ROM 0x770b30 */
static const char add_fn[] = "SVC_ANCC_AddNotification"; /* ROM 0x770b4c */
static const char remove_fn[] = "SVC_ANCC_RemoveNotification"; /* ROM 0x770b68 */
static const char treat_fn[] = "SVC_ANCC_NotificationMsgTreat"; /* ROM 0x764870 */
static const char create_failed[] = "Failed to create ANCC message mutex"; /* ROM 0x75906c */
static const char create_failed_short[] = "[svc.ancc]Failed to create ANCC message mutex"; /* ROM 0x737bd4 */
static const char init_acquire[] = "Failed to acquire ANCC message mutex during init"; /* ROM 0x72cdd0 */
static const char init_acquire_short[] = "[svc.ancc]Failed to acquire ANCC message mutex during init"; /* ROM 0x71816c */
static const char no_mutex[] = "ANCC message mutex not initialized"; /* ROM 0x759090 */
static const char no_mutex_short[] = "[svc.ancc]ANCC message mutex not initialized"; /* ROM 0x737c04 */
static const char find_acquire[] = "Failed to acquire ANCC message mutex during find notification"; /* ROM 0x70e824 */
static const char find_acquire_short[] = "[svc.ancc]Failed to acquire ANCC message mutex during find notification"; /* ROM 0x6fca04 */
static const char add_acquire[] = "Failed to acquire ANCC message mutex during add notification"; /* ROM 0x70e864 */
static const char add_acquire_short[] = "[svc.ancc]Failed to acquire ANCC message mutex during add notification"; /* ROM 0x6fca4c */
static const char remove_acquire[] = "Failed to acquire ANCC message mutex during remove notification"; /* ROM 0x70e8a4 */
static const char remove_acquire_short[] = "[svc.ancc]Failed to acquire ANCC message mutex during remove notification"; /* ROM 0x6f5b64 */
static const char invalid_msg[] = "Invalid message"; /* ROM 0x7886b0 */
static const char invalid_msg_short[] = "[svc.ancc]Invalid message"; /* ROM 0x770b84 */
static const char add_failed[] = "Failed to add notification"; /* ROM 0x770ba0 */
static const char add_failed_short[] = "[svc.ancc]Failed to add notification"; /* ROM 0x74d7b4 */
static const char received[] = "******************Notification Received**********************"; /* ROM 0x70e8e4 */
static const char received_short[] = "[svc.ancc]******************Notification Received**********************"; /* ROM 0x6fca94 */
static const char app_id_fmt[] = "* app_id          = %s"; /* ROM 0x77b284 */
static const char app_id_short[] = "[svc.ancc]* app_id          = %s"; /* ROM 0x7590b4 */
static const char app_name_fmt[] = "* app_display_name= %s"; /* ROM 0x77b29c */
static const char app_name_short[] = "[svc.ancc]* app_display_name= %s"; /* ROM 0x7590d8 */
static const char calib_warn[] = "warn: can not show notification, calibration_ui_status = %d"; /* ROM 0x7181e4 */
static const char calib_warn_short[] = "[svc.ancc]warn: can not show notification, calibration_ui_status = %d"; /* ROM 0x6fcadc */
static const char terminal_mode[] = "terminal mode is enabled, no need to show notification"; /* ROM 0x722510 */
static const char terminal_mode_short[] = "[svc.ancc]terminal mode is enabled, no need to show notification"; /* ROM 0x70533c */

static void log0(uint8_t level, const char *fn, uint32_t line, const char *msg, const char *msg_short)
{
    if (audio_log_flags() & 2u)
        audio_log_extended(level, module_tag, source_file, fn, line, msg);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compress_log_output((uint32_t)level << 26, msg_short, msg_short);
}

static g2_ancc_record_t *records(void)
{
    return (g2_ancc_record_t *)(void *)g2_audio_ancc_records_20104c54;
}

static g2_ancc_record_t *list_head(void)
{
    return (g2_ancc_record_t *)(uintptr_t)g2_audio_ancc_sequence_20074918;
}

static void set_list_head(g2_ancc_record_t *record)
{
    g2_audio_ancc_sequence_20074918 = (uint32_t)(uintptr_t)record;
}

/* ANCC service state record (RAM 0x200036c8): +0 enable, +1 notification display
 * enable, +3 interrupt-foreground flag, +4 stored by service_ancc_state_byte4_set. */
uint8_t service_ancc_state_byte0_get(void)
{
    return audio_ble_ancc_service_state[0];
}

uint8_t service_ancc_state_byte1_get(void)
{
    return audio_ble_ancc_service_state[1];
}

uint8_t service_ancc_state_byte4_get(void)
{
    return audio_ble_ancc_service_state[4];
}

/* SVC_ANCC_Init: create the mutex once, then clear all records under it. */
void service_ancc_init(void)
{
    if (audio_settings_ancc_mutex == NULL) {
        audio_settings_ancc_mutex = osMutexNew(NULL);
        if (audio_settings_ancc_mutex == NULL) {
            log0(1u, init_fn, 99u, create_failed, create_failed_short);
            return;
        }
    }
    if (osMutexAcquire(audio_settings_ancc_mutex, 1000u) != 0) {
        log0(1u, init_fn, 106u, init_acquire, init_acquire_short);
        return;
    }
    audio_uart_buffer_zero(g2_audio_ancc_records_20104c54, sizeof(g2_ancc_record_t) * ANCC_RECORD_COUNT, 0u);
    set_list_head(NULL);
    audio_settings_ancc_count = 0u;
    (void)osMutexRelease(audio_settings_ancc_mutex);
    CB_ANCC_InitMsgCountCallbacks();
}

/* SVC_ANCC_FindNotification: the index-th record of the in-use list, or NULL. */
g2_ancc_record_t *service_ancc_record_find(uint8_t index)
{
    void *mutex = audio_settings_ancc_mutex;
    if (mutex == NULL) {
        log0(1u, find_fn, 197u, no_mutex, no_mutex_short);
        return NULL;
    }
    if (osMutexAcquire(mutex, UINT32_MAX) != 0) {
        log0(1u, find_fn, 202u, find_acquire, find_acquire_short);
        return NULL;
    }
    if (index >= audio_settings_ancc_count) {
        (void)osMutexRelease(audio_settings_ancc_mutex);
        return NULL;
    }
    g2_ancc_record_t *record = list_head();
    if (record == NULL) {
        (void)osMutexRelease(audio_settings_ancc_mutex);
        return NULL;
    }
    for (uint8_t i = 0u; i < index; i++) {
        if (record->next == NULL) {
            (void)osMutexRelease(audio_settings_ancc_mutex);
            return NULL;
        }
        record = record->next;
    }
    (void)osMutexRelease(audio_settings_ancc_mutex);
    return record;
}

/* SVC_ANCC_AddNotification: take a free slot and append it to the list (count++,
 * message-count callbacks notified); with no free slot, move the oldest record to
 * the tail and reuse it without changing the count. */
g2_ancc_record_t *service_ancc_record_allocate(void)
{
    if (audio_settings_ancc_mutex == NULL) {
        log0(1u, add_fn, 235u, no_mutex, no_mutex_short);
        return NULL;
    }
    if (osMutexAcquire(audio_settings_ancc_mutex, UINT32_MAX) != 0) {
        log0(1u, add_fn, 240u, add_acquire, add_acquire_short);
        return NULL;
    }
    g2_ancc_record_t *table = records();
    for (int32_t i = 0; i < ANCC_RECORD_COUNT; i++) {
        if (table[i].used != 0u)
            continue;
        audio_uart_buffer_zero(&table[i], sizeof(g2_ancc_record_t), 0u);
        table[i].used = 1u;
        if (list_head() == NULL) {
            set_list_head(&table[i]);
        } else {
            g2_ancc_record_t *tail = list_head();
            while (tail->next != NULL)
                tail = tail->next;
            tail->next = &table[i];
        }
        audio_settings_ancc_count++;
        uint8_t count = audio_settings_ancc_count;
        (void)osMutexRelease(audio_settings_ancc_mutex);
        audio_even_ai_ancc_display_clear_4e1af8(0u, count);
        return &table[i];
    }
    if (list_head() == NULL) {
        (void)osMutexRelease(audio_settings_ancc_mutex);
        return NULL;
    }
    g2_ancc_record_t *oldest = list_head();
    set_list_head(oldest->next);
    audio_uart_buffer_zero(oldest, sizeof(g2_ancc_record_t), 0u);
    oldest->used = 1u;
    oldest->next = NULL;
    g2_ancc_record_t *tail = list_head();
    while (tail->next != NULL)
        tail = tail->next;
    tail->next = oldest;
    (void)osMutexRelease(audio_settings_ancc_mutex);
    return oldest;
}

/* SVC_ANCC_RemoveNotification: unlink record (searching at most count nodes),
 * free it and notify the new count. */
void service_ancc_record_remove(g2_ancc_record_t *record)
{
    if (record == NULL)
        return;
    if (audio_settings_ancc_mutex == NULL) {
        log0(1u, remove_fn, 311u, no_mutex, no_mutex_short);
        return;
    }
    if (osMutexAcquire(audio_settings_ancc_mutex, UINT32_MAX) != 0) {
        log0(1u, remove_fn, 316u, remove_acquire, remove_acquire_short);
        return;
    }
    g2_ancc_record_t *previous = NULL;
    g2_ancc_record_t *node = list_head();
    for (uint8_t i = 0u; node != NULL && i < audio_settings_ancc_count; i++) {
        if (node == record) {
            if (previous == NULL)
                set_list_head(node->next);
            else
                previous->next = node->next;
            node->used = 0u;
            node->next = NULL;
            audio_settings_ancc_count--;
            uint8_t count = audio_settings_ancc_count;
            (void)osMutexRelease(audio_settings_ancc_mutex);
            audio_even_ai_ancc_display_clear_4e1af8(0u, count);
            return;
        }
        previous = node;
        node = node->next;
    }
    (void)osMutexRelease(audio_settings_ancc_mutex);
}

/* SVC_ANCC_NotificationMsgTreat: store a received ANCS notification and, on the
 * master with notification display enabled, start (or refresh) the notification
 * app on the display. The stock body also switches on category_id, event_id and
 * each of the 5 event_flags bits and measures the text fields, with every case
 * body compiled out; only the strlen calls survive. */
void service_ancc_notification_process(const void *message, uint16_t length)
{
    if (message == NULL || length == 0u) {
        log0(1u, treat_fn, 399u, invalid_msg, invalid_msg_short);
        return;
    }
    g2_ancc_record_t *record = service_ancc_record_allocate();
    if (record == NULL) {
        log0(1u, treat_fn, 405u, add_failed, add_failed_short);
        return;
    }
    (void)audio_queue_copy_bytes(record, message, sizeof(g2_ancc_notification_t));
    record->used = 1u;
    log0(3u, treat_fn, 411u, received, received_short);
    if (audio_log_flags() & 2u)
        audio_log_extended(3u, module_tag, source_file, treat_fn, 417u, app_id_fmt,
                           record->notif.app_identifier);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compress_log_output(0x0c400000u, app_id_short, app_id_short,
                                  record->notif.app_identifier);
    if (audio_log_flags() & 2u)
        audio_log_extended(3u, module_tag, source_file, treat_fn, 418u, app_name_fmt,
                           record->notif.display_name);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compress_log_output(0x0c400000u, app_name_short, app_name_short,
                                  record->notif.display_name);
    (void)g2_log_module_length(record->notif.title);
    (void)g2_log_module_length(record->notif.subtitle);
    (void)g2_log_module_length(record->notif.message);
    (void)g2_log_module_length(record->notif.date);

    if (service_ancc_state_byte1_get() != 1u)
        return;
    if (onboarding_active_flag_467f08() == 1u) {
        if (audio_log_flags() & 2u)
            audio_log_extended(2u, module_tag, source_file, treat_fn, 532u, calib_warn,
                               (uint32_t)onboarding_active_flag_467f08());
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compress_log_output(0x08400000u, calib_warn_short, calib_warn_short,
                                      (uint32_t)onboarding_active_flag_467f08());
        return;
    }
    if (settings_get_terminal_mode() != 0u) {
        log0(2u, treat_fn, 537u, terminal_mode, terminal_mode_short);
        return;
    }
    if (audio_uart_device_role_get() != 1u)
        return;
    uint8_t frame[6];
    uint8_t n = 0u;
    audio_uart_buffer_zero(frame, sizeof(frame), 0u);
    if (audio_log_wake_allowed() == 1u && audio_quicklist_refresh_enabled_4434d0(4u) == 1u) {
        /* Notification app already in front: refresh it. */
        frame[n++] = 4u;
        frame[n++] = 1u;
        audio_uart_master_display_refresh(4u, frame, sizeof(frame), 0u);
        return;
    }
    if (audio_ble_ancc_service_state[3] == 0u || audio_log_wake_allowed() == 0u ||
        display_foreground_app_running_4434b4() == 0u ||
        audio_quicklist_refresh_enabled_4434d0(1u) == 1u) {
        audio_message_notify_set_startup_4e1b28(1u);
        frame[n++] = 1u;
        frame[n++] = 3u;
        audio_uart_master_display_start(4u, frame, sizeof(frame), 0u);
    }
}
