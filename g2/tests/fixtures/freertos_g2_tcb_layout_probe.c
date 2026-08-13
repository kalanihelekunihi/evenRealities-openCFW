#include <stddef.h>
#include "FreeRTOS.h"

_Static_assert(sizeof(StaticTask_t) == 0x70U, "G2 StaticTask_t size");
_Static_assert(
    offsetof(StaticTask_t, ulDummyG2StackDepth) == 0x54U,
    "G2 stack-depth offset"
);
_Static_assert(
    offsetof(StaticTask_t, uxDummy10) == 0x58U,
    "G2 trace-number offset"
);
_Static_assert(
    offsetof(StaticTask_t, uxDummy12) == 0x60U,
    "G2 mutex metadata offset"
);
_Static_assert(
    offsetof(StaticTask_t, ulDummy18) == 0x68U,
    "G2 notification-value offset"
);
_Static_assert(
    offsetof(StaticTask_t, ucDummy19) == 0x6CU,
    "G2 notification-state offset"
);
_Static_assert(
    offsetof(StaticTask_t, uxDummy20) == 0x6DU,
    "G2 allocation-provenance offset"
);

int open_cfw_g2_tcb_layout_probe(void) {
    return (int)sizeof(StaticTask_t);
}
