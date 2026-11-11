/* Product size/SN model selection and slider calibration from stock. */
#include <stdint.h>
#include "native_touch_calibration.h"
#include "native_kv_class.h"
#include "native_battery_memory.h"
extern void *volatile r1_r_size_kv_handle,*volatile r1_device_info_kv_handle;
#include "../../include/r1_product_serial.h"
extern const uint8_t *r1_touch_model_table_get(uint32_t);
volatile uint16_t r1_touch_slider_origin __attribute__((section(".r1.touch.slider_origin"),aligned(2)))=0;
volatile float r1_touch_slider_step __attribute__((section(".r1.touch.slider_step"),aligned(4)))=0.0f;
/* Historical names: rec8 uses r_size, and word4c uses nv_r1, not power. */
uint32_t r1_batcfg_byte_rec8_get(void)
{
 _Alignas(4) uint8_t record[1]={0};
 (void)r1_kv_class_read(r1_r_size_kv_handle,record,1);
 return record[0];
}
uint32_t r1_batcfg_word_4c_get(void)
{
 _Alignas(4) uint8_t record[124]={0};
 (void)r1_kv_class_read(r1_device_info_kv_handle,record,sizeof record);
 return read32(record+76);
}
uint32_t r1_product_sn_letter_decode(void)
{
 uint32_t decoded=r1_batcfg_byte_rec8_get();
 if((uint32_t)(decoded-6u)<=9u)return decoded;
 uint8_t serial[30]={0xff};
 r1_advertising_product_sn_read(serial,0);
 decoded=13;
 if(serial[0]!=0xff && serial[5]!=0 && serial[5]!=0xff) {
  uint32_t letter=serial[5];
  if(letter-'A'<=9u)decoded=letter-0x3bu;
  else if(letter-'a'<=9u)decoded=letter-0x5bu;
  if((uint32_t)(decoded-6u)>=10u)decoded=13;
 }
 return decoded;
}
void r1_touch_slider_calibration(void)
{
 uint32_t decoded=r1_product_sn_letter_decode();
 const volatile uint8_t *configuration=r1_touch_model_table_get(decoded);
 uint32_t lower=configuration[3],upper=configuration[4];
 /* Exact native binary32 constant 0x43555555, not an algebraic 640/3. */
 const float scale=0x1.aaaaaap+7f;
 float span=(float)((int32_t)upper-(int32_t)lower)*scale;
 float minimum=(float)lower*scale;
 r1_touch_slider_origin=(uint16_t)(uint32_t)minimum;
 r1_touch_slider_step=span/200.0f;
}
