/* Native332b60..332b6e: retain low-word R0 after eight-byte packing. */
uint32_t opencfw_em9305_primary_masks_332b60(uintptr_t destination,uintptr_t input)
{
 uint64_t bits=opencfw_em9305_ll_pack64_304648(input);
 *(volatile uint32_t *)(destination+4u)=(uint32_t)(bits>>32u);
 *(volatile uint32_t *)destination=(uint32_t)bits;
 return (uint32_t)bits;
}
/* Native30b190..30b1a8: argument dead, busy latch before reset. */
uint32_t opencfw_em9305_command_primary_30b190(uint32_t ignored)
{
 (void)ignored;
 if(*(volatile uint8_t *)(uintptr_t)0x805a76u!=0u)return 12u;
 (void)opencfw_em9305_radio_address_reset_303e38();
 return 0u;
}
/* Native30af98..30aff4 and30cac4..30cb20: fullword initial kind check,
 * wrapped-byte second check and exact special 255 mode branch. */
static uint32_t opencfw_em9305_primary_address_gate(uint32_t kind)
{
 uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
 uint32_t version=*(volatile uint8_t *)(config+4u);
 if(kind>=2u&&version<9u)return 18u;
 if((uint8_t)(kind+1u)>=3u&&version>=9u)return 18u;
 if(*(volatile uint8_t *)(uintptr_t)0x805a76u!=0u)return 12u;
 return 0u;
}
uint32_t opencfw_em9305_command_primary_30af98(uint32_t kind,uintptr_t input)
{
 uint32_t error=opencfw_em9305_primary_address_gate(kind);
 if(error!=0u)return error;
 if(kind==255u){(void)opencfw_em9305_radio_address_enable_303dec();return 0u;}
 uint64_t address=opencfw_em9305_controller_pack_address(input);
 uint32_t result=opencfw_em9305_radio_address_add_303da4(kind!=0u,(uint32_t)address,(uint32_t)(address>>32u));
 return result==0u?7u:0u;
}
uint32_t opencfw_em9305_command_primary_30cac4(uint32_t kind,uintptr_t input)
{
 uint32_t error=opencfw_em9305_primary_address_gate(kind);
 if(error!=0u)return error;
 if(kind==255u){(void)opencfw_em9305_radio_address_disable_303ec0();return 0u;}
 uint64_t address=opencfw_em9305_controller_pack_address(input);
 uint32_t result=opencfw_em9305_radio_address_remove_303e68(kind!=0u,(uint32_t)address,(uint32_t)(address>>32u));
 return result==0u?18u:0u;
}
