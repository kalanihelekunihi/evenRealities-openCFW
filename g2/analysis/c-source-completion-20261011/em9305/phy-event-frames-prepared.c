/* Native3232dc/32317c reserve their original event frames before C executes.
 * Untouched native stack bytes remain untouched, never zero-initialized. */
static inline uint32_t opencfw_em9305_phy_event_index(uintptr_t record)
{int32_t delta=(int32_t)((uint32_t)record-*(volatile uint32_t *)(uintptr_t)0x805c70u);int32_t index;__asm__ volatile("div %0,%1,912":"=r"(index):"r"(delta));return (uint8_t)index;}
uint32_t opencfw_em9305_phy_response_frame_3232dc(uintptr_t record,uint32_t reason,uintptr_t event)
{
 uint32_t index=opencfw_em9305_phy_event_index(record);
 *(volatile uint8_t *)(event+4u)=(uint8_t)reason;
 *(volatile uint8_t *)(event+3u)=(uint8_t)reason;
 uint32_t mode=*(volatile uint16_t *)(record+76u);
 *(volatile uint8_t *)(event+2u)=22u;
 *(volatile uint16_t *)(event+8u)=(uint16_t)mode;
 *(volatile uint16_t *)(event+6u)=(uint16_t)index;
 *(volatile uint16_t *)event=(uint16_t)index;
 return opencfw_em9305_ll_event_callback_30e79c(event);
}
uint32_t opencfw_em9305_phy_length_frame_32317c(uintptr_t record,uint32_t reason,uintptr_t event)
{
 uint32_t index=opencfw_em9305_phy_event_index(record);
 *(volatile uint8_t *)(event+3u)=(uint8_t)reason;
 *(volatile uint8_t *)(event+2u)=18u;
 uint32_t a=*(volatile uint16_t *)(record+578u),b=*(volatile uint16_t *)(record+580u);
 *(volatile uint16_t *)(event+6u)=(uint16_t)a;
 uint32_t c=*(volatile uint16_t *)(record+574u),d=*(volatile uint16_t *)(record+576u);
 *(volatile uint16_t *)(event+8u)=(uint16_t)b;
 *(volatile uint16_t *)(event+10u)=(uint16_t)c;
 *(volatile uint16_t *)(event+12u)=(uint16_t)d;
 *(volatile uint16_t *)(event+4u)=(uint16_t)index;
 *(volatile uint16_t *)event=(uint16_t)index;
 return opencfw_em9305_ll_event_callback_30e79c(event);
}
__asm__(
".text\n.balign 4\n.global opencfw_em9305_phy_response_3232dc\n.type opencfw_em9305_phy_response_3232dc,@function\nopencfw_em9305_phy_response_3232dc:\nst.aw blink,[sp,-16]\nadd r2,sp,4\nbl opencfw_em9305_phy_response_frame_3232dc\nld.ab blink,[sp,16]\nj_s [blink]\n.size opencfw_em9305_phy_response_3232dc,.-opencfw_em9305_phy_response_3232dc\n"
);
__asm__(
".text\n.balign 4\n.global opencfw_em9305_phy_length_notify_32317c\n.type opencfw_em9305_phy_length_notify_32317c,@function\nopencfw_em9305_phy_length_notify_32317c:\nst.aw blink,[sp,-20]\nadd r2,sp,4\nbl opencfw_em9305_phy_length_frame_32317c\nld.ab blink,[sp,20]\nj_s [blink]\n.size opencfw_em9305_phy_length_notify_32317c,.-opencfw_em9305_phy_length_notify_32317c\n"
);
