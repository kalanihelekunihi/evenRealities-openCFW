/* Dashboard watchface manager, stock
 * D:\01_workspace\s200_ap510b_iar_git\app\gui\dashboard\dashboard_watchface_manager.c.
 * Native 0x500410..0x5007cb; literal pool 0x5007cc..0x500823.
 *
 * The current layout's watchface kind (byte 0 of the layout's watchface block
 * at layout + 8) selects one of four ROM ops tables. The manager keeps the
 * active table in RAM 0x200744bc and forwards every dashboard_watchface_manager_call_NN
 * to the slot at byte offset NN when it is non-NULL.
 *
 * call_14 forwards a float (temperature) in s0: hard-float ABI, profile
 * g2-apollo-main-3. */
#include <stdint.h>
#include <stddef.h>

#define VFP __attribute__((pcs("aapcs-vfp")))

typedef struct {
    int32_t (*create)(void *parent, uint32_t arg, const uint8_t *layout_cfg); /* +0x00, 0 = ok */
    void (*deinit)(void);                                                    /* +0x04 */
    void (*fn_08)(int32_t value);                                            /* +0x08 */
    void (*fn_0c)(uint32_t hour, uint32_t minute, uint32_t h24);             /* +0x0c */
    void (*fn_10)(uint32_t weekday, uint32_t month, uint32_t day, uint32_t date_format); /* +0x10 */
    VFP void (*fn_14)(uint16_t weather_icon, uint32_t weather_valid, uint32_t fahrenheit,
                      float temperature);                                    /* +0x14 */
    void (*set_battery)(uint8_t level);                                      /* +0x18 */
    void (*fn_1c)(uint32_t value);                                           /* +0x1c */
    void (*fn_20)(uint32_t connected);                                       /* +0x20 */
    void (*fn_24)(uint32_t connected, uint8_t battery);                      /* +0x24 */
    void (*fn_28)(uint32_t charging);                                        /* +0x28 */
    void (*fn_2c)(uint8_t value);                                            /* +0x2c */
    void (*fn_30)(void);                                                     /* +0x30 */
    void (*fn_34)(void);                                                     /* +0x34 */
    void (*fn_38)(void);                                                     /* +0x38 */
} g2_watchface_ops_t;
_Static_assert(sizeof(g2_watchface_ops_t) == 0x3cu, "watchface ops table is 15 slots");

extern const g2_watchface_ops_t g2_watchface_ops_kind1; /* ROM 0x713f54 */
extern const g2_watchface_ops_t g2_watchface_ops_kind2; /* ROM 0x713fcc */
extern const g2_watchface_ops_t g2_watchface_ops_kind3; /* ROM 0x714008 */
extern const g2_watchface_ops_t g2_watchface_ops_kind4; /* ROM 0x7140bc */
extern const g2_watchface_ops_t *g2_watchface_active_ops; /* RAM 0x200744bc */

extern const uint8_t *dashboard_layout_get_current_558142(void);
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

static const char module_tag[] = "dashboard.wf.mgr"; /* ROM 0x77ec30 */
static const char source_file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\dashboard\\dashboard_watchface_manager.c"; /* ROM 0x6e748c */
static const char try_create_fn[] = "try_create";                          /* ROM 0x78a7c0 */
static const char init_fn[] = "dashboard_watchface_manager_init";          /* ROM 0x7534e0 */
static const char battery_fn[] = "dashboard_watchface_manager_set_battery"; /* ROM 0x749024 */
static const char create_failed[] = "layout create returned %d"; /* ROM 0x76ac24 */
static const char create_failed_short[] = "[dashboard.wf.mgr]layout create returned %d"; /* ROM 0x73db08 */
static const char parent_null[] = "manager init: parent NULL"; /* ROM 0x76ac40 */
static const char parent_null_short[] = "[dashboard.wf.mgr]manager init: parent NULL"; /* ROM 0x73db34 */
static const char already[] = "manager init: already inited, deinit first"; /* ROM 0x73db60 */
static const char already_short[] = "[dashboard.wf.mgr]manager init: already inited, deinit first"; /* ROM 0x70aaa4 */
static const char init_ok[] = "manager init OK, kind=%d"; /* ROM 0x76ac5c */
static const char init_ok_short[] = "[dashboard.wf.mgr]manager init OK, kind=%d"; /* ROM 0x73db8c */
static const char all_failed[] = "manager init: all layouts failed to create"; /* ROM 0x73dbb8 */
static const char all_failed_short[] = "[dashboard.wf.mgr]manager init: all layouts failed to create"; /* ROM 0x70aae4 */
static const char set_battery[] = "dashboard_watchface_manager_set_battery: level=%d"; /* ROM 0x728824 */
static const char set_battery_short[] =
    "[dashboard.wf.mgr]dashboard_watchface_manager_set_battery: level=%d"; /* ROM 0x701ee8 */

const g2_watchface_ops_t *watchface_ops_for_kind(uint8_t kind)
{
    switch (kind) {
    case 1u: return &g2_watchface_ops_kind1;
    case 2u: return &g2_watchface_ops_kind2;
    case 3u: return &g2_watchface_ops_kind3;
    case 4u: return &g2_watchface_ops_kind4;
    default: return NULL;
    }
}

