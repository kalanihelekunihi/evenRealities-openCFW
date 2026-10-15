/* Native board-binding wrappers 0x56508/20/38/50. Owner-authorized recovery
 * from the hash-locked R1 application. Typed initializers recover stock scalar data and relocate callbacks to C
 * bodies. Original instruction placement and delay cycle identity remain open. */
#include <stddef.h>
#include "stock_records.h"
_Static_assert(offsetof(r1_stock_twi_record, engine)==8, "stock engine");
_Static_assert(offsetof(r1_stock_twi_record, device)==52, "stock registry record");
_Static_assert(offsetof(r1_stock_twi_record, ops)==76, "stock operations");
_Static_assert(sizeof(r1_stock_twi_record)==112, "stock stride");
extern void r1_twi_gpio_low(uint32_t pin), r1_twi_gpio_high(uint32_t pin);
extern void r1_twi_gpio_output(uint32_t pin), r1_twi_gpio_input(uint32_t pin,uint32_t pull);
extern void r1_twi_gpio_release(uint32_t pin);
extern uint32_t r1_twi_gpio_read(uint32_t pin);
extern void r1_twi_delay_busy(uint32_t value),r1_twi_delay_noop(uint32_t value);
#define RECORD(bus,scl,sda,delay,delayfn) { \
    .name="i2c_" #bus, .engine={.delay_context=delay,.scl_pin=scl,.sda_pin=sda, \
    .drive_low=r1_twi_gpio_low,.release_high=r1_twi_gpio_high,.set_output=r1_twi_gpio_output, \
    .set_input=r1_twi_gpio_input,.input_pull=3,.udelay=delayfn,.read_pin=r1_twi_gpio_read}, \
    .pin_release=r1_twi_gpio_release,.ops={.open=r1_stock_i2c##bus##_open, \
    .close=r1_stock_i2c##bus##_close,.read=r1_stock_i2c##bus##_read,.write=r1_stock_i2c##bus##_write} }
r1_stock_twi_record r1_stock_twi_records[4]
    __attribute__((section(".r1.twi.records"),aligned(4)))={
    RECORD(2,28,45,1,r1_twi_delay_busy),
    RECORD(3,12,11,5,r1_twi_delay_busy),
    RECORD(4,31,41,1,r1_twi_delay_noop),
    RECORD(5,43,46,1,r1_twi_delay_noop)
};
static uint32_t bind_record(r1_stock_twi_record *record) {
    record->device.name=record->name;
    record->device.ops=(const generic_device_registry_ops *)&record->ops;
    return r1_stock_registry_register(&record->device);
}
uint32_t r1_stock_i2c2_register(void) { return bind_record(&r1_stock_twi_records[0]); }
uint32_t r1_stock_i2c3_register(void) { return bind_record(&r1_stock_twi_records[1]); }
uint32_t r1_stock_i2c4_register(void) { return bind_record(&r1_stock_twi_records[2]); }
uint32_t r1_stock_i2c5_register(void) { return bind_record(&r1_stock_twi_records[3]); }

extern void r1_twi_gpio_output(uint32_t pin);
static uint32_t open_record(r1_stock_twi_record *record, unsigned extra_config) {
    if (record->opened != 0) return 0;
    record->engine.set_output(record->engine.scl_pin);
    record->engine.set_output(record->engine.sda_pin);
    record->engine.release_high(record->engine.scl_pin);
    record->engine.release_high(record->engine.sda_pin);
    if (extra_config) {
        /* Stock i2c_4 additionally calls nrf_gpio_cfg(pin,1,1,0,0,0). */
        r1_twi_gpio_output(record->engine.scl_pin);
        r1_twi_gpio_output(record->engine.sda_pin);
    }
    record->opened=1;
    return 0;
}
static uint32_t close_record(r1_stock_twi_record *record) {
    if (record->opened != 0) {
        record->pin_release(record->engine.scl_pin);
        record->pin_release(record->engine.sda_pin);
        record->opened=0;
    }
    return 0;
}
#define LIFECYCLE(bus,index,extra) \
uint32_t r1_stock_i2c##bus##_open(generic_device_registry_device *device) { (void)device;return open_record(&r1_stock_twi_records[index],extra); } \
uint32_t r1_stock_i2c##bus##_close(generic_device_registry_device *device) { (void)device;return close_record(&r1_stock_twi_records[index]); }
LIFECYCLE(2,0,0)
LIFECYCLE(3,1,0)
LIFECYCLE(4,2,1)
LIFECYCLE(5,3,0)

static uint32_t read_record(unsigned index, const software_twi_read_request *request) {
    r1_stock_twi_record *record=&r1_stock_twi_records[index];
    if (request==NULL) return 4;
    if (record->opened==0) return index==3 ? 4 : 10;
    uint32_t status;
    if (index<2)
        status=software_twi_read_transaction_reg8(request->address,(uint8_t)request->register_address,
            request->buffer,(uint8_t)request->length,&record->engine);
    else
        status=software_twi_read_transaction_reg16(request->address,request->register_address,
            request->buffer,index==2 ? request->length : (uint8_t)request->length,&record->engine);
    return status==0 ? 0 : 12;
}
static uint32_t write_record(unsigned index, const software_twi_write_request *request) {
    r1_stock_twi_record *record=&r1_stock_twi_records[index];
    if (request==NULL) return 4;
    if (record->opened==0) return 8;
    software_twi_engine *engine=&record->engine;
    uint8_t address=request->address;
    uint16_t reg=request->register_address;
    uint16_t length=request->length;
    const uint8_t *buffer=request->buffer;
    /* Stock fetches single-byte payload before any wire callback. */
    uint8_t single=length==1 ? buffer[0] : 0;
    if (index==3) {
        uint32_t status=length==1 ? software_twi_write_transaction_reg16_byte(address,reg,single,engine) :
            software_twi_write_transaction_reg16(address,reg,buffer,(uint8_t)length,engine);
        return status==0 ? 0 : 11;
    }
    if (index<2 && length!=1) {
        uint32_t status=software_twi_write_transaction_reg8(address,(uint8_t)reg,buffer,(uint8_t)length,engine);
        return status==0 ? 0 : 11;
    }
    software_twi_start(engine);
    software_twi_write_byte(address,engine);
    if (software_twi_wait_ack(engine)) return 11;
    if (index<2) {
        software_twi_write_byte((uint8_t)reg,engine);
        if (software_twi_wait_ack(engine)) return 11;
    }
    if (length==1) {
        software_twi_write_byte(single,engine);
        if (software_twi_wait_ack(engine)) return 11;
    } else {
        for (uint32_t i=0;i<length;++i) {
            software_twi_write_byte(buffer[i],engine);
            if (software_twi_wait_ack(engine)) return 11;
        }
    }
    software_twi_stop(engine);
    return 0;
}
#define TRANSFER(bus,index) \
uint32_t r1_stock_i2c##bus##_read(generic_device_registry_device *device,uintptr_t operation,uintptr_t request,uintptr_t extra) { \
    (void)device;(void)operation;(void)extra;return read_record(index,(const software_twi_read_request *)request); } \
uint32_t r1_stock_i2c##bus##_write(generic_device_registry_device *device,uintptr_t operation,uintptr_t request,uintptr_t extra) { \
    (void)device;(void)operation;(void)extra;return write_record(index,(const software_twi_write_request *)request); }
TRANSFER(2,0)
TRANSFER(3,1)
TRANSFER(4,2)
TRANSFER(5,3)
