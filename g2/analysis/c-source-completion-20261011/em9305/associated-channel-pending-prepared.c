/* Native3279a4/3279b4 indirect tails preserve R1 = loaded callback address. */
extern uint32_t opencfw_em9305_associated_channel_notify_3279a4(uintptr_t);
extern uint32_t opencfw_em9305_associated_phy_notify_3279b4(uintptr_t);
__asm__(".text\n.align 2\n.global opencfw_em9305_associated_channel_notify_3279a4\n"
".type opencfw_em9305_associated_channel_notify_3279a4,@function\n"
"opencfw_em9305_associated_channel_notify_3279a4:\nld r1,[r0,2796]\ncmp_s r1,0\njeq_s [blink]\nldb_s r0,[r0,1]\nj_s [r1]\n"
".size opencfw_em9305_associated_channel_notify_3279a4,.-opencfw_em9305_associated_channel_notify_3279a4\n"
".align 2\n.global opencfw_em9305_associated_phy_notify_3279b4\n"
".type opencfw_em9305_associated_phy_notify_3279b4,@function\n"
"opencfw_em9305_associated_phy_notify_3279b4:\nld r1,[r0,2800]\ncmp_s r1,0\njeq_s [blink]\nldb_s r0,[r0,1]\nj_s [r1]\n"
".size opencfw_em9305_associated_phy_notify_3279b4,.-opencfw_em9305_associated_phy_notify_3279b4\n");
uint32_t opencfw_em9305_associated_channel_reset_3279c4(uintptr_t record)
{return (uint32_t)(uintptr_t)opencfw_em9305_memset((void *)(record+80u),0u,96u);}
uint32_t opencfw_em9305_associated_channel_apply_3279d0(uintptr_t record)
{
 if(*(volatile uint8_t *)(record+80u)==1u)return (uint32_t)record;
 uintptr_t event=*(volatile uint32_t *)(uintptr_t)0x805c34u;
 uint32_t count=*(volatile uint16_t *)(record+752u);
 uint32_t lower=*(volatile uint32_t *)(event+4u),upper=*(volatile uint32_t *)(event+8u);
 *(volatile uint16_t *)(record+92u)=(uint16_t)(count+6u);
 *(volatile uint8_t *)(record+82u)=8u;*(volatile uint8_t *)(record+80u)=1u;
 *(volatile uint32_t *)(record+780u)=upper;*(volatile uint32_t *)(record+776u)=lower;
 *(volatile uint32_t *)(record+88u)=upper;*(volatile uint32_t *)(record+84u)=lower;
 return (uint32_t)record;
}
uint32_t opencfw_em9305_associated_phy_apply_327a04(uintptr_t record)
{
 if(*(volatile uint8_t *)(record+272u)==1u)return (uint32_t)record;
 uint32_t value=*(volatile uint32_t *)(record+784u);
 *(volatile uint32_t *)(record+276u)=value;
 value=*(volatile uint8_t *)(record+788u);*(volatile uint8_t *)(record+274u)=9u;
 *(volatile uint8_t *)(record+280u)=(uint8_t)value;
 value=*(volatile uint8_t *)(record+796u);
 uint32_t second=*(volatile uint8_t *)(record+789u),last=*(volatile uint8_t *)(record+797u);
 *(volatile uint8_t *)(record+282u)=(uint8_t)value;
 *(volatile uint8_t *)(record+281u)=(uint8_t)second;
 *(volatile uint8_t *)(record+283u)=(uint8_t)last;
 return last;
}
uint32_t opencfw_em9305_associated_phy_reset_327a3c(uintptr_t record)
{
 *(volatile uint32_t *)(record+280u)=0u;*(volatile uint32_t *)(record+276u)=0u;*(volatile uint32_t *)(record+272u)=0u;return (uint32_t)record;
}
/* Native3344a4/3344aa maps and334b00 typed six function destinations.
 * Transition334b18 has four reachable states bytes and four native padding bytes. */
static const uint8_t opencfw_em9305_associated_channel_event_kind[6]={0,0,1,1,2,2};
static const uint8_t opencfw_em9305_associated_channel_event_action[6]={0,1,0,1,0,1};
static uint32_t (*const opencfw_em9305_associated_channel_actions[6])(uintptr_t)={
 opencfw_em9305_associated_channel_apply_3279d0,opencfw_em9305_associated_channel_reset_3279c4,
 opencfw_em9305_associated_channel_notify_3279a4,opencfw_em9305_associated_phy_notify_3279b4,
 opencfw_em9305_associated_phy_apply_327a04,opencfw_em9305_associated_phy_reset_327a3c};
static const uint8_t opencfw_em9305_associated_channel_transitions[8]={1,0,1,0,0,0,0,0};
uint32_t opencfw_em9305_associated_channel_state_327aac(uintptr_t record,uint32_t event)
{
 if(event>=6u)return (uint32_t)record;
 uint32_t action=opencfw_em9305_associated_channel_event_action[event],kind=opencfw_em9305_associated_channel_event_kind[event];
 (void)opencfw_em9305_associated_channel_actions[action+kind*2u](record);
 uintptr_t slot=record+kind*96u;
 uint32_t state=*(volatile uint8_t *)(slot+80u);
 uint32_t next=*(const uint8_t *)((uintptr_t)opencfw_em9305_associated_channel_transitions+action+state*2u);
 *(volatile uint8_t *)(slot+80u)=(uint8_t)next;
 return next;
}
uint32_t opencfw_em9305_associated_channel_pending_327af4(uintptr_t record)
{
 uintptr_t slot=record+80u,channels=record+720u;uint32_t result=(uint32_t)record;
 for(uint32_t index=0u;index<3u;++index){
  uint32_t active=*(volatile uint8_t *)slot;result=active;slot+=96u;
  if(active!=1u||index!=0u)continue;
  uint32_t count=*(volatile uint16_t *)(record+752u),instant=*(volatile uint16_t *)(record+92u);
  if(instant!=count)continue;
  uint32_t lower=*(volatile uint32_t *)(record+84u),upper=*(volatile uint32_t *)(record+88u);
  *(volatile uint32_t *)channels=lower;*(volatile uint32_t *)(channels+4u)=upper;
  (void)opencfw_em9305_radio_channel_transform_30e3fc(channels);
  (void)opencfw_em9305_associated_channel_state_327aac(record,1u);
  upper=*(volatile uint32_t *)(channels+4u);lower=*(volatile uint32_t *)channels;
  uint32_t oldupper=*(volatile uint32_t *)(record+780u),oldlower=*(volatile uint32_t *)(record+776u);
  *(volatile uint32_t *)(record+132u)=upper;*(volatile uint32_t *)(record+128u)=lower;
  result=upper;
  if(((oldupper^upper)|(oldlower^lower))!=0u)result=opencfw_em9305_associated_channel_state_327aac(record,0u);
 }
 return result; /* Final third-slot active byte in native R0; caller ignores it. */
}