const g2_watchface_ops_t *try_create(const g2_watchface_ops_t *ops, void *parent, uint32_t arg,
                                     const uint8_t *layout_cfg)
{
    int32_t ret;

    if (ops == NULL || ops->create == NULL)
        return NULL;
    ret = ops->create(parent, arg, layout_cfg);
    if (ret != 0) {
        LOG_E(2u, try_create_fn, 0x2bu, create_failed, ret);
        LOG_C(0x08400000u, create_failed_short, create_failed_short, ret);
        return NULL;
    }
    return ops;
}

void dashboard_watchface_manager_deinit(void);

int32_t dashboard_watchface_manager_init(void *parent, uint32_t arg)
{
    const uint8_t *layout;
    const uint8_t *cfg;
    uint8_t kind;

    if (parent == NULL) {
        LOG_E(1u, init_fn, 0x35u, parent_null);
        LOG_C(0x04000000u, parent_null_short, parent_null_short);
        return -1;
    }
    if (g2_watchface_active_ops != NULL) {
        LOG_E(2u, init_fn, 0x3bu, already);
        LOG_C(0x08000000u, already_short, already_short);
        dashboard_watchface_manager_deinit();
    }
    layout = dashboard_layout_get_current_558142();
    cfg = (layout != NULL) ? layout + 8 : NULL;
    kind = (cfg != NULL) ? cfg[0] : 0u;
    g2_watchface_active_ops = try_create(watchface_ops_for_kind(kind), parent, arg, cfg);
    if (g2_watchface_active_ops == NULL) {
        LOG_E(1u, init_fn, 0x4eu, all_failed);
        LOG_C(0x04000000u, all_failed_short, all_failed_short);
        return -1;
    }
    LOG_E(3u, init_fn, 0x4au, init_ok, kind);
    LOG_C(0x0c400000u, init_ok_short, init_ok_short, kind);
    return 0;
}

void dashboard_watchface_manager_deinit(void)
{
    if (g2_watchface_active_ops != NULL && g2_watchface_active_ops->deinit != NULL)
        g2_watchface_active_ops->deinit();
    g2_watchface_active_ops = NULL;
}

void dashboard_watchface_manager_call_08(int32_t value)
{
    if (g2_watchface_active_ops != NULL && g2_watchface_active_ops->fn_08 != NULL)
        g2_watchface_active_ops->fn_08(value);
}

void dashboard_watchface_manager_call_0c(uint32_t hour, uint32_t minute, uint32_t h24)
{
    if (g2_watchface_active_ops != NULL && g2_watchface_active_ops->fn_0c != NULL)
        g2_watchface_active_ops->fn_0c(hour, minute, h24);
}

void dashboard_watchface_manager_call_10(uint32_t weekday, uint32_t month, uint32_t day, uint32_t date_format)
{
    if (g2_watchface_active_ops != NULL && g2_watchface_active_ops->fn_10 != NULL)
        g2_watchface_active_ops->fn_10(weekday, month, day, date_format);
}

VFP void dashboard_watchface_manager_call_14(uint16_t weather_icon, uint32_t weather_valid, uint32_t fahrenheit,
                                             float temperature)
{
    if (g2_watchface_active_ops != NULL && g2_watchface_active_ops->fn_14 != NULL)
        g2_watchface_active_ops->fn_14(weather_icon, weather_valid, fahrenheit, temperature);
}

void dashboard_watchface_manager_set_battery(uint8_t level)
{
    LOG_E(4u, battery_fn, 0x7eu, set_battery, level);
    LOG_C(0x10400000u, set_battery_short, set_battery_short, level);
    if (g2_watchface_active_ops != NULL && g2_watchface_active_ops->set_battery != NULL)
        g2_watchface_active_ops->set_battery(level);
}

void dashboard_watchface_manager_call_1c(uint32_t value)
{
    if (g2_watchface_active_ops != NULL && g2_watchface_active_ops->fn_1c != NULL)
        g2_watchface_active_ops->fn_1c(value);
}

void dashboard_watchface_manager_call_20(uint32_t connected)
{
    if (g2_watchface_active_ops != NULL && g2_watchface_active_ops->fn_20 != NULL)
        g2_watchface_active_ops->fn_20(connected);
}

void dashboard_watchface_manager_call_30(void)
{
    if (g2_watchface_active_ops != NULL && g2_watchface_active_ops->fn_30 != NULL)
        g2_watchface_active_ops->fn_30();
}

void dashboard_watchface_manager_call_34(void)
{
    if (g2_watchface_active_ops != NULL && g2_watchface_active_ops->fn_34 != NULL)
        g2_watchface_active_ops->fn_34();
}

void dashboard_watchface_manager_call_38(void)
{
    if (g2_watchface_active_ops != NULL && g2_watchface_active_ops->fn_38 != NULL)
        g2_watchface_active_ops->fn_38();
}

void dashboard_watchface_manager_call_24(uint32_t connected, uint8_t battery)
{
    if (g2_watchface_active_ops != NULL && g2_watchface_active_ops->fn_24 != NULL)
        g2_watchface_active_ops->fn_24(connected, battery);
}

void dashboard_watchface_manager_call_28(uint32_t charging)
{
    if (g2_watchface_active_ops != NULL && g2_watchface_active_ops->fn_28 != NULL)
        g2_watchface_active_ops->fn_28(charging);
}

void dashboard_watchface_manager_call_2c(uint8_t value)
{
    if (g2_watchface_active_ops != NULL && g2_watchface_active_ops->fn_2c != NULL)
        g2_watchface_active_ops->fn_2c(value);
}
