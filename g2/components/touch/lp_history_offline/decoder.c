/* New offline/app interface derived from original producer tests. It neither
 * runs firmware processing nor changes firmware/baselines/history. */
#include "history.h"
static uint32_t little16(const uint8_t *p){return p[0]|((uint32_t)p[1]<<8);}
uint32_t touch_lp_history_span(const uint8_t *c,uint32_t cap,uint32_t *needed){
 if(!c || !needed)return TOUCH_LP_BAD_META;
 *needed=0;if(!(little16(c+22)&1u))return TOUCH_LP_DISABLED;
 if(!c[26])return TOUCH_LP_EMPTY;
 if(!c[25] || c[24]>=4u || (uint32_t)c[24]+c[25]>4u)return TOUCH_LP_BAD_META;
 *needed=2u*c[25]*c[26];return cap<*needed?TOUCH_LP_TOO_SHORT:TOUCH_LP_SAMPLE;
}
uint32_t touch_lp_history_read(const uint8_t *c,const uint8_t *data,uint32_t cap,uint32_t enabled,uint32_t frame,uint32_t slot,touch_lp_sample *out){
 uint32_t needed,status=touch_lp_history_span(c,cap,&needed);if(status)return status;
 if(!out || !data || frame>=c[26] || slot>=c[25])return TOUCH_LP_BAD_META;
 out->value=0;out->slot=(uint8_t)(c[24]+slot);out->frame=(uint8_t)frame;out->counter=c[27];out->baseline_reset=c[28]&1u;out->baseline_valid=(c[28]>>1)&1u;out->written=(uint8_t)((enabled>>out->slot)&1u);
 if(!out->written)return TOUCH_LP_UNWRITTEN;
 out->value=(uint16_t)little16(data+2u*(frame*c[25]+slot));return TOUCH_LP_SAMPLE;
}
