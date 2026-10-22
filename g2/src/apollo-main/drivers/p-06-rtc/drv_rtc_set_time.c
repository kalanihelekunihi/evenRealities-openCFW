/* Stock source: D:\01_workspace\s200_ap510b_iar_git\driver\rtc\drv_rtc.c
 * Native DRV_RtcSetTime 0x47ee78..0x47eefa. */
#include <stdint.h>

/* Ambiq am_hal_rtc_time_t word layout (setter 0x4d3adc); the driver takes
 * the same layout and ignores its first three words. */
typedef struct {
    uint32_t read_error; /* +0 */
    uint32_t weekday;    /* +4 */
    uint32_t century;    /* +8 */
    uint32_t year;       /* +12, years since 2000 */
    uint32_t month;      /* +16 */
    uint32_t day;        /* +20 */
    uint32_t hour;       /* +24 */
    uint32_t minute;     /* +28 */
    uint32_t second;     /* +32 */
    uint32_t hundredths; /* +36 */
} g2_rtc_time_t;
_Static_assert(sizeof(g2_rtc_time_t) == 40u, "am_hal_rtc_time_t");

extern uint32_t rtc_weekday_from_date_4d3cf8(uint32_t year, uint32_t month, uint32_t day);
extern uint32_t am_hal_rtc_time_set_4d3adc(const g2_rtc_time_t *time);
extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t level, const char *module, const char *path,
                               const char *function, uint32_t line, const char *format, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t mask, const char *message,
                                    const char *message_copy, ...); /* 0x43ce9e */

static const char module[] = "drv.rtc"; /* ROM 0x78d4a4 */
static const char path[] = "D:\\01_workspace\\s200_ap510b_iar_git\\driver\\rtc\\drv_rtc.c"; /* ROM 0x7149a4 */
static const char function[] = "DRV_RtcSetTime"; /* ROM 0x785d30 */
static const char invalid_message[] = "Invalid Input Value"; /* ROM 0x77f180 */
static const char invalid_short[] = "[drv.rtc]Invalid Input Value"; /* ROM 0x75fa90 */

/* Recomputes the weekday from the calendar date, forces century bit 1 and
 * zero hundredths, then programs the RTC. Returns 0 ok, 1 if the HAL
 * validator rejects the time. */
uint32_t DRV_RtcSetTime(const g2_rtc_time_t *time)
{
    g2_rtc_time_t hal;
    hal.hour = time->hour;
    hal.minute = time->minute;
    hal.second = time->second;
    hal.hundredths = 0u;
    hal.weekday = rtc_weekday_from_date_4d3cf8(time->year + 2000u, time->month, time->day);
    hal.day = time->day;
    hal.month = time->month;
    hal.year = time->year;
    hal.century = 1u;
    /* hal.read_error is left uninitialised by stock; the setter ignores it. */
    hal.read_error = 0u;
    if (am_hal_rtc_time_set_4d3adc(&hal) == 0u)
        return 0u;
    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(1u, module, path, function, 0xddu, invalid_message);
    if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
        (void)compress_log_output(0x04000000u, invalid_short, invalid_short);
    return 1u;
}
