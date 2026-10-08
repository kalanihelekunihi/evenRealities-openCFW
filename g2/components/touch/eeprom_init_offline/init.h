#ifndef OPENCFW_TOUCH_EEPROM_INIT_OFFLINE_H
#define OPENCFW_TOUCH_EEPROM_INIT_OFFLINE_H
#include <stdint.h>
/* ARM32 configuration ABI: u32capacity+0, mode/wear/redundancy/blocking+4..7,
 * u32physicalbase+8; twelve bytes. Borrowed context and provider must remain valid. */
typedef struct { uint32_t capacity; uint8_t simple,wear,redundant,blocking; uint32_t base; } touch_eeprom_configuration;
_Static_assert(sizeof(touch_eeprom_configuration)==12,"configuration ABI");
extern const touch_eeprom_configuration touch_factory_eeprom_configuration;
uint32_t touch_eeprom_init_bd(const uint8_t *config,uint8_t *context,uint32_t *provider);
uint32_t touch_eeprom_init(const uint8_t *config,uint8_t *context);
uint32_t touch_application_eeprom_init(void);
uint32_t touch_provider_init(uint32_t *provider);
uint32_t touch_init_ranges(const uint8_t *config,const uint8_t *context);
uint32_t touch_init_physical_size(const uint8_t *context,const uint8_t *config);
void touch_init_program_size(uint8_t *context);
#endif
