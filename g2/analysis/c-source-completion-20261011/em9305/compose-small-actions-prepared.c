/* Native 3237e8..32381c: channel-map control element, ordered volatile loads. */
uint32_t opencfw_em9305_compose_action_3237e8(uintptr_t record,uintptr_t output)
{
 volatile uint8_t *r=(volatile uint8_t *)record,*o=(volatile uint8_t *)output;
 o[0]=8u;o[1]=40u;
 o[2]=r[84];o[3]=r[85];o[4]=r[86];o[5]=r[87];o[6]=r[88];
 o[7]=r[92];o[8]=r[93];return 9u;
}
/* Native 323820..32385a: PHY update element. Scaled native loads refer
 * to record+276 and record+278; subsequent byte loads retain their order. */
uint32_t opencfw_em9305_compose_action_323820(uintptr_t record,uintptr_t output)
{
 volatile uint8_t *r=(volatile uint8_t *)record,*o=(volatile uint8_t *)output;
 o[0]=9u;o[1]=50u;
 uint32_t value=*(volatile uint32_t *)(record+276u);o[2]=(uint8_t)value;
 value=*(volatile uint32_t *)(record+276u);o[3]=(uint8_t)(value>>8);
 uint16_t half=*(volatile uint16_t *)(record+278u);o[4]=(uint8_t)half;
 o[5]=r[279];o[6]=r[280];o[7]=r[281];o[8]=r[282];o[9]=r[283];return 10u;
}
