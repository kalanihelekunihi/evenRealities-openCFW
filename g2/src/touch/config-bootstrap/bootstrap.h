#ifndef TOUCH_CONFIG_BOOTSTRAP_OFFLINE_H
#define TOUCH_CONFIG_BOOTSTRAP_OFFLINE_H
#include <stdint.h>
typedef struct {uint32_t magic; uint16_t baseline,parameter;} touch_saved_record;
_Static_assert(sizeof(touch_saved_record)==8,"saved record ABI");
uint32_t touch_eeprom_erase(uint8_t *context);
uint32_t touch_application_read(uint32_t address,uint8_t *out,uint32_t size);
uint32_t touch_application_write(uint32_t address,const uint8_t *data,uint32_t size);
uint32_t touch_application_erase(void);
void touch_config_bootstrap(void);
void touch_bootstrap_delay(uint32_t argument);
#endif
