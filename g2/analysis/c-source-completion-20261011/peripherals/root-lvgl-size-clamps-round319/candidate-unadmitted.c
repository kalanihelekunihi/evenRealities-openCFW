/* Native4408d6..440966/440968..4409f8; source-backed LVGL size clamps.
 * LVGL lv_obj_pos.c969..980; native wrap and signed percentage boundaries retained. */
#include <stdint.h>
static int32_t lv319_resolve(int32_t bound,int32_t reference)
{
 uint32_t raw=(uint32_t)bound;
 int32_t plain=(int32_t)(raw & 0x9fffffffu);
 if((raw & 0x60000000u)==0x20000000u && plain<0x1fffffff){
  int32_t percent=plain>=0x10000000 ? (int32_t)(0x0fffffffu-(uint32_t)plain) : plain;
  int32_t product=(int32_t)((uint32_t)percent*(uint32_t)reference);
  return product/100;
 }
 return bound;
}
static int32_t lv319_clamp(int32_t value,int32_t minimum,int32_t maximum,int32_t reference)
{
 minimum=lv319_resolve(minimum,reference);
 maximum=lv319_resolve(maximum,reference);
 int32_t limited=value<maximum?value:maximum;
 return limited<minimum?minimum:limited;
}
int32_t audio_uart_lv_clamp_width_4408d6(int32_t v,int32_t lo,int32_t hi,int32_t ref)
{return lv319_clamp(v,lo,hi,ref);}
int32_t audio_uart_lv_clamp_height_440968(int32_t v,int32_t lo,int32_t hi,int32_t ref)
{return lv319_clamp(v,lo,hi,ref);}
