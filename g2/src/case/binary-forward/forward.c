/* Selected nonlocal binary handler prefix; destination2 and command3D excluded. */
#include <stdint.h>
extern uint32_t case_forward_event(void *,uint32_t);
void case_forward_nonlocal(const uint8_t *p,uint32_t n,uint32_t mode){
 if(p[2]==2 || p[0]==0x3d)return; /* Outside selected contract, not local/aging semantics. */
 if(n<5 || p[1]!=0 || p[2]>1)return;
 uint32_t flags;
 if(mode==0){if((uint32_t)p[3]+5!=n)return;flags=0x20;}
 else{if((uint32_t)p[3]+((uint32_t)p[4]<<8)+6!=n)return;flags=0x400;}
 (void)case_forward_event(*(void **)0x200000f0u,flags);
 uint8_t *out=(uint8_t *)0x200001b4u;for(uint32_t i=0;i<n;i++)out[i]=p[i];
}
