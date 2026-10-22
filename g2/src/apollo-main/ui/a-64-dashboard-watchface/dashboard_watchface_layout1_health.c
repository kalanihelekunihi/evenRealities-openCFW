/* Dashboard watchface layout1 health complication refresh, stock
 * D:\01_workspace\s200_ap510b_iar_git\app\gui\dashboard\dashboard_watchface_layout1.c
 * (log tag "dashboard.wf.l1"). Native 0x5b873c..0x5b87cb; literal pool shared
 * with the rest of layout1 (0x5b87cc..0x5b89ef).
 *
 * 0x5b87bc is ops slot +0x30 of the layout1 ops table (ROM 0x713f54).
 * Passes the health value in s0 (hard-float ABI): profile g2-apollo-main-3. */
#include <stdint.h>
#include <stddef.h>

#define VFP __attribute__((pcs("aapcs-vfp")))

/* One complication slot (12 bytes), same layout as layout2's records. */
typedef struct {
    void *icon;     /* +0x0 lv_image */
    void *label;    /* +0x4 lv_label */
    uint8_t kind;   /* +0x8 complication kind */
    uint8_t side;   /* +0x9 read by layout1_slot_layout_5b7a4c */
    uint8_t pad[2];
} g2_wf_slot_t;
_Static_assert(sizeof(g2_wf_slot_t) == 12u, "watchface slot record");

typedef struct {
    uint8_t type;      /* +0x00 */
    uint8_t pad1[3];
    uint32_t goal;     /* +0x04 */
    float value;       /* +0x08 */
    float avg_value;   /* +0x0c */
    uint32_t duration; /* +0x10 */
    uint8_t trend;     /* +0x14 */
    uint8_t pad15[3];
} g2_wf_health_metric_t;
_Static_assert(sizeof(g2_wf_health_metric_t) == 0x18u, "health metric record");

typedef struct {
    uint32_t head;                    /* +0x00 */
    g2_wf_health_metric_t metric[8];  /* +0x04 */
} g2_wf_health_data_t;

extern g2_wf_health_data_t g2_health_data;   /* RAM 0x200f41b4 */
extern g2_wf_slot_t g2_layout1_slot_a;       /* RAM 0x200005dc */
extern g2_wf_slot_t g2_layout1_slot_b;       /* RAM 0x20073fa8 */

extern uint32_t audio_terminal_ui_object_valid_43e2ea(void *object); /* lv_obj_is_valid */
extern void *aeabi_memset_43c0e4(void *dst, uint32_t len, int32_t value);
extern const char *audio_uart_page_49942e(void *label, const char *text); /* lv_label_set_text */
extern uint32_t health_lock_storage(void);                            /* 0x4ffc32 */
extern void health_unlock_storage(void);                              /* 0x4ffc90 */
extern int32_t watchface_health_metric_index_5b8a6a(uint8_t kind);
extern VFP void watchface_health_value_format_5b8a9c(float value, uint8_t kind, uint32_t duration,
                                                     char *buf, uint32_t size);
extern void layout1_slot_layout_5b7a4c(g2_wf_slot_t *slot);           /* re-aligns icon/label */

void layout1_slot_health_refresh_5b873c(g2_wf_slot_t *slot);
void layout1_refresh_health_5b87bc(void);

void layout1_slot_health_refresh_5b873c(g2_wf_slot_t *slot)
{
    char text[16];
    int32_t index;
    float value;
    uint32_t duration;

    if (slot == NULL || slot->label == NULL)
        return;
    if (audio_terminal_ui_object_valid_43e2ea(slot->label) == 0u)
        return;
    index = watchface_health_metric_index_5b8a6a(slot->kind);
    if (index < 0)
        return;
    (void)health_lock_storage();
    value = g2_health_data.metric[index].value;
    duration = g2_health_data.metric[index].duration;
    health_unlock_storage();
    (void)aeabi_memset_43c0e4(text, sizeof(text), 0);
    watchface_health_value_format_5b8a9c(value, slot->kind, duration, text, sizeof(text));
    (void)audio_uart_page_49942e(slot->label, text);
    layout1_slot_layout_5b7a4c(slot);
}

void layout1_refresh_health_5b87bc(void)
{
    layout1_slot_health_refresh_5b873c(&g2_layout1_slot_a);
    layout1_slot_health_refresh_5b873c(&g2_layout1_slot_b);
}
