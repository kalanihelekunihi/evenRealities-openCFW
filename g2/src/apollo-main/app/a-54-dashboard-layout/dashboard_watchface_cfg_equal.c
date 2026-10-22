/* Dashboard watchface-config comparison, stock
 * D:\01_workspace\s200_ap510b_iar_git\app\gui\dashboard\dashboard_layout.c.
 * Native 0x55819e..0x558313 (no literal pool). Split from
 * dashboard_layout_store.c only because kind 4 compares single-precision
 * floats with vcmp.f32 (profile g2-apollo-main-3).
 *
 * The config sits at layout +8; byte +0 is the kind (0 none, 1..4). Kinds
 * 1 and 3 use bytes +4..+6, kind 2 adds +7 = slot count and slots +8..,
 * kind 4 (see below) carries up to three floats and three 32-byte names. */
#include <stdint.h>
#include <stddef.h>

typedef struct {
    uint8_t kind;           /* +0x00 4 */
    uint8_t reserved_01[3];
    uint8_t field_04;       /* +0x04 */
    uint8_t field_05;       /* +0x05 */
    uint8_t value_count;    /* +0x06 */
    uint8_t reserved_07;
    float values[3];        /* +0x08 */
    uint8_t name_count;     /* +0x14 */
    char names[3][32];      /* +0x15 */
} g2_dashboard_watchface_kind4_t;
_Static_assert(offsetof(g2_dashboard_watchface_kind4_t, values) == 0x08, "values at +8");
_Static_assert(offsetof(g2_dashboard_watchface_kind4_t, name_count) == 0x14, "name_count at +0x14");
_Static_assert(offsetof(g2_dashboard_watchface_kind4_t, names) == 0x15, "names at +0x15");

extern int32_t audio_ble_hci_vendor_compare_44b610(const void *a, const void *b, uint32_t n); /* strncmp */

/* 1 when both configs are equal for their kind (kind 0 and unknown kinds
 * compare equal once the kind bytes match), 0 otherwise. */
int32_t dashboard_watchface_cfg_equal_55819e(const uint8_t *a, const uint8_t *b)
{
    if (a[0] != b[0])
        return 0;
    switch (a[0]) {
    case 1u:
    case 3u:
        return a[4] == b[4] && a[5] == b[5] && a[6] == b[6];
    case 2u:
        if (a[4] != b[4] || a[5] != b[5] || a[6] != b[6] || a[7] != b[7])
            return 0;
        for (uint8_t i = 0u; i < a[7]; i++) {
            if (a[8u + i] != b[8u + i])
                return 0;
        }
        return 1;
    case 4u: {
        const g2_dashboard_watchface_kind4_t *x = (const g2_dashboard_watchface_kind4_t *)(const void *)a;
        const g2_dashboard_watchface_kind4_t *y = (const g2_dashboard_watchface_kind4_t *)(const void *)b;
        if (x->field_04 != y->field_04 || x->field_05 != y->field_05 || x->value_count != y->value_count)
            return 0;
        for (uint8_t i = 0u; i < x->value_count; i++) {
            if (x->values[i] != y->values[i])
                return 0;
        }
        if (x->name_count != y->name_count)
            return 0;
        for (uint8_t i = 0u; i < x->name_count; i++) {
            if (audio_ble_hci_vendor_compare_44b610(x->names[i], y->names[i], 32u) != 0)
                return 0;
        }
        return 1;
    }
    default:
        return 1;
    }
}
