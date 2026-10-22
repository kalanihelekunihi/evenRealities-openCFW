/* Health data manager, stock
 * D:\01_workspace\s200_ap510b_iar_git\app\gui\health\health_data_manager.c
 * (path ROM 0x6f3e00, module tag "health.data_mgr" ROM 0x7860c0).
 * Native 0x5597f0..0x55a2af; literal pools 0x559f88..0x559fb7,
 * 0x55a200..0x55a22f, 0x55a2b0..0x55a34f.
 *
 * Converts the decoded pb_service_health messages (app/a-55-pb-health) into the
 * health record at RAM 0x200f41b4 that the health pages read under
 * health_lock_storage. Metric types: 0 UNKNOWN, 1 ALL, 2 STEPS, 3 CALORIES,
 * 4 SLEEP, 5 HEART_RATE, 6 BLOOD_OXYGEN, 7 TEMPERATURE, 8 HRV, 9 PRODUCTIVITY;
 * types 2..9 own metric slots 0..7. Highlights are stored as length-clamped
 * NUL-terminated strings, at most five.
 *
 * The saved-data logs promote the float fields with vcvt.f64.f32: build with
 * profile g2-apollo-main-20 (fpv5-d16). No float crosses a call boundary
 * except as a variadic double. */
#include <stdint.h>
#include <stddef.h>

#include "g2_health_data_manager.h"

#define HEALTH_METRIC_SLOTS       8u
#define HEALTH_HIGHLIGHT_SLOTS    5u
#define HEALTH_HIGHLIGHT_TEXT_MAX 0xffu

/* Stored metric (0x18 bytes). */
typedef struct {
    uint8_t type;       /* +0x00 */
    uint8_t pad1[3];
    uint32_t goal;      /* +0x04 */
    float value;        /* +0x08 */
    float avg_value;    /* +0x0c */
    uint32_t duration;  /* +0x10 */
    uint8_t trend;      /* +0x14 */
    uint8_t pad15[3];
} g2_health_metric_rec_t;
_Static_assert(sizeof(g2_health_metric_rec_t) == 0x18u, "health metric record");

/* Stored highlight: type then NUL-terminated text. */
typedef struct {
    uint8_t type;        /* +0x00 */
    uint8_t text[0x100]; /* +0x01 */
} g2_health_highlight_rec_t;
_Static_assert(sizeof(g2_health_highlight_rec_t) == 0x101u, "health highlight record");

/* Health record, RAM 0x200f41b4 (0x5d0 bytes). */
typedef struct {
    uint32_t head;                                              /* +0x000 */
    g2_health_metric_rec_t metric[HEALTH_METRIC_SLOTS];         /* +0x004 */
    uint32_t highlight_count;                                   /* +0x0c4 */
    g2_health_highlight_rec_t highlight[HEALTH_HIGHLIGHT_SLOTS];/* +0x0c8 */
    uint8_t pad5cd[3];
} g2_health_store_t;
_Static_assert(offsetof(g2_health_store_t, highlight_count) == 0xc4u, "highlight count");
_Static_assert(offsetof(g2_health_store_t, highlight) == 0xc8u, "highlights");
_Static_assert(sizeof(g2_health_store_t) == 0x5d0u, "health record");

extern g2_health_store_t g2_health_data; /* RAM 0x200f41b4 */

extern uint32_t health_lock_storage(void);   /* 0x4ffc32, 1 locked */
extern void health_unlock_storage(void);     /* 0x4ffc90 */
extern void *aeabi_memset_43c0e4(void *dst, uint32_t len, int32_t value); /* 0x43c0e4 */
extern void *audio_queue_copy_bytes(void *dst, const void *src, uint32_t len); /* memcpy 0x439be4 */
extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t,
                               const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */

static const char module_tag[] = "health.data_mgr"; /* ROM 0x7860c0 */
static const char source_file[] = "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\health\\health_data_manager.c"; /* ROM 0x6f3e00 */
static const char fn_save_single[] = "health_data_save_single";                 /* ROM 0x777aa4 */
static const char fn_save_mult[] = "health_data_save_mult";                     /* ROM 0x777ad4 */
static const char fn_convert[] = "health_data_convert_from_pb";                 /* ROM 0x76bd6c */
static const char fn_save_single_hl[] = "health_data_save_single_highlight";    /* ROM 0x754ba8 */
static const char fn_save_mult_hl[] = "health_data_save_mult_highlight";        /* ROM 0x760350 */
static const char fn_convert_hl[] = "health_data_convert_highlight_from_pb";    /* ROM 0x74a4ec */

