/* Complete native leaf providers used by32eb34; runtime descriptors stay live. */
uint32_t opencfw_em9305_vendor_control_3101f0(uint32_t a,uint32_t b,uint32_t c){(void)a;(void)b;(void)c;return 0u;}
uint32_t opencfw_em9305_vendor_control_31035c(uint32_t a){(void)a;return 1u;}
uint32_t opencfw_em9305_vendor_control_310358(uint32_t a){(void)a;return 1u;}
uint32_t opencfw_em9305_vendor_command_31071c(uint32_t a){*(volatile uint8_t *)(uintptr_t)0x801318u=(uint8_t)a;return a;}
uint32_t opencfw_em9305_vendor_query_30e0d4(uint32_t incoming){(void)incoming;return *(volatile uint16_t *)(uintptr_t)0x8058d8u;}
uint32_t opencfw_em9305_vendor_query_313760(void){return *(volatile uint16_t *)(uintptr_t)0x805f1cu;}
uint32_t opencfw_em9305_vendor_snapshot_30329c(uintptr_t out){return (uint32_t)(uintptr_t)opencfw_em9305_memcpy((void *)out,(const void *)(uintptr_t)0x8015e4u,38u);}
uint32_t opencfw_em9305_vendor_snapshot_3032c0(uintptr_t out){return (uint32_t)(uintptr_t)opencfw_em9305_memcpy((void *)out,(const void *)(uintptr_t)0x801848u,28u);}
uint32_t opencfw_em9305_vendor_query_30bb30(uintptr_t first,uintptr_t second)
{uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;uint32_t value=config!=0u?*(volatile uint8_t *)(config+12u):0u;*(volatile uint8_t *)first=(uint8_t)value;value=*(volatile uint16_t *)(uintptr_t)0x805b1cu;*(volatile uint16_t *)second=(uint16_t)value;return value;}
uint32_t opencfw_em9305_vendor_query_30bc40(uintptr_t first,uintptr_t second)
{uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;uint32_t value=config!=0u?*(volatile uint8_t *)(config+34u):0u;*(volatile uint8_t *)first=(uint8_t)value;value=*(volatile uint16_t *)(uintptr_t)0x805b1au;*(volatile uint16_t *)second=(uint16_t)value;return value;}
uint32_t opencfw_em9305_vendor_query_30bd94(uintptr_t first,uintptr_t second)
{*(volatile uint8_t *)first=3u;uint32_t value=*(volatile uint16_t *)(uintptr_t)0x805b20u;*(volatile uint16_t *)second=(uint16_t)value;return value;}
uint32_t opencfw_em9305_vendor_query_30bda4(uintptr_t first,uintptr_t second)
{*(volatile uint8_t *)first=3u;uint32_t value=*(volatile uint16_t *)(uintptr_t)0x805b1eu;*(volatile uint16_t *)second=(uint16_t)value;return value;}
uint32_t opencfw_em9305_vendor_query_30be2c(uintptr_t first,uintptr_t second)
{*(volatile uint8_t *)first=6u;uint32_t value=*(volatile uint16_t *)(uintptr_t)0x805b22u;*(volatile uint16_t *)second=(uint16_t)value;return value;}
uint32_t opencfw_em9305_vendor_query_30bb84(uintptr_t first,uintptr_t second,uintptr_t third,uintptr_t fourth)
{uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;uint32_t value=0u;
 if(config!=0u){value=*(volatile uint8_t *)(config+57u);*(volatile uint8_t *)first=(uint8_t)value;config=*(volatile uint32_t *)(uintptr_t)0x805cacu;value=*(volatile uint8_t *)(config+58u);}else{*(volatile uint8_t *)first=0u;}
 *(volatile uint8_t *)third=(uint8_t)value;value=*(volatile uint16_t *)(uintptr_t)0x805b2au;*(volatile uint16_t *)second=(uint16_t)value;value=*(volatile uint16_t *)(uintptr_t)0x805b28u;*(volatile uint16_t *)fourth=(uint16_t)value;return value;}
uint32_t opencfw_em9305_vendor_query_30bc04(uintptr_t first,uintptr_t second,uintptr_t third,uintptr_t fourth)
{uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;uint32_t value=0u;
 if(config!=0u){value=*(volatile uint8_t *)(config+52u);*(volatile uint8_t *)first=(uint8_t)value;config=*(volatile uint32_t *)(uintptr_t)0x805cacu;value=*(volatile uint8_t *)(config+53u);}else{*(volatile uint8_t *)first=0u;}
 *(volatile uint8_t *)third=(uint8_t)value;value=*(volatile uint16_t *)(uintptr_t)0x805b26u;*(volatile uint16_t *)second=(uint16_t)value;value=*(volatile uint16_t *)(uintptr_t)0x805b24u;*(volatile uint16_t *)fourth=(uint16_t)value;return value;}
