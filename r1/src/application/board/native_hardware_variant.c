/* Stock 0x6a244: cached board variant derived from the product BSN. */
#include <stdint.h>
#include "native_product_bsn.h"
/* Native 0x2000775c and +1; values are independent of touch IRQ state. */
volatile uint8_t r1_hardware_variant_cached __attribute__((section(".r1.hardware.variant")))=0;
volatile uint8_t r1_hardware_variant_checked __attribute__((section(".r1.hardware.variant_checked")))=0;
uint32_t r1_hardware_variant_bsn_detect(void)
{
 if(!r1_hardware_variant_checked) {
  uint8_t bsn[30]={0xff};
  (void)r1_product_bsn_read(bsn,sizeof bsn);
  if(bsn[0]=='B' && bsn[1]=='2' && bsn[2]=='1' && bsn[3]=='0' && bsn[9]=='A')
   r1_hardware_variant_cached=1;
  r1_hardware_variant_checked=1;
 }
 return r1_hardware_variant_cached;
}
