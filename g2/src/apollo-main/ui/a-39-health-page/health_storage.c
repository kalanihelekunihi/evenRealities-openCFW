/* Health page storage lock and common data handler, stock
 * D:\01_workspace\s200_ap510b_iar_git\app\gui\health\health.c.
 * Native 0x4ffbd8..0x4ffdcf; literal pool 0x4ffdd0..0x4ffe13.
 *
 * Health_common_data_handler is the 0x0e entry of the UI registry table
 * (system/ui-registry/ui_registry_table.c, extern name
 * audio_uart_registry_callback_4ffca2). Event 0 carries a health protobuf
 * frame from the app; when it parses, the master side asks the display for a
 * refresh of app 1 if the health page is running. Event 5 carries a one-byte
 * command, of which only 1 is known (and needs no action here). */
#include <stdint.h>
#include <stddef.h>

typedef struct {
    uint8_t bytes[8];
} g2_health_refresh_req_t;

extern void *g2_health_storage_mutex; /* RAM 0x20074658 */

extern void *osMutexNew(const void *attr);                   /* 0x44971c */
extern int32_t osMutexAcquire(void *mutex, uint32_t timeout); /* 0x4497b6 */
extern int32_t osMutexRelease(void *mutex);                  /* 0x44981c */
extern uint32_t APP_PbRxHealthFrameDataProcess_55a350(const uint8_t *data, uint16_t len); /* pb_service_health.c */
extern uint8_t audio_uart_device_role_get(void);             /* 0x45a568, 1 = master */
extern uint32_t audio_log_wake_allowed(void);                /* 0x443484 */
extern uint32_t audio_quicklist_refresh_enabled_4434d0(uint32_t app);
extern int32_t audio_uart_master_display_refresh(uint32_t app, const void *data, uint16_t len,
                                                 uint32_t flags); /* RequestDisplayReflash 0x464bb2 */
extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */

#define LOG_E(level, fn, line, ...)                                                          \
    do {                                                                                     \
        if (audio_log_flags() & 2u)                                                          \
            audio_log_extended((level), module_tag, source_file, (fn), (line), __VA_ARGS__); \
    } while (0)
#define LOG_C(code, ...)                                                \
    do {                                                                \
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))       \
            (void)compress_log_output((code), __VA_ARGS__);             \
    } while (0)

static const char module_tag[] = "health.page"; /* ROM 0x78ab14 */
static const char source_file[] = "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\health\\health.c"; /* ROM 0x7158e0 */
static const char init_fn[] = "health_data_mutex_init";        /* ROM 0x7779cc */
static const char lock_fn[] = "health_lock_storage";           /* ROM 0x77f734 */
static const char handler_fn[] = "Health_common_data_handler"; /* ROM 0x76bcfc */
static const char mutex_failed[] = "Failed to create health storage mutex"; /* ROM 0x74a3d4 */
static const char mutex_failed_short[] = "[health.page]Failed to create health storage mutex"; /* ROM 0x729eb0 */
static const char mutex_null[] = "mutex is NULL"; /* ROM 0x786090 */
static const char mutex_null_short[] = "[health.page]mutex is NULL"; /* ROM 0x76bce0 */
static const char bad_raw[] = "Invalid raw_data or len"; /* ROM 0x7779e4 */
static const char bad_raw_short[] = "[health.page]Invalid raw_data or len"; /* ROM 0x74a3fc */
static const char bad_cmd[] = "Unknown command: %d"; /* ROM 0x77f748 */
static const char bad_cmd_short[] = "[health.page]Unknown command: %d"; /* ROM 0x754af4 */
static const char bad_event[] = "Unknown event type: %d"; /* ROM 0x7779fc */
static const char bad_event_short[] = "[health.page]Unknown event type: %d"; /* ROM 0x754b18 */
static const g2_health_refresh_req_t refresh_req = {{6u, 0u, 0u, 0u, 0u, 0u, 0u, 0u}}; /* ROM 0x78d704 */

int32_t health_data_mutex_init(void)
{
    if (g2_health_storage_mutex == NULL) {
        g2_health_storage_mutex = osMutexNew(NULL);
        if (g2_health_storage_mutex == NULL) {
            LOG_E(1u, init_fn, 0x28u, mutex_failed);
            LOG_C(0x04000000u, mutex_failed_short, mutex_failed_short);
            return -1;
        }
    }
    return 0;
}

/* Returns 1 when the storage lock was taken. */
uint8_t health_lock_storage(void)
{
    if (g2_health_storage_mutex == NULL) {
        LOG_E(2u, lock_fn, 0x38u, mutex_null);
        LOG_C(0x08000000u, mutex_null_short, mutex_null_short);
        return 0u;
    }
    return (uint8_t)(osMutexAcquire(g2_health_storage_mutex, 0xffffffffu) == 0);
}

void health_unlock_storage(void)
{
    if (g2_health_storage_mutex != NULL)
        (void)osMutexRelease(g2_health_storage_mutex);
}

uint32_t Health_common_data_handler(uint32_t event, const uint8_t *data, uint32_t len)
{
    g2_health_refresh_req_t req;
    uint8_t cmd;

    (void)health_data_mutex_init();
    if (event == 0u) {
        if (APP_PbRxHealthFrameDataProcess_55a350(data, (uint16_t)len) == 0u &&
            audio_uart_device_role_get() == 1u && audio_log_wake_allowed() == 1u &&
            audio_quicklist_refresh_enabled_4434d0(1u) == 1u) {
            req = refresh_req;
            (void)audio_uart_master_display_refresh(1u, &req, 6u, 0u);
        }
    } else if (event == 5u) {
        if (data == NULL || len == 0u) {
            LOG_E(2u, handler_fn, 0x6au, bad_raw);
            LOG_C(0x08000000u, bad_raw_short, bad_raw_short);
        } else {
            cmd = data[0];
            if (cmd != 1u) {
                LOG_E(2u, handler_fn, 0xa1u, bad_cmd, cmd);
                LOG_C(0x08400000u, bad_cmd_short, bad_cmd_short, cmd);
            }
        }
    } else {
        LOG_E(2u, handler_fn, 0xaau, bad_event, event);
        LOG_C(0x08400000u, bad_event_short, bad_event_short, event);
    }
    return 0u;
}
