/* Dashboard watchface layout4 (world clocks) helpers, stock
 * D:\01_workspace\s200_ap510b_iar_git\app\gui\dashboard\dashboard_watchface_layout4.c
 * (log tag "dashboard.wf.l4"). Native 0x5bab2c..0x5bab75 and
 * 0x5baba6..0x5bb1cb; literal pools 0x5bafac..0x5bafc3, 0x5bb1fc..0x5bb207,
 * 0x5bb2cc..0x5bb36b and the TU pool 0x5bbaa4..0x5bbccf.
 * 0x5bab76 (layout4_place_5bab76) is in ui/u-09/watchface_layout_slots.c; the
 * rest of the TU (create and the ops entries) is in
 * ui/a-65-watchface-layout4/dashboard_watchface_layout4.c, which calls these
 * helpers by the names used here.
 *
 * UTC offsets are floats in hours passed in s0 (hard-float ABI): profile
 * g2-apollo-main-3. */
#include <stdint.h>
#include <stddef.h>

#define VFP __attribute__((pcs("aapcs-vfp")))

#define LAYOUT4_MAX_CLOCKS 3u
#define LV_ALIGN_TOP_LEFT  1u
#define LV_ALIGN_TOP_MID   2u
#define LV_ALIGN_TOP_RIGHT 3u

/* Watchface config record handed to create (same layout as a-65). */
typedef struct {
    uint8_t kind;                       /* +0x00 4 = layout 4 */
    uint8_t reserved_01[3];             /* +0x01 */
    uint8_t align;                      /* +0x04 */
    uint8_t clock_count;                /* +0x05 1..3 */
    uint8_t offset_count;               /* +0x06 must equal clock_count */
    uint8_t reserved_07;                /* +0x07 */
    float tz_hours[LAYOUT4_MAX_CLOCKS]; /* +0x08 UTC offset in hours */
    uint8_t name_count;                 /* +0x14 must equal clock_count */
    char names[LAYOUT4_MAX_CLOCKS][32]; /* +0x15 city names */
} g2_layout4_cfg_t;
_Static_assert(offsetof(g2_layout4_cfg_t, clock_count) == 0x05, "clock_count at +0x05");
_Static_assert(offsetof(g2_layout4_cfg_t, name_count) == 0x14, "name_count at +0x14");

extern char g2_layout4_offset_frac_200744b8[4]; /* RAM 0x200744b8 "%02d" fraction scratch */

/* ROM assets. */
extern const uint8_t g2_wf_glasses_batt_0[];    /* ROM 0x76bae8, 31x10 */
extern const uint8_t g2_wf_glasses_batt_20[];   /* ROM 0x76bb20, 31x10 */
extern const uint8_t g2_wf_glasses_batt_40[];   /* ROM 0x76bb3c, 31x10 */
extern const uint8_t g2_wf_glasses_batt_60[];   /* ROM 0x76bb58, 31x10 */
extern const uint8_t g2_wf_glasses_batt_80[];   /* ROM 0x76bb74, 31x10 */
extern const uint8_t g2_wf_glasses_batt_100[];  /* ROM 0x76bb04, 31x10 */
extern const uint8_t g2_wf_ring_batt_0[];       /* ROM 0x7708e4, 30x10 */
extern const uint8_t g2_wf_ring_batt_20[];      /* ROM 0x77091c, 30x10 */
extern const uint8_t g2_wf_ring_batt_40[];      /* ROM 0x770938, 30x10 */
extern const uint8_t g2_wf_ring_batt_60[];      /* ROM 0x770954, 30x10 */
extern const uint8_t g2_wf_ring_batt_80[];      /* ROM 0x770970, 30x10 */
extern const uint8_t g2_wf_ring_batt_100[];     /* ROM 0x770900, 30x10 */
extern const uint8_t g2_wf_hour_1[];   /* ROM 0x76ee88, 26x26 */
extern const uint8_t g2_wf_hour_2[];   /* ROM 0x76eef8 */
extern const uint8_t g2_wf_hour_3[];   /* ROM 0x76ef14 */
extern const uint8_t g2_wf_hour_4[];   /* ROM 0x76ef30 */
extern const uint8_t g2_wf_hour_5[];   /* ROM 0x76ef4c */
extern const uint8_t g2_wf_hour_6[];   /* ROM 0x76ef68 */
extern const uint8_t g2_wf_hour_7[];   /* ROM 0x76ef84 */
extern const uint8_t g2_wf_hour_8[];   /* ROM 0x76efa0 */
extern const uint8_t g2_wf_hour_9[];   /* ROM 0x76efbc */
extern const uint8_t g2_wf_hour_10[];  /* ROM 0x76eea4 */
extern const uint8_t g2_wf_hour_11[];  /* ROM 0x76eec0 */
extern const uint8_t g2_wf_hour_12[];  /* ROM 0x76eedc */
extern const uint8_t g2_wf_minute_1[];   /* ROM 0x76efd8, 26x26 */
extern const uint8_t g2_wf_minute_2[];   /* ROM 0x76f048 */
extern const uint8_t g2_wf_minute_3[];   /* ROM 0x76f064 */
extern const uint8_t g2_wf_minute_4[];   /* ROM 0x76f080 */
extern const uint8_t g2_wf_minute_5[];   /* ROM 0x76f09c */
extern const uint8_t g2_wf_minute_6[];   /* ROM 0x76f0b8 */
extern const uint8_t g2_wf_minute_7[];   /* ROM 0x76f0d4 */
extern const uint8_t g2_wf_minute_8[];   /* ROM 0x76f0f0 */
extern const uint8_t g2_wf_minute_9[];   /* ROM 0x76f10c */
extern const uint8_t g2_wf_minute_10[];  /* ROM 0x76eff4 */
extern const uint8_t g2_wf_minute_11[];  /* ROM 0x76f010 */
extern const uint8_t g2_wf_minute_12[];  /* ROM 0x76f02c */

