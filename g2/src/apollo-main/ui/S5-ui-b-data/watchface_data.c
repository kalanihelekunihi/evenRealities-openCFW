/* Dashboard watchface storage (S5-ui-b storage-definition pass, 2.2.6.10).
 *
 * Stock owners: app\gui\dashboard\dashboard_watchface_layout1.c ..
 * dashboard_watchface_layout4.c (ui/a-63-watchface-layout1,
 * ui/a-64-dashboard-watchface, ui/a-65-watchface-layout4, ui/u-09,
 * ui/x-03-watchface). Types are those of the referencing declarations; the
 * layout1 header is included for g2_wf_slot_t. .data values come from the
 * decoded 0x20000000 init stream (scatter record 0x75d3f4); ROM bytes from
 * ota_s200_firmware_ota.bin.
 *
 * The battery, complication, hour/minute hand and status icons are in
 * watchface_image_assets_data.c. The clock fonts (ROM 0x754794 / 0x7547dc /
 * 0x754800 lv_font_t) are not defined: g2/src has no font-asset convention. */
#include <stdint.h>
#include <stddef.h>
#include "../a-63-watchface-layout1/dashboard_watchface_layout1.h"

/* Same layout as ui/u-09/watchface_layout_slots.c and
 * ui/a-64-dashboard-watchface/dashboard_watchface_layout2.c. */
typedef struct {
    void *icon;     /* +0x0 lv_image */
    void *label;    /* +0x4 lv_label */
    uint8_t kind;   /* +0x8 complication kind (0 = none) */
    uint8_t active; /* +0x9 */
    uint8_t pad[2];
} g2_layout2_slot_data_t;
_Static_assert(sizeof(g2_layout2_slot_data_t) == 12, "layout2 slot record");

/* Same layout as ui/a-65-watchface-layout4/dashboard_watchface_layout4.c. */
typedef struct {
    void *cont;
    void *hour_hand;
    void *minute_hand;
    void *local_row;
    void *local_icon;
    void *time_label;
    void *offset_label;
} g2_layout4_clock_data_t;
_Static_assert(sizeof(g2_layout4_clock_data_t) == 0x1c, "layout4 clock record");

/* ---- dashboard_watchface_layout1.c -------------------------------------- */
/* RAM 0x200005dc (.data): left slot {icon NULL, label NULL, kind 0, side 1}. */
g2_wf_slot_t g2_layout1_slot_a = {NULL, NULL, 0u, 1u, {0u, 0u}};
g2_wf_slot_t g2_layout1_slot_b;          /* RAM 0x20073fa8 right slot */
void *g2_layout1_root;                   /* RAM 0x20074434 */
void *g2_layout1_hour_label;             /* RAM 0x20074438 */
void *g2_layout1_minute_label;           /* RAM 0x2007443c */
void *g2_layout1_colon_label;            /* RAM 0x20074440 */
void *g2_layout1_date_label;             /* RAM 0x20074444 */
void *g2_layout1_status_row;             /* RAM 0x20074448 */
void *g2_layout1_glasses_battery_img;    /* RAM 0x2007444c */
void *g2_layout1_ring_battery_img;       /* RAM 0x20074450 */
void *g2_layout1_ble_off_cont;           /* RAM 0x20074454 */
void *g2_layout1_ble_off_img;            /* RAM 0x20074458 */
uint8_t g2_layout1_clock_style;          /* RAM 0x20074fa6 */

/* RAM 0x20004240 (.data): i18n weekday keys, Sunday first. */
const char *g2_dashboard_weekday_keys_20004240[7] = {
    "ID_DASHBOARD_SUN", /* ROM 0x784734 */
    "ID_DASHBOARD_MON", /* ROM 0x784748 */
    "ID_DASHBOARD_TUE", /* ROM 0x78475c */
    "ID_DASHBOARD_WED", /* ROM 0x784770 */
    "ID_DASHBOARD_THU", /* ROM 0x784784 */
    "ID_DASHBOARD_FRI", /* ROM 0x784798 */
    "ID_DASHBOARD_SAT", /* ROM 0x7847ac */
};