static const char name_steps[] = "STEPS";               /* ROM 0x78d71c */
static const char name_calories[] = "CALORIES";         /* ROM 0x78ab20 */
static const char name_sleep[] = "SLEEP";               /* ROM 0x78d724 */
static const char name_heart_rate[] = "HEART_RATE";     /* ROM 0x78ab2c */
static const char name_blood_oxygen[] = "BLOOD_OXYGEN"; /* ROM 0x7860a0 */
static const char name_temperature[] = "TEMPERATURE";   /* ROM 0x78ab38 */
static const char name_hrv[] = "HRV";                   /* ROM 0x5598c4 */
static const char name_all[] = "ALL";                   /* ROM 0x5598c8 */
static const char name_productivity[] = "PRODUCTIVITY"; /* ROM 0x7860b0 */
static const char name_unknown[] = "UNKNOWN";           /* ROM 0x78d72c */

static const char bad_type[] = "Invalid data type: %d";                            /* ROM 0x777a8c */
static const char bad_type_s[] = "[health.data_mgr]Invalid data type: %d";         /* ROM 0x74a424 */
static const char single_null[] = "pb_single_data is NULL";                        /* ROM 0x777abc */
static const char single_null_s[] = "[health.data_mgr]pb_single_data is NULL";     /* ROM 0x74a44c */
static const char convert_fail[] = "Failed to convert pb data to internal format"; /* ROM 0x7345a4 */
static const char convert_fail_s[] = "[health.data_mgr]Failed to convert pb data to internal format"; /* ROM 0x70c164 */
static const char saved_fmt[] = "Saved health data: type=%s, goal=%u, value=%.2f, avg=%.2f, duration=%u, trend=%d"; /* ROM 0x6e82a8 */
static const char saved_fmt_s[] = "[health.data_mgr]Saved health data: type=%s, goal=%u, value=%.2f, avg=%.2f, duration=%u, trend=%d"; /* ROM 0x6dab24 */
static const char mult_null[] = "pb_mult_data is NULL";                            /* ROM 0x777aec */
static const char mult_null_s[] = "[health.data_mgr]pb_mult_data is NULL";         /* ROM 0x74a474 */
static const char no_data[] = "No data to save";                                   /* ROM 0x7860d0 */
static const char no_data_s[] = "[health.data_mgr]No data to save";                /* ROM 0x754b3c */
static const char batch_fmt[] = "Batch save health data: type=%s, goal=%u, value=%.2f, avg=%.2f, duration=%u, trend=%d"; /* ROM 0x6e3778 */
static const char batch_fmt_s[] = "[health.data_mgr]Batch save health data: type=%s, goal=%u, value=%.2f, avg=%.2f, duration=%u, trend=%d"; /* ROM 0x6d8c0c */
static const char convert_idx_fail[] = "Failed to convert pb data at index %d";    /* ROM 0x74a4c4 */
static const char convert_idx_fail_s[] = "[health.data_mgr]Failed to convert pb data at index %d"; /* ROM 0x71f640 */
static const char skip_idx[] = "Skipping invalid data type at index %d";           /* ROM 0x74a49c */
static const char skip_idx_s[] = "[health.data_mgr]Skipping invalid data type at index %d"; /* ROM 0x71f608 */
static const char bad_idx[] = "Invalid data type at index %d: %d";                 /* ROM 0x754b60 */
static const char bad_idx_s[] = "[health.data_mgr]Invalid data type at index %d: %d"; /* ROM 0x729f18 */
static const char batch_done[] = "Batch save completed: %d/%d items saved successfully"; /* ROM 0x71f678 */
static const char batch_done_s[] = "[health.data_mgr]Batch save completed: %d/%d items saved successfully"; /* ROM 0x6fad54 */
static const char convert_null[] = "pb_data or internal_data is NULL";             /* ROM 0x754b84 */
static const char convert_null_s[] = "[health.data_mgr]pb_data or internal_data is NULL"; /* ROM 0x729f4c */
static const char shl_null[] = "pb_single_highlight is NULL";                      /* ROM 0x76bd88 */
static const char shl_null_s[] = "[health.data_mgr]pb_single_highlight is NULL";   /* ROM 0x7345d4 */
static const char hl_convert_fail[] = "Failed to convert pb highlight to internal format"; /* ROM 0x729f80 */
static const char hl_convert_fail_s[] = "[health.data_mgr]Failed to convert pb highlight to internal format"; /* ROM 0x70335c */
static const char hl_saved[] = "Saved health highlight: type=%s, text_len=%d";     /* ROM 0x734604 */
static const char hl_saved_s[] = "[health.data_mgr]Saved health highlight: type=%s, text_len=%d"; /* ROM 0x70c1a4 */
static const char mhl_null[] = "pb_mult_highlight is NULL";                        /* ROM 0x76bda4 */
static const char mhl_null_s[] = "[health.data_mgr]pb_mult_highlight is NULL";     /* ROM 0x73f058 */
static const char hl_none[] = "No highlight data to save";                         /* ROM 0x76bdc0 */
static const char hl_none_s[] = "[health.data_mgr]No highlight data to save";      /* ROM 0x73f084 */
static const char hl_idx_fail[] = "Failed to convert pb highlight at index %d";    /* ROM 0x73f0b0 */
static const char hl_idx_fail_s[] = "[health.data_mgr]Failed to convert pb highlight at index %d"; /* ROM 0x71591c */
static const char hl_skip[] = "Skipping invalid highlight data type at index %d";  /* ROM 0x729fb4 */
static const char hl_skip_s[] = "[health.data_mgr]Skipping invalid highlight data type at index %d"; /* ROM 0x7033a0 */
static const char hl_full[] = "Highlight storage is full, skipping remaining items"; /* ROM 0x729fe8 */
static const char hl_full_s[] = "[health.data_mgr]Highlight storage is full, skipping remaining items"; /* ROM 0x6fad9c */
static const char hl_done[] = "Batch highlight save completed: %d/%d items saved successfully"; /* ROM 0x70c1e4 */
static const char hl_done_s[] = "[health.data_mgr]Batch highlight save completed: %d/%d items saved successfully"; /* ROM 0x6ed6f8 */
static const char hl_convert_null[] = "pb_highlight or internal_highlight is NULL"; /* ROM 0x73f0dc */
static const char hl_convert_null_s[] = "[health.data_mgr]pb_highlight or internal_highlight is NULL"; /* ROM 0x715958 */