/* Logging. */
extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t,
                               const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */

extern int32_t g2_audio_dump_snprintf(char *dst, uint32_t size, const char *format, ...); /* 0x44b728 */
extern uint32_t service_time_current_epoch_get(void);             /* 0x44a1c6 */
extern uint32_t audio_time_format_mode_46650c(void);              /* 1 = 12-hour clock */
extern VFP float roundf_577d08(float x);                          /* IAR roundf (half away from zero) */

/* LVGL 9.3 (stock copies). */
extern void audio_uart_page_44120e(void *obj, int32_t v, uint32_t sel); /* pad_top */
extern void audio_uart_page_44121c(void *obj, int32_t v, uint32_t sel); /* pad_bottom */
extern void audio_uart_page_44122a(void *obj, int32_t v, uint32_t sel); /* pad_left */
extern void audio_uart_page_441238(void *obj, int32_t v, uint32_t sel); /* pad_right */

static const char tag[] = "dashboard.wf.l4";                                         /* ROM 0x7859a0 */
static const char src[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\dashboard\\dashboard_watchface_layout4.c"; /* ROM 0x6e73e4 */
static const char fn_pick[] = "layout4_pick_g_battery_dsc";                          /* ROM 0x76abd0 */
static const char m_pick[] = "layout4_pick_g_battery_dsc: level=%d";                 /* ROM 0x748fd4 */
static const char t_pick[] = "[dashboard.wf.l4]layout4_pick_g_battery_dsc: level=%d"; /* ROM 0x71dae8 */
static const char fn_validate[] = "layout4_validate_cfg";                            /* ROM 0x7766c4 */
static const char m_cfg_null[] = "layout4 cfg validate: cfg NULL";                   /* ROM 0x75f250 */
static const char t_cfg_null[] = "[dashboard.wf.l4]layout4 cfg validate: cfg NULL";  /* ROM 0x732e94 */
static const char m_kind[] = "layout4 cfg validate: kind mismatch (%d, want %d)";    /* ROM 0x728788 */
static const char t_kind[] =
    "[dashboard.wf.l4]layout4 cfg validate: kind mismatch (%d, want %d)";            /* ROM 0x701e1c */
static const char m_count_zero[] =
    "layout4 cfg validate: world_clock_count==0 (illegal, expect 1..%d)";            /* ROM 0x701e60 */
static const char t_count_zero[] =
    "[dashboard.wf.l4]layout4 cfg validate: world_clock_count==0 (illegal, expect 1..%d)"; /* ROM 0x6e7438 */
static const char m_count_max[] = "layout4 cfg validate: world_clock_count=%u exceeds max=%d"; /* ROM 0x714044 */
static const char t_count_max[] =
    "[dashboard.wf.l4]layout4 cfg validate: world_clock_count=%u exceeds max=%d";    /* ROM 0x6f2df8 */
static const char m_names[] = "layout4 cfg validate: name_count=%u != clock_count=%u"; /* ROM 0x71db20 */
static const char t_names[] =
    "[dashboard.wf.l4]layout4 cfg validate: name_count=%u != clock_count=%u";        /* ROM 0x6f9c2c */
static const char m_offsets[] = "layout4 cfg validate: offset_count=%u != clock_count=%u"; /* ROM 0x71db58 */
static const char t_offsets[] =
    "[dashboard.wf.l4]layout4 cfg validate: offset_count=%u != clock_count=%u";      /* ROM 0x6f2e44 */
static const char s_name_time_fmt[] = "%s %d:%02d%s";                                /* ROM 0x7859b0 */
static const char s_time_fmt[] = "%d:%02d%s";                                        /* ROM 0x78a7a8 */
static const char s_none[] = "";                                                     /* ROM 0x5bafb0 */
static const char s_am[] = " AM";                                                    /* ROM 0x5bafb4 */
static const char s_pm[] = " PM";                                                    /* ROM 0x5bafb8 */
static const char s_plus[] = "+";                                                    /* ROM 0x5bafbc */
static const char s_minus[] = "\xe2\x88\x92";                                        /* ROM 0x5bafc0 U+2212 */
static const char s_frac_25[] = "25";                                                /* ROM 0x5bb1fc */
static const char s_frac_5[] = "5";                                                  /* ROM 0x5bb200 */
static const char s_frac_75[] = "75";                                                /* ROM 0x5bb204 */
static const char s_offset_fmt[] = "%s%d";                                           /* ROM 0x78d34c */
static const char s_frac_fmt[] = "%02d";                                             /* ROM 0x78d354 */
static const char s_offset_frac_fmt[] = "%s%d.%s";                                   /* ROM 0x78d35c */

#define L4_LOG(lvl, fn, line, msg, ...)                                                    \
    do {                                                                                   \
        if (audio_log_flags() & 2u)                                                        \
            audio_log_extended((lvl), tag, src, (fn), (line), (msg), ##__VA_ARGS__);       \
    } while (0)
#define L4_SHORT(code, text, ...)                                                          \
    do {                                                                                   \
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))                          \
            (void)compress_log_output((code), (text), (text), ##__VA_ARGS__);              \
    } while (0)

void lv_obj_set_style_pad_all_5bab2c(void *obj, uint32_t value, uint32_t selector);
uint8_t layout4_align_from_setting_5bab5e(uint8_t setting);
const void *layout4_glasses_battery_dsc_5baba6(uint8_t level);
const void *layout4_ring_battery_dsc_5bac42(uint8_t level);
const void *layout4_hour_hand_src_5bac8c(int32_t hour);
const void *layout4_minute_hand_src_5bad10(int32_t minute);
VFP void layout4_zone_time_5bad98(float tz_hours, int32_t hour, int32_t minute,
                                  int32_t *out_hour, int32_t *out_minute);
void layout4_now_hm_5badf4(int32_t *hour, int32_t *minute);
int32_t layout4_display_hour_5bae2e(int32_t hour);
void layout4_format_time_5bae52(const char *name, int32_t hour, int32_t minute,
                                char *buf, uint32_t size);
VFP void layout4_format_offset_5baef0(float tz_hours, char *buf, uint32_t size);
uint32_t layout4_cfg_valid_5bafc4(const g2_layout4_cfg_t *cfg);

void lv_obj_set_style_pad_all_5bab2c(void *obj, uint32_t value, uint32_t selector)
{
    audio_uart_page_44122a(obj, (int32_t)value, selector);
    audio_uart_page_441238(obj, (int32_t)value, selector);
    audio_uart_page_44120e(obj, (int32_t)value, selector);
    audio_uart_page_44121c(obj, (int32_t)value, selector);
}

uint8_t layout4_align_from_setting_5bab5e(uint8_t setting)
{
    if (setting == 1u)
        return LV_ALIGN_TOP_MID;
    if (setting == 2u)
        return LV_ALIGN_TOP_RIGHT;
    return LV_ALIGN_TOP_LEFT;
}

/* Stock function name "layout4_pick_g_battery_dsc" (from its log string). */
const void *layout4_glasses_battery_dsc_5baba6(uint8_t level)
{
    L4_LOG(4u, fn_pick, 173u, m_pick, (uint32_t)level);
    L4_SHORT(0x10400000u, t_pick, (uint32_t)level);
    if (level == 0u)
        return g2_wf_glasses_batt_0;
    if (level < 21u)
        return g2_wf_glasses_batt_20;
    if (level < 41u)
        return g2_wf_glasses_batt_40;
    if (level < 61u)
        return g2_wf_glasses_batt_60;
    if (level < 81u)
        return g2_wf_glasses_batt_80;
    return g2_wf_glasses_batt_100;
}

const void *layout4_ring_battery_dsc_5bac42(uint8_t level)
{
    if (level == 0u)
        return g2_wf_ring_batt_0;
    if (level < 21u)
        return g2_wf_ring_batt_20;
    if (level < 41u)
        return g2_wf_ring_batt_40;
    if (level < 61u)
        return g2_wf_ring_batt_60;
    if (level < 81u)
        return g2_wf_ring_batt_80;
    return g2_wf_ring_batt_100;
}

const void *layout4_hour_hand_src_5bac8c(int32_t hour)
{
    int32_t h = hour % 12;

    if (h < 0)
        h += 12;
    if (h == 0)
        h = 12;
    switch (h) {
    case 1:
        return g2_wf_hour_1;
    case 2:
        return g2_wf_hour_2;
    case 3:
        return g2_wf_hour_3;
    case 4:
        return g2_wf_hour_4;
    case 5:
        return g2_wf_hour_5;
    case 6:
        return g2_wf_hour_6;
    case 7:
        return g2_wf_hour_7;
    case 8:
        return g2_wf_hour_8;
    case 9:
        return g2_wf_hour_9;
    case 10:
        return g2_wf_hour_10;
    case 11:
        return g2_wf_hour_11;
    default:
        return g2_wf_hour_12;
    }
}

const void *layout4_minute_hand_src_5bad10(int32_t minute)
{
    int32_t step;

    if (minute < 0)
        minute = 0;
    if (minute >= 60)
        minute = 59;
    step = minute / 5;
    if (step == 0)
        step = 12;
    switch (step) {
    case 1:
        return g2_wf_minute_1;
    case 2:
        return g2_wf_minute_2;
    case 3:
        return g2_wf_minute_3;
    case 4:
        return g2_wf_minute_4;
    case 5:
        return g2_wf_minute_5;
    case 6:
        return g2_wf_minute_6;
    case 7:
        return g2_wf_minute_7;
    case 8:
        return g2_wf_minute_8;
    case 9:
        return g2_wf_minute_9;
    case 10:
        return g2_wf_minute_10;
    case 11:
        return g2_wf_minute_11;
    default:
        return g2_wf_minute_12;
    }
}

/* Local time in a zone: (hour*60 + minute + round(tz*60)) mod 1440. */
VFP void layout4_zone_time_5bad98(float tz_hours, int32_t hour, int32_t minute,
                                  int32_t *out_hour, int32_t *out_minute)
{
    int32_t total = (int32_t)roundf_577d08(tz_hours * 60.0f) + hour * 60 + minute;

    total = (total % 1440 + 1440) % 1440;
    if (out_hour != NULL)
        *out_hour = total / 60;
    if (out_minute != NULL)
        *out_minute = total % 60;
}

/* UTC hour and minute from the epoch clock. */
void layout4_now_hm_5badf4(int32_t *hour, int32_t *minute)
{
    uint32_t now = service_time_current_epoch_get();

    if (hour != NULL)
        *hour = (int32_t)((now / 3600u) % 24u);
    if (minute != NULL)
        *minute = (int32_t)((now / 60u) % 60u);
}

int32_t layout4_display_hour_5bae2e(int32_t hour)
{
    if (audio_time_format_mode_46650c() == 1u) {
        hour %= 12;
        if (hour == 0)
            hour = 12;
        return hour;
    }
    return hour;
}

/* "<name> h:mm[ AM| PM]" or "h:mm[ AM| PM]" without a name. */
void layout4_format_time_5bae52(const char *name, int32_t hour, int32_t minute,
                                char *buf, uint32_t size)
{
    int32_t shown;
    const char *suffix;

    if (buf == NULL || size == 0u)
        return;
    buf[0] = '\0';
    if (minute < 0)
        minute = 0;
    if (minute >= 60)
        minute = 59;
    shown = layout4_display_hour_5bae2e(hour);
    suffix = s_none;
    if (audio_time_format_mode_46650c() == 1u)
        suffix = (hour % 24 < 12) ? s_am : s_pm;
    if (name != NULL && name[0] != '\0')
        (void)g2_audio_dump_snprintf(buf, size, s_name_time_fmt, name, shown, minute, suffix);
    else
        (void)g2_audio_dump_snprintf(buf, size, s_time_fmt, shown, minute, suffix);
}

/* "+5", "−3.5", "+5.75": quarter hours use fixed fractions, other minutes
 * are rendered as hundredths of an hour into a 4-byte scratch buffer. */
VFP void layout4_format_offset_5baef0(float tz_hours, char *buf, uint32_t size)
{
    const char *sign;
    const char *frac;
    int32_t total, hours, rest;

    if (buf == NULL || size == 0u)
        return;
    buf[0] = '\0';
    if (tz_hours < 0.0f) {
        sign = s_minus;
        tz_hours = -tz_hours;
    } else {
        sign = s_plus;
    }
    total = (int32_t)roundf_577d08(tz_hours * 60.0f);
    hours = total / 60;
    rest = total % 60;
    if (rest == 0) {
        (void)g2_audio_dump_snprintf(buf, size, s_offset_fmt, sign, hours);
        return;
    }
    if (rest == 15) {
        frac = s_frac_25;
    } else if (rest == 30) {
        frac = s_frac_5;
    } else if (rest == 45) {
        frac = s_frac_75;
    } else {
        frac = g2_layout4_offset_frac_200744b8;
        (void)g2_audio_dump_snprintf(g2_layout4_offset_frac_200744b8, 4u, s_frac_fmt,
                                     (rest * 100 + 30) / 60);
    }
    (void)g2_audio_dump_snprintf(buf, size, s_offset_frac_fmt, sign, hours, frac);
}

/* Returns 1 when the block is a layout4 config with 1..3 clocks and matching
 * name/offset counts. */
uint32_t layout4_cfg_valid_5bafc4(const g2_layout4_cfg_t *cfg)
{
    if (cfg == NULL) {
        L4_LOG(1u, fn_validate, 398u, m_cfg_null);
        L4_SHORT(0x04000000u, t_cfg_null);
        return 0u;
    }
    if (cfg->kind != 4u) {
        L4_LOG(1u, fn_validate, 403u, m_kind, (uint32_t)cfg->kind, 4u);
        L4_SHORT(0x04800000u, t_kind, (uint32_t)cfg->kind, 4u);
        return 0u;
    }
    if (cfg->clock_count == 0u) {
        L4_LOG(1u, fn_validate, 411u, m_count_zero, LAYOUT4_MAX_CLOCKS);
        L4_SHORT(0x04400000u, t_count_zero, LAYOUT4_MAX_CLOCKS);
        return 0u;
    }
    if (cfg->clock_count > LAYOUT4_MAX_CLOCKS) {
        L4_LOG(1u, fn_validate, 416u, m_count_max, (uint32_t)cfg->clock_count, LAYOUT4_MAX_CLOCKS);
        L4_SHORT(0x04800000u, t_count_max, (uint32_t)cfg->clock_count, LAYOUT4_MAX_CLOCKS);
        return 0u;
    }
    if (cfg->name_count != cfg->clock_count) {
        L4_LOG(1u, fn_validate, 421u, m_names, (uint32_t)cfg->name_count, (uint32_t)cfg->clock_count);
        L4_SHORT(0x04800000u, t_names, (uint32_t)cfg->name_count, (uint32_t)cfg->clock_count);
        return 0u;
    }
    if (cfg->offset_count != cfg->clock_count) {
        L4_LOG(1u, fn_validate, 426u, m_offsets, (uint32_t)cfg->offset_count,
               (uint32_t)cfg->clock_count);
        L4_SHORT(0x04800000u, t_offsets, (uint32_t)cfg->offset_count, (uint32_t)cfg->clock_count);
        return 0u;
    }
    return 1u;
}
