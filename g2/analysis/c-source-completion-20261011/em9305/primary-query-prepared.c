/* Native313960..313988: full eight-byte serialization; exact store order
 * 4,0,7,6,5,3,2,1 and original destination in R0. */
uint32_t opencfw_em9305_primary_query_313960(uintptr_t output,uint32_t low,uint32_t high)
{
 *(volatile uint8_t *)(output+4u)=(uint8_t)high;
 *(volatile uint8_t *)output=(uint8_t)low;
 *(volatile uint8_t *)(output+7u)=(uint8_t)(high>>24u);
 *(volatile uint8_t *)(output+6u)=(uint8_t)(high>>16u);
 *(volatile uint8_t *)(output+5u)=(uint8_t)(high>>8u);
 *(volatile uint8_t *)(output+3u)=(uint8_t)(low>>24u);
 *(volatile uint8_t *)(output+2u)=(uint8_t)(low>>16u);
 *(volatile uint8_t *)(output+1u)=(uint8_t)(low>>8u);
 return (uint32_t)output;
}
/* Native30bf04..30bf1c: fields captured before output; second config pointer fresh. */
uint32_t opencfw_em9305_primary_query_30bf04(uintptr_t first,uintptr_t version,uintptr_t second)
{
 uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
 uint32_t first_value=*(volatile uint16_t *)config;
 uint32_t version_value=*(volatile uint8_t *)(config+4u);
 *(volatile uint16_t *)first=(uint16_t)first_value;
 *(volatile uint8_t *)version=(uint8_t)version_value;
 config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
 uint32_t second_value=*(volatile uint16_t *)(config+2u);
 *(volatile uint16_t *)second=(uint16_t)second_value;
 return second_value;
}
/* Native30c92c tail31026c; selected complete child retains output pointer R0. */
uint32_t opencfw_em9305_primary_query_30c92c(uintptr_t lower,uintptr_t upper)
{return opencfw_em9305_ll_signed_bounds_31026c(lower,upper);}
/* Native30bb74..30bb80: high-word before low-word, selected six-byte serializer. */
uint32_t opencfw_em9305_primary_query_30bb74(uintptr_t output)
{
 uint32_t high=*(volatile uint32_t *)(uintptr_t)0x805b44u;
 uint32_t low=*(volatile uint32_t *)(uintptr_t)0x805b40u;
 return (uint32_t)opencfw_em9305_radio_address_write_3045e8(output,low,high);
}
/* Native30bdb4..30bdc0: high-word before low-word, full serializer tail. */
uint32_t opencfw_em9305_primary_query_30bdb4(uintptr_t output)
{
 uint32_t high=*(volatile uint32_t *)(uintptr_t)0x805a98u;
 uint32_t low=*(volatile uint32_t *)(uintptr_t)0x805a94u;
 return opencfw_em9305_primary_query_313960(output,low,high);
}
/* Native30bf20 tail303e50; incoming R0 unused by actual child. */
uint32_t opencfw_em9305_primary_query_30bf20(uint32_t ignored)
{(void)ignored;return opencfw_em9305_radio_address_status_303e50();}
/* Native30bea4..30beb0: high-word first, full serializer tail. */
uint32_t opencfw_em9305_primary_query_30bea4(uintptr_t output)
{
 uint32_t high=*(volatile uint32_t *)(uintptr_t)0x805b4cu;
 uint32_t low=*(volatile uint32_t *)(uintptr_t)0x805b48u;
 return opencfw_em9305_primary_query_313960(output,low,high);
}
/* Native310328..31033c: first halfword written before second read. */
uint32_t opencfw_em9305_primary_controls_310328(uintptr_t first,uintptr_t second)
{
 uint32_t first_value=*(volatile uint16_t *)(uintptr_t)0x8012eeu;
 *(volatile uint16_t *)first=(uint16_t)first_value;
 uint32_t second_value=*(volatile uint16_t *)(uintptr_t)0x8012ecu;
 *(volatile uint16_t *)second=(uint16_t)second_value;
 return second_value;
}
uint32_t opencfw_em9305_primary_query_30c928(uintptr_t first,uintptr_t second)
{return opencfw_em9305_primary_controls_310328(first,second);}
