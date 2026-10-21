/* Independent4c44/4c7c composition with pinned public PDL capture8fa0. */
#include "mode.h"
extern uint32_t Cy_MSCLP_Capture(void *,uint32_t,void *);
uint32_t touch_capture_default(uint8_t *c){const uint8_t *common=*(const uint8_t **)c,*ch=*(const uint8_t **)(common+8);uint8_t *lock=*(uint8_t **)(ch+4);if(*lock)return 0x80;if(Cy_MSCLP_Capture(*(void **)ch,2,lock))return 8;return touch_switch_mode(1,c,0);}
uint32_t touch_cap_init(uint8_t *c){uint32_t status=touch_cap_init_fields(c);if(status)return status;status=touch_switch_mode(0,c,0);if(status)return status;return touch_capture_default(c);}
