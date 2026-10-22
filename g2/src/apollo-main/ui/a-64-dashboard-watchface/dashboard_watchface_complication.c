/* Dashboard watchface complication helpers (icon, health metric lookup and
 * value text per complication kind). Native 0x5b89f0..0x5b8d1b; the TU also
 * holds 0x5b8d20 (layout2_slot_icon_refresh_5b8d20, ui/u-09) and its literal
 * pool 0x5b8d60..0x5b8dcf. No log strings name the stock file; it sits between
 * the dashboard_watchface_layout1.c and dashboard_watchface_layout2.c objects
 * and is called from both (layout1 0x5b873c, layout2 0x5b9b04).
 *
 * Complication kinds: 1 weather, 2/3 weather-block text fields, 4 unread
 * messages, 5 heart rate, 6 steps, 7 calories, 8 blood oxygen, 9 sleep.
 *
 * Hard-float ABI (value in s0) and a double-precision temperature conversion:
 * profile g2-apollo-main-20. */
#include <stdint.h>
#include <stddef.h>

#define VFP __attribute__((pcs("aapcs-vfp")))

/* Health record metric (0x18 bytes), see ui/a-55-health-data-manager. */
typedef struct {
    uint8_t type;      /* +0x00 */
    uint8_t pad1[3];
    uint32_t goal;     /* +0x04 */
    float value;       /* +0x08 */
    float avg_value;   /* +0x0c */
    uint32_t duration; /* +0x10 seconds */
    uint8_t trend;     /* +0x14 */
    uint8_t pad15[3];
} g2_wf_health_metric_t;
_Static_assert(sizeof(g2_wf_health_metric_t) == 0x18u, "health metric record");

typedef struct {
    uint32_t head;                    /* +0x00 */
    g2_wf_health_metric_t metric[8];  /* +0x04 */
} g2_wf_health_data_t;

extern g2_wf_health_data_t g2_health_data;   /* RAM 0x200f41b4 */
extern uint8_t g2_dashboard_state[];         /* RAM 0x200e3e80, 0xa0 bytes */

/* g2_dashboard_state weather block fields read here. */
#define DS_WEATHER_VALID 0x20u /* u8 */
#define DS_TEMPERATURE   0x24u /* float, Celsius */
#define DS_KIND3_FLAG    0x58u /* u32, 1 selects the alternate kind-3 icon */
#define DS_KIND3_TEXT    0x5cu /* NUL-terminated */
#define DS_KIND2_FLAG    0x7cu /* u32, non-zero selects the alternate kind-2 icon */
#define DS_KIND2_TEXT    0x80u /* NUL-terminated */

/* lv_image_dsc_t assets (ROM, 24x24). */
extern const uint8_t g2_wf_icon_kind2_off[];     /* ROM 0x7725fc */
extern const uint8_t g2_wf_icon_kind2_on[];      /* ROM 0x7725e0 */
extern const uint8_t g2_wf_icon_kind3_on[];      /* ROM 0x77098c */
extern const uint8_t g2_wf_icon_kind3_off[];     /* ROM 0x76b490 */
extern const uint8_t g2_wf_icon_unread[];        /* ROM 0x774a14 */
extern const uint8_t g2_wf_icon_heart_rate[];    /* ROM 0x7749f8 */
extern const uint8_t g2_wf_icon_steps[];         /* ROM 0x774a68 */
extern const uint8_t g2_wf_icon_calories[];      /* ROM 0x7749dc */
extern const uint8_t g2_wf_icon_blood_oxygen[];  /* ROM 0x774a4c */
extern const uint8_t g2_wf_icon_sleep[];         /* ROM 0x774a30 */

extern int32_t g2_audio_dump_snprintf(char *dst, uint32_t size, const char *format, ...); /* 0x44b728 */
extern uint8_t svc_universal_setting_get_temperature_unit_466512(void); /* 1 = show Celsius as stored */
extern uint32_t ui_common_api_fn_00509f86(void);                        /* unread message count */
extern uint32_t health_lock_storage(void);                              /* 0x4ffc32 */
extern void health_unlock_storage(void);                                /* 0x4ffc90 */

static const char s_dash[] = "-";                          /* ROM 0x5b8d1c */
static const char s_sleep_fmt[] = "%u.%uh";                /* ROM 0x78d364 */
static const char s_pct_full[] = "100%%";                  /* ROM 0x78d36c */
static const char s_pct_fmt[] = "%d%%";                    /* ROM 0x78d374 */
static const char s_int_fmt[] = "%d";                      /* ROM 0x5b8d94 */
static const char s_kilo_frac_fmt[] = "%d.%dk";            /* ROM 0x78d37c */
static const char s_kilo_fmt[] = "%dk";                    /* ROM 0x5b8da8 */
static const char s_deg_c_fmt[] = "%d\xe2\x84\x83";        /* ROM 0x78d384 "%d℃" */
static const char s_deg_f_fmt[] = "%d\xe2\x84\x89";        /* ROM 0x78d38c "%d℉" */
static const char s_str_fmt[] = "%s";                      /* ROM 0x5b8dcc */

const void *layout2_slot_icon_src_5b89f0(uint8_t kind);
int32_t watchface_health_metric_index_5b8a6a(uint8_t kind);
VFP void watchface_health_value_format_5b8a9c(float value, uint8_t kind, uint32_t duration,
                                              char *buf, uint32_t size);
void layout2_slot_text_5b8bc8(uint8_t kind, char *buf, uint32_t size);

