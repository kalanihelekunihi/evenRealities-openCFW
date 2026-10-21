/* Independent process-slider5a94. Defined X/activity/count/history behavior;
 * stock local Y/Z/padding bytes are uninitialized, native makes themzero. */
#include "slider.h"
void touch_slider_process(uint8_t *w){
 uint8_t *c=*(uint8_t **)w,*s=*(uint8_t **)(w+4),*debounce=*(uint8_t **)(w+40);uint32_t n=*(uint16_t *)(w+56);
 uint32_t threshold=*(uint16_t *)(c+8),h=*(uint16_t *)(c+30),active=0;threshold=(c[35]&1u)?threshold-h:threshold+h;
 if(*debounce)(*debounce)--;
 for(uint32_t i=0;i<n;i++){s[i*10+6]=*(uint16_t *)(s+i*10+4)>threshold?1:0;active|=s[i*10+6];}
 if(!active){*debounce=c[32];c[35]&=(uint8_t)~1u;}
 if(!*debounce)c[35]|=1u;
 else if(active)for(uint32_t i=0;i<n;i++)s[i*10+6]=0;
 uint8_t position[8],touch[8];for(unsigned j=0;j<8;j++){((volatile uint8_t *)position)[j]=0;((volatile uint8_t *)touch)[j]=0;}*(uint8_t **)touch=position;
 if((c[35]&1u) && w[123]==2)touch_linear_centroid(touch,w);
 if(*(uint32_t *)(w+112)&255u)touch_position_filters(touch,w);
 c[40]=touch[4];uint8_t *out=*(uint8_t **)(c+36);
 for(uint32_t i=0;i<touch[4];i++)for(unsigned j=0;j<8;j++)out[i*8+j]=position[i*8+j];
}
