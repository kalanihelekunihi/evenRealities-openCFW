#ifndef OPENCFW_TOUCH_EEPROM_OFFLINE_H
#define OPENCFW_TOUCH_EEPROM_OFFLINE_H
#include <stdint.h>
#include "provider.h"
#include "history.h"
/* Stock return codes. Success does not imply physical durability. */
enum { TOUCH_EEPROM_BAD_PARAM=0x093e0000u, TOUCH_EEPROM_BAD_CHECKSUM=0x093e0001u,
 TOUCH_EEPROM_BAD_DATA=0x093e0002u, TOUCH_EEPROM_WRITE_FAIL=0x093e0003u,
 TOUCH_EEPROM_REDUNDANT_USED=0x093e0004u };
uint32_t touch_eeprom_read(uint32_t address,uint8_t *out,uint32_t size,uint8_t *context);
uint32_t touch_eeprom_write(uint32_t address,const uint8_t *data,uint32_t size,uint8_t *context);
uint32_t touch_extended_read(uint32_t address,uint8_t *out,uint32_t size,uint8_t *context);
uint32_t touch_simple_read(uint32_t address,uint8_t *out,uint32_t size,uint8_t *context);
uint32_t touch_extended_write(uint32_t address,const uint8_t *data,uint32_t size,uint8_t *context);
/* Offline ARM32 guest ABI. Valid128-byte geometry/context/provider/header domain,
 * stable caller memory and no concurrent mutation are tested preconditions. */
#endif
