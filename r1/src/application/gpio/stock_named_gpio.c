/* Owner-authorized reconstruction from authenticated R1 named-GPIO records.
 * Original 0x54C24 registration, 0x54AFC callback, 0x54ED0 read, 0x54B40 close.
 * Event-open and shared-pin IRQ dispatch use authenticated nrfx interfaces. */
#include <stddef.h>
#include "nrfx_gpiote.h"
#include "stock_named_gpio.h"
extern int strcmp(const char *,const char *);
typedef struct {
    uintptr_t reserved_00,reserved_04;
    uint32_t (*open)(generic_device_registry_device *);
    uint32_t (*close)(generic_device_registry_device *);
    generic_device_registry_operation read;
    uintptr_t reserved_14,reserved_18,reserved_1c;
    uint32_t (*callback)(generic_device_registry_device *,uintptr_t,uintptr_t);
} named_gpio_ops;
_Static_assert(sizeof(r1_named_gpio_record)==44,"stock stride");
_Static_assert(offsetof(r1_named_gpio_record,device)==16,"embedded registry");
_Static_assert(offsetof(r1_named_gpio_record,callback)==40,"callback slot");
_Static_assert(sizeof(named_gpio_ops)==36,"shared nine-word table");
static const named_gpio_ops operations __attribute__((section(".r1.gpio.ops"),aligned(4)))={
    .open=r1_named_gpio_open,.close=r1_named_gpio_close,.read=r1_named_gpio_read,.callback=r1_named_gpio_callback
};
#define RECORD(text,number,edge) {.name=text,.pin=number,.polarity=edge}
r1_named_gpio_record r1_named_gpio_records[7]
    __attribute__((section(".r1.gpio.records"),aligned(4)))={
    RECORD("acc_int_1",15,1),RECORD("ppg_int",21,2),RECORD("touch_rdy_in",17,2),
    RECORD("mcu_reset_irq",18,2),RECORD("pmic_irq",33,2),RECORD("nfc_gpo_irq",3,1),
    RECORD("device_stacmd_irq",33,2)
};
static r1_named_gpio_record *find_record(generic_device_registry_device *device) {
    for (unsigned i=0;i<7;++i) {
        /* Stock reloads the caller name before the record name each time. */
        const char *device_name=((volatile generic_device_registry_device *)device)->name;
        const char *record_name=((volatile r1_named_gpio_record *)&r1_named_gpio_records[i])->name;
        if (strcmp(record_name,device_name)==0) return &r1_named_gpio_records[i];
    }
    return NULL;
}
uint32_t r1_named_gpio_register_all(void) {
    uint32_t status=0;
    for (unsigned i=0;i<7;++i) {
        r1_named_gpio_records[i].device.name=r1_named_gpio_records[i].name;
        r1_named_gpio_records[i].device.ops=(const generic_device_registry_ops *)&operations;
        status=r1_stock_registry_register(&r1_named_gpio_records[i].device);
    }
    return status;
}
uint32_t r1_named_gpio_callback(generic_device_registry_device *device,uintptr_t operation,uintptr_t callback) {
    (void)operation;
    r1_named_gpio_record *record=find_record(device);
    if (record==NULL) return 2;
    record->callback=callback;
    return 0;
}
/* The pin decoder uses local scratch; R3 is not a C operation output. */
__attribute__((used,noinline)) static uint32_t named_gpio_read_body(
        generic_device_registry_device *device,uintptr_t operation,uintptr_t output,
        uint32_t *saved_r3) {
    (void)operation;
    r1_named_gpio_record *record=find_record(device);
    if (record==NULL) return 2;
    *saved_r3=record->pin;
    NRF_GPIO_Type *port=nrf_gpio_pin_port_decode(saved_r3);
    *(uint8_t *)output=(uint8_t)((port->IN>>*saved_r3)&1u);
    return 0;
}
uint32_t r1_named_gpio_read(generic_device_registry_device *device,
        uintptr_t operation,uintptr_t output,uintptr_t extra) {
    (void)extra;
    uint32_t pin=0;
    return named_gpio_read_body(device,operation,output,&pin);
}
uint32_t r1_named_gpio_close(generic_device_registry_device *device) {
    r1_named_gpio_record *record=find_record(device);
    if (record==NULL) return 2;
    if (record->opened!=0) {
        nrfx_gpiote_in_event_disable(record->pin);
        nrfx_gpiote_in_uninit(record->pin);
        record->opened=0;
    }
    return 0;
}

/* Stock 0x6ED94 dispatches every matching record, including shared P1.01. */
void r1_named_gpio_irq_dispatch(nrfx_gpiote_pin_t pin,nrf_gpiote_polarity_t action) {
    for (unsigned i=0;i<7;++i) {
        r1_named_gpio_record *record=&r1_named_gpio_records[i];
        if (record->pin==pin && record->callback!=0) {
            void (*callback)(uint8_t,nrf_gpiote_polarity_t)=(void (*)(uint8_t,nrf_gpiote_polarity_t))record->callback;
            callback((uint8_t)pin,action);
        }
    }
}
/* Local words supply the decoded pin and initialized GPIOTE configuration. */
__attribute__((used,noinline)) static uint32_t named_gpio_open_body(
        generic_device_registry_device *device,volatile uint32_t *frame) {
    r1_named_gpio_record *record=find_record(device);
    if (record==NULL) return 2;
    if (record->opened!=0) return 0;
    frame[0]=record->pin;
    NRF_GPIO_Type *port=nrf_gpio_pin_port_decode((uint32_t *)(uintptr_t)frame);
    port->PIN_CNF[frame[0]]=2;
    if (!nrfx_gpiote_is_init()) (void)nrfx_gpiote_init();
    frame[1]=3;
    volatile uint8_t *configuration=(volatile uint8_t *)(frame+1);
    configuration[0]=record->polarity;
    configuration[1]=record->pull;
    _Static_assert(sizeof(nrfx_gpiote_in_config_t)<=4,"stock config extent");
    _Static_assert(offsetof(nrfx_gpiote_in_config_t,pull)==1,"short-enum pull offset");
    (void)nrfx_gpiote_in_init(record->pin,
            (const nrfx_gpiote_in_config_t *)(uintptr_t)configuration,
            r1_named_gpio_irq_dispatch);
    nrfx_gpiote_in_event_enable(record->pin,true);
    record->opened=1;
    return 0;
}
uint32_t r1_named_gpio_open(generic_device_registry_device *device) {
    volatile uint32_t frame[3]={0};
    return named_gpio_open_body(device,frame);
}
