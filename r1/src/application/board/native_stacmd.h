#ifndef R1_NATIVE_STACMD_H
#define R1_NATIVE_STACMD_H
#include <stdint.h>
#include "../registry/stock_registry.h"
typedef uint32_t (*r1_stacmd_device_op)(generic_device_registry_device *);
typedef struct {
    uintptr_t reserved_00,reserved_04;
    r1_stacmd_device_op open,close;
    generic_device_registry_operation read,write;
    uintptr_t reserved_18,reserved_1c,reserved_20;
} r1_stacmd_operations;
typedef struct r1_stacmd_configuration {
    const char *name;uint32_t opened,config_08,pin;
    void (*low)(uint32_t),(*high)(uint32_t),(*output)(uint32_t),(*input)(uint32_t,uint32_t);
    uint32_t pull;void (*delay_us)(uint32_t);uint32_t (*read_pin)(uint32_t);void (*release)(uint32_t);
    generic_device_registry_device device;r1_stacmd_operations ops;
} r1_stacmd_configuration;
_Static_assert(sizeof(r1_stacmd_operations)==36,"native nine-word operations");
_Static_assert(sizeof(r1_stacmd_configuration)==108 && offsetof(r1_stacmd_configuration,device)==48 && offsetof(r1_stacmd_configuration,ops)==72,"native STACMD layout");
_Static_assert(offsetof(r1_stacmd_operations,open)==8 && offsetof(r1_stacmd_operations,close)==12 && offsetof(r1_stacmd_operations,read)==16 && offsetof(r1_stacmd_operations,write)==20,"native operation offsets");
extern r1_stacmd_configuration r1_stacmd;
extern volatile uint32_t r1_stacmd_failed_transactions;
uint32_t r1_stacmd_open(generic_device_registry_device *);
uint32_t r1_stacmd_close(generic_device_registry_device *);
uint32_t r1_stacmd_read(generic_device_registry_device *,uintptr_t,uintptr_t,uintptr_t);
uint32_t r1_stacmd_write(generic_device_registry_device *,uintptr_t,uintptr_t,uintptr_t);
uint32_t r1_stacmd_read_frame_native(uint32_t,uint32_t,uint32_t,uint8_t *);
uint32_t r1_stacmd_write_frame_native(uint32_t,uint32_t,uint32_t,const uint8_t *);
uint32_t r1_stacmd_write_retry_native(uint32_t,uint32_t,const uint8_t *);
uint32_t r1_stacmd_bus_recovery_native(void);
uint32_t r1_stacmd_recovery_delay_native(void);
uint32_t r1_stacmd_drive_bit_native(uint32_t);
uint32_t r1_stacmd_write_bits_native(uint32_t,uint32_t);
uint32_t r1_stacmd_idle_native(void);
uint32_t r1_stacmd_parity_native(uint32_t);
uint32_t r1_stacmd_read_bit_native(uint32_t *);
uint32_t r1_stacmd_read_bit_adapter_native(uint32_t *);
/* Wire helpers preserve target raw callback words through address views where
 * native tail returns are observed. Actual GPIO return/timing proof remains open. */
#endif
