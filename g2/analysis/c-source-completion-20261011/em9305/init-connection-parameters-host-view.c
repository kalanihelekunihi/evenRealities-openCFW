extern uint32_t opencfw_em9305_init_callback_320908(uintptr_t,uint32_t);
extern uint32_t opencfw_em9305_init_callback_3205c4(uintptr_t,uint32_t);
/* Native31e5ec ignores its incoming registers, sets pending then signals. */
uint32_t opencfw_em9305_init_callback_31e5ec(uintptr_t incoming,uint32_t state)
{(void)incoming;(void)state;*(volatile uint8_t *)(uintptr_t)0x803c28u=1u;(void)opencfw_em9305_auxiliary_signal_304394();return 0u;}
/* Native325708..32571c: exact bit-priority channel selector. */
uint32_t opencfw_em9305_init_channel_first_325708(uint32_t flags)
{if((flags&1u)==0u)return 37u;if((flags&2u)==0u)return 38u;if((flags&4u)==0u)return 39u;return 37u;}
static uint32_t opencfw_em9305_init_parameter_bit(uint32_t value)
{return (value>>14u)&1u;}
/* Complete32074c..320904. Header postincrement at320864 is retained;
 * callback identities use genuine relocations, never absolute code pointers. */
uint32_t opencfw_em9305_init_connection_parameters_32074c(uintptr_t input,uint32_t kind,uint32_t low_in,uint32_t high_in)
{
 uintptr_t record=0x803b94u,header=0x803bd5u,second=header+1u;
 (void)opencfw_em9305_memset((void *)(record+152u),0u,240u);
 *(volatile uint32_t *)(second+130u)=(uint32_t)(record+200u);
 uint32_t flags=*(volatile uint8_t *)(uintptr_t)0x805b00u;
 *(volatile uint8_t *)(second+112u)=1u;
 *(volatile uint8_t *)(second+110u)=2u;
 *(volatile uint32_t *)(second+114u)=(uint32_t)(uintptr_t)opencfw_em9305_init_callback_320908;
 *(volatile uint8_t *)(second+134u)=2u;
 *(volatile uint32_t *)(second+118u)=(uint32_t)(uintptr_t)opencfw_em9305_init_callback_320908;
 uint32_t channel=opencfw_em9305_init_channel_first_325708(flags);
 uint32_t type=*(volatile uint8_t *)second;
 *(volatile uint8_t *)(second+135u)=(uint8_t)channel;
 *(volatile uint32_t *)(second+142u)=0x555555u;
 uint32_t option=*(volatile uint8_t *)(uintptr_t)0x805a9cu;
 *(volatile uint16_t *)(second+210u)=3u;
 *(volatile uint16_t *)(second+146u)=257u;
 *(volatile uint32_t *)(second+138u)=0x8e89bed6u;
 *(volatile uint8_t *)(second+136u)=(uint8_t)option;
 if(type!=0u)*(volatile uint16_t *)(uintptr_t)0x803caau=3u;
 flags=*(volatile uint8_t *)(uintptr_t)0x805b00u;
 uintptr_t event=header+284u;
 *(volatile uint8_t *)(event+2u)=(uint8_t)flags;
 *(volatile uint32_t *)(header+251u)=(uint32_t)(uintptr_t)opencfw_em9305_init_callback_3205c4;
 *(volatile uint8_t *)(event+1u)=45u;
 uintptr_t packet=opencfw_em9305_wsf_event_allocate(45u);
 *(volatile uint32_t *)(header+259u)=(uint32_t)(uintptr_t)opencfw_em9305_init_callback_31e5ec;
 *(volatile uint32_t *)(header+235u)=(uint32_t)packet;
 uint32_t value=opencfw_em9305_radio_access_raw_318878();
 *(volatile uint32_t *)(header+19u)=value;
 value=opencfw_em9305_radio_crc_seed_318960();
 uint32_t upper=*(volatile uint32_t *)(uintptr_t)0x805aa4u;
 uint32_t lower=*(volatile uint32_t *)(uintptr_t)0x805aa0u;
 uint32_t period=*(volatile uint16_t *)(header+57u);
 uint32_t minimum=*(volatile uint16_t *)(input+4u);
 uint32_t maximum=*(volatile uint16_t *)(input+6u);
 *(volatile uint8_t *)(header+41u)=1u;
 *(volatile uint32_t *)(header+23u)=value;
 *(volatile uint32_t *)(header+31u)=upper;
 *(volatile uint32_t *)(header+27u)=lower;
 *(volatile uint16_t *)(header+35u)=(uint16_t)period;
 *(volatile uint16_t *)(header+37u)=(uint16_t)minimum;
 *(volatile uint16_t *)(header+39u)=(uint16_t)maximum;
 value=opencfw_em9305_associated_random_31896c();
 *(volatile uint8_t *)(header+45u)=(uint8_t)value;
 value=opencfw_em9305_compose_accuracy_318988();
 *(volatile uint8_t *)(header+46u)=(uint8_t)value;
 uintptr_t descriptor=0x803d1cu;
 uint32_t feature=*(volatile uint32_t *)(uintptr_t)0x805a94u;
 *(volatile uint8_t *)(descriptor+4u)=34u;
 flags=*(volatile uint8_t *)header;header+=3u;
 uintptr_t address=0x803cacu;
 uint32_t bit=opencfw_em9305_init_parameter_bit(feature);
 *(volatile uint8_t *)descriptor=5u;
 *(volatile uint8_t *)(descriptor+1u)=(uint8_t)bit;
 if((flags&1u)==0u){upper=*(volatile uint32_t *)(uintptr_t)0x805b44u;lower=*(volatile uint32_t *)(uintptr_t)0x805b40u;value=*(volatile uint32_t *)address;*(volatile uint32_t *)(address+8u)=upper;*(volatile uint32_t *)(address+4u)=lower;}
 else {upper=*(volatile uint32_t *)(uintptr_t)0x805a90u;lower=*(volatile uint32_t *)(uintptr_t)0x805a8cu;value=*(volatile uint32_t *)address;*(volatile uint32_t *)(address+8u)=upper;*(volatile uint32_t *)(address+4u)=lower;value|=2u;}
 uint32_t privacy=*(volatile uint8_t *)(uintptr_t)0x805a9du;
 uint32_t output_flags=value|1u;
 *(volatile uint32_t *)address=output_flags;
 if(privacy!=0u){output_flags=value|81u;*(volatile uint32_t *)address=output_flags;}
 type=*(volatile uint8_t *)second;
 *(volatile uint32_t *)(second+2u)=lower;
 *(volatile uint32_t *)(second+6u)=upper;
 *(volatile uint8_t *)(descriptor+2u)=(uint8_t)((output_flags>>1u)&1u);
 if(type==0u){bit=kind&1u;*(volatile uint8_t *)(descriptor+3u)=(uint8_t)bit;output_flags|=(bit<<3u)|4u;*(volatile uint32_t *)(record+292u)=low_in;*(volatile uint32_t *)(record+76u)=low_in;*(volatile uint32_t *)(record+296u)=high_in;*(volatile uint32_t *)(record+80u)=high_in;*(volatile uint32_t *)(record+280u)=output_flags;}
 uintptr_t encoded=0x803cf1u;
 uint32_t length=opencfw_em9305_radio_encode_3239d4(record,encoded+43u);
 (void)opencfw_em9305_radio_encode_323c94(record+length,header);
 *(volatile uint32_t *)(address+24u)=(uint32_t)record;
 *(volatile uint8_t *)encoded=36u;
 return 36u;
}