#define LOG_E(level, fn, line, ...)                                                          \
    do {                                                                                     \
        if ((audio_log_flags() & 2u) != 0u)                                                  \
            audio_log_extended((level), module_tag, source_file, (fn), (line), __VA_ARGS__); \
    } while (0)
#define LOG_C(code, text, ...)                                                    \
    do {                                                                          \
        if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)     \
            (void)compress_log_output((code), (text), (text), ##__VA_ARGS__);     \
    } while (0)

uint8_t health_data_convert_from_pb_559d82(const g2_health_pb_data_t *pb, g2_health_metric_rec_t *rec);
uint8_t health_data_convert_highlight_from_pb_55a230(const g2_health_pb_highlight_t *pb,
                                                     g2_health_highlight_rec_t *rec);

/* Metric type -> slot index (types 2..9 -> 0..7), -1 otherwise. */
int32_t health_data_type_to_index_5597f0(uint8_t type)
{
    switch (type) {
    case HEALTH_TYPE_STEPS:        return 0;
    case HEALTH_TYPE_CALORIES:     return 1;
    case HEALTH_TYPE_SLEEP:        return 2;
    case HEALTH_TYPE_HEART_RATE:   return 3;
    case HEALTH_TYPE_BLOOD_OXYGEN: return 4;
    case HEALTH_TYPE_TEMPERATURE:  return 5;
    case HEALTH_TYPE_HRV:          return 6;
    case HEALTH_TYPE_PRODUCTIVITY: return 7;
    default:                       return -1;
    }
}

g2_health_metric_rec_t *health_data_slot_get_559836(uint8_t type)
{
    uint32_t index = (uint32_t)health_data_type_to_index_5597f0(type);
    if (index >= HEALTH_METRIC_SLOTS)
        return NULL;
    return &g2_health_data.metric[index];
}

const char *health_data_type_name_559854(uint8_t type)
{
    switch (type) {
    case HEALTH_TYPE_UNKNOWN:      return name_unknown;
    case HEALTH_TYPE_ALL:          return name_all;
    case HEALTH_TYPE_STEPS:        return name_steps;
    case HEALTH_TYPE_CALORIES:     return name_calories;
    case HEALTH_TYPE_SLEEP:        return name_sleep;
    case HEALTH_TYPE_HEART_RATE:   return name_heart_rate;
    case HEALTH_TYPE_BLOOD_OXYGEN: return name_blood_oxygen;
    case HEALTH_TYPE_TEMPERATURE:  return name_temperature;
    case HEALTH_TYPE_HRV:          return name_hrv;
    case HEALTH_TYPE_PRODUCTIVITY: return name_productivity;
    default:                       return name_unknown;
    }
}

