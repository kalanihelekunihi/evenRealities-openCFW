#include <stdint.h>

extern void *host_box_timer_force;
extern void *host_box_timer_reconnect;
extern uint8_t host_box_local[4];
extern uint8_t host_box_last_local[4];
extern uint8_t host_box_case[8];
extern uint8_t host_box_force;
extern uint8_t host_box_ring_connected;
extern uint8_t host_box_ring_reconnect;

#define OPEN_CFW_BOX_DETECT_TIMER_FORCE host_box_timer_force
#define OPEN_CFW_BOX_DETECT_TIMER_RECONNECT host_box_timer_reconnect
#define OPEN_CFW_BOX_DETECT_LOCAL_STATE host_box_local
#define OPEN_CFW_BOX_DETECT_LAST_LOCAL_STATE host_box_last_local
#define OPEN_CFW_BOX_DETECT_CASE_STATE host_box_case
#define OPEN_CFW_BOX_DETECT_FORCE_OUT host_box_force
#define OPEN_CFW_BOX_DETECT_RING_CONNECTED host_box_ring_connected
#define OPEN_CFW_BOX_DETECT_RING_RECONNECT host_box_ring_reconnect
#define OPEN_CFW_BOX_DETECT_TIMER_FORCE_ATTRIBUTES ((const void *)1)
#define OPEN_CFW_BOX_DETECT_TIMER_RECONNECT_ATTRIBUTES ((const void *)2)
