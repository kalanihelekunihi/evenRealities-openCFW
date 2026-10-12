/* Native policy callback332db4..332e2c, complete body; pending selection. */
uint32_t opencfw_em9305_command_callback_332db4(uintptr_t object,uint32_t event)
{
 uintptr_t state=0x8058dcu;
 uint32_t count=*(volatile uint16_t *)(state+4u);
 uint32_t captured=*(volatile uint8_t *)state;
 uint32_t next=count+1u;
 *(volatile uint16_t *)(state+4u)=(uint16_t)next;
 if(captured!=1u||event==1u)return 0u;
 uint32_t limit=*(volatile uint16_t *)(state+2u);
 if(limit!=0u&&(uint16_t)next>=limit)return 0u;
 uintptr_t record=*(volatile uint32_t *)(object+44u),policy=0x805994u;
 uint32_t channel=*(volatile uint8_t *)(policy+2u);
 uint32_t recorded_channel=*(volatile uint8_t *)(record+1u);
 if(channel!=recorded_channel)return 0u;
 uintptr_t packet=*(volatile uint32_t *)(record+104u);
 uint32_t kind=*(volatile uint8_t *)(policy+1u);
 uint32_t header=*(volatile uint8_t *)packet;
 if(kind!=(header&~32u))return 0u;
 uint32_t packet_pattern=*(volatile uint8_t *)(packet+1u);
 uint32_t pattern=*(volatile uint8_t *)policy;
 if(pattern!=packet_pattern)return 0u;
 uint32_t recorded_mode=*(volatile uint8_t *)(record+12u);
 uint32_t mode=*(volatile uint8_t *)(policy+3u);
 if(mode!=recorded_mode)return 0u;
 uint32_t index=*(volatile uint32_t *)(policy+16u);
 uint32_t bits=*(volatile uint32_t *)(policy+12u);
 uint32_t value=(bits&(1u<<(index&31u)))!=0u?0x555555u:0xaaaaaau;
 *(volatile uint32_t *)(policy+16u)=(index+1u)&31u;
 *(volatile uint32_t *)(record+8u)=value;
 return 1u;
}