int32_t health_data_reset_5598ae(void)
{
    (void)aeabi_memset_43c0e4(&g2_health_data, sizeof g2_health_data, 0);
    return 0;
}

/* Returns 0 saved, 1 NULL input, 3 invalid type, else the converter's code. */
uint8_t health_data_save_single_5598cc(const g2_health_pb_data_t *pb)
{
    if (pb == NULL) {
        LOG_E(1u, fn_save_single, 0x76u, single_null);
        LOG_C(0x04000000u, single_null_s);
        return 1u;
    }
    if (pb->type == HEALTH_TYPE_UNKNOWN || pb->type == HEALTH_TYPE_ALL) {
        LOG_E(1u, fn_save_single, 0x7cu, bad_type, pb->type);
        LOG_C(0x04400000u, bad_type_s, pb->type);
        return 3u;
    }
    g2_health_metric_rec_t *slot = health_data_slot_get_559836(pb->type);
    if (slot == NULL) {
        LOG_E(1u, fn_save_single, 0x83u, bad_type, pb->type);
        LOG_C(0x04400000u, bad_type_s, pb->type);
        return 3u;
    }
    (void)health_lock_storage();
    uint8_t rc = health_data_convert_from_pb_559d82(pb, slot);
    if (rc != 0u) {
        LOG_E(1u, fn_save_single, 0x8cu, convert_fail);
        LOG_C(0x04000000u, convert_fail_s);
        health_unlock_storage();
        return rc;
    }
    health_unlock_storage();
    LOG_E(4u, fn_save_single, 0x96u, saved_fmt, health_data_type_name_559854(pb->type), pb->goal,
          (double)pb->value, (double)pb->avg_value, pb->duration, pb->trend);
    LOG_C(0x11800000u, saved_fmt_s, health_data_type_name_559854(pb->type), pb->goal,
          (double)pb->value, (double)pb->avg_value, pb->duration, pb->trend);
    return 0u;
}

uint8_t health_data_save_mult_559ad2(const g2_health_pb_mult_data_t *pb)
{
    if (pb == NULL) {
        LOG_E(1u, fn_save_mult, 0xa1u, mult_null);
        LOG_C(0x04000000u, mult_null_s);
        return 1u;
    }
    if (pb->count == 0u) {
        LOG_E(2u, fn_save_mult, 0xa6u, no_data);
        LOG_C(0x08000000u, no_data_s);
        return 0u;
    }
    int32_t saved = 0;
    (void)health_lock_storage();
    for (int32_t i = 0; i < (int32_t)pb->count; i++) {
        const g2_health_pb_data_t *item = &pb->data[i];
        if (item->type == HEALTH_TYPE_UNKNOWN || item->type == HEALTH_TYPE_ALL) {
            LOG_E(2u, fn_save_mult, 0xb5u, skip_idx, i);
            LOG_C(0x08400000u, skip_idx_s, i);
            continue;
        }
        g2_health_metric_rec_t *slot = health_data_slot_get_559836(item->type);
        if (slot == NULL) {
            LOG_E(2u, fn_save_mult, 0xbcu, bad_idx, i, item->type);
            LOG_C(0x08800000u, bad_idx_s, i, item->type);
            continue;
        }
        if (health_data_convert_from_pb_559d82(item, slot) != 0u) {
            LOG_E(1u, fn_save_mult, 0xc3u, convert_idx_fail, i);
            LOG_C(0x04400000u, convert_idx_fail_s, i);
            continue;
        }
        LOG_E(4u, fn_save_mult, 0xc9u, batch_fmt, health_data_type_name_559854(item->type),
              item->goal, (double)item->value, (double)item->avg_value, item->duration, item->trend);
        LOG_C(0x11800000u, batch_fmt_s, health_data_type_name_559854(item->type), item->goal,
              (double)item->value, (double)item->avg_value, item->duration, item->trend);
        saved++;
    }
    health_unlock_storage();
    LOG_E(3u, fn_save_mult, 0xd1u, batch_done, saved, pb->count);
    LOG_C(0x0c800000u, batch_done_s, saved, pb->count);
    return 0u;
}

uint8_t health_data_convert_from_pb_559d82(const g2_health_pb_data_t *pb, g2_health_metric_rec_t *rec)
{
    if (pb == NULL || rec == NULL) {
        LOG_E(1u, fn_convert, 0x128u, convert_null);
        LOG_C(0x04000000u, convert_null_s);
        return 1u;
    }
    (void)aeabi_memset_43c0e4(rec, sizeof *rec, 0);
    rec->type = pb->type;
    rec->goal = pb->goal;
    rec->value = pb->value;
    rec->avg_value = pb->avg_value;
    rec->duration = pb->duration;
    rec->trend = pb->trend;
    return 0u;
}

