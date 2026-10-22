/* System time sync service, stock
 * D:\01_workspace\s200_ap510b_iar_git\platform\service\time\service_time.c
 * (log tag "srv.time"). Native 0x44a192..0x44a3ef, literal pool 0x44a3f0..0x44a43b.
 *
 * This unit: service_time_calendar_to_epoch_wrapper 0x44a192, SVC_SystemTimeSync
 * 0x44a1fe, RPC_SystemTimeSync 0x44a2b2 and service_time_sync_callback 0x44a3b4.
 * service_time_rtc_refresh 0x44a1ea is drivers/peripherals/ring-rtc
 * (audio_uart_ring_rtc_refresh); the calendar helpers 0x449ed4..0x44a1c6 live
 * under app/time-epoch, system/log/log-datetime and audio-log-format.
 *
 * Timezone: signed byte at +8 of the settings record behind pointer cell
 * RAM 0x200036fc, in quarter hours (local = UTC + zone * 900 s).
 * RPC_SystemTimeSync runs only on the role-1 (master) side: it sends a
 * 16-byte record on service 0x100 and re-arms itself every 30 s. */
#include <stdint.h>
#include <stddef.h>

/* am_hal_rtc_time_t word layout (40 bytes). */
typedef struct {
    uint32_t read_error; /* +0 */
    uint32_t weekday;    /* +4 index into the "Sun".."Sat" table */
    uint32_t century;    /* +8 */
    uint32_t year;       /* +12 years since 2000 */
    uint32_t month;      /* +16 */
    uint32_t day;        /* +20 */
    uint32_t hour;       /* +24 */
    uint32_t minute;     /* +28 */
    uint32_t second;     /* +32 */
    uint32_t hundredths; /* +36 */
} g2_rtc_time_t;
_Static_assert(sizeof(g2_rtc_time_t) == 40u, "am_hal_rtc_time_t");

/* Peer time-sync record sent on service 0x100 (template ROM 0x788f10). */
typedef struct {
    uint8_t header[4]; /* +0  80 00 08 00 from the template */
    uint8_t role;      /* +4  sender role */
    uint8_t peer_role; /* +5  2 when the sender is role 1, else 1 */
    uint8_t pad[2];    /* +6 */
    uint32_t epoch;    /* +8  local RTC seconds */
    int32_t zone;      /* +12 quarter-hour timezone */
} g2_time_sync_record_t;
_Static_assert(sizeof(g2_time_sync_record_t) == 16u, "time sync record");

#define TIME_SYNC_SERVICE 0x100u
#define TIME_SYNC_PERIOD_MS 30000u
#define ROLE_MASTER 1u

extern const uint8_t *g2_audio_log_timezone;               /* pointer cell RAM 0x200036fc */
extern const char *const g2_time_weekday_names[7];         /* ROM 0x7717a8 "Sun".."Sat" */
extern const g2_time_sync_record_t g2_time_sync_template;  /* ROM 0x788f10 */

extern uint32_t audio_time_epoch_seconds(const uint8_t in[40]);           /* 0x44a108 */
extern void audio_time_epoch_to_calendar_449ed4(uint32_t seconds, void *record); /* 0x449ed4 */
extern void g2_log_datetime_now_44a19a(void *record);                      /* 0x44a19a */
extern void audio_time_snapshot(uint8_t out[40]);                          /* 0x47ef10 */
extern uint32_t DRV_RtcSetTime(const g2_rtc_time_t *time);                 /* 0x47ee78 */
extern uint8_t audio_uart_device_role_get(void);                           /* 0x45a568 */
extern uint32_t audio_uart_request_send(uint32_t app, const void *bytes, uint32_t length,
                                        uint32_t flags);                   /* 0x4651e0 */
extern void audio_event_loop_push_delayed(void (*callback)(void), uint32_t argument,
                                          uint32_t delay);                 /* 0x47697e */
extern uint32_t audio_event_loop_remove_delayed(void (*callback)(void));   /* 0x476ace */
extern void *aeabi_memcpy4_439c04(void *dst, const void *src, uint32_t len); /* 0x439c04 */
extern void audio_uart_buffer_zero(void *dst, uint32_t len, uint32_t fill); /* 0x43c0e4 */
extern uint32_t audio_log_flags(void);                                      /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t,
                               const char *, ...);                          /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */

