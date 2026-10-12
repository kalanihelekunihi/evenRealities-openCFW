#include <stdint.h>
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
