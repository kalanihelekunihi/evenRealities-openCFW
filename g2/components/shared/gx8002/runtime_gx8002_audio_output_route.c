/* SPDX-License-Identifier: MIT */
#include <stdint.h>
#include <stddef.h>
typedef void (*frame_callback)(uint32_t,uint32_t);
typedef void (*completion_callback)(void);
typedef struct {
    const char *name;
    uint8_t active,padding5[3];
    uint32_t reserved8;
    uint8_t available_route,padding13[3];
    int16_t mute,cached_db;
    uint32_t reserved20;
    uint8_t selected_route,stride,frame_interrupt_armed,frame_callback_enabled;
    uint8_t drain_complete,padding29[3];
    uint32_t frame_start,frame_end;
    frame_callback frame;
    completion_callback completed;
    void *settings;
} output_route;
_Static_assert(sizeof(output_route)==52,"Playback route size");
_Static_assert(offsetof(output_route,mute)==16,"Playback mutable state");
_Static_assert(offsetof(output_route,drain_complete)==28,"Completion flag");
_Static_assert(offsetof(output_route,frame)==40,"Frame callback");
_Static_assert(offsetof(output_route,settings)==48,"Settings pointer");
const char open_cfw_gx8002_aout_route_name[]="0 route play";
/* Initial state recovered from pinned SDK s_hw_route and the stock image.
 * Configuration/allocation routines own subsequent state transitions. */
output_route open_cfw_gx8002_aout_route={.name=open_cfw_gx8002_aout_route_name};
