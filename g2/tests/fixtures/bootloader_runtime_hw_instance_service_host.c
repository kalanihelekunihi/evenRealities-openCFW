#include <stdint.h>
#include <string.h>

#include "../../components/bootloader/core_overlay/runtime_hw_instance_service_422ba8.c"

open_cfw_hws_u32 open_cfw_hws_host_registers[4][32];
open_cfw_hws_u32 open_cfw_hws_host_revision;
open_cfw_hws_u32 open_cfw_hws_host_clock;
open_cfw_hws_u32 open_cfw_hws_host_events[16][3];
open_cfw_hws_u32 open_cfw_hws_host_event_count;

static void open_cfw_hws_host_event(open_cfw_hws_u32 kind, open_cfw_hws_u32 a, open_cfw_hws_u32 b)
{
    open_cfw_hws_u32 n = open_cfw_hws_host_event_count++;
    if (n < 16U) { open_cfw_hws_host_events[n][0] = kind; open_cfw_hws_host_events[n][1] = a; open_cfw_hws_host_events[n][2] = b; }
}

void open_cfw_hws_host_resource_enter(open_cfw_hws_u32 resource) { open_cfw_hws_host_event(1, resource, 0); }
void open_cfw_hws_host_mode_enable(open_cfw_hws_u32 mode, open_cfw_hws_u32 resource) { open_cfw_hws_host_event(2, mode, resource); }
void open_cfw_hws_host_mode_disable(open_cfw_hws_u32 mode, open_cfw_hws_u32 resource) { open_cfw_hws_host_event(3, mode, resource); }
void open_cfw_hws_host_teardown(open_cfw_hws_instance *instance, open_cfw_hws_u32 value) { open_cfw_hws_host_event(4, (open_cfw_hws_u32)(uintptr_t)instance, value); }
void open_cfw_hws_host_resource_exit(open_cfw_hws_u32 resource) { open_cfw_hws_host_event(5, resource, 0); }

void open_cfw_hws_host_reset(void)
{
    memset(open_cfw_hws_host_registers, 0, sizeof(open_cfw_hws_host_registers));
    memset(open_cfw_hws_host_events, 0, sizeof(open_cfw_hws_host_events));
    open_cfw_hws_host_revision = 0;
    open_cfw_hws_host_clock = 0;
    open_cfw_hws_host_event_count = 0;
}
