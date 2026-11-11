#include <stdint.h>
#include "../board/native_battery_context.h"
#include "../registry/stock_registry.h"
/* ADC cache aliases the shared runtime context at offset 16. */
const char r1_vbat_adc_name[9]
 __attribute__((section(".r1.vbat.name"),aligned(4)))="vbat_adc";
void r1_vbat_adc_handle_cache(void)
{
 if(!r1_vbat_adc_device)r1_vbat_adc_device=r1_stock_registry_find(r1_vbat_adc_name);
}
