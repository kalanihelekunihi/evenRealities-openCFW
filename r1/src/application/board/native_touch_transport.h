#ifndef R1_NATIVE_TOUCH_TRANSPORT_H
#define R1_NATIVE_TOUCH_TRANSPORT_H
#include "../registry/stock_registry.h"
extern volatile generic_device_registry_request_block r1_touch_request;
uint32_t r1_touch_request_read_native(uint32_t reg,void *data,uint32_t length);
uint32_t r1_touch_request_write_native(uint32_t reg,const void *data,uint32_t length);
uint32_t r1_touch_ready_level_read(void);
/* Stock 0x2fe9c/0x2feac ignore the supplied address and option. The bound
 * registry device and retained request own those transport settings. */
uint32_t r1_iqs7211e_register_read_port(uint32_t address,uint32_t reg,void *data,uint32_t length,uint32_t option);
uint32_t r1_iqs7211e_register_write_port(uint32_t address,uint32_t reg,const void *data,uint32_t length,uint32_t option);
#endif
