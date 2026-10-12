/* Native323ac8..323b0c: fully initialized five-byte header and ninth stack arg. */
uint32_t opencfw_em9305_associated_packet_continue_323ac8(uintptr_t record,uintptr_t payload,uintptr_t size,uint32_t count)
{
 uint8_t header[5] __attribute__((aligned(4)))={7u,0u,0u,0u,0u};
 uint32_t flags=0u;
 if(count==0u&&(*(volatile uint8_t *)(record+32u)&2u)==0u)flags=8u;
 return opencfw_em9305_radio_compose_323dc0(record,flags,16u,0u,(uintptr_t)header,size,payload,5u,count);
}
/* Native3243e0..324436: flags are full captured config/input then byte cast. */
uint32_t opencfw_em9305_associated_packet_start_3243e0(uintptr_t record,uintptr_t payload,uintptr_t size,uint32_t count)
{
 uint32_t policy=*(volatile uint32_t *)(uintptr_t)0x805a98u;
 uint32_t mode=*(volatile uint8_t *)(record+716u),enabled=*(volatile uint8_t *)(record+804u);
 uint8_t header[5] __attribute__((aligned(4)))={7u,0u,0u,0u,0u};
 uint32_t flags=((policy>>1u)&8u)|(mode&64u)|(enabled<<2u)|16u;
 return opencfw_em9305_radio_compose_323dc0(record,0u,(uint8_t)flags,0u,(uintptr_t)header,size,payload,4u,count);
}
