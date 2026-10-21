#include <stdint.h>
#include <stddef.h>
#include "nrfx_wdt.h"
#include "stock_registry.h"

typedef uint32_t (*life_op)(generic_device_registry_device *);
typedef uint32_t (*words_op)(generic_device_registry_device *,uintptr_t,uintptr_t);
struct wdt_ops {
    life_op slot_00;uintptr_t reserved_04;life_op slot_08,slot_0c;
    generic_device_registry_operation slot_10,slot_14;
    words_op slot_18;uintptr_t reserved_1c;words_op slot_20;
};
struct wdt_state {
    const char *name;uint8_t opened;nrfx_wdt_channel_id channel;
    nrfx_wdt_config_t config;generic_device_registry_device record;struct wdt_ops ops;
};
extern void r1_adc_error(uint32_t);
uint32_t r1_native_named_wdt_open(generic_device_registry_device *);
uint32_t r1_native_named_wdt_feed(generic_device_registry_device *,uintptr_t,uintptr_t);
void r1_native_wdt_timeout(void) {}
struct wdt_state r1_native_named_wdt
 __attribute__((section(".r1.wdt.state"),aligned(4)))={
    .name="watchdog",.config={.behaviour=NRF_WDT_BEHAVIOUR_RUN_SLEEP,.reload_value=10000,.interrupt_priority=6},
    .ops={.slot_00=r1_native_named_wdt_open,.slot_18=r1_native_named_wdt_feed}
};
_Static_assert(offsetof(struct wdt_state,opened)==4,"stock opened flag");
_Static_assert(offsetof(struct wdt_state,channel)==5,"stock channel");
_Static_assert(offsetof(struct wdt_state,config)==8,"stock config");
_Static_assert(offsetof(struct wdt_state,record)==20,"stock registry record");
_Static_assert(offsetof(struct wdt_state,ops)==44,"stock ops table");
_Static_assert(sizeof(struct wdt_state)==80,"stock state bytes");
uint32_t r1_native_named_wdt_open(generic_device_registry_device *device)
{
    (void)device;
    if (!r1_native_named_wdt.opened) {
        nrfx_err_t status=nrfx_wdt_init(&r1_native_named_wdt.config,r1_native_wdt_timeout);
        if (status) r1_adc_error(status);
        status=nrfx_wdt_channel_alloc(&r1_native_named_wdt.channel);
        if (status) r1_adc_error(status);
        nrfx_wdt_enable();r1_native_named_wdt.opened=1;
    }
    return 0;
}
uint32_t r1_native_named_wdt_feed(generic_device_registry_device *device,uintptr_t command,uintptr_t ignored)
{
    (void)device;(void)ignored;
    if (!r1_native_named_wdt.opened) return 19;
    if (command) return 25;
    nrfx_wdt_channel_feed(r1_native_named_wdt.channel);return 0;
}
uint32_t r1_native_named_wdt_register(void)
{
    r1_native_named_wdt.record.name=r1_native_named_wdt.name;
    r1_native_named_wdt.record.ops=(const generic_device_registry_ops *)(const void *)&r1_native_named_wdt.ops;
    return r1_stock_registry_register(&r1_native_named_wdt.record);
}
