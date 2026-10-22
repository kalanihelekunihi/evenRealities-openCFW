/* Shared declarations of the stock dashboard_watchface_layout1.c units in this
 * directory (layout1: big clock, date, glasses/ring battery row and two
 * complication slots). */
#ifndef G2_A63_DASHBOARD_WATCHFACE_LAYOUT1_H
#define G2_A63_DASHBOARD_WATCHFACE_LAYOUT1_H

#include <stdint.h>

/* One complication slot (12 bytes); same record as layout2's slots and the
 * a-64 layout1 health refresh (g2_wf_slot_t there). */
typedef struct {
    void *icon;     /* +0x0 lv_image */
    void *label;    /* +0x4 lv_label */
    uint8_t kind;   /* +0x8 complication kind (0 none, 1 weather, 4 value ...) */
    uint8_t side;   /* +0x9 1 = left slot, 0 = right slot */
    uint8_t pad[2];
} g2_wf_slot_t;
_Static_assert(sizeof(g2_wf_slot_t) == 12u, "watchface slot record");

typedef void (*g2_wf_slot_fn_t)(g2_wf_slot_t *slot, const void *arg);

extern g2_wf_slot_t g2_layout1_slot_a; /* RAM 0x200005dc, left slot */
extern g2_wf_slot_t g2_layout1_slot_b; /* RAM 0x20073fa8, right slot */

void layout1_slot_layout_5b7a4c(g2_wf_slot_t *slot);
void layout1_slots_for_kind_5b845c(uint8_t kind, g2_wf_slot_fn_t fn, const void *arg);

#endif
