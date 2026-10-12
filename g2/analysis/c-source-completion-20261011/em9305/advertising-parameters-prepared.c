/* Native30ce18..30cee0: captured capability, full interval/mode/address
 * validation and sparse live advertising-state projection. */
uint32_t opencfw_em9305_command_advertising_parameters_30ce18(uint32_t minimum,uint32_t maximum,uint32_t type,uint32_t own,uint32_t peer,uintptr_t address,uint32_t channels,uint32_t filter)
{
 uint32_t capabilities=*(volatile uint32_t *)(uintptr_t)0x805a94u;
 uint32_t gate=opencfw_em9305_ll_connection_gate_30e524();
 if(*(volatile uint8_t *)(uintptr_t)0x805a71u!=0u||gate==0u)return 12u;
 if(type!=1u){if(type>=5u||maximum>=0x4001u||minimum<32u||maximum<minimum)return 17u;}
 uint32_t maximum_own=(capabilities&64u)?3u:1u;
 if(own>maximum_own)return 17u;
 if(type==1u||type==4u||(own&2u)!=0u){if(peer>=2u||address==0u)return 17u;}
 if(channels-1u>=7u)return 17u;
 if(filter>=4u&&type!=4u&&type!=1u)return 17u;
 uint32_t upper=opencfw_em9305_config_limit_mpyuw(maximum,625u),lower=opencfw_em9305_config_limit_mpyuw(minimum,625u);
 uintptr_t state=0x805b88u;
 *(volatile uint8_t *)(state+21u)=(uint8_t)filter;
 *(volatile uint8_t *)(state+20u)=(uint8_t)channels;
 *(volatile uint8_t *)(state+10u)=(uint8_t)peer;
 *(volatile uint8_t *)(state+9u)=(uint8_t)own;
 *(volatile uint8_t *)(state+8u)=(uint8_t)type;
 *(volatile uint32_t *)(state+4u)=upper;
 *(volatile uint32_t *)state=lower;
 uint64_t value=opencfw_em9305_controller_pack_address(address);
 *(volatile uint32_t *)(state+12u)=(uint32_t)value;
 *(volatile uint32_t *)(state+16u)=(uint32_t)(value>>32u);
 return 0u;
}
