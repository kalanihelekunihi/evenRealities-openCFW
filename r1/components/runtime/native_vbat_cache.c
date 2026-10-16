#include <stdint.h>
#include "../registry/stock_registry.h"
/* Only the authenticated cache cell is owned here, not the surrounding root. */
generic_device_registry_device *volatile r1_vbat_adc_device
 __attribute__((section(".r1.vbat.cache"),aligned(4)))=0;
const char r1_vbat_adc_name[9]
 __attribute__((section(".r1.vbat.name"),aligned(4)))="vbat_adc";
void r1_vbat_adc_handle_cache(void)
{
 if(!r1_vbat_adc_device)r1_vbat_adc_device=r1_stock_registry_find(r1_vbat_adc_name);
}
