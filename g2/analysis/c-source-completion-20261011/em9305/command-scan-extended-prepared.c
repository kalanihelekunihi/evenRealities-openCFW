/* Native307a58/307b8c: ARC dynamic bit index uses low five bits. */
void opencfw_em9305_scan_mask_clear_307a58(uint32_t bit)
{volatile uint8_t *p=(volatile uint8_t *)(uintptr_t)0x803560u;uint32_t v=*p;*p=(uint8_t)(v&~(1u<<(bit&31u)));}
void opencfw_em9305_scan_mask_set_307b8c(uint32_t bit)
{volatile uint8_t *p=(volatile uint8_t *)(uintptr_t)0x803560u;uint32_t v=*p;*p=(uint8_t)(v|(1u<<(bit&31u)));}
/* Native307b70..307b8c: authenticated table, callers supply index0 or2. */
void opencfw_em9305_scan_config_307b70(uint32_t index,uint32_t first,uint32_t second,uintptr_t input)
{
 static const uintptr_t states[3]={0x8035dcu,0x802a60u,0x80389cu};
 uintptr_t row=states[index];
 uint32_t duration=*(volatile uint16_t *)(input+2u),interval=*(volatile uint16_t *)input;
 *(volatile uint8_t *)(row+14u)=(uint8_t)second;
 *(volatile uint16_t *)(row+10u)=(uint16_t)duration;
 uint32_t mode=*(volatile uint8_t *)(input+4u);
 *(volatile uint16_t *)(row+8u)=(uint16_t)interval;
 *(volatile uint8_t *)(row+13u)=(uint8_t)first;
 *(volatile uint8_t *)(row+12u)=(uint8_t)mode;
}
/* Native332fa8..332fc4: interval>=duration>=4, mode<2. */
uint32_t opencfw_em9305_scan_row_valid_332fa8(uintptr_t input)
{
 uint32_t duration=*(volatile uint16_t *)(input+2u),interval=*(volatile uint16_t *)input;
 if(interval<duration||duration<4u)return 0u;
 return *(volatile uint8_t *)(input+4u)<2u;
}
static inline uint32_t opencfw_em9305_scan_stride6(uint32_t value)
{
 uint32_t result;
 __asm__ volatile("mpyuw %0,%1,6" : "=r"(result) : "r"(value));
 return result;
}
/* Native30d774..30d854: full extended scan guard and compact row graph. */
uint32_t opencfw_em9305_command_scan_extended_30d774(uint32_t first,uint32_t second,uint32_t mask,uintptr_t input)
{
 uintptr_t root=0x805a70u;
 uint32_t cap=*(volatile uint32_t *)(root+36u),cap2=*(volatile uint32_t *)(root+40u);
 uint32_t allowed=(cap&128u)?3u:1u;
 if((cap2&1024u)==0u){if(second&12u)return 17u;}else allowed|=12u;
 if(opencfw_em9305_ll_stream_gate_30e510()==0u)return 12u;
 uint32_t state4=*(volatile uint8_t *)(root+4u),state3=*(volatile uint8_t *)(root+3u);
 if(state3|state4)return 12u;
 uint32_t allowed_mask=((cap>>9u)&4u)|1u;
 if(mask&~allowed_mask)return 17u;
 if(first>((cap&64u)?3u:1u))return 18u;
 if((second&12u)==8u||mask==0u||second>allowed)return 18u;
 uint32_t count=0u,row_index=0u,has1=mask&1u,has4=mask&4u;
 if(has1){if(opencfw_em9305_scan_row_valid_332fa8(input)==0u)return 18u;row_index=1u;}
 if(has4&&opencfw_em9305_scan_row_valid_332fa8(input+opencfw_em9305_scan_stride6(row_index))==0u)return 18u;
 if(!has1)opencfw_em9305_scan_mask_clear_307a58(0u);
 else{opencfw_em9305_scan_mask_set_307b8c(0u);opencfw_em9305_scan_config_307b70(0u,first,second,input);count=1u;}
 if(!has4)opencfw_em9305_scan_mask_clear_307a58(2u);
 else{opencfw_em9305_scan_mask_set_307b8c(2u);opencfw_em9305_scan_config_307b70(2u,first,second,input+opencfw_em9305_scan_stride6(count));++count;}
 *(volatile uint8_t *)(root+12u)=(uint8_t)count;
 return 0u;
}