static const char module_tag[] = "srv.time"; /* ROM 0x78c080 */
static const char source_file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\service\\time\\service_time.c"; /* ROM 0x6f6024 */
static const char svc_fn[] = "SVC_SystemTimeSync"; /* ROM 0x78362c */
static const char rpc_fn[] = "RPC_SystemTimeSync"; /* ROM 0x783640 */
static const char svc_message[] =
    "SVC_SystemTimeSync: %04d-%02d-%02d %02d:%02d:%02d %s zone=%d"; /* ROM 0x70f164 */
static const char svc_short[] =
    "[srv.time]SVC_SystemTimeSync: %04d-%02d-%02d %02d:%02d:%02d %s zone=%d"; /* ROM 0x6fd154 */
static const char rpc_message[] =
    "RPC---> Slave: %04d-%02d-%02d %02d:%02d:%02d %s zone=%d"; /* ROM 0x723038 */
static const char rpc_short[] =
    "[srv.time]RPC---> Slave: %04d-%02d-%02d %02d:%02d:%02d %s zone=%d"; /* ROM 0x705d10 */

static int32_t timezone_quarters(void)
{
    return (int8_t)g2_audio_log_timezone[8];
}

uint32_t service_time_calendar_to_epoch_wrapper(const g2_rtc_time_t *time)
{
    return audio_time_epoch_seconds((const uint8_t *)time);
}

/* Program the RTC from epoch seconds and log the resulting local time. */
void SVC_SystemTimeSync(uint32_t epoch, int8_t zone)
{
    g2_rtc_time_t time;

    audio_time_epoch_to_calendar_449ed4(epoch, &time);
    (void)DRV_RtcSetTime(&time);
    audio_uart_buffer_zero(&time, sizeof time, 0u);
    g2_log_datetime_now_44a19a(&time);
    if (audio_log_flags() & 2u)
        audio_log_extended(4u, module_tag, source_file, svc_fn, 0xbdu, svc_message,
                           time.year + 2000u, time.month, time.day, time.hour, time.minute,
                           time.second, g2_time_weekday_names[time.weekday], (int32_t)zone);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compress_log_output(0x12000000u, svc_short, svc_short,
                                  time.year + 2000u, time.month, time.day, time.hour, time.minute,
                                  time.second, g2_time_weekday_names[time.weekday], (int32_t)zone);
}

void RPC_SystemTimeSync(void)
{
    g2_rtc_time_t now;
    g2_time_sync_record_t record;

    if (audio_uart_device_role_get() != ROLE_MASTER)
        return;
    audio_time_snapshot((uint8_t *)&now);
    uint32_t epoch = audio_time_epoch_seconds((const uint8_t *)&now);
    (void)aeabi_memcpy4_439c04(&record, &g2_time_sync_template, sizeof record);
    record.role = audio_uart_device_role_get();
    record.peer_role = audio_uart_device_role_get() == ROLE_MASTER ? 2u : 1u;
    record.epoch = epoch;
    record.zone = timezone_quarters();
    if (audio_log_flags() & 2u)
        audio_log_extended(4u, module_tag, source_file, rpc_fn, 0xd1u, rpc_message,
                           now.year + 2000u, now.month, now.day, now.hour, now.minute, now.second,
                           g2_time_weekday_names[now.weekday], timezone_quarters());
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compress_log_output(0x12000000u, rpc_short, rpc_short,
                                  now.year + 2000u, now.month, now.day, now.hour, now.minute,
                                  now.second, g2_time_weekday_names[now.weekday], timezone_quarters());
    (void)audio_uart_request_send(TIME_SYNC_SERVICE, &record, sizeof record, 0u);
    (void)audio_event_loop_remove_delayed(RPC_SystemTimeSync);
    audio_event_loop_push_delayed(RPC_SystemTimeSync, 0u, TIME_SYNC_PERIOD_MS);
}

/* On the master, re-apply the RTC time locally, then kick an immediate peer sync. */
void service_time_sync_callback(void)
{
    g2_rtc_time_t now;

    if (audio_uart_device_role_get() == ROLE_MASTER) {
        audio_time_snapshot((uint8_t *)&now);
        SVC_SystemTimeSync(audio_time_epoch_seconds((const uint8_t *)&now), (int8_t)timezone_quarters());
    }
    (void)audio_event_loop_remove_delayed(RPC_SystemTimeSync);
    audio_event_loop_push_delayed(RPC_SystemTimeSync, 0u, 0u);
}
