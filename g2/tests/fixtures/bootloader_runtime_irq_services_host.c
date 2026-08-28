/* SPDX-License-Identifier: MIT */
#define OPEN_CFW_IRQ_SERVICES_HOST 1
#include "../../components/bootloader/core_overlay/runtime_irq_services_41fdc0.c"

static open_cfw_irq_u32 calls[16];
static open_cfw_irq_u32 count;
static open_cfw_irq_u32 status_value;
static int handle_object;

void open_cfw_irq_host_enable(open_cfw_irq_u32 index, open_cfw_irq_u32 mask)
{ calls[count++] = 0x10000000U | index; calls[count++] = mask; }
void open_cfw_irq_host_priority(open_cfw_irq_u32 index, open_cfw_irq_u8 value)
{ calls[count++] = 0x20000000U | index; calls[count++] = value; }
void open_cfw_irq_host_system_priority(open_cfw_irq_u32 index, open_cfw_irq_u8 value)
{ calls[count++] = 0x30000000U | index; calls[count++] = value; }
void *open_cfw_irq_host_mspi_handle(void) { calls[count++] = 0x40000000U; return &handle_object; }
void open_cfw_irq_host_mspi_status(void *handle, open_cfw_irq_u32 *status, open_cfw_irq_u32 enabled_only)
{ calls[count++] = handle == &handle_object ? 0x50000000U : 0U; calls[count++] = enabled_only; *status = status_value; }
void open_cfw_irq_host_mspi_clear(void *handle, open_cfw_irq_u32 status)
{ calls[count++] = handle == &handle_object ? 0x60000000U : 0U; calls[count++] = status; }
void open_cfw_irq_host_mspi_service(void *handle, open_cfw_irq_u32 status)
{ calls[count++] = handle == &handle_object ? 0x70000000U : 0U; calls[count++] = status; }

void open_cfw_irq_fixture_reset(open_cfw_irq_u32 status)
{ open_cfw_irq_u32 i; count = 0U; status_value = status; for (i = 0U; i < 16U; ++i) calls[i] = 0U; }
open_cfw_irq_u32 open_cfw_irq_fixture_count(void) { return count; }
open_cfw_irq_u32 open_cfw_irq_fixture_call(open_cfw_irq_u32 index) { return calls[index]; }