/* Kind 1 (weather) has no static icon: the caller uses the live weather icon. */
const void *layout2_slot_icon_src_5b89f0(uint8_t kind)
{
    switch (kind) {
    case 1u:
        return NULL;
    case 2u:
        if (*(const uint32_t *)(const void *)&g2_dashboard_state[DS_KIND2_FLAG] != 0u)
            return g2_wf_icon_kind2_on;
        return g2_wf_icon_kind2_off;
    case 3u:
        if (*(const uint32_t *)(const void *)&g2_dashboard_state[DS_KIND3_FLAG] == 1u)
            return g2_wf_icon_kind3_on;
        return g2_wf_icon_kind3_off;
    case 4u:
        return g2_wf_icon_unread;
    case 5u:
        return g2_wf_icon_heart_rate;
    case 6u:
        return g2_wf_icon_steps;
    case 7u:
        return g2_wf_icon_calories;
    case 8u:
        return g2_wf_icon_blood_oxygen;
    case 9u:
        return g2_wf_icon_sleep;
    default:
        return NULL;
    }
}

/* Complication kind -> g2_health_data.metric[] index, -1 for non-health kinds. */
int32_t watchface_health_metric_index_5b8a6a(uint8_t kind)
{
    switch (kind) {
    case 5u:
        return 3; /* heart rate */
    case 6u:
        return 0; /* steps */
    case 7u:
        return 1; /* calories */
    case 8u:
        return 4; /* blood oxygen */
    case 9u:
        return 2; /* sleep */
    default:
        return -1;
    }
}

/* Health value text: sleep as hours with one decimal (6-minute steps), steps
 * and calories abbreviated above 1000, blood oxygen capped at "100%". A value
 * that is not > 0 prints "-". */
VFP void watchface_health_value_format_5b8a9c(float value, uint8_t kind, uint32_t duration,
                                              char *buf, uint32_t size)
{
    if (buf == NULL || size == 0u)
        return;
    if (kind == 9u) {
        if (duration == 0u)
            (void)g2_audio_dump_snprintf(buf, size, s_dash);
        else
            (void)g2_audio_dump_snprintf(buf, size, s_sleep_fmt, duration / 3600u,
                                         (duration % 3600u) / 360u);
        return;
    }
    if (!(value > 0.0f)) {
        (void)g2_audio_dump_snprintf(buf, size, s_dash);
        return;
    }
    switch (kind) {
    case 5u:
        (void)g2_audio_dump_snprintf(buf, size, s_int_fmt, (int32_t)value);
        break;
    case 6u:
    case 7u:
        if (value < 1000.0f)
            (void)g2_audio_dump_snprintf(buf, size, s_int_fmt, (int32_t)value);
        else if (value < 10000.0f)
            (void)g2_audio_dump_snprintf(buf, size, s_kilo_frac_fmt, (int32_t)(value / 1000.0f),
                                         (int32_t)(value / 100.0f) % 10);
        else
            (void)g2_audio_dump_snprintf(buf, size, s_kilo_fmt, (int32_t)(value / 1000.0f));
        break;
    case 8u:
        if (value >= 100.0f)
            (void)g2_audio_dump_snprintf(buf, size, s_pct_full);
        else
            (void)g2_audio_dump_snprintf(buf, size, s_pct_fmt, (int32_t)value);
        break;
    default:
        (void)g2_audio_dump_snprintf(buf, size, s_dash);
        break;
    }
}

void layout2_slot_text_5b8bc8(uint8_t kind, char *buf, uint32_t size)
{
    uint8_t *const st = g2_dashboard_state;
    int32_t index;
    float value;
    uint32_t duration;

    if (buf == NULL || size == 0u)
        return;
    buf[0] = '\0';
    switch (kind) {
    case 1u:
        if (st[DS_WEATHER_VALID] == 0u) {
            (void)g2_audio_dump_snprintf(buf, size, s_dash);
        } else if (svc_universal_setting_get_temperature_unit_466512() == 1u) {
            (void)g2_audio_dump_snprintf(buf, size, s_deg_c_fmt,
                                         (int32_t)*(const float *)(const void *)&st[DS_TEMPERATURE]);
        } else {
            (void)g2_audio_dump_snprintf(
                buf, size, s_deg_f_fmt,
                (int32_t)((double)*(const float *)(const void *)&st[DS_TEMPERATURE] * 1.8 + 32.0));
        }
        break;
    case 2u:
        if (st[DS_WEATHER_VALID] == 0u || st[DS_KIND2_TEXT] == 0u)
            (void)g2_audio_dump_snprintf(buf, size, s_dash);
        else
            (void)g2_audio_dump_snprintf(buf, size, s_str_fmt, (const char *)&st[DS_KIND2_TEXT]);
        break;
    case 3u:
        if (st[DS_WEATHER_VALID] == 0u || st[DS_KIND3_TEXT] == 0u)
            (void)g2_audio_dump_snprintf(buf, size, s_dash);
        else
            (void)g2_audio_dump_snprintf(buf, size, s_str_fmt, (const char *)&st[DS_KIND3_TEXT]);
        break;
    case 4u:
        (void)g2_audio_dump_snprintf(buf, size, s_int_fmt, ui_common_api_fn_00509f86());
        break;
    case 5u:
    case 6u:
    case 7u:
    case 8u:
    case 9u:
        index = watchface_health_metric_index_5b8a6a(kind);
        if (index < 0) {
            (void)g2_audio_dump_snprintf(buf, size, s_dash);
            break;
        }
        (void)health_lock_storage();
        value = g2_health_data.metric[index].value;
        duration = g2_health_data.metric[index].duration;
        health_unlock_storage();
        watchface_health_value_format_5b8a9c(value, kind, duration, buf, size);
        break;
    default:
        break;
    }
}
