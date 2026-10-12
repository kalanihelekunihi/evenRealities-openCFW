/* Native30be48..30be64: six bytes go to input, not response payload. */
uint32_t opencfw_em9305_vendor_command_30be48(uintptr_t input)
{
 if(*(volatile uint8_t *)(uintptr_t)0x805a81u==0u)return 18u;
 uint32_t high=*(volatile uint32_t *)(uintptr_t)0x805a90u;
 uint32_t low=*(volatile uint32_t *)(uintptr_t)0x805a8cu;
 (void)opencfw_em9305_radio_address_write_3045e8(input,low,high);
 return 0u;
}
/* Native30d87c..30d89c: only upper word controls range rejection. */
uint32_t opencfw_em9305_vendor_command_30d87c(uintptr_t input)
{
 uint64_t bits=opencfw_em9305_ll_pack64_304648(input);
 uint32_t low=(uint32_t)bits,high=(uint32_t)(bits>>32u);
 if(high>=0x2000u)return 18u;
 *(volatile uint32_t *)(uintptr_t)0x805a94u=low;
 *(volatile uint32_t *)(uintptr_t)0x805a98u=high;
 return 0u;
}
/* Native30d9b4..30d9f0: BMSK24 includes bits0..24. High then low
 * captures precede low then high publication; fullword enable truth. */
uint32_t opencfw_em9305_vendor_command_30d9b4(uint32_t low,uint32_t high,uint32_t enable)
{
 if(((low&0xc0010000u)|(high&0x01ffffffu))!=0u)return 18u;
 uint32_t old_high=*(volatile uint32_t *)(uintptr_t)0x805a88u;
 uint32_t old_low=*(volatile uint32_t *)(uintptr_t)0x805a84u;
 if(enable!=0u){old_high|=high;old_low|=low;}else{old_high&=~high;old_low&=~low;}
 *(volatile uint32_t *)(uintptr_t)0x805a84u=old_low;
 *(volatile uint32_t *)(uintptr_t)0x805a88u=old_high;
 return 0u;
}
/* Native30cd5c..30cd68: native R0 returns the byte-cell address. */
uint32_t opencfw_em9305_vendor_command_30cd5c(uint32_t enabled)
{*(volatile uint8_t *)(uintptr_t)0x805becu=(uint8_t)(enabled!=0u);return 0x805becu;}
/* Native30db24..30db30: native R0 returns the normalized flag. */
uint32_t opencfw_em9305_vendor_command_30db24(uint32_t enabled)
{uint32_t flag=enabled!=0u;*(volatile uint8_t *)(uintptr_t)0x805beeu=(uint8_t)flag;return flag;}
uint32_t opencfw_em9305_vendor_command_30e034(uint32_t value)
{*(volatile uint32_t *)(uintptr_t)0x8059a0u=value;return 0u;}
/* Native313fa8..313fb6: genuine ROM capacity/query contracts remain imports. */
extern uint32_t opencfw_em9305_rom_allocator_capacity_1030e8(uint32_t);
uint32_t opencfw_em9305_vendor_allocator_second_313fa8(uint32_t incoming)
{
 uint32_t capacity=opencfw_em9305_rom_allocator_capacity_1030e8(incoming);
 uint32_t query=opencfw_em9305_controller_allocator_query(capacity);
 return capacity-query;
}
