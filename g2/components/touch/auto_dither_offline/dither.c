/* Independent68ec; status boundary preserved, no device operations outside
 * explicitly supplied/synthetic context in offline tests. */
#include "dither.h"
#include "../all_slot_offline/slots.h"
#include "../base_frame_offline/base.h"
#include "../mode_offline/mode.h"
#include "../pin_control_offline/pins.h"
extern uint32_t Cy_MSCLP_Configure(volatile uint32_t *,const void *,uint32_t,void *);
uint32_t touch_configure_auto_dither(uint8_t *c){
 const uint8_t *common=*(const uint8_t **)c,*ch=*(const uint8_t **)(common+8);volatile uint32_t *hw=*(volatile uint32_t **)ch;
 touch_generate_all_slots(0,c);touch_generate_all_slots(1,c);
 uint32_t status=Cy_MSCLP_Configure(hw,*(const void **)(c+36),2,*(void **)(ch+4));
 touch_cpu_operating(c);return status?0x40u:0;
}
static void discard_dither_status(uint8_t *c){(void)touch_configure_auto_dither(c);}
static const touch_mode_dependencies deps={touch_mode_ios,touch_mode_shield,touch_mode_cmod,Cy_MSCLP_Configure,discard_dither_status};
uint32_t touch_switch_dither_dependency(uint32_t desired,uint8_t *c){return touch_switch_mode(desired,c,&deps);}
uint32_t touch_prepare_auto_dither(uint8_t *c){(void)touch_generate_base(c);return touch_configure_auto_dither(c);}