/* Replaces all stored highlights with this one. */
uint8_t health_data_save_single_highlight_559dfc(const g2_health_pb_highlight_t *pb)
{
    if (pb == NULL) {
        LOG_E(1u, fn_save_single_hl, 0x141u, shl_null);
        LOG_C(0x04000000u, shl_null_s);
        return 1u;
    }
    if (pb->type == HEALTH_TYPE_UNKNOWN || pb->type == HEALTH_TYPE_ALL) {
        LOG_E(1u, fn_save_single_hl, 0x147u, bad_type, pb->type);
        LOG_C(0x04400000u, bad_type_s, pb->type);
        return 3u;
    }
    (void)health_lock_storage();
    g2_health_store_t *store = &g2_health_data;
    (void)aeabi_memset_43c0e4(store->highlight, sizeof store->highlight, 0);
    store->highlight_count = 0u;
    store->highlight_count = 1u;
    uint8_t rc = health_data_convert_highlight_from_pb_55a230(pb, &store->highlight[0]);
    if (rc != 0u) {
        LOG_E(1u, fn_save_single_hl, 0x158u, hl_convert_fail);
        LOG_C(0x04000000u, hl_convert_fail_s);
        store->highlight_count = 0u;
        health_unlock_storage();
        return rc;
    }
    health_unlock_storage();
    LOG_E(3u, fn_save_single_hl, 0x163u, hl_saved, health_data_type_name_559854(pb->type), pb->text_size);
    LOG_C(0x0c800000u, hl_saved_s, health_data_type_name_559854(pb->type), pb->text_size);
    return 0u;
}

uint8_t health_data_save_mult_highlight_559fb8(const g2_health_pb_mult_highlight_t *pb)
{
    if (pb == NULL) {
        LOG_E(1u, fn_save_mult_hl, 0x16eu, mhl_null);
        LOG_C(0x04000000u, mhl_null_s);
        return 1u;
    }
    if (pb->count == 0u) {
        LOG_E(2u, fn_save_mult_hl, 0x173u, hl_none);
        LOG_C(0x08000000u, hl_none_s);
        return 0u;
    }
    (void)health_lock_storage();
    g2_health_store_t *store = &g2_health_data;
    (void)aeabi_memset_43c0e4(store->highlight, sizeof store->highlight, 0);
    store->highlight_count = 0u;
    int32_t saved = 0;
    for (int32_t i = 0; i < (int32_t)pb->count; i++) {
        const g2_health_pb_highlight_t *item = &pb->item[i];
        if (item->type == HEALTH_TYPE_UNKNOWN || item->type == HEALTH_TYPE_ALL) {
            LOG_E(2u, fn_save_mult_hl, 0x185u, hl_skip, i);
            LOG_C(0x08400000u, hl_skip_s, i);
            continue;
        }
        if (store->highlight_count > HEALTH_HIGHLIGHT_SLOTS - 1u) {
            LOG_E(2u, fn_save_mult_hl, 0x18bu, hl_full);
            LOG_C(0x08000000u, hl_full_s);
            break;
        }
        if (health_data_convert_highlight_from_pb_55a230(item, &store->highlight[store->highlight_count]) == 0u) {
            store->highlight_count++;
            saved++;
        } else {
            LOG_E(1u, fn_save_mult_hl, 0x195u, hl_idx_fail, i);
            LOG_C(0x04400000u, hl_idx_fail_s, i);
        }
    }
    health_unlock_storage();
    LOG_E(3u, fn_save_mult_hl, 0x1a0u, hl_done, saved, pb->count);
    LOG_C(0x0c800000u, hl_done_s, saved, pb->count);
    return 0u;
}

uint8_t health_data_convert_highlight_from_pb_55a230(const g2_health_pb_highlight_t *pb,
                                                     g2_health_highlight_rec_t *rec)
{
    if (pb == NULL || rec == NULL) {
        LOG_E(1u, fn_convert_hl, 0x1e6u, hl_convert_null);
        LOG_C(0x04000000u, hl_convert_null_s);
        return 1u;
    }
    (void)aeabi_memset_43c0e4(rec, sizeof *rec, 0);
    rec->type = pb->type;
    uint32_t len = pb->text_size;
    if (len > HEALTH_HIGHLIGHT_TEXT_MAX)
        len = HEALTH_HIGHLIGHT_TEXT_MAX;
    (void)audio_queue_copy_bytes(rec->text, pb->text, len);
    rec->text[len] = 0u;
    return 0u;
}
