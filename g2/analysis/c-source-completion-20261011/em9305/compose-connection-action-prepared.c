/* Native 32366c..3237e4: extended connection state control element.
 * Every repeated native load remains a fresh volatile access. */
uint32_t opencfw_em9305_compose_action_32366c(uintptr_t record,uintptr_t output)
{
 volatile uint8_t *r=(volatile uint8_t *)record,*o=(volatile uint8_t *)output;
 uintptr_t fields=record+188u;
 uint32_t length=r[178], captured=r[232];
 o[1]=44u;o[0]=(uint8_t)(length+1u);o[2]=r[186];
 uint32_t half=*(volatile uint16_t *)(record+186u);
 uint32_t bit=r[188]&1u;
 uint32_t interval=*(volatile uint16_t *)(record+190u);
 o[3]=(uint8_t)(((half&0x3f00u)+(bit<<14)+(interval<<15))>>8);
 o[4]=(uint8_t)(*(volatile uint16_t *)(record+190u)>>1);
 interval=*(volatile uint16_t *)(record+190u);
 uint32_t byte=r[192];o[5]=(uint8_t)(((interval<<15)|(byte<<27))>>24);
 byte=r[194];uint32_t other=r[193];o[6]=(uint8_t)((byte<<5)|other);
 uint32_t word=*(volatile uint32_t *)(fields+8u);byte=r[194];
 o[7]=(uint8_t)(((word<<8)|(byte<<5))>>8);
 o[8]=(uint8_t)(*(volatile uint32_t *)(fields+8u)>>8);
 word=*(volatile uint32_t *)(fields+8u);byte=r[200];
 o[9]=(uint8_t)(((word<<8)|(byte<<28))>>24);
 o[10]=(uint8_t)*(volatile uint32_t *)(fields+16u);
 o[11]=(uint8_t)(*(volatile uint32_t *)(fields+16u)>>8);
 byte=r[208];word=*(volatile uint32_t *)(fields+16u);
 o[12]=(uint8_t)(((byte<<20)|word)>>16);
 byte=r[208];half=*(volatile uint16_t *)(record+210u);word=*(volatile uint32_t *)(fields+16u);
 o[14]=0u;o[13]=(uint8_t)(((byte<<20)|word|(half<<24))>>24);
 o[15]=(uint8_t)*(volatile uint32_t *)(fields+24u);
 o[16]=(uint8_t)(*(volatile uint32_t *)(fields+24u)>>8);
 o[17]=(uint8_t)*(volatile uint16_t *)(record+214u);o[18]=r[215];
 o[19]=(uint8_t)*(volatile uint32_t *)(fields+28u);
 o[20]=(uint8_t)(*(volatile uint32_t *)(fields+28u)>>8);
 half=*(volatile uint16_t *)(fields+32u);word=*(volatile uint32_t *)(fields+28u);
 o[21]=(uint8_t)(((half<<20)|word)>>16);
 half=*(volatile uint16_t *)(fields+32u);word=*(volatile uint32_t *)(fields+28u);
 o[22]=(uint8_t)(((half<<20)|word)>>24);
 o[23]=r[222];o[24]=r[223];o[25]=r[224];o[26]=r[225];o[27]=r[226];o[28]=r[227];
 word=*(volatile uint32_t *)(fields+40u);o[29]=(uint8_t)(((captured<<5)-32u)|word);
 o[30]=r[236];o[31]=r[237];o[32]=r[238];o[33]=r[239];
 word=*(volatile uint32_t *)(fields+52u);byte=r[244];o[34]=(uint8_t)((word&127u)+(byte<<7));
 if(r[245]!=0u){
  (void)opencfw_em9305_memcpy((void *)(output+35u),(const void *)(record+246u),8u);
  (void)opencfw_em9305_memcpy((void *)(output+43u),(const void *)(record+254u),16u);
 }
 return (uint8_t)(length+2u);
}