/* ---- dashboard_watchface_layout2.c -------------------------------------- */
/* RAM 0x200005e8 (.data): three slots, each {NULL, NULL, kind 0, active 1}. */
g2_layout2_slot_data_t g2_layout2_slots[3] = {
    {NULL, NULL, 0u, 1u, {0u, 0u}},
    {NULL, NULL, 0u, 1u, {0u, 0u}},
    {NULL, NULL, 0u, 1u, {0u, 0u}},
};
void *g2_layout2_slot_conts[3];          /* RAM 0x20073fb4 */
void *g2_layout2_parent;                 /* RAM 0x2007445c */
void *g2_layout2_time_label;             /* RAM 0x20074460 */
void *g2_layout2_date_label;             /* RAM 0x20074464 */
void *g2_layout2_status_row;             /* RAM 0x20074468 */
void *g2_layout2_glasses_battery_img;    /* RAM 0x2007446c */
void *g2_layout2_ring_battery_img;       /* RAM 0x20074470 */
void *g2_layout2_ble_off_img;            /* RAM 0x20074474 */
uint8_t g2_layout2_clock_style;          /* RAM 0x20074fa7 cfg[5] */
uint8_t g2_layout2_date_enabled;         /* RAM 0x20074fa8 cfg[6] */
uint8_t g2_layout2_align_setting;        /* RAM 0x20074fa9 */
uint8_t g2_layout2_slot_count;           /* RAM 0x20074faa */

/* ---- dashboard_watchface_layout3.c -------------------------------------- */
void *g2_layout3_root;                   /* RAM 0x20074478 */
void *g2_layout3_hands;                  /* RAM 0x2007447c */
void *g2_layout3_hour_img;               /* RAM 0x20074480 */
void *g2_layout3_minute_img;             /* RAM 0x20074484 */
void *g2_layout3_time_label;             /* RAM 0x20074488 */
void *g2_layout3_ble_off_img;            /* RAM 0x2007448c */
void *g2_layout3_weather_label;          /* RAM 0x20074490 */
void *g2_layout3_date_label;             /* RAM 0x20074494 */
void *g2_layout3_status_row;             /* RAM 0x20074498 */
void *g2_layout3_glasses_battery_img;    /* RAM 0x2007449c */
void *g2_layout3_ring_battery_img;       /* RAM 0x200744a0 */
uint8_t g2_layout3_align_setting;        /* RAM 0x20074fab cfg[4] */
uint8_t g2_layout3_date_enabled;         /* RAM 0x20074fac cfg[5] */
uint8_t g2_layout3_temperature_enabled;  /* RAM 0x20074fad cfg[6] */

/* ---- dashboard_watchface_layout4.c -------------------------------------- */
/* LAYOUT4_MAX_CLOCKS = 3. */
char g2_layout4_city_names[3][32];       /* RAM 0x20072670 */
g2_layout4_clock_data_t g2_layout4_clocks[3]; /* RAM 0x2007284c */
float g2_layout4_tz_hours[3];            /* RAM 0x20073fc0 UTC offsets in hours */
void *g2_layout4_root;                   /* RAM 0x200744a4 */
void *g2_layout4_ble_icon;               /* RAM 0x200744a8 */
void *g2_layout4_status_row;             /* RAM 0x200744ac */
void *g2_layout4_battery_icon;           /* RAM 0x200744b0 */
void *g2_layout4_ring_icon;              /* RAM 0x200744b4 */
char g2_layout4_offset_frac_200744b8[4]; /* RAM 0x200744b8 "%02d" scratch */
uint8_t g2_layout4_align_setting;        /* RAM 0x20074fae */
uint8_t g2_layout4_clock_count;          /* RAM 0x20074faf */
/* ROM 0x78a7b4: slot y per clock. */
const int32_t g2_layout4_slot_y[3] = {6, 84, 168};
