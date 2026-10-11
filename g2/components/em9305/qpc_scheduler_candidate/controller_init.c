/* Native controller initialization 0x30f4b0..0x30f568. Preserve
 * distinct context reloads and native major-6/minor-0x1e operation.
 * Real lower contracts are not substituted by stub implementations. */
#include <stdint.h>
extern uint32_t opencfw_em9305_native_config_product(uint32_t,uint32_t);
extern uint32_t opencfw_em9305_controller_configure_mode(uint32_t); /* 0x30f768 */
extern uint32_t opencfw_em9305_controller_prepare_timer(void); /* 0x30f288 */
extern uint32_t opencfw_em9305_controller_timer_reset(uint32_t); /* 0x30fa40 */
extern uint32_t opencfw_em9305_controller_finish_init(uint32_t); /* 0x30f668 */
extern uint32_t opencfw_em9305_controller_rom_init(uint32_t); /* 0x103c40 */
static uintptr_t context(void) { return *(volatile uint32_t *)(uintptr_t)0x80fb8cu; }
static void word(uint32_t offset,uint32_t value) { *(volatile uint32_t *)(context()+offset)=value; }
static void byte(uint32_t offset,uint8_t value) { *(volatile uint8_t *)(context()+offset)=value; }
extern uint32_t opencfw_em9305_controller_apply_level(uint32_t,uint32_t); /* 0x30f864 */
extern uint32_t opencfw_em9305_controller_rom_mode_action(uint32_t); /* 0x103cf0 */
extern uint32_t opencfw_em9305_controller_rom_level_prepare(uint32_t); /* 0x103b9c */
extern uint32_t opencfw_em9305_controller_rom_level_set(uint32_t); /* 0x103bdc */
extern uint32_t opencfw_em9305_controller_rom_level_finish(uint32_t); /* 0x103bbc */
extern void opencfw_em9305_sleep_rom_restore(uint32_t); /* 0x103b7c */
extern uint32_t opencfw_em9305_timer_rom_set_b(uint32_t); /* 0x104d04 */
extern uint32_t opencfw_em9305_controller_rom_second_value(uint32_t); /* 0x104d24 */
extern void opencfw_em9305_controller_timer_changed(uint32_t);
extern uint64_t opencfw_em9305_sleep_sync_divide(uint32_t,uint32_t,uint32_t,uint32_t);
extern uint64_t opencfw_em9305_sleep_sync_convert(uint32_t,uint32_t);
extern uint32_t opencfw_em9305_controller_early_lower(uint32_t); /* 0x3068c8 */
extern uint32_t opencfw_em9305_controller_rom_boot_status(uint32_t); /* 0x103678 */
extern uint32_t opencfw_em9305_controller_rom_boot_ready(uint32_t); /* 0x10361c */
extern uint32_t opencfw_em9305_sleep_rom_start(uint32_t); /* 0x103b20 */
extern uint32_t opencfw_em9305_controller_rom_construct(uint32_t,uint32_t,uint32_t,uint32_t,uint32_t); /* 0x10aa8c */
extern uint32_t opencfw_em9305_controller_cold_lower(uint32_t); /* 0x302be4 */
extern uint32_t opencfw_em9305_controller_warm_lower(uint32_t); /* 0x302c30 */
extern uint32_t opencfw_em9305_controller_lock_lower(uint32_t); /* 0x302e14 */
extern uint32_t opencfw_em9305_sleep_lock_update(uint32_t);
extern uint32_t opencfw_em9305_controller_rom_delay(uint32_t); /* 0x100c10 */
extern uint32_t opencfw_em9305_timer_rom_set_a(uint32_t);
extern uint32_t opencfw_em9305_timer_rom_probe_a(uint32_t);
extern uint32_t opencfw_em9305_controller_rom_register_irq(uint32_t,uint32_t,uint32_t,uint32_t); /* 0x1035dc */
extern void opencfw_em9305_sleep_controller_enable(uint32_t,uint32_t,uint32_t);
extern uint32_t opencfw_em9305_controller_warm_arch_lower(uint32_t,uint32_t,uint32_t,uint32_t); /* 0x30690c */
extern uint32_t opencfw_em9305_sleep_metadata_sync(uint32_t); /* 0x310990 */
/* Native BOOT_IRQHandlerPMLHFColdStart 0x302d40..0x302d80. */
void opencfw_em9305_controller_cold_irq(void)
{
 volatile uint32_t *pending=(volatile uint32_t *)(uintptr_t)0x8018e4u;
 uint32_t mask=*pending;
 if (mask==0u) return;
 uint32_t locks=*(volatile uint32_t *)(uintptr_t)0x8018f0u;
 if ((locks & mask)!=0u) {
  uint32_t mode=*(volatile uint8_t *)(uintptr_t)0xf0383bu & 3u;
  if (mode==3u) (void)opencfw_em9305_sleep_metadata_sync(mode);
 }
 uint32_t irq;
 __asm__ volatile("clri %0\n\tsync" : "=r"(irq) :: "memory");
 *pending=*pending & ~mask;
 __asm__ volatile("seti %0" :: "r"(irq) : "memory");
}
/* Native BOOT_IrqActionRoutine 0x302d84..0x302de4. The final callback
 * receives the action mask, rather than callback-self R0. */
void opencfw_em9305_controller_irq_action(uint32_t mask)
{
 uint32_t low=*(volatile uint32_t *)(uintptr_t)0x8018ecu;
 int enabled=(low & mask)!=0u;
 if (!enabled) enabled=(*(volatile uint32_t *)(uintptr_t)0x8018f0u & mask)!=0u;
 if (enabled) {
  uint32_t irq;
  __asm__ volatile("clri %0\n\tsync" : "=r"(irq) :: "memory");
  volatile uint32_t *pending=(volatile uint32_t *)(uintptr_t)0x8018e4u;
  *pending=*pending | mask;
  __asm__ volatile("seti %0" :: "r"(irq) : "memory");
  uint32_t status=*(volatile uint32_t *)(uintptr_t)0xf03838u & 0x03000000u;
  if (status==0x03000000u) *(volatile uint32_t *)(uintptr_t)0xf009a8u=2;
  else (void)opencfw_em9305_sleep_rom_start(3);
 }
 uintptr_t callback=*(volatile uint32_t *)(uintptr_t)0x805bf8u;
 if (callback!=0u) ((void (*)(uint32_t))callback)(mask);
}
/* Native 0x3068c8..0x30690c: seventeen normal entries and one final
 * entry omit only the first write; all eighteen retain both sync points. */
uint32_t opencfw_em9305_controller_early_lower(uint32_t incoming)
{
 (void)incoming;
 __asm__ volatile("clri 0\n\tsync" ::: "memory");
 uintptr_t address=0xf00808u;
 for (uint32_t index=0;index<18u;index++,address+=36u) {
  if (index!=17u) *(volatile uint32_t *)address=UINT32_MAX;
  *(volatile uint32_t *)(address+12u)=UINT32_MAX;
  __asm__ volatile("sync" ::: "memory");
  *(volatile uint32_t *)(address+24u)=UINT32_MAX;
  __asm__ volatile("sync" ::: "memory");
 }
 return 0xf00a6cu;
}
/* Native 0x30690c..0x306924 consumes no incoming argument registers. */
uint32_t opencfw_em9305_controller_warm_arch_lower(uint32_t a,uint32_t b,
                                                uint32_t c,uint32_t d)
{
 (void)a;(void)b;(void)c;(void)d;
 uintptr_t object=*(volatile uint32_t *)(uintptr_t)0x80fb70u;
 uint32_t value=(*(volatile uint8_t *)(object+186u)&15u)|16u;
 __asm__ volatile("seti %0" :: "r"(value) : "memory");
 return value;
}
/* Native warm startup 0x302c30..0x302d20. Retain both stable timer
 * reads, duplicate SETI, and the final disabled-interrupt state. */
uint32_t opencfw_em9305_controller_warm_lower(uint32_t incoming)
{
 (void)incoming;
 (void)opencfw_em9305_sleep_lock_update(2);
 volatile uint8_t *state=(volatile uint8_t *)(uintptr_t)0xf00405u;
 uint32_t irq;
 __asm__ volatile("clri %0\n\tsync" : "=r"(irq) :: "memory");
 *state=(uint8_t)(*state & ~1u);
 __asm__ volatile("seti %0" :: "r"(irq) : "memory");
 __asm__ volatile("clri %0\n\tsync" : "=r"(irq) :: "memory");
 *state=(uint8_t)(*state & ~2u);
 __asm__ volatile("seti %0" :: "r"(irq) : "memory");
 volatile uint32_t *clock=(volatile uint32_t *)(uintptr_t)0xf0045cu;
 uint32_t first,second;
 do { first=*clock;second=*clock; } while (first!=second);
 *(volatile uint32_t *)(uintptr_t)0x80fdf8u=first;
 uintptr_t object=*(volatile uint32_t *)(uintptr_t)0x801090u;
 uint32_t selected=255;
 if (object!=0u) {
  uintptr_t callback=*(volatile uint32_t *)(object+16u);
  if (callback!=0u) selected=((uint32_t (*)(uintptr_t))callback)(callback);
 }
 if (selected<12u)
  *(volatile uint32_t *)(uintptr_t)0xf008c4u=(1u<<selected)&4095u;
 uint32_t value=*(volatile uint32_t *)(uintptr_t)0xf0383cu;
 uint32_t extract=value;
 __asm__ volatile("xbfu %0,%0,112" : "+r"(extract));
 uint32_t low=value&4095u;
 __asm__ volatile("xbfu %0,%0,88" : "+r"(value));
 /* ST.AB writes old base then adds144; ST.AS scales72 by word width. */
 *(volatile uint32_t *)(uintptr_t)0xf00840u=extract;
 *(volatile uint32_t *)(uintptr_t)0xf008d0u=low;
 *(volatile uint32_t *)(uintptr_t)0xf009f0u=value;
 (void)opencfw_em9305_controller_warm_arch_lower(value,0xf008d0u,extract,low);
 for (;;) {
  __asm__ volatile("clri %0\n\tsync" : "=r"(irq) :: "memory");
  if (*(volatile uint32_t *)(uintptr_t)0x8018e4u==0u) break;
  uint32_t masked=irq&31u;
  __asm__ volatile("sleep %0" :: "r"(masked) : "memory");
 }
 __asm__ volatile("seti %0\n\tseti %0\n\tclri 0\n\tsync" :: "r"(irq) : "memory");
 if (selected<=11u) {
  *(volatile uint32_t *)(uintptr_t)0xf008c8u=(1u<<selected)&4095u;
  __asm__ volatile("sync" ::: "memory");
 }
 do { first=*clock;second=*clock; } while (first!=second);
 uint32_t result=first-*(volatile uint32_t *)(uintptr_t)0x80fdf8u;
 *(volatile uint32_t *)(uintptr_t)0x80fdf8u=result;
 return result;
}
/* Native registration 0x313904..0x313960: the two indirect calls have
 * different observed R0 values, object first and callback address second. */
void opencfw_em9305_controller_register_timer(uintptr_t object)
{
 *(volatile uint32_t *)(uintptr_t)0x801090u=(uint32_t)object;
 if (object==0u) return;
 uintptr_t callback=*(volatile uint32_t *)(object+20u);
 uint32_t priority=0;
 if (callback!=0u) {
  priority=((uint32_t (*)(uintptr_t))callback)(object);
  object=*(volatile uint32_t *)(uintptr_t)0x801090u;
  if (object==0u) return;
 }
 callback=*(volatile uint32_t *)(object+16u);
 if (callback==0u) return;
 uint32_t irq=((uint32_t (*)(uintptr_t))callback)(callback);
 if (irq>=12u) return;
 (void)opencfw_em9305_controller_rom_register_irq(irq,priority,1,0);
 uint32_t mask=1u<<irq;
 *(volatile uint32_t *)(uintptr_t)0xf008d4u=mask;
 __asm__ volatile("sync" ::: "memory");
 *(volatile uint32_t *)(uintptr_t)0xf008b8u=mask;
 *(volatile uint32_t *)(uintptr_t)0xf008c8u=mask;
 __asm__ volatile("sync" ::: "memory");
 opencfw_em9305_sleep_controller_enable(1,mask,1);
}
/* Native cold startup 0x302be4..0x302c30 leaves interrupts disabled. */
uint32_t opencfw_em9305_controller_cold_lower(uint32_t incoming)
{
 (void)incoming;
 (void)opencfw_em9305_sleep_lock_update(0);
 opencfw_em9305_controller_register_timer(*(volatile uint32_t *)(uintptr_t)0x80fb30u);
 volatile uint8_t *state=(volatile uint8_t *)(uintptr_t)0xf00405u;
 uint32_t irq,value;
 __asm__ volatile("clri %0\n\tsync" : "=r"(irq) :: "memory");
 value=*state & ~1u;
 *state=(uint8_t)value;
 __asm__ volatile("seti %0" :: "r"(irq) : "memory");
 __asm__ volatile("clri %0\n\tsync" : "=r"(irq) :: "memory");
 value=*state & ~2u;
 *state=(uint8_t)value;
 __asm__ volatile("seti %0\n\tclri 0\n\tsync" :: "r"(irq) : "memory");
 return value;
}
/* Native 0x302e14..0x302e64: actual ROM poll and device writes. */
uint32_t opencfw_em9305_controller_lock_lower(uint32_t incoming)
{
 (void)incoming;
 if ((*(volatile uint8_t *)(uintptr_t)0xf0383bu & 12u)==12u) {
  (void)opencfw_em9305_controller_rom_mode_action(2);
  *(volatile uint8_t *)(uintptr_t)0xf0041eu=3;
  (void)opencfw_em9305_timer_rom_set_a(0);
  uint32_t value=opencfw_em9305_controller_rom_delay(5);
  for (;;) {
   value=opencfw_em9305_timer_rom_probe_a(value);
   if (value!=0u) break;
   __asm__ volatile("nop" ::: "memory");
  }
  *(volatile uint8_t *)(uintptr_t)0xf0041eu=1;
 }
 volatile uint32_t *control=(volatile uint32_t *)(uintptr_t)0xf00434u;
 *control=*control | 1u;
 return 0xf00434u;
}
uint32_t opencfw_em9305_controller_seed_timer_mode(void);
uint32_t opencfw_em9305_controller_seed_tables(void);
uint32_t opencfw_em9305_controller_set_period(uint32_t,uint32_t);
extern uint32_t opencfw_em9305_controller_pal_sys_init(uint32_t); /* 0x3106e4 */
extern uint32_t opencfw_em9305_controller_pal_load_config(uintptr_t); /* 0x30fd3c */
extern uint32_t opencfw_em9305_controller_ll_config_seed(uintptr_t); /* 0x30bc60 */
/* Native 0x30bc60..0x30bd18: sparse product-default field writes.
 * Unwritten bytes retain their caller-owned values. */
uint32_t opencfw_em9305_controller_ll_config_seed(uintptr_t destination)
{
 #define LLW(o,v) (*(volatile uint32_t *)(destination+(o))=(v))
 #define LLH(o,v) (*(volatile uint16_t *)(destination+(o))=(v))
 #define LLB(o,v) (*(volatile uint8_t *)(destination+(o))=(v))
 LLW(72,2500u);LLW(40,0x06060000u);
 LLB(24,10u);LLB(14,6u);LLB(4,13u);
 LLH(64,0u);LLH(62,0u);LLW(68,0xba040032u);
 LLH(66,0xc2d8u);LLB(58,4u);LLH(56,260u);
 LLH(54,140u);LLH(50,950u);LLB(48,4u);
 LLW(44,0x00fb0100u);LLH(38,256u);LLB(36,4u);
 LLW(32,0x04040100u);LLH(26,251u);LLW(20,0x00020000u);
 LLB(18,64u);LLH(16,256u);LLH(12,514u);
 LLW(8,0u);LLW(0,0x7be2005au);LLH(52,513u);
 LLH(60,10000u);LLW(28,0x04060000u);
 #undef LLW
 #undef LLH
 #undef LLB
 return (uint32_t)destination;
}
extern uint32_t opencfw_em9305_controller_read_config(uint32_t,uintptr_t,uint32_t); /* 0x30fd70 */
extern uint32_t opencfw_em9305_controller_allocator_zero(void); /* 0x313fb8 */
extern uint32_t opencfw_em9305_controller_allocator_query(uint32_t); /* 0x313fa4 */
extern uint32_t opencfw_em9305_controller_allocator_align(uint32_t); /* 0x313f98 */
extern uint32_t opencfw_em9305_controller_ll_init(uintptr_t); /* 0x30c098 */
extern uint32_t opencfw_em9305_controller_set_address(uintptr_t); /* 0x30cf2c */
extern uint32_t opencfw_em9305_controller_install_callbacks(uintptr_t); /* 0x30aeb8 */
/* Native 0x30aeb8..0x30aec4: install the callback pointer, retain R0. */
uint32_t opencfw_em9305_controller_install_callbacks(uintptr_t callback)
{
 *(volatile uint32_t *)(uintptr_t)0x805790u=(uint32_t)callback;
 return (uint32_t)callback;
}
extern uint32_t opencfw_em9305_controller_wsf_os_init(uint32_t,uintptr_t); /* 0x313dfc */
extern uint32_t opencfw_em9305_controller_wsf_timer_init(uint32_t); /* 0x314280 */
extern uint32_t opencfw_em9305_controller_wsf_register(uintptr_t); /* 0x3140b4 */
/* Native hooks 0x3101e4/0x3101e8/0x3101ec are authenticated return/NOP
 * bodies; they leave incoming R0 unchanged. These are not fallback stubs. */
uint32_t opencfw_em9305_pal_hook_one(uint32_t value) { return value; }
uint32_t opencfw_em9305_pal_hook_two(uint32_t value) { return value; }
uint32_t opencfw_em9305_pal_hook_three(uint32_t value) { return value; }
extern uint32_t opencfw_em9305_pal_baseband_initialize(uint32_t); /* 0x310088 */
extern uint32_t opencfw_em9305_pal_timer_initialize(uint32_t); /* 0x310128 */
extern uint32_t opencfw_em9305_pal_timer_route(uint32_t); /* 0x310b94 */
extern uint32_t opencfw_em9305_pal_timer_mode(uint32_t,uint32_t); /* 0x310b84 */
extern uint32_t opencfw_em9305_pal_timer_channel(uint32_t,uint32_t); /* 0x310b54 */
uint32_t opencfw_em9305_pal_timer_channel(uint32_t index,uint32_t enable)
{
 uint32_t mask=1u,irq;
 __asm__ volatile("asl %0,%0,%1" : "+r"(mask) : "r"(index));
 mask=(uint8_t)mask;
 __asm__ volatile("clri %0\n\tsync" : "=r"(irq) :: "memory");
 uint32_t value=*(volatile uint32_t *)(uintptr_t)0xf01818u;
 value=enable!=0u ? value|mask : value&~mask;
 *(volatile uint32_t *)(uintptr_t)0xf01818u=value;
 __asm__ volatile("seti %0" :: "r"(irq) : "memory");
 return value;
}
uint32_t opencfw_em9305_pal_timer_mode(uint32_t mode,uint32_t flag)
{
 if (flag!=0u) mode|=2u;
 *(volatile uint8_t *)(uintptr_t)0xf01806u=(uint8_t)mode;
 return mode;
}
uint32_t opencfw_em9305_pal_timer_route(uint32_t route)
{
 *(volatile uint8_t *)(uintptr_t)0xf01804u=(uint8_t)(route-1u);
 *(volatile uint8_t *)(uintptr_t)0xf01805u=1u;
 return 0xf01804u;
}
/* Native 0x310128..0x3101b8; resident ROM remains an explicit ABI facade. */
uint32_t opencfw_em9305_pal_timer_initialize(uint32_t incoming)
{
 (void)incoming;
 (void)((uint32_t (*)(uint32_t))(uintptr_t)0x103b0cu)(3u);
 (void)opencfw_em9305_pal_timer_route(24u);
 (void)opencfw_em9305_pal_timer_mode(1u,0u);
 *(volatile uint32_t *)(uintptr_t)0xf01810u=UINT32_MAX;
 *(volatile uint32_t *)(uintptr_t)0xf00814u=UINT32_MAX;
 __asm__ volatile("sync" ::: "memory");
 *(volatile uint32_t *)(uintptr_t)0xf00820u=UINT32_MAX;
 __asm__ volatile("sync" ::: "memory");
 const uint32_t masks[3]={1u,8u,4u};
 for (uint32_t i=0;i<3u;i++) {
  *(volatile uint32_t *)(uintptr_t)0xf00820u=masks[i];
  __asm__ volatile("sync" ::: "memory");
  *(volatile uint32_t *)(uintptr_t)0xf00804u=masks[i];
  *(volatile uint32_t *)(uintptr_t)0xf00810u=masks[i];
 }
 for (uint32_t i=0;i<4u;i++)
  (void)opencfw_em9305_pal_timer_channel(i,0u);
 *(volatile uint32_t *)(uintptr_t)0xf01800u=256u;
 *(volatile uint32_t *)(uintptr_t)0xf01800u=1u;
 return 256u; /* R0 retained through the final two stores. */
}
extern uint32_t opencfw_em9305_pal_rom_baseband_init(uintptr_t,uintptr_t); /* 0x10a84c */
extern uint32_t opencfw_em9305_pal_baseband_lower(uint32_t); /* 0x310814 */
extern uint32_t opencfw_em9305_pal_address_lower(uintptr_t); /* 0x310894 */
/* Native 0x310814..0x310850: deterministic state reset, not entropy input. */
uint32_t opencfw_em9305_pal_baseband_lower(uint32_t incoming)
{
 (void)incoming;
 *(volatile uint32_t *)(uintptr_t)0x805ef0u=0x075bcd15u;
 *(volatile uint32_t *)(uintptr_t)0x805eecu=0x05491333u;
 *(volatile uint32_t *)(uintptr_t)0x805ef4u=0x159a55e5u;
 *(volatile uint32_t *)(uintptr_t)0x805ef8u=0x1f123bb5u;
 return 0x805ef8u;
}
/* Native 0x310850..0x310894: preserve volatile state access ordering. */
uint32_t opencfw_em9305_pal_random_step(void)
{
 uint32_t a=*(volatile uint32_t *)(uintptr_t)0x805eecu;
 uint32_t b=*(volatile uint32_t *)(uintptr_t)0x805ef0u;
 uint32_t d=*(volatile uint32_t *)(uintptr_t)0x805ef8u;
 *(volatile uint32_t *)(uintptr_t)0x805ef8u=a;
 uint32_t mixed=(b<<11)^b;
 uint32_t c=*(volatile uint32_t *)(uintptr_t)0x805ef4u;
 *(volatile uint32_t *)(uintptr_t)0x805ef4u=d;
 mixed^=mixed>>8;
 *(volatile uint32_t *)(uintptr_t)0x805ef0u=c;
 uint32_t next=(a>>19)^mixed^a;
 *(volatile uint32_t *)(uintptr_t)0x805eecu=next;
 return next;
}
/* Native 0x310894..0x3108d0: mix one caller-owned word into all lanes. */
uint32_t opencfw_em9305_pal_address_lower(uintptr_t address)
{
 uint32_t value=*(volatile uint32_t *)address;
 uint32_t a=*(volatile uint32_t *)(uintptr_t)0x805eecu;
 uint32_t b=*(volatile uint32_t *)(uintptr_t)0x805ef0u;
 uint32_t c=*(volatile uint32_t *)(uintptr_t)0x805ef4u;
 uint32_t d=*(volatile uint32_t *)(uintptr_t)0x805ef8u;
 *(volatile uint32_t *)(uintptr_t)0x805eecu=a^value;
 *(volatile uint32_t *)(uintptr_t)0x805ef0u=b^value;
 *(volatile uint32_t *)(uintptr_t)0x805ef4u=c^value;
 value^=d;
 *(volatile uint32_t *)(uintptr_t)0x805ef8u=value;
 return value;
}
/* Native 0x310088..0x3100c8. Unassigned configuration bytes remain
 * product-owned; only the exact native stores are authored here. */
uint32_t opencfw_em9305_pal_baseband_initialize(uint32_t incoming)
{
 (void)incoming;
 *(volatile uint32_t *)(uintptr_t)0x805e44u=320;
 *(volatile uint16_t *)(uintptr_t)0x805e40u=512;
 *(volatile uint8_t *)(uintptr_t)0x805e42u=1;
 uint8_t address[6];
 (void)opencfw_em9305_controller_read_config(0,(uintptr_t)address,6);
 uint32_t result=opencfw_em9305_pal_rom_baseband_init(0x805e40u,(uintptr_t)address);
 if (result!=0u) __asm__ volatile("trap_s 0" ::: "memory");
 (void)opencfw_em9305_pal_baseband_lower(result);
 return opencfw_em9305_pal_address_lower((uintptr_t)address);
}
/* Native PalSysInit 0x3106e4..0x310718. */
uint32_t opencfw_em9305_controller_pal_sys_init(uint32_t incoming)
{
 (void)incoming;
 *(volatile uint8_t *)(uintptr_t)0x801318u=1;
 *(volatile uint32_t *)(uintptr_t)0x805eccu=0;
 (void)opencfw_em9305_pal_hook_one(0x805eccu);
 (void)opencfw_em9305_pal_hook_two(17);
 (void)opencfw_em9305_pal_hook_three(16);
 uint32_t value=opencfw_em9305_pal_baseband_initialize(16);
 return opencfw_em9305_pal_timer_initialize(value);
}
/* Native PalSysGetCurrentTime 0x310104..0x310110. */
uint32_t opencfw_em9305_pal_current_time(void)
{ return *(volatile uint32_t *)(uintptr_t)0xf01808u; }
/* Native WsfTimerInit 0x314280..0x3142a0. */
uint32_t opencfw_em9305_controller_wsf_timer_init(uint32_t incoming)
{
 (void)incoming;
 *(volatile uint32_t *)(uintptr_t)0x80607cu=0;
 *(volatile uint32_t *)(uintptr_t)0x806078u=0;
 uint32_t now=opencfw_em9305_pal_current_time();
 *(volatile uint32_t *)(uintptr_t)0x8019f4u=now;
 return now;
}
/* Native BstreamToBda64 0x304624..0x304648. */
uint64_t opencfw_em9305_controller_pack_address(uintptr_t address)
{
 volatile uint8_t *bytes=(volatile uint8_t *)address;
 uint32_t second=bytes[1],third=bytes[2],first=bytes[0];
 uint32_t sixth=bytes[5],fourth=bytes[3],fifth=bytes[4];
 uint32_t low=first|(second<<8)|(third<<16)|(fourth<<24);
 uint32_t high=fifth|(sixth<<8);
 return ((uint64_t)high<<32)|low;
}
uint32_t opencfw_em9305_controller_set_address(uintptr_t address)
{
 uint64_t value=opencfw_em9305_controller_pack_address(address);
 *(volatile uint32_t *)(uintptr_t)0x805b44u=(uint32_t)(value>>32);
 *(volatile uint32_t *)(uintptr_t)0x805b40u=(uint32_t)value;
 return (uint32_t)value;
}
/* Native PalBbLoadCfg 0x30fd3c..0x30fd6c: exact widths/store order. */
uint32_t opencfw_em9305_controller_pal_load_config(uintptr_t destination)
{
 uint32_t value=*(volatile uint16_t *)(uintptr_t)0x80fb9cu;
 *(volatile uint16_t *)destination=(uint16_t)value;
 *(volatile uint8_t *)(destination+12u)=7;
 *(volatile uint16_t *)(destination+6u)=500;
 *(volatile uint16_t *)(destination+4u)=1000;
 *(volatile uint8_t *)(destination+2u)=250;
 *(volatile uint16_t *)(destination+10u)=0x1110;
 *(volatile uint16_t *)(destination+8u)=1812;
 return 1812;
}
/* Native WsfOsSetNextHandler 0x3140b4..0x3140d0. */
uint32_t opencfw_em9305_controller_wsf_register(uintptr_t callback)
{
 uint32_t index=*(volatile uint8_t *)(uintptr_t)0x80605du;
 *(volatile uint8_t *)(uintptr_t)0x80605du=(uint8_t)(index+1u);
 *(volatile uint32_t *)(uintptr_t)(0x805ff4u+index*4u)=(uint32_t)callback;
 return index;
}
struct controller_init_record {
 uint32_t baseband;
 uint16_t capabilities;
 uint8_t mode,reserved;
 uint32_t link_layer,allocator_first,allocator_second;
};
extern uint32_t opencfw_em9305_controller_rom_allocator(uint32_t); /* 0x10305c */
extern uint32_t opencfw_em9305_controller_rom_alloc_query(uint32_t); /* 0x103084 */
uint32_t opencfw_em9305_controller_allocator_zero(void)
{ return opencfw_em9305_controller_rom_allocator(0); }
uint32_t opencfw_em9305_controller_allocator_query(uint32_t incoming)
{ return opencfw_em9305_controller_rom_alloc_query(incoming); }
uint32_t opencfw_em9305_controller_allocator_align(uint32_t bytes)
{ return opencfw_em9305_controller_rom_allocator((bytes+3u)&~3u); }
/* Native 0x313f84: arithmetic wraps in the ARC 32-bit address domain. */
uint32_t opencfw_em9305_controller_align_pointer(uint32_t value)
{ return (value&3u)==0u ? value : (value+4u)&~3u; }
extern uint32_t opencfw_em9305_pal_critical_enter(uint32_t); /* 0x310678 */
extern uint32_t opencfw_em9305_pal_critical_exit(uint32_t); /* 0x31069c */
uint32_t opencfw_em9305_pal_critical_enter(uint32_t incoming)
{
 (void)incoming;
 uint32_t depth=*(volatile uint8_t *)(uintptr_t)0x805ed4u;
 if (depth==0u) {
  uint32_t irq;
  __asm__ volatile("clri %0\n\tsync" : "=r"(irq) :: "memory");
  depth=*(volatile uint8_t *)(uintptr_t)0x805ed4u;
  *(volatile uint32_t *)(uintptr_t)0x805ed0u=irq;
 }
 depth+=1u;
 *(volatile uint8_t *)(uintptr_t)0x805ed4u=(uint8_t)depth;
 return depth;
}
uint32_t opencfw_em9305_pal_critical_exit(uint32_t incoming)
{
 (void)incoming;
 uint32_t depth=*(volatile uint8_t *)(uintptr_t)0x805ed4u;
 depth-=1u;
 *(volatile uint8_t *)(uintptr_t)0x805ed4u=(uint8_t)depth;
 if ((uint8_t)depth!=0u) return 0x805ed4u;
 uint32_t irq=*(volatile uint32_t *)(uintptr_t)0x805ed0u;
 __asm__ volatile("seti %0" :: "r"(irq) : "memory");
 return irq;
}
/* Authenticated native 0x3106bc..0x3106dc, protected pending consumption. */
uint32_t opencfw_em9305_pal_pending_consume(uint32_t incoming)
{
 (void)opencfw_em9305_pal_critical_enter(incoming);
 uint32_t pending=*(volatile uint32_t *)(uintptr_t)0x805eccu;
 if (incoming!=0u) *(volatile uint32_t *)(uintptr_t)0x805eccu=0u;
 (void)opencfw_em9305_pal_critical_exit(0x805eccu);
 return pending;
}
/* Native 0x3106dc/0x3106e0 both return literal zero, not absent providers. */
uint32_t opencfw_em9305_pal_status(void) { return 0u; }
uint32_t opencfw_em9305_pal_status_secondary(void) { return 0u; }
/* Native 0x313f54..0x313f6c: enter the outermost WSF critical region. */
uint32_t opencfw_em9305_wsf_critical_enter(void)
{
 uint32_t depth=*(volatile uint8_t *)(uintptr_t)0x805ff1u;
 if (depth==0u) {
  (void)opencfw_em9305_pal_critical_enter(depth);
  depth=*(volatile uint8_t *)(uintptr_t)0x805ff1u;
 }
 depth+=1u;
 *(volatile uint8_t *)(uintptr_t)0x805ff1u=(uint8_t)depth;
 return depth;
}
/* Native 0x313f6c..0x313f84: restore only at byte-depth zero. */
uint32_t opencfw_em9305_wsf_critical_exit(void)
{
 uint32_t depth=*(volatile uint8_t *)(uintptr_t)0x805ff1u;
 depth-=1u;
 *(volatile uint8_t *)(uintptr_t)0x805ff1u=(uint8_t)depth;
 if ((uint8_t)depth!=0u) return 0x805ff1u;
 return opencfw_em9305_pal_critical_exit(0x805ff1u);
}
extern void *opencfw_em9305_memset(void *,uint32_t,uint32_t);
/* Native 0x313dfc..0x313f54: WSF pool metadata and free-list construction.
 * ROM allocator/query semantics and product pool descriptors remain external. */
uint32_t opencfw_em9305_controller_wsf_os_init(uint32_t pools,uintptr_t descriptors)
{
 uint32_t cursor=opencfw_em9305_controller_allocator_zero();
 uint32_t base=cursor;
 uintptr_t product=*(volatile uint32_t *)(uintptr_t)0x805cacu;
 *(volatile uint32_t *)(uintptr_t)0x805fe8u=cursor;
 if (*(volatile uint8_t *)(product+75u)!=0u) {
  cursor=opencfw_em9305_controller_align_pointer(cursor);
  *(volatile uint32_t *)(uintptr_t)0x805fe4u=cursor;
  (void)opencfw_em9305_memset((void *)(uintptr_t)cursor,0u,128u);
  cursor+=1024u;
  *(volatile uint32_t *)(uintptr_t)0x805fe8u=cursor;
  cursor=opencfw_em9305_controller_align_pointer(cursor);
  *(volatile uint32_t *)(uintptr_t)0x806074u=cursor;
  (void)opencfw_em9305_memset((void *)(uintptr_t)cursor,0u,32u);
  base=cursor+256u;
  *(volatile uint32_t *)(uintptr_t)0x805fe8u=base;
 }
 uint32_t metadata=base,free_head=base+(pools<<4);
 uint32_t failed=0u,result=0u,status=1u,r0=0x805ff0u;
 *(volatile uint8_t *)(uintptr_t)0x805ff0u=(uint8_t)pools;
 for (;;) {
  r0=opencfw_em9305_controller_allocator_query(r0);
  r0=(r0&~7u)+base;
  if (r0<free_head) break;
  if ((uint8_t)pools==0u) { status=failed;break; }
  uint32_t size=*(volatile uint16_t *)descriptors;
  if (size<8u) size=8u;
  else if ((size&7u)!=0u) size=(size+8u)&~7u;
  *(volatile uint16_t *)(uintptr_t)metadata=(uint16_t)size;
  uint32_t count=*(volatile uint8_t *)(descriptors+2u);
  uint32_t stride=size&0xfff8u;
  *(volatile uint32_t *)(uintptr_t)(metadata+8u)=free_head;
  *(volatile uint32_t *)(uintptr_t)(metadata+4u)=free_head;
  *(volatile uint32_t *)(uintptr_t)(metadata+12u)=0u;
  *(volatile uint8_t *)(uintptr_t)(metadata+2u)=(uint8_t)count;
  r0=size;
  if (count>=2u) {
   uint32_t links=(uint8_t)(count-2u)+1u;
   r0=count-2u;
   do {
    r0=opencfw_em9305_controller_allocator_query(r0);
    base=*(volatile uint32_t *)(uintptr_t)0x805fe8u;
    uint32_t limit=(r0&~7u)+base;
    r0=stride&~7u;
    if (limit<free_head) { failed=1u;break; }
    r0+=free_head;
    *(volatile uint32_t *)(uintptr_t)free_head=r0;
    free_head=r0;
   } while (--links!=0u);
  }
  if (failed!=0u) { status=failed;break; }
  r0=opencfw_em9305_controller_allocator_query(r0);
  base=*(volatile uint32_t *)(uintptr_t)0x805fe8u;
  uint32_t limit=(r0&~7u)+base;
  r0=stride&~7u;
  if (limit<free_head) break;
  *(volatile uint32_t *)(uintptr_t)free_head=0u;
  base=*(volatile uint32_t *)(uintptr_t)0x805fe8u;
  pools-=1u;descriptors+=4u;metadata+=16u;
  free_head+=r0;r0=free_head;
 }
 if (status==0u) {
  product=*(volatile uint32_t *)(uintptr_t)0x805cacu;
  uint32_t current=*(volatile uint32_t *)(uintptr_t)0x805fe8u;
  uint32_t enabled=*(volatile uint8_t *)(product+75u);
  result=free_head-current;
  *(volatile uint32_t *)(uintptr_t)0x805fecu=result;
  if (enabled!=0u) {
   result+=160u;
   *(volatile uint32_t *)(uintptr_t)0x805fecu=result;
  }
 }
 return result;
}
extern void opencfw_em9305_controller_config_address(uintptr_t); /* 0x333338 */
extern void opencfw_em9305_controller_config_extended(uintptr_t); /* 0x333398 */
extern void opencfw_em9305_controller_config_radio(uintptr_t); /* 0x333374 */
extern uintptr_t opencfw_em9305_controller_rom_address(uintptr_t); /* 0x1031a4 */
/* Native 0x333338..0x333374: optional factory bytes, else observed
 * 0..5 fallback with the final byte's upper bits set. */
void opencfw_em9305_controller_config_address(uintptr_t destination)
{
 uintptr_t source=opencfw_em9305_controller_rom_address(destination);
 volatile uint8_t *bytes=(volatile uint8_t *)destination;
 if (source!=0u) {
  for (uint32_t index=0;index<6u;index++)
   bytes[index]=*(volatile uint8_t *)(source+index);
 } else {
  for (uint32_t index=0;index<6u;index++) bytes[index]=(uint8_t)index;
  bytes[5]=197;
 }
}
/* Native 0x333374..0x333398. */
void opencfw_em9305_controller_config_radio(uintptr_t destination)
{
 volatile uint8_t *bytes=(volatile uint8_t *)destination;
 for (uint32_t index=0;index<16u;index++) bytes[index]=(uint8_t)index;
 uint32_t first=bytes[7],second=bytes[8];
 bytes[7]=(uint8_t)((first & 15u)|64u);
 bytes[8]=(uint8_t)((second & 63u)|128u);
}
/* Native 0x333398..0x3333d0. */
void opencfw_em9305_controller_config_extended(uintptr_t destination)
{
 uint8_t address[6];
 opencfw_em9305_controller_config_address((uintptr_t)address);
 uint32_t first=address[0],third=address[2],second=address[1];
 uint32_t fourth=address[3],fifth=address[4],sixth=address[5];
 volatile uint8_t *bytes=(volatile uint8_t *)destination;
 bytes[3]=255;bytes[4]=254;bytes[2]=(uint8_t)third;
 bytes[1]=(uint8_t)second;bytes[5]=(uint8_t)fourth;
 bytes[6]=(uint8_t)fifth;bytes[7]=(uint8_t)sixth;
 bytes[0]=(uint8_t)(first|2u);
}
/* Native selector table 0x30fd70..0x30fdb8 discards incoming R2.
 * Selector2 is a successful no-write path, not a fabricated zero-fill. */
uint32_t opencfw_em9305_controller_read_config(uint32_t selector,uintptr_t destination,uint32_t incoming)
{
 (void)incoming;
 volatile uint8_t *bytes=(volatile uint8_t *)destination;
 switch (selector) {
 case 0:opencfw_em9305_controller_config_address(destination);return 1;
 case 1:bytes[3]=1;bytes[2]=1;bytes[1]=1;bytes[0]=1;return 1;
 case 2:return 1;
 case 3:opencfw_em9305_controller_config_extended(destination);return 1;
 case 4:opencfw_em9305_controller_config_radio(destination);return 1;
 case 6:bytes[1]=1;bytes[0]=1;return 1;
 default:return 0;
 }
}
_Static_assert(sizeof(struct controller_init_record)==20,"native init record offsets");
/* Native 0x302ae4..0x302ae8 consumes no argument. */
void opencfw_em9305_controller_empty_handler(void) { }
/* Native 0x302a20..0x302ae4. Reserved byte7 has no stock assignment;
 * its product contract remains open rather than being fabricated. */
uint32_t opencfw_em9305_controller_initialize_stack(uint32_t incoming)
{
 (void)opencfw_em9305_controller_pal_sys_init(incoming);
 (void)opencfw_em9305_controller_pal_load_config(0x8018f4u);
 (void)opencfw_em9305_controller_ll_config_seed(0x801924u);
 (void)opencfw_em9305_controller_read_config(2,0x801930u,64);
 (void)opencfw_em9305_controller_read_config(1,0x801962u,14);
 (void)opencfw_em9305_controller_read_config(6,0x801969u,7);
 *(volatile uint8_t *)(uintptr_t)0x801948u=4;
 *(volatile uint8_t *)(uintptr_t)0x80196eu=0;
 *(volatile uint8_t *)(uintptr_t)0x801932u=3;
 struct controller_init_record record;
 record.baseband=0x8018f4u;
 record.capabilities=0x0b04u;
 record.mode=4;
 record.link_layer=0x801924u;
 *(volatile uint16_t *)(uintptr_t)0x80194au=251;
 *(volatile uint16_t *)(uintptr_t)0x801946u=1028;
 record.allocator_first=opencfw_em9305_controller_allocator_zero();
 record.allocator_second=opencfw_em9305_controller_allocator_query(record.allocator_first);
 uint32_t result=opencfw_em9305_controller_ll_init((uintptr_t)&record);
 (void)opencfw_em9305_controller_allocator_align(result);
 uint8_t address[6];
 (void)opencfw_em9305_controller_read_config(0,(uintptr_t)address,6);
 (void)opencfw_em9305_controller_set_address((uintptr_t)address);
 (void)opencfw_em9305_controller_install_callbacks(0x332b70u);
 result=opencfw_em9305_controller_wsf_os_init(7,0x334ae4u);
 result=opencfw_em9305_controller_allocator_align(result);
 (void)opencfw_em9305_controller_wsf_timer_init(result);
 result=opencfw_em9305_controller_wsf_register((uintptr_t)opencfw_em9305_controller_empty_handler);
 *(volatile uint8_t *)(uintptr_t)0x8018e8u=(uint8_t)result;
 return result;
}
/* Native startup 0x302ae8..0x302be4. Architectural configuration is
 * explicit; actual lower bodies and resident ROM contracts stay visible. */
uint32_t opencfw_em9305_controller_startup(void)
{
 uint32_t value;
 __asm__ volatile("kflag 0\n\tlr %0,[197]" : "=r"(value) :: "memory");
 if ((value & 255u)==2u) {
  uint32_t upper=0x80f978u,lower=0x80e978u;
  __asm__ volatile("sr %0,[613]\n\tsr %1,[612]" :: "r"(upper),"r"(lower) : "memory");
  __asm__ volatile("lr %0,[status32]" : "=r"(value) :: "memory");
  value|=1u<<14;
  __asm__ volatile("kflag %0" :: "r"(value) : "memory");
 }
 __asm__ volatile("lr %0,[status32]" : "=r"(value) :: "memory");
 value|=1u<<13;
 __asm__ volatile("kflag %0" :: "r"(value) : "memory");
 (void)opencfw_em9305_controller_early_lower(value);
 uint32_t count;
 __asm__ volatile("lr %0,[count0]" : "=r"(count) :: "memory");
 *(volatile uint32_t *)(uintptr_t)0x801108u=count;
 value=0;
 __asm__ volatile("sr %0,[count0]" :: "r"(value) : "memory");
 value=opencfw_em9305_controller_rom_boot_status(value);
 int warm=0;
 if ((value & 768u)!=0u) {
  value=opencfw_em9305_controller_rom_boot_ready(value);
  if (value==0u) warm=1;
 }
 if (!warm) {
  value=opencfw_em9305_controller_rom_boot_status(value);
  if ((value & 1u)==0u) {
   (void)opencfw_em9305_sleep_rom_start(2);
   volatile uint32_t *status=(volatile uint32_t *)(uintptr_t)0xf03838u;
   while ((*status & 0x03000000u)!=0x02000000u)
    __asm__ volatile("nop" ::: "memory");
  }
  (void)opencfw_em9305_controller_seed_timer_mode();
  (void)opencfw_em9305_controller_seed_tables();
  value=opencfw_em9305_controller_rom_construct(0x801040u,0,2,320,1);
  value=opencfw_em9305_controller_cold_lower(value);
  (void)opencfw_em9305_controller_lock_lower(value);
  __asm__ volatile("lr %0,[count0]" : "=r"(count) :: "memory");
  value=*(volatile uint32_t *)(uintptr_t)0x801108u+count;
  *(volatile uint32_t *)(uintptr_t)0x80fdf4u=value;
  value=*(volatile uint32_t *)(uintptr_t)0x80fdf4u;
  return opencfw_em9305_controller_set_period(value+0x9ab0u,0);
 }
 (void)opencfw_em9305_controller_warm_lower(value);
 value=*(volatile uint8_t *)(uintptr_t)0xf0383bu & 3u;
 if (value!=3u) return value;
 (void)opencfw_em9305_controller_lock_lower(value);
 __asm__ volatile("lr %0,[count0]" : "=r"(count) :: "memory");
 value=*(volatile uint32_t *)(uintptr_t)0x801108u+count;
 uint32_t delta=*(volatile uint32_t *)(uintptr_t)0x80fdf8u;
 return opencfw_em9305_controller_set_period(value,delta);
}
/* Native inverse conversion 0x30f2b8..0x30f2d8: unsigned full-width
 * product plus a wrapping high-word contribution. */
uint64_t opencfw_em9305_controller_inverse_convert(uint32_t low,uint32_t high)
{
 uintptr_t first=context();
 uint32_t factor=*(volatile uint32_t *)(first+12u);
 uint64_t product=(uint64_t)factor*low;
 uintptr_t second=context();
 uint32_t divisor=*(volatile uint32_t *)(second+8u);
 return opencfw_em9305_sleep_sync_divide((uint32_t)product,
   (uint32_t)(product>>32)+high*factor,divisor,0);
}
uint32_t opencfw_em9305_controller_numeric_level(int32_t value) /* 0x30f2f0 */
{
 if (value>8) return 7;
 if (value>6) return 6;
 if (value==6) return 5;
 if (value>4) return 4;
 if (value==4) return 3;
 return value>=1 ? 2u : 1u;
}
/* Native mode seed 0x30fa78..0x30fa9c. */
uint32_t opencfw_em9305_controller_seed_timer_mode(void)
{
 uintptr_t c=*(volatile uint32_t *)(uintptr_t)0x80fde0u;
 *(volatile uint32_t *)c=0;
 uint32_t mode=*(volatile uint8_t *)(uintptr_t)0xf0383bu;
 __asm__ volatile("xbfu %0,%0,0x22" : "+r"(mode));
 *(volatile uint32_t *)(uintptr_t)0x80199cu=mode;
 return 0x80199cu;
}
/* Native product table root selection 0x30f67c..0x30f6c8. No table
 * contents are synthesized; the authenticated addresses stay explicit. */
uint32_t opencfw_em9305_controller_seed_tables(void)
{
 volatile uint32_t *mode=(volatile uint32_t *)(uintptr_t)0x80199cu;
 if (*mode==0u) {
  uint32_t configuration=*(volatile uint32_t *)(uintptr_t)0x8012d0u;
  *(volatile uint32_t *)(uintptr_t)0x8012c0u=0x80fbd8u;
  uintptr_t first=configuration!=0u ? 0x80fbe0u : 0x80fc60u;
  uintptr_t second=configuration!=0u ? 0x80fc00u : 0x80fc80u;
  *(volatile uint32_t *)(uintptr_t)0x8012c8u=(uint32_t)second;
  *(volatile uint32_t *)(uintptr_t)0x8012c4u=(uint32_t)first;
 }
 uint32_t current=*mode;
 if (current!=2u) return current;
 uint32_t configuration=*(volatile uint32_t *)(uintptr_t)0x8012d0u;
 uint32_t selected=configuration!=0u ? 0x80fd00u : 0x80fce0u;
 *(volatile uint32_t *)(uintptr_t)0x8012c8u=selected;
 *(volatile uint32_t *)(uintptr_t)0x8012c4u=selected;
 return selected;
}
/* Native period setter 0x30f998..0x30f9bc. */
uint32_t opencfw_em9305_controller_set_period(uint32_t extra,uint32_t delta)
{
 uint32_t converted=(uint32_t)opencfw_em9305_sleep_sync_convert(delta,delta);
 uint32_t count=*(volatile uint32_t *)(uintptr_t)0x80fbb0u;
 uint32_t factor=*(volatile uint16_t *)(uintptr_t)0x80fbaeu;
 uint32_t value=converted+extra+opencfw_em9305_native_config_product(count,factor);
 *(volatile uint32_t *)context()=value;
 return value;
}
static uint32_t level_class(uint32_t level)
{
 if (level>=6u) return 3;
 if (level<=2u) return level==2u;
 return 2;
}
/* Native 0x30f864..0x30f934. The subtraction at 0x30f8f0 is a branch
 * delay instruction and changes the later comparison operand. */
uint32_t opencfw_em9305_controller_apply_level(uint32_t level,uint32_t alternate)
{
 volatile uint32_t *mode=(volatile uint32_t *)(uintptr_t)0x80199cu;
 if (*mode!=0u) {
  if (*mode!=1u) return level;
  uint32_t category=level_class(level);
  (void)opencfw_em9305_controller_rom_level_prepare(0);
  (void)opencfw_em9305_controller_rom_level_set(category);
  return opencfw_em9305_controller_rom_level_finish(1);
 }
 uintptr_t table=*(volatile uint32_t *)(uintptr_t)0x8012c0u;
 int32_t first=*(volatile int8_t *)table;
 int32_t second;
 uint32_t category;
 if (alternate!=0u) {
  category=level_class(level);
  second=first;
 } else {
  uint32_t configuration=*(volatile uint32_t *)(uintptr_t)0x8012d0u;
  second=*(volatile int8_t *)(table+level);
  uintptr_t selected=configuration!=0u ? 0x80fc00u : 0x80fc80u;
  if (level==2u) selected+=32u;
  else if (level!=1u && level-3u<3u) selected+=64u;
  *(volatile uint32_t *)(uintptr_t)0x8012c8u=(uint32_t)selected;
  opencfw_em9305_controller_timer_changed((uint32_t)selected);
  category=0;
 }
 (void)opencfw_em9305_controller_rom_level_prepare(0);
 (void)opencfw_em9305_controller_rom_level_set(category);
 (void)opencfw_em9305_controller_rom_level_finish(alternate);
 if (*(volatile uint32_t *)(uintptr_t)0x8012d0u==0u)
  opencfw_em9305_sleep_rom_restore(alternate);
 (void)opencfw_em9305_timer_rom_set_b((uint32_t)first);
 return opencfw_em9305_controller_rom_second_value((uint32_t)second);
}
/* Native 0x30f9bc..0x30f9d0. */
uint32_t opencfw_em9305_controller_mode_action(void)
{
 uint32_t mode=*(volatile uint32_t *)(uintptr_t)0x80199cu;
 return mode==3u ? opencfw_em9305_controller_rom_mode_action(2) : mode;
}
static uint32_t timer_flag(uint32_t bit)
{
 uintptr_t c=*(volatile uint32_t *)(uintptr_t)0x80fde0u;
 return (*(volatile uint8_t *)(c+14u)>>bit)&1u;
}
/* Native 0x30f31c..0x30f368: each flag query reloads its product root. */
uint32_t opencfw_em9305_controller_available_level(void)
{
 volatile uint32_t *mode=(volatile uint32_t *)(uintptr_t)0x80199cu;
 if (*mode==0u || *mode==1u) return timer_flag(0)!=0u ? 7u : 5u;
 if (timer_flag(1)!=0u) return 5;
 if (timer_flag(2)!=0u) return 4;
 if (timer_flag(3)!=0u) return 3;
 return timer_flag(4)!=0u ? 2u : 1u;
}
uint32_t opencfw_em9305_controller_product_halfword(void) /* 0x30f368 */
{
 return *(volatile uint16_t *)(uintptr_t)0x80fb9cu;
}
/* Native 0x30f794..0x30f864. Labels preserve the native fallthrough
 * decisions after each query returns in R0. */
uint32_t opencfw_em9305_controller_select_level(uint32_t value)
{
 uint32_t selected,flag_two=0,flag_three=0,result;
 if (value>=7u) {
  value=timer_flag(0);
  if (value!=0u) { selected=7;flag_three=1;goto apply; }
  goto six;
 }
 if (value==6u) {
six:
  value=timer_flag(0);
  if (value!=0u) { selected=6;flag_three=1;goto apply; }
  goto five;
 }
 if (value>=5u) {
five:
  value=timer_flag(1);
  if (value!=0u) { selected=5;flag_two=1;goto apply; }
  goto four;
 }
 if (value==4u) {
four:
  value=timer_flag(2);
  if (value!=0u) { selected=4;goto apply; }
  goto three;
 }
 if (value>=3u) {
three:
  value=timer_flag(3);
  if (value!=0u) { selected=3;goto apply; }
  goto two;
 }
 if (value==0u) { selected=0;goto apply; }
 if (value==2u) {
two:
  value=timer_flag(4);
  if (value!=0u) { selected=2;goto apply; }
 }
 value=timer_flag(5);
 selected=value!=0u ? 1u : 0u;
apply:
 result=0;
 if (*(volatile uint32_t *)(uintptr_t)0x80199cu==0u) {
  uint32_t mode=*(volatile uint32_t *)(uintptr_t)0x8012d0u;
  if (mode!=0u) {
   result=flag_three;
   if (mode==1u) {
    if (flag_two!=0u) {
     int32_t v=*(volatile int8_t *)(uintptr_t)0x8019a0u;
     if (v<6) result=1;
    }
    if (*(volatile int8_t *)(uintptr_t)0x8019a0u<1) result=1;
   }
  } else {
   int32_t v=*(volatile int8_t *)(uintptr_t)0x8019a0u;
   result=flag_three;
   if (v<1) result=1;
  }
 }
 (void)opencfw_em9305_controller_apply_level(selected,result);
 *(volatile uint32_t *)(uintptr_t)0x8012ccu=selected;
 (void)opencfw_em9305_controller_mode_action();
 return selected;
}
uint32_t opencfw_em9305_controller_finish_init(uint32_t incoming)
{
 (void)incoming;
 uint32_t result=opencfw_em9305_controller_select_level(1);
 *(volatile uint32_t *)(uintptr_t)0x8012ccu=result;
 return result;
}
/* Native 0x30f768..0x30f794: low two mode bits under IRQ protection. */
uint32_t opencfw_em9305_controller_configure_mode(uint32_t mode)
{
 uint32_t irq;
 __asm__ volatile("clri %0\n\tsync" : "=r"(irq) :: "memory");
 volatile uint8_t *control=(volatile uint8_t *)(uintptr_t)0xf00404u;
 uint32_t previous=*control;
 *control=(uint8_t)((previous & ~3u) | (mode & 3u));
 __asm__ volatile("seti %0" :: "r"(irq) : "memory");
 uintptr_t c=context();
 *(volatile uint8_t *)(c+37u)=0;
 return (uint32_t)c;
}
uint32_t opencfw_em9305_controller_init(void)
{
 uint32_t first=*(volatile uint32_t *)(uintptr_t)0x80fbb4u;
 uint32_t second=*(volatile uint32_t *)(uintptr_t)0x80fbb8u;
 uint32_t factor=*(volatile uint16_t *)(uintptr_t)0x80fbaeu;
 word(4,opencfw_em9305_native_config_product(second+first,factor));
 uint8_t flag=*(volatile uint8_t *)(uintptr_t)0x80fb9fu;
 uintptr_t flag_context=context();
 uint32_t value=*(volatile uint32_t *)(uintptr_t)0x80fb94u; word(8,value);
 value=*(volatile uint32_t *)(uintptr_t)0x80fb98u; word(12,value);
 word(20,0);word(24,0);
 uintptr_t third=context();
 *(volatile uint8_t *)(flag_context+38u)=flag;
 *(volatile uint32_t *)(third+28u)=0;
 word(32,0);byte(39,0);byte(40,0);word(16,0);byte(41,0);
 byte(42,1);byte(44,0);byte(45,0);byte(43,0);
 uint8_t mode=*(volatile uint8_t *)(uintptr_t)0x80fb9eu;
 uintptr_t c=context();
 if(mode!=0) { *(volatile uint8_t *)(c+36u)=1; (void)opencfw_em9305_controller_configure_mode(*(volatile uint8_t *)(uintptr_t)0x80fb9eu); }
 else *(volatile uint8_t *)(c+36u)=0;
 value=*(volatile uint32_t *)(uintptr_t)0xf00404u;
 c=context(); __asm__ volatile("xbfu %0,%0,3" : "+r"(value));
 *(volatile uint8_t *)(c+37u)=(uint8_t)value;
 value=*(volatile uint8_t *)(context()+38u);
 if(value==0) value=opencfw_em9305_controller_prepare_timer();
 value=opencfw_em9305_controller_timer_reset(value);
 (void)opencfw_em9305_controller_finish_init(value);
 return opencfw_em9305_controller_rom_init(*(volatile uint8_t *)(uintptr_t)0x80fbbeu);
}

/* Native LL dispatch initializers: source callback providers remain explicit.
 * Function addresses are relocated C symbols, not embedded stock code bytes. */
extern uint32_t opencfw_em9305_dispatch_32eec8(uintptr_t); /* native 0x32eec8 */
extern uint32_t opencfw_em9305_dispatch_32fea4(uintptr_t,uintptr_t); /* native0x32fea4 */
extern uint32_t opencfw_em9305_dispatch_32ff20(uintptr_t); /* native0x32ff20 */
extern void opencfw_em9305_dispatch_3300c8(void); /* native 0x3300c8, ABI not qualified */
extern void opencfw_em9305_dispatch_330400(void); /* native 0x330400, ABI not qualified */
extern uint32_t opencfw_em9305_dispatch_330568(uintptr_t request,uintptr_t input); /* native 0x330568 */
extern uint32_t opencfw_em9305_dispatch_3305ac(uintptr_t request,uintptr_t input); /* native 0x3305ac */
extern void opencfw_em9305_dispatch_331dc0(void); /* native 0x331dc0, ABI not qualified */
extern uint32_t opencfw_em9305_dispatch_331ec0(uintptr_t); /* native packet ABI */
extern uint32_t opencfw_em9305_dispatch_331f5c(uintptr_t); /* native packet ABI */
extern uint32_t opencfw_em9305_dispatch_332038(uintptr_t,uintptr_t); /* native request/input ABI */
extern uint32_t opencfw_em9305_dispatch_332194(uintptr_t,uintptr_t); /* native command ABI */
extern uint32_t opencfw_em9305_dispatch_332200(uintptr_t); /* native packet ABI */
/* Native 0x30a70c. */
uint32_t opencfw_em9305_ll_seed_30a70c(void)
{
 *(volatile uint32_t *)(uintptr_t)0x8057d8u=(uint32_t)(uintptr_t)&opencfw_em9305_dispatch_331ec0;
 *(volatile uint32_t *)(uintptr_t)0x805748u=(uint32_t)(uintptr_t)&opencfw_em9305_dispatch_331dc0;
 return 0x805748u;
}
/* Native 0x30a72c. */
uint32_t opencfw_em9305_ll_seed_30a72c(void)
{
 *(volatile uint32_t *)(uintptr_t)0x8057fcu=(uint32_t)(uintptr_t)&opencfw_em9305_dispatch_32ff20;
 *(volatile uint32_t *)(uintptr_t)0x80576cu=(uint32_t)(uintptr_t)&opencfw_em9305_dispatch_32fea4;
 return 0x80576cu;
}
/* Native 0x30a74c. */
uint32_t opencfw_em9305_ll_seed_30a74c(void)
{
 *(volatile uint32_t *)(uintptr_t)0x805800u=(uint32_t)(uintptr_t)&opencfw_em9305_dispatch_331f5c;
 *(volatile uint32_t *)(uintptr_t)0x805770u=(uint32_t)(uintptr_t)&opencfw_em9305_dispatch_332038;
 return 0x805770u;
}
/* Native 0x30a77c. */
uint32_t opencfw_em9305_ll_seed_30a77c(void)
{
 *(volatile uint32_t *)(uintptr_t)0x8057f4u=(uint32_t)(uintptr_t)&opencfw_em9305_dispatch_330400;
 *(volatile uint32_t *)(uintptr_t)0x805764u=(uint32_t)(uintptr_t)&opencfw_em9305_dispatch_3300c8;
 return 0x805764u;
}
/* Native 0x30a79c. */
uint32_t opencfw_em9305_ll_seed_30a79c(void)
{
 *(volatile uint32_t *)(uintptr_t)0x8057f8u=(uint32_t)(uintptr_t)&opencfw_em9305_dispatch_332200;
 *(volatile uint32_t *)(uintptr_t)0x805768u=(uint32_t)(uintptr_t)&opencfw_em9305_dispatch_332194;
 return 0x805768u;
}
/* Native 0x30a840. */
uint32_t opencfw_em9305_ll_seed_30a840(void)
{
 *(volatile uint32_t *)(uintptr_t)0x8057c8u=(uint32_t)(uintptr_t)&opencfw_em9305_dispatch_3305ac;
 *(volatile uint32_t *)(uintptr_t)0x805738u=(uint32_t)(uintptr_t)&opencfw_em9305_dispatch_330568;
 return 0x805738u;
}
/* Native 0x30a76c..0x30a77c. */
uint32_t opencfw_em9305_ll_seed_30a76c(void)
{
 *(volatile uint32_t *)(uintptr_t)0x8057c4u=(uint32_t)(uintptr_t)&opencfw_em9305_dispatch_32eec8;
 return 0x8057c4u;
}

extern uintptr_t opencfw_em9305_ll_event_allocate(uint32_t,uint32_t); /*0x32e454*/
extern uintptr_t opencfw_em9305_wsf_pool_allocate(uint32_t); /*0x313ce0*/
/* Native0x313fd8..0x313ff0: 16-bit total allocation and eight-byte header. */
uintptr_t opencfw_em9305_wsf_event_allocate(uint32_t bytes)
{
 uintptr_t node=opencfw_em9305_wsf_pool_allocate((uint16_t)(bytes+8u));
 return node!=0u ? node+8u : 0u;
}
/* Native0x32e454..0x32e470: type/length header before returned payload. */
uintptr_t opencfw_em9305_ll_event_allocate(uint32_t type,uint32_t bytes)
{
 uintptr_t event=opencfw_em9305_wsf_event_allocate(bytes+2u);
 if (event==0u) return 0u;
 *(volatile uint8_t *)(event+1u)=(uint8_t)bytes;
 *(volatile uint8_t *)event=(uint8_t)type;
 return event+2u;
}
extern uint32_t opencfw_em9305_ll_event_send(uintptr_t); /*0x30ae90*/
extern uint32_t opencfw_em9305_ll_event_enqueue(uintptr_t,uint32_t,uintptr_t); /*0x314008*/
/* Native0x31416c..0x314190: singly linked queue append under WSF guard. */
uint32_t opencfw_em9305_wsf_queue_append(uintptr_t queue,uintptr_t node)
{
 *(volatile uint32_t *)node=0u; /* native delay slot before enter call */
 (void)opencfw_em9305_wsf_critical_enter();
 uint32_t head=*(volatile uint32_t *)queue;
 if (head!=0u) {
  uintptr_t tail=*(volatile uint32_t *)(queue+4u);
  *(volatile uint32_t *)(queue+4u)=(uint32_t)node;
  *(volatile uint32_t *)tail=(uint32_t)node;
 } else {
  *(volatile uint32_t *)(queue+4u)=(uint32_t)node;
  *(volatile uint32_t *)queue=(uint32_t)node;
 }
 return opencfw_em9305_wsf_critical_exit();
}
/* Native0x314008..0x314014: handler byte and eight-byte header adjustment. */
uint32_t opencfw_em9305_ll_event_enqueue(uintptr_t queue,uint32_t handler,uintptr_t event)
{
 *(volatile uint8_t *)(event-4u)=(uint8_t)handler;
 return opencfw_em9305_wsf_queue_append(queue,event-8u);
}
extern uint32_t opencfw_em9305_ll_event_kick(uint32_t); /*0x3047c0*/
uint32_t opencfw_em9305_ll_event_send(uintptr_t event)
{
 if (event!=0u) (void)opencfw_em9305_ll_event_enqueue(0x805870u,0u,event);
 uint32_t flag=*(volatile uint8_t *)(uintptr_t)0x805884u;
 if (flag==0u) return opencfw_em9305_ll_event_kick(0u);
 return flag;
}
/* Native0x32eec8..0x32ef10: gated four-byte event, ST.AB stores use old base. */
uint32_t opencfw_em9305_dispatch_32eec8(uintptr_t event)
{
 if (*(volatile uint8_t *)(event+2u)!=0x21u) return 0u;
 if ((*(volatile uint8_t *)(uintptr_t)0x8056fau&8u)==0u) return 0u;
 if ((*(volatile uint8_t *)(uintptr_t)0x8056efu&32u)==0u) return 0u;
 uintptr_t payload=opencfw_em9305_ll_event_allocate(0x3eu,4u);
 if (payload==0u) return 0u;
 *(volatile uint8_t *)payload=20u;payload+=1u;
 *(volatile uint8_t *)payload=*(volatile uint8_t *)(event+4u);payload+=1u;
 *(volatile uint8_t *)payload=*(volatile uint8_t *)(event+5u);payload+=1u;
 *(volatile uint8_t *)payload=*(volatile uint8_t *)(event+6u);payload-=5u;
 (void)opencfw_em9305_ll_event_send(payload);
 return 1u;
}

/* Native0x313ce0..0x313d98: first fitting pool, exact optional statistics. */
uintptr_t opencfw_em9305_wsf_pool_allocate(uint32_t requested)
{
 uint32_t remaining=*(volatile uint8_t *)(uintptr_t)0x805ff0u;
 uintptr_t pool=*(volatile uint32_t *)(uintptr_t)0x805fe8u;
 while (remaining!=0u) {
  uint32_t capacity=*(volatile uint16_t *)pool;
  if (capacity>=requested) {
   (void)opencfw_em9305_wsf_critical_enter();
   uintptr_t node=*(volatile uint32_t *)(pool+8u);
   uintptr_t product=*(volatile uint32_t *)(uintptr_t)0x805cacu;
   uint32_t stats;
   if (node!=0u) {
    uint32_t allocations=*(volatile uint32_t *)(uintptr_t)0x806070u;
    uint32_t next=*(volatile uint32_t *)node;
    stats=*(volatile uint8_t *)(product+75u);
    *(volatile uint32_t *)(node+4u)=0u;
    *(volatile uint32_t *)(pool+8u)=next;
    *(volatile uint32_t *)(uintptr_t)0x806070u=allocations+1u;
    if (stats!=0u) {
     uintptr_t histogram=*(volatile uint32_t *)(uintptr_t)0x805fe4u;
     if (histogram!=0u) {
      uintptr_t entry=histogram+(requested<=127u ? requested : 0u);
      uint32_t count=*(volatile uint8_t *)entry;
      *(volatile uint8_t *)entry=(uint8_t)(count+1u);
     }
     uint32_t used=*(volatile uint8_t *)(pool+12u);
     uint32_t peak=*(volatile uint8_t *)(pool+13u);
     used+=1u;
     *(volatile uint8_t *)(pool+12u)=(uint8_t)used;
     if (peak<(uint8_t)used) *(volatile uint8_t *)(pool+13u)=(uint8_t)used;
    }
    uint32_t largest=*(volatile uint16_t *)(pool+14u);
    __asm__ volatile("max %0,%0,%1" : "+r"(largest) : "r"(requested));
    *(volatile uint16_t *)(pool+14u)=(uint16_t)largest;
    (void)opencfw_em9305_wsf_critical_exit();
    return node;
   }
   stats=*(volatile uint8_t *)(product+75u);
   if (stats!=0u) {
    uintptr_t misses=*(volatile uint32_t *)(uintptr_t)0x806074u;
    if (misses!=0u) {
     uint32_t total=*(volatile uint8_t *)(uintptr_t)0x805ff0u;
     uintptr_t entry=misses+total-remaining;
     uint32_t count=*(volatile uint8_t *)entry;
     *(volatile uint8_t *)entry=(uint8_t)(count+1u);
    }
   }
   (void)opencfw_em9305_wsf_critical_exit();
  }
  remaining-=1u;pool+=16u;
 }
 return 0u;
}


/* Native0x313d98..0x313dfc: reverse pool search and free-list prepend. */
uint32_t opencfw_em9305_wsf_pool_release(uintptr_t node)
{
 uint32_t count=*(volatile uint8_t *)(uintptr_t)0x805ff0u;
 if (count==0u) return (uint32_t)node;
 uint32_t base=*(volatile uint32_t *)(uintptr_t)0x805fe8u;
 uint32_t pool=base+(count<<4)-16u;
 uint32_t boundary;
 for (;;) {
  boundary=*(volatile uint32_t *)(uintptr_t)(pool+4u);
  if ((uint32_t)node>=boundary) break;
  pool-=16u;
  if (pool<base) return boundary;
 }
 (void)opencfw_em9305_wsf_critical_enter();
 uintptr_t product=*(volatile uint32_t *)(uintptr_t)0x805cacu;
 *(volatile uint32_t *)(node+4u)=0xfaabd00du;
 uint32_t stats=*(volatile uint8_t *)(product+75u);
 if (stats!=0u) {
  uint32_t used=*(volatile uint8_t *)(uintptr_t)(pool+12u);
  *(volatile uint8_t *)(uintptr_t)(pool+12u)=(uint8_t)(used-1u);
 }
 uint32_t outstanding=*(volatile uint32_t *)(uintptr_t)0x806070u;
 uint32_t next=*(volatile uint32_t *)(uintptr_t)(pool+8u);
 *(volatile uint32_t *)(uintptr_t)(pool+8u)=(uint32_t)node;
 *(volatile uint32_t *)node=next;
 *(volatile uint32_t *)(uintptr_t)0x806070u=outstanding-1u;
 return opencfw_em9305_wsf_critical_exit();
}
/* Native0x314014..0x31401c: remove the eight-byte allocation header. */
uint32_t opencfw_em9305_wsf_event_release(uintptr_t event)
{ return opencfw_em9305_wsf_pool_release(event-8u); }

/* Native0x314134..0x314154: remove queue head under WSF protection. */
uintptr_t opencfw_em9305_wsf_queue_remove(uintptr_t queue)
{
 (void)opencfw_em9305_wsf_critical_enter();
 uintptr_t node=*(volatile uint32_t *)queue;
 if (node!=0u) {
  uint32_t next=*(volatile uint32_t *)node;
  *(volatile uint32_t *)queue=next;
  if (next==0u) *(volatile uint32_t *)(queue+4u)=0u;
 }
 (void)opencfw_em9305_wsf_critical_exit();
 return node;
}
/* Native0x314154..0x31416c. */
uint32_t opencfw_em9305_wsf_queue_empty(uintptr_t queue)
{
 (void)opencfw_em9305_wsf_critical_enter();
 uint32_t empty=*(volatile uint32_t *)queue==0u;
 (void)opencfw_em9305_wsf_critical_exit();
 return empty;
}
/* Native0x313ff0..0x314008. Handler output untouched on empty queue. */
uintptr_t opencfw_em9305_wsf_event_remove(uintptr_t queue,uintptr_t handler)
{
 uintptr_t node=opencfw_em9305_wsf_queue_remove(queue);
 if (node==0u) return 0u;
 uint8_t value=*(volatile uint8_t *)(node+4u);
 *(volatile uint8_t *)handler=value;
 return node+8u;
}
/* Native0x31403c..0x31404c: unprotected head inspection. */
uintptr_t opencfw_em9305_wsf_event_peek(uintptr_t queue,uintptr_t handler)
{
 uintptr_t node=*(volatile uint32_t *)queue;
 if (node==0u) return 0u;
 uint8_t value=*(volatile uint8_t *)(node+4u);
 *(volatile uint8_t *)handler=value;
 return node+8u;
}

/* Native0x3141c8..0x3141e4: nested-safe queue prepend. */
uint32_t opencfw_em9305_wsf_queue_prepend(uintptr_t queue,uintptr_t node)
{
 (void)opencfw_em9305_wsf_critical_enter();
 uint32_t head=*(volatile uint32_t *)queue;
 *(volatile uint32_t *)node=head;
 if (head==0u) *(volatile uint32_t *)(queue+4u)=(uint32_t)node;
 *(volatile uint32_t *)queue=(uint32_t)node;
 return opencfw_em9305_wsf_critical_exit();
}
/* Native0x314190..0x3141c8: insert after predecessor, with native nested guards. */
uint32_t opencfw_em9305_wsf_queue_insert(uintptr_t queue,uintptr_t node,uintptr_t previous)
{
 (void)opencfw_em9305_wsf_critical_enter();
 uint32_t head=*(volatile uint32_t *)queue;
 if (head==0u) (void)opencfw_em9305_wsf_queue_append(queue,node);
 else {
  uintptr_t tail=*(volatile uint32_t *)(queue+4u);
  if (tail==previous) (void)opencfw_em9305_wsf_queue_append(queue,node);
  else if (previous==0u) (void)opencfw_em9305_wsf_queue_prepend(queue,node);
  else {
   uint32_t next=*(volatile uint32_t *)previous;
   *(volatile uint32_t *)node=next;
   *(volatile uint32_t *)previous=(uint32_t)node;
  }
 }
 return opencfw_em9305_wsf_critical_exit();
}
/* Native0x31401c..0x31403c: byte-sized index, no critical guard. */
uintptr_t opencfw_em9305_wsf_event_at(uintptr_t queue,uint32_t index,uintptr_t handler)
{
 uintptr_t node=*(volatile uint32_t *)queue;
 while ((uint8_t)index!=0u && node!=0u) {
  index-=1u;
  node=*(volatile uint32_t *)node;
 }
 if (node==0u) return 0u;
 uint8_t value=*(volatile uint8_t *)(node+4u);
 *(volatile uint8_t *)handler=value;
 return node+8u;
}

/* Native0x3141e4..0x314210: caller-supplied node/predecessor, no membership scan. */
uint32_t opencfw_em9305_wsf_queue_unlink(uintptr_t queue,uintptr_t node,uintptr_t previous)
{
 (void)opencfw_em9305_wsf_critical_enter();
 uintptr_t head=*(volatile uint32_t *)queue;
 if (head==node) {
  uint32_t next=*(volatile uint32_t *)node;
  *(volatile uint32_t *)queue=next;
 } else if (previous!=0u) {
  uint32_t next=*(volatile uint32_t *)node;
  *(volatile uint32_t *)previous=next;
 }
 uintptr_t tail=*(volatile uint32_t *)(queue+4u);
 if (tail==node) *(volatile uint32_t *)(queue+4u)=(uint32_t)previous;
 return opencfw_em9305_wsf_critical_exit();
}
extern uint32_t opencfw_em9305_wsf_wake_lower(uint32_t); /*0x333d18*/
extern uintptr_t opencfw_em9305_qpc_event_allocate(uint32_t,uint32_t,uint32_t); /*0x311060*/
/* Native0x333d18..0x333d7c: wake event posting and protected wake counter. */
uint32_t opencfw_em9305_wsf_wake_lower(uint32_t incoming)
{
 (void)incoming;
 uint32_t irq;
 __asm__ volatile("clri %0\n\tsync" : "=r"(irq) :: "memory");
 uint32_t depth=*(volatile uint8_t *)(uintptr_t)0x801398u;
 *(volatile uint8_t *)(uintptr_t)0x801398u=(uint8_t)(depth+1u);
 __asm__ volatile("seti %0" :: "r"(irq) : "memory");
 uintptr_t event=opencfw_em9305_qpc_event_allocate(8u,0xffffu,8u);
 uintptr_t dispatch_table=*(volatile uint32_t *)(uintptr_t)0x80139cu;
 *(volatile uint32_t *)(event+4u)=0u;
 uintptr_t callback=*(volatile uint32_t *)(dispatch_table+12u);
 (void)((uint32_t (*)(uintptr_t,uintptr_t,uint32_t))callback)(0x80139cu,event,0xffffu);
 __asm__ volatile("clri %0\n\tsync" : "=r"(irq) :: "memory");
 depth=*(volatile uint8_t *)(uintptr_t)0x801398u;
 if (depth!=0u) {
  depth=*(volatile uint8_t *)(uintptr_t)0x801398u;
  depth-=1u;
  *(volatile uint8_t *)(uintptr_t)0x801398u=(uint8_t)depth;
 }
 *(volatile uint32_t *)(uintptr_t)0xf00a80u=1u;
 __asm__ volatile("seti %0" :: "r"(irq) : "memory");
 return depth;
}
/* Native0x314210..0x31424c: handler event bits plus scheduler wake flag. */
uint32_t opencfw_em9305_wsf_event_post(uint32_t handler,uint32_t events)
{
 (void)opencfw_em9305_wsf_critical_enter();
 uint32_t index=handler&15u;
 uintptr_t cell=0x806034u+index*2u;
 uint32_t bits=*(volatile uint16_t *)cell;
 uint32_t previous=*(volatile uint8_t *)(uintptr_t)0x80605cu;
 bits|=events;
 *(volatile uint16_t *)cell=(uint16_t)bits;
 *(volatile uint8_t *)(uintptr_t)0x80605cu=(uint8_t)(previous|4u);
 uint32_t result=opencfw_em9305_wsf_critical_exit();
 if (previous==0u) return opencfw_em9305_wsf_wake_lower(result);
 return result;
}

extern void opencfw_em9305_assert(uint32_t,uint32_t);
extern uintptr_t opencfw_em9305_qpc_pool_get(uintptr_t,uint32_t); /*0x31166c*/
/* Native0x311060..0x3110f4: first fitting QP pool and event header fields.
 * The returning assertion callback is retained; no invented fault policy. */
uintptr_t opencfw_em9305_qpc_event_allocate(uint32_t bytes,uint32_t margin,uint32_t signal)
{
 uint32_t count=*(volatile uint8_t *)(uintptr_t)0x801360u;
 uint32_t index=0u;
 for (;index<count;index++) {
  uint32_t capacity=*(volatile uint16_t *)(uintptr_t)(0x801374u+20u*index);
  if (capacity>=bytes) break;
 }
 if (index==count) opencfw_em9305_assert(0x334520u,310u);
 uint32_t required=margin==0xffffu ? 0u : margin;
 uintptr_t event=opencfw_em9305_qpc_pool_get(0x801368u+index*20u,required);
 if (event!=0u) {
  *(volatile uint8_t *)(event+3u)=0u;
  *(volatile uint16_t *)event=(uint16_t)signal;
  *(volatile uint8_t *)(event+2u)=(uint8_t)(index+1u);
 } else if (margin==0xffffu) opencfw_em9305_assert(0x334520u,320u);
 return event;
}

/* Native0x31166c..0x3116f4: IRQ-protected pool pop with returning assertions. */
uintptr_t opencfw_em9305_qpc_pool_get(uintptr_t pool,uint32_t margin)
{
 uint32_t irq;
 __asm__ volatile("clri %0\n\tsync" : "=r"(irq) :: "memory");
 uint32_t available=*(volatile uint16_t *)(pool+16u);
 uintptr_t node=0u;
 if ((uint16_t)margin<available) {
  node=*(volatile uint32_t *)pool;
  if (node==0u) {
   __asm__ volatile("seti %0" :: "r"(irq) : "memory");
   opencfw_em9305_assert(0x334540u,310u);
  }
  uintptr_t next=*(volatile uint32_t *)node;
  available=*(volatile uint16_t *)(pool+16u);
  *(volatile uint16_t *)(pool+16u)=(uint16_t)(available-1u);
  available=*(volatile uint16_t *)(pool+16u);
  if (available!=0u) {
   uintptr_t first=*(volatile uint32_t *)(pool+4u);
   uint32_t valid=next>=first;
   if (valid!=0u) {
    uintptr_t last=*(volatile uint32_t *)(pool+8u);
    valid=last>=next;
   }
   if (valid==0u) {
    __asm__ volatile("seti %0" :: "r"(irq) : "memory");
    opencfw_em9305_assert(0x334540u,330u);
   }
   available=*(volatile uint16_t *)(pool+16u);
   uint32_t minimum=*(volatile uint16_t *)(pool+18u);
   if (available<minimum) {
    available=*(volatile uint16_t *)(pool+16u);
    *(volatile uint16_t *)(pool+18u)=(uint16_t)available;
   }
  } else {
   if (next!=0u) {
    __asm__ volatile("seti %0" :: "r"(irq) : "memory");
    opencfw_em9305_assert(0x334540u,320u);
   }
   *(volatile uint16_t *)(pool+18u)=0u;
  }
  *(volatile uint32_t *)pool=(uint32_t)next;
 }
 __asm__ volatile("seti %0" :: "r"(irq) : "memory");
 return node;
}

/* Native0x3116f4..0x311798: four-byte granularity QP pool chain. */
uint32_t opencfw_em9305_qpc_pool_initialize(uintptr_t pool,uintptr_t storage,uint32_t bytes,uint32_t block)
{
 if (storage==0u || bytes<4u || block>=0xfffffffcu)
  opencfw_em9305_assert(0x334540u,100u);
 uint32_t stride=4u,words=1u,count=1u;
 *(volatile uint16_t *)(pool+12u)=4u;
 *(volatile uint32_t *)pool=(uint32_t)storage;
 if ((uint16_t)block>=5u) {
  uint32_t rounds=(((block-5u)&0xfffcu)>>2)+1u;
  stride+=rounds*4u;words+=rounds;
  *(volatile uint16_t *)(pool+12u)=(uint16_t)stride;
 }
 if (bytes<stride) opencfw_em9305_assert(0x334540u,110u);
 *(volatile uint16_t *)(pool+14u)=1u;
 uint32_t remainder=bytes-stride;
 uintptr_t node=*(volatile uint32_t *)pool;
 if (remainder>=stride) {
  uint32_t numerator=bytes-(stride<<1);
  uint32_t links;
  __asm__ volatile("divu %0,%1,%2" : "=r"(links) : "r"(numerator),"r"(stride));
  links+=1u;
  do {
   uintptr_t next=node+(words<<2);
   count+=1u;
   *(volatile uint32_t *)node=(uint32_t)next;
   *(volatile uint16_t *)(pool+14u)=(uint16_t)count;
   node=*(volatile uint32_t *)node;
  } while (--links!=0u);
  remainder=0u;
 }
 *(volatile uint32_t *)node=0u;
 *(volatile uint16_t *)(pool+18u)=(uint16_t)count;
 *(volatile uint32_t *)(pool+8u)=(uint32_t)node;
 *(volatile uint32_t *)(pool+4u)=(uint32_t)storage;
 *(volatile uint16_t *)(pool+16u)=(uint16_t)count;
 return remainder;
}

/* Native0x314250..0x314258: task-handler SRAM table address. */
uintptr_t opencfw_em9305_wsf_task_handlers(void) { return 0x806054u; }
/* Native0x314258..0x31427c: events are incoming R1, not incoming R0. */
uint32_t opencfw_em9305_wsf_task_event_post(uint32_t incoming,uint32_t events)
{
 (void)incoming;
 (void)opencfw_em9305_wsf_critical_enter();
 uint32_t previous=*(volatile uint8_t *)(uintptr_t)0x80605cu;
 *(volatile uint8_t *)(uintptr_t)0x80605cu=(uint8_t)(events|previous);
 uint32_t result=opencfw_em9305_wsf_critical_exit();
 if (previous==0u) return opencfw_em9305_wsf_wake_lower(result);
 return result;
}

/* Native0x3142a0..0x3142c8: first timer delta and caller presence byte. */
uint32_t opencfw_em9305_wsf_timer_next(uintptr_t present)
{
 (void)opencfw_em9305_wsf_critical_enter();
 uintptr_t timer=*(volatile uint32_t *)(uintptr_t)0x806078u;
 uint32_t delta=0u;
 if (timer!=0u) {
  delta=*(volatile uint32_t *)(timer+8u);
  *(volatile uint8_t *)present=1u;
 } else *(volatile uint8_t *)present=0u;
 (void)opencfw_em9305_wsf_critical_exit();
 return delta;
}
/* Native0x3142c8..0x3142f8: only dequeue zero-delta head, nested IRQ guards. */
uintptr_t opencfw_em9305_wsf_timer_expired(void)
{
 (void)opencfw_em9305_wsf_critical_enter();
 uintptr_t timer=*(volatile uint32_t *)(uintptr_t)0x806078u;
 if (timer==0u || *(volatile uint32_t *)(timer+8u)!=0u) {
  (void)opencfw_em9305_wsf_critical_exit();
  return 0u;
 }
 (void)opencfw_em9305_wsf_queue_unlink(0x806078u,timer,0u);
 *(volatile uint8_t *)(timer+13u)=0u;
 (void)opencfw_em9305_wsf_critical_exit();
 return timer;
}

extern uint32_t opencfw_em9305_wsf_timer_stop_lower(uintptr_t); /*0x333e24*/
/* Native0x314314..0x314328: timer removal under scheduler critical guard. */
uint32_t opencfw_em9305_wsf_timer_stop(uintptr_t timer)
{
 (void)opencfw_em9305_wsf_critical_enter();
 (void)opencfw_em9305_wsf_timer_stop_lower(timer);
 return opencfw_em9305_wsf_critical_exit();
}
/* Native0x31424c and0x31427c are real tail aliases. */
uint32_t opencfw_em9305_wsf_scheduler_lock(void)
{ return opencfw_em9305_wsf_critical_enter(); }
uint32_t opencfw_em9305_wsf_scheduler_unlock(void)
{ return opencfw_em9305_wsf_critical_exit(); }

/* Native0x333e24..0x333e4c: pointer search, unlink and running-byte clear. */
uint32_t opencfw_em9305_wsf_timer_stop_lower(uintptr_t timer)
{
 uintptr_t previous=0u,current=*(volatile uint32_t *)(uintptr_t)0x806078u;
 while (current!=0u) {
  if (current==timer) {
   uint32_t result=opencfw_em9305_wsf_queue_unlink(0x806078u,timer,previous);
   *(volatile uint8_t *)(timer+13u)=0u;
   return result;
  }
  previous=current;
  current=*(volatile uint32_t *)current;
 }
 return 0x806078u;
}

/* Native0x333dcc..0x333e24: sorted timer insertion, equal deltas remain ordered. */
uint32_t opencfw_em9305_wsf_timer_start_ticks(uintptr_t timer,uint32_t ticks)
{
 (void)opencfw_em9305_wsf_critical_enter();
 if (*(volatile uint8_t *)(timer+13u)!=0u)
  (void)opencfw_em9305_wsf_timer_stop_lower(timer);
 uintptr_t current=*(volatile uint32_t *)(uintptr_t)0x806078u;
 *(volatile uint32_t *)(timer+8u)=ticks;
 *(volatile uint8_t *)(timer+13u)=1u;
 uintptr_t previous=0u;
 if (current!=0u) {
  while (current!=0u) {
   uint32_t pending=*(volatile uint32_t *)(current+8u);
   if (ticks<pending) break;
   previous=current;
   current=*(volatile uint32_t *)current;
  }
 } else {
  uint32_t now=opencfw_em9305_pal_current_time();
  *(volatile uint32_t *)(uintptr_t)0x8019f4u=now;
 }
 (void)opencfw_em9305_wsf_queue_insert(0x806078u,timer,previous);
 return opencfw_em9305_wsf_critical_exit();
}
/* Native0x3142f8..0x314304: wrapping rounding to ten-unit ticks. */
uint32_t opencfw_em9305_wsf_timer_start_ms(uintptr_t timer,uint32_t time)
{
 return opencfw_em9305_wsf_timer_start_ticks(timer,(time+9u)/10u);
}

/* Native0x314328..0x31435c: update every timer and post task bit2 at expiry. */
uint32_t opencfw_em9305_wsf_timer_update(uint32_t elapsed)
{
 (void)opencfw_em9305_wsf_critical_enter();
 uintptr_t timer=*(volatile uint32_t *)(uintptr_t)0x806078u;
 while (timer!=0u) {
  uint32_t pending=*(volatile uint32_t *)(timer+8u);
  if (elapsed<pending) *(volatile uint32_t *)(timer+8u)=pending-elapsed;
  else {
   uint32_t handler=*(volatile uint8_t *)(timer+12u);
   *(volatile uint32_t *)(timer+8u)=0u;
   (void)opencfw_em9305_wsf_task_event_post(handler,2u);
  }
  timer=*(volatile uint32_t *)timer;
 }
 return opencfw_em9305_wsf_critical_exit();
}

extern uint32_t opencfw_em9305_native_clock_product(uint32_t,uint32_t);
/* Native0x3100f0..0x3100f8: wrapping difference then unsigned DIVU1000. */
uint32_t opencfw_em9305_pal_elapsed(uint32_t current,uint32_t previous)
{ return (current-previous)/1000u; }
/* Native0x333dc4..0x333dcc: alarm callback posts task event2. */
uint32_t opencfw_em9305_wsf_alarm_callback(void)
{ return opencfw_em9305_wsf_task_event_post(0u,2u); }
/* Native0x3101c0..0x3101e4: alarm time and source callback pointer. */
uint32_t opencfw_em9305_pal_alarm(uint32_t offset,uintptr_t callback)
{
 uint32_t now=*(volatile uint32_t *)(uintptr_t)0xf01808u;
 *(volatile uint32_t *)(uintptr_t)0xf01828u=offset+now;
 (void)opencfw_em9305_pal_timer_channel(3u,1u);
 *(volatile uint32_t *)(uintptr_t)0x805e74u=(uint32_t)callback;
 return 0x805e74u;
}
/* Native0x333e4c..0x333e9c: coarse elapsed update then next alarm.
 * Custom major6/minor1c products retain native opcode, not guessed multiply. */
uint32_t opencfw_em9305_wsf_timer_periodic(void)
{
 uint32_t now=opencfw_em9305_pal_current_time();
 uint32_t previous=*(volatile uint32_t *)(uintptr_t)0x8019f4u;
 uint32_t elapsed=opencfw_em9305_pal_elapsed(now,previous);
 if (elapsed>=11u) {
  uint32_t ticks=elapsed/10u;
  uint32_t step=opencfw_em9305_native_clock_product(ticks*10u,1000u);
  previous=*(volatile uint32_t *)(uintptr_t)0x8019f4u;
  *(volatile uint32_t *)(uintptr_t)0x8019f4u=step+previous;
  (void)opencfw_em9305_wsf_timer_update(ticks);
 }
 uint8_t present;
 uint32_t next=opencfw_em9305_wsf_timer_next((uintptr_t)&present);
 if (next!=0u) {
  uint32_t offset=opencfw_em9305_native_clock_product(next,10000u);
  return opencfw_em9305_pal_alarm(offset,(uintptr_t)&opencfw_em9305_wsf_alarm_callback);
 }
 return next;
}

/* Native0x3101b8..0x3101c0: native custom-product adapter, no arithmetic guess. */
uint32_t opencfw_em9305_pal_time_scale(uint32_t value)
{ return opencfw_em9305_native_clock_product(value,1000u); }
/* Native0x314304..0x314314: custom-product, wrapping+9, DIVU10. */
uint32_t opencfw_em9305_wsf_timer_start_seconds(uintptr_t timer,uint32_t time)
{
 uint32_t scaled=opencfw_em9305_native_clock_product(time,1000u);
 return opencfw_em9305_wsf_timer_start_ticks(timer,(scaled+9u)/10u);
}
/* Native0x3100f8..0x3100fc. */
uint32_t opencfw_em9305_pal_elapsed_raw(uint32_t current,uint32_t previous)
{ return current-previous; }
/* Native0x3100fc..0x310104: channel0 disable tail. */
uint32_t opencfw_em9305_pal_timer_disarm(void)
{ return opencfw_em9305_pal_timer_channel(0u,0u); }

/* Native0x3108d0..0x3108e8: shift, mask, then byte-truncated truth value. */
uint32_t opencfw_em9305_pal_timer_channel_enabled(uint32_t index)
{
 uint32_t bits=*(volatile uint32_t *)(uintptr_t)0xf01818u;
 uint32_t mask=1u;
 __asm__ volatile("asl %0,%0,%1" : "+r"(mask) : "r"(index));
 return (uint8_t)(bits&mask)!=0u;
}
/* Native0x3108e8..0x3108f4. */
uint32_t opencfw_em9305_pal_timer_divisor(void)
{ return *(volatile uint8_t *)(uintptr_t)0xf01804u+1u; }
/* Native0x3108f4..0x310900: product config read remains real SRAM. */
uint32_t opencfw_em9305_pal_timer_configuration(void)
{ return *(volatile uint32_t *)(uintptr_t)0x801998u; }

/* Native0x310914..0x310944: repeated pointer reads and old-base byte stores. */
uint32_t opencfw_em9305_pal_metadata_reset(void)
{
 uintptr_t object=*(volatile uint32_t *)(uintptr_t)0x80fd2cu;
 *(volatile uint32_t *)(object+76u)=2u;
 object=*(volatile uint32_t *)(uintptr_t)0x80fd2cu;
 *(volatile uint32_t *)(object+4u)=0u;
 object=*(volatile uint32_t *)(uintptr_t)0x80fd2cu;
 *(volatile uint32_t *)(object+68u)=0u;
 *(volatile uint8_t *)(uintptr_t)0xf01804u=0u;
 *(volatile uint8_t *)(uintptr_t)0xf01805u=1u;
 *(volatile uint8_t *)(uintptr_t)0xf01806u=1u;
 *(volatile uint32_t *)(uintptr_t)0xf01810u=UINT32_MAX;
 return (uint32_t)object;
}
/* Native0x310944..0x310990: append unique node under captured IRQ state. */
uint32_t opencfw_em9305_pal_metadata_register(uintptr_t node)
{
 if (node==0u) return 0u;
 uint32_t irq;
 __asm__ volatile("clri %0\n\tsync" : "=r"(irq) :: "memory");
 uintptr_t current=*(volatile uint32_t *)(uintptr_t)0x801998u;
 if (current==0u) {
  *(volatile uint32_t *)(node+4u)=0u;
  *(volatile uint32_t *)(uintptr_t)0x801998u=(uint32_t)node;
 } else {
  for (;;) {
   if (current==node) {
    __asm__ volatile("seti %0" :: "r"(irq) : "memory");
    return 0u;
   }
   uintptr_t next=*(volatile uint32_t *)(current+4u);
   if (next==0u) break;
   current=next;
  }
  *(volatile uint32_t *)(current+4u)=(uint32_t)node;
  *(volatile uint32_t *)(node+4u)=0u;
 }
 __asm__ volatile("seti %0" :: "r"(irq) : "memory");
 return 1u;
}

extern uint32_t opencfw_em9305_controller_transport_configure(uint32_t,uint32_t,uint32_t); /*0x304764*/
extern uint32_t opencfw_em9305_controller_transport_callbacks(uint32_t,uintptr_t,uintptr_t,uintptr_t); /*0x3047d4*/
extern uint32_t opencfw_em9305_dispatch_331a40(uint32_t,uintptr_t); /*native R0 type/R1 event*/
extern uint32_t opencfw_em9305_dispatch_331c20(uint32_t,uintptr_t); /*native R0 type/R1 event*/
extern uint32_t opencfw_em9305_dispatch_331cdc(uintptr_t,uintptr_t,uintptr_t); /*type/length/packet outputs*/
/* Native0x310798..0x3107dc: guarded transport restore and callback reinstall. */
uint32_t opencfw_em9305_pal_resume_dispatch(void)
{
 uint32_t state=*(volatile uint8_t *)(uintptr_t)0x805ed8u;
 if (state!=1u) return state;
 uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
 uint32_t mode=*(volatile uint8_t *)(uintptr_t)0x801864u;
 uint32_t second=*(volatile uint16_t *)(config+44u);
 uint32_t first=*(volatile uint16_t *)(config+38u);
 (void)opencfw_em9305_controller_transport_configure(mode,first,second);
 return opencfw_em9305_controller_transport_callbacks(0u,
  (uintptr_t)&opencfw_em9305_dispatch_331a40,
  (uintptr_t)&opencfw_em9305_dispatch_331c20,
  (uintptr_t)&opencfw_em9305_dispatch_331cdc);
}

/* Native0x3047d4..0x3047f0: five callback triplets, reverse field store order. */
uint32_t opencfw_em9305_controller_transport_callbacks(uint32_t index,uintptr_t first,uintptr_t second,uintptr_t third)
{
 if (index>4u) return index;
 uintptr_t row=0x801880u+index*12u;
 *(volatile uint32_t *)(row+8u)=(uint32_t)third;
 *(volatile uint32_t *)(row+4u)=(uint32_t)second;
 *(volatile uint32_t *)row=(uint32_t)first;
 return (uint32_t)row;
}
/* Native0x3047f0..0x3047fc. */
uint32_t opencfw_em9305_controller_transport_hook(uintptr_t callback)
{
 *(volatile uint32_t *)(uintptr_t)0x80187cu=(uint32_t)callback;
 return (uint32_t)callback;
}

/* Native0x3110f4..0x31114c: timer IRQ hooks, virtual callback and wake count. */
uint32_t opencfw_em9305_controller_timer_irq(void)
{
 *(volatile uint32_t *)(uintptr_t)0xf00a74u=3u;
 uintptr_t callback=*(volatile uint32_t *)(uintptr_t)0x80fe08u;
 if (callback!=0u) (void)((uint32_t (*)(uintptr_t))callback)(callback);
 callback=*(volatile uint32_t *)(uintptr_t)0x80fe04u;
 if (callback!=0u) (void)((uint32_t (*)(uintptr_t))callback)(callback);
 uintptr_t object=*(volatile uint32_t *)(uintptr_t)0x801090u;
 if (object!=0u) {
  callback=*(volatile uint32_t *)(object+12u);
  if (callback!=0u) (void)((uint32_t (*)(uint32_t))callback)(0u);
 }
 uint32_t irq;
 __asm__ volatile("clri %0\n\tsync" : "=r"(irq) :: "memory");
 uint32_t depth=*(volatile uint8_t *)(uintptr_t)0x801398u;
 if (depth!=0u) {
  depth=*(volatile uint8_t *)(uintptr_t)0x801398u;
  depth-=1u;
  *(volatile uint8_t *)(uintptr_t)0x801398u=(uint8_t)depth;
 }
 *(volatile uint32_t *)(uintptr_t)0xf00a80u=1u;
 __asm__ volatile("seti %0" :: "r"(irq) : "memory");
 return depth;
}

/* Native0x332fc4..0x33301c: forward copy with matching-alignment word path.
 * Preserves native access widths and order; not memmove semantics. */
void *opencfw_em9305_memcpy(void *destination,const void *source,uint32_t bytes)
{
 uintptr_t out=(uintptr_t)destination,in=(uintptr_t)source;
 if (((out^in)&3u)==0u) {
  uint32_t align=(4u-(uint32_t)(out&3u))&3u;
  while (align!=0u) {
   if (bytes==0u) return destination;
   uint8_t value=*(volatile const uint8_t *)in;
   *(volatile uint8_t *)out=value;
   in+=1u;out+=1u;bytes-=1u;align-=1u;
  }
  while (bytes>=4u) {
   uint32_t value=*(volatile const uint32_t *)in;
   *(volatile uint32_t *)out=value;
   in+=4u;out+=4u;bytes-=4u;
  }
 }
 while (bytes!=0u) {
  uint8_t value=*(volatile const uint8_t *)in;
  *(volatile uint8_t *)out=value;
  in+=1u;out+=1u;bytes-=1u;
 }
 return destination;
}

extern uint32_t opencfw_em9305_pal_transport_initialize(uint32_t,uintptr_t); /*0x310730*/
extern uint32_t opencfw_em9305_controller_transport_state(uint32_t); /*0x3156cc*/
extern void opencfw_em9305_dispatch_3158e4(void); /*source callback ABI unqualified*/
/* Native0x304764..0x3047b0: transport object and 16-byte callback record.
 * Record bytes13..15 are native ambient stack inputs, intentionally unassigned.
 * Compilation does not qualify stack residue or indirect callback ABI. */
uint32_t opencfw_em9305_controller_transport_configure(uint32_t handler,uint32_t first,uint32_t second)
{
 (void)opencfw_em9305_memset((void *)(uintptr_t)0x801864u,0u,112u);
 volatile uint8_t record[16] __attribute__((aligned(4)));
 *(volatile uint32_t *)(record+8u)=1000000u;
 *(volatile uint32_t *)record=(uint32_t)(uintptr_t)&opencfw_em9305_controller_transport_state;
 *(volatile uint16_t *)(uintptr_t)0x801872u=(uint16_t)second;
 *(volatile uint16_t *)(uintptr_t)0x801870u=(uint16_t)first;
 *(volatile uint8_t *)(uintptr_t)0x801864u=(uint8_t)handler;
 *(volatile uint32_t *)(record+4u)=(uint32_t)(uintptr_t)&opencfw_em9305_dispatch_3158e4;
 record[12]=1u;
 uint32_t result=opencfw_em9305_pal_transport_initialize(1u,(uintptr_t)record);
 return opencfw_em9305_controller_transport_state(result);
}

/* Native0x310730..0x310764: transport record copy and metadata registration.
 * Out-of-domain selectors retain native low-address accesses; no validation
 * contract is invented here. Native compares the full decremented selector
 * for destination selection and its low byte for the state write. */
uint32_t opencfw_em9305_pal_transport_initialize(uint32_t selector,uintptr_t record)
{
 uint32_t index=selector-1u;
 uintptr_t destination=index<2u?0x805edcu:4u;
 (void)opencfw_em9305_memcpy((void *)destination,(const void *)record,16u);
 uintptr_t state=(uint8_t)index<2u?0x805ed8u:0u;
 *(volatile uint8_t *)state=1u;
 return opencfw_em9305_pal_metadata_register(0x8012f0u);
}

/* Native0x31585c..0x31586c: optional transport error hook. */
uint32_t opencfw_em9305_controller_transport_error(uint32_t error)
{
 uintptr_t hook=*(volatile uint32_t *)(uintptr_t)0x80187cu;
 if (hook==0u) return error;
 return ((uint32_t (*)(uint32_t))hook)(error);
}
/* Native0x31586c..0x31588c: classify two received packet counters. */
uint32_t opencfw_em9305_controller_transport_count(uint32_t type)
{
 uintptr_t address;
 if (type==0u) address=0x801874u;
 else if (type==2u) address=0x801878u;
 else return type;
 uint32_t count=*(volatile uint32_t *)address+1u;
 *(volatile uint32_t *)address=count;
 return count;
}
/* Native0x31588c..0x3158bc: packet route or allocation release.
 * The native helper preserves R2/R3/R12 as an internal calling convention;
 * this typed C projection needs final native ABI qualification. */
uint32_t opencfw_em9305_controller_transport_deliver(uint32_t index,uint32_t type,uintptr_t packet)
{
 (void)opencfw_em9305_controller_transport_count(type);
 uintptr_t callback=0u;
 if (index<5u) callback=*(volatile uint32_t *)(uintptr_t)(0x801880u+index*12u);
 if (callback!=0u) return ((uint32_t (*)(uint32_t,uintptr_t))callback)(type,packet);
 return opencfw_em9305_wsf_event_release(packet);
}

/* Native0x3158bc..0x3158e4: completed transmit callback then task event. */
uint32_t opencfw_em9305_controller_transport_complete(void)
{
 uintptr_t object=0x801864u;
 uint32_t slot=*(volatile uint8_t *)(object+9u);
 uintptr_t packet=*(volatile uint32_t *)(object+4u);
 *(volatile uint32_t *)(object+4u)=0u;
 uintptr_t callback=*(volatile uint32_t *)(object+32u+slot*12u);
 uint32_t type=*(volatile uint8_t *)(object+8u);
 (void)((uint32_t (*)(uint32_t,uintptr_t))callback)(type,packet);
 uint32_t handler=*(volatile uint8_t *)object;
 return opencfw_em9305_wsf_event_post(handler,1u);
}
extern uint32_t opencfw_em9305_pal_transport_write(uint32_t,uintptr_t,uint32_t); /*0x3107dc*/
/* Native0x3158e4..0x315914: send at most 255 bytes or complete the packet.
 * Signed MIN precedes low-halfword extraction even for malformed offsets. */
void opencfw_em9305_dispatch_3158e4(void)
{
 uintptr_t object=0x8018ccu;
 uint32_t offset=*(volatile uint16_t *)object;
 uint32_t total=*(volatile uint16_t *)(object+2u);
 int32_t difference=(int32_t)total-(int32_t)offset;
 int32_t selected=difference<255?difference:255;
 uint32_t bytes=(uint16_t)selected;
 if (bytes!=0u) {
  uintptr_t packet=*(volatile uint32_t *)(object+4u);
  (void)opencfw_em9305_pal_transport_write(1u,packet+offset,bytes);
  uint32_t current=*(volatile uint16_t *)object;
  *(volatile uint16_t *)object=(uint16_t)(current+(uint32_t)selected);
 } else (void)opencfw_em9305_controller_transport_complete();
}

/* Native0x3335a4..0x3335c8: transport completion status and record hooks. */
uint32_t opencfw_em9305_pal_transport_completion(uint32_t event,uintptr_t record)
{
 if (event==0u) return event;
 uintptr_t callback;
 if (event==1u) callback=*(volatile uint32_t *)(record+4u);
 else if (event==2u) {
  callback=*(volatile uint32_t *)(record+8u);
  *(volatile uint8_t *)record=1u;
 } else {
  *(volatile uint8_t *)record=0u;
  return event;
 }
 if (callback==0u) return 0u;
 return ((uint32_t (*)(uintptr_t,uintptr_t))callback)(callback,record);
}
/* Native0x3107dc..0x310814: transport write through platform vtable.
 * R3 forwards the selected transport record as the callback context. */
uint32_t opencfw_em9305_pal_transport_write(uint32_t selector,uintptr_t data,uint32_t bytes)
{
 uint32_t index=selector-1u;
 uintptr_t record=index<2u?0x805ed8u:0u;
 uintptr_t object=*(volatile uint32_t *)(uintptr_t)0x801090u;
 *(volatile uint8_t *)record=2u;
 if (object==0u) return index;
 uintptr_t callback=*(volatile uint32_t *)(object+4u);
 if (callback==0u) return index;
 return ((uint32_t (*)(uintptr_t,uint32_t,uintptr_t,uintptr_t))callback)(
  data,bytes,(uintptr_t)&opencfw_em9305_pal_transport_completion,record);
}

extern uint32_t opencfw_em9305_pal_transport_read(uint32_t,uintptr_t,uint32_t); /*0x310764*/
/* Native0x3156cc..0x31585a: incremental transport receive state machine.
 * Product RAM/header fields and native error hooks are retained; callback
 * vtable ABI and malformed-state behavior still require native qualification. */
uint32_t opencfw_em9305_controller_transport_state(uint32_t incoming)
{
 (void)incoming;
 uintptr_t object=0x8018bcu,buffer=0u;
 uint32_t amount=0u,state=*(volatile uint8_t *)object;
 uint32_t header=0u,length=0u,type=0u;
 if (state==1u) {
  type=*(volatile uint8_t *)(object+1u);
  buffer=object+2u;amount=3u;
  *(volatile uint8_t *)object=2u;
  if ((type-128u)<2u || type==1u) goto request;
  if (type==2u || type==5u) {amount=4u;goto request;}
  (void)opencfw_em9305_controller_transport_error(0xa0u);
  goto restart;
 }
 if (state==2u) {
  type=*(volatile uint8_t *)(object+1u);header=3u;
  if ((type-128u)<2u) {
   length=((uint32_t)*(volatile uint8_t *)(object+4u)<<8u)+*(volatile uint8_t *)(object+3u);
   buffer=length;
  } else if (type==1u) {
   length=*(volatile uint8_t *)(object+4u);buffer=length;
  } else if (type==2u) {
   length=((uint32_t)*(volatile uint8_t *)(uintptr_t)0x8018c1u<<8u)+*(volatile uint8_t *)(uintptr_t)0x8018c0u;
   uint32_t limit=*(volatile uint16_t *)(uintptr_t)0x801870u;
   buffer=limit+4u;
   if (limit<(uint16_t)length) goto limit_error;
   header=4u;
  } else if (type==5u) {
   length=(((uint32_t)*(volatile uint8_t *)(uintptr_t)0x8018c1u<<8u)+*(volatile uint8_t *)(uintptr_t)0x8018c0u)&0x3fffu;
   uint32_t limit=*(volatile uint16_t *)(uintptr_t)0x801872u;
   buffer=limit+12u;
   if (limit+8u<length) goto limit_error;
   header=4u;
  } else {header=0u;length=0u;}
  if ((uint16_t)length>=0x1001u) {
   (void)opencfw_em9305_controller_transport_error(0xa0u);goto restart;
  }
  buffer+=header;
  uintptr_t packet=opencfw_em9305_wsf_event_allocate((uint16_t)buffer);
  *(volatile uint32_t *)(object+12u)=(uint32_t)packet;
  if (packet==0u) {
   (void)opencfw_em9305_controller_transport_error(0xa2u);goto restart;
  }
  amount=(uint16_t)length;
  if (amount!=0u) {
   if (amount>255u) amount=255u;
   buffer=packet+header;
   *(volatile uint16_t *)(object+8u)=(uint16_t)(length+header);
   *(volatile uint16_t *)(object+6u)=(uint16_t)(amount+header);
   *(volatile uint8_t *)object=3u;
  } else {buffer=0u;*(volatile uint8_t *)object=4u;}
  (void)opencfw_em9305_memcpy((void *)packet,(const void *)(object+2u),header);
  state=*(volatile uint8_t *)object;
 } else if (state==3u) {
  uint32_t offset=*(volatile uint16_t *)(object+6u);
  uint32_t total=*(volatile uint16_t *)(object+8u);
  int32_t difference=(int32_t)total-(int32_t)offset;
  amount=(uint16_t)(difference<255?difference:255);
  if (amount!=0u) {
   buffer=*(volatile uint32_t *)(object+12u)+offset;
   if (amount>255u) amount=255u;
   *(volatile uint16_t *)(object+6u)=(uint16_t)(amount+offset);
   goto request;
  }
  *(volatile uint8_t *)object=4u;state=4u;
 }
 if (state==0u) goto restart;
 if (state!=4u) {if (buffer!=0u) goto request;return state;}
 type=*(volatile uint8_t *)(object+1u);
 uintptr_t packet=*(volatile uint32_t *)(object+12u);
 if (type==1u) (void)opencfw_em9305_controller_transport_deliver(0u,0u,packet);
 else if (type==2u) (void)opencfw_em9305_controller_transport_deliver(0u,1u,packet);
 else if (type==128u) (void)opencfw_em9305_controller_transport_deliver(2u,0u,packet);
 else if (type==129u) (void)opencfw_em9305_controller_transport_deliver(2u,1u,packet);
 else if (type==5u) (void)opencfw_em9305_controller_transport_deliver(0u,3u,packet);
 *(volatile uint32_t *)(object+12u)=0u;
restart:
 amount=1u;buffer=object+1u;*(volatile uint8_t *)object=1u;
request:
 return opencfw_em9305_pal_transport_read(1u,buffer,amount);
limit_error:;
 uint32_t result=opencfw_em9305_controller_transport_error(0xa1u);
 *(volatile uint8_t *)object=0u;
 return result;
}

/* Native0x310764..0x310798: platform receive request. R3 is a record context. */
uint32_t opencfw_em9305_pal_transport_read(uint32_t selector,uintptr_t data,uint32_t bytes)
{
 uint32_t index=selector-1u;
 uintptr_t record=index<2u?0x805ed8u:0u;
 uintptr_t object=*(volatile uint32_t *)(uintptr_t)0x801090u;
 if (object==0u) return index;
 uintptr_t callback=*(volatile uint32_t *)(object+8u);
 if (callback==0u) return index;
 return ((uint32_t (*)(uintptr_t,uint32_t,uintptr_t,uintptr_t))callback)(
  data,bytes,(uintptr_t)&opencfw_em9305_pal_transport_completion,record);
}

/* Native0x304698..0x304764: five-source round-robin transmit poll.
 * Callback local output layout and internal register ABI remain unqualified. */
uint32_t opencfw_em9305_controller_transport_poll(uint32_t incoming)
{
 (void)incoming;
 uintptr_t object=0x801864u;
 uint32_t busy=*(volatile uint32_t *)(object+4u);
 if (busy!=0u) return busy;
 uint32_t slot=*(volatile uint8_t *)(object+9u);
 for (uint32_t attempt=1u;attempt<=5u;attempt++) {
  uint32_t previous=(uint8_t)slot;
  slot+=1u;
  if (previous>3u) slot=0u;
  uint32_t selected=(uint8_t)slot;
  volatile uint8_t type=0u;
  volatile uintptr_t packet=0u;
  volatile uint16_t length=0u;
  uintptr_t callback=*(volatile uint32_t *)(object+36u+selected*12u);
  if (callback==0u) continue;
  uint32_t available=((uint32_t (*)(volatile uint8_t *,volatile uint16_t *,volatile uintptr_t *))callback)(&type,&length,&packet);
  if (available==0u) continue;
  uintptr_t data=packet;
  uint32_t classification=type;
  *(volatile uint8_t *)(object+9u)=(uint8_t)slot;
  *(volatile uint32_t *)(object+4u)=(uint32_t)data;
  *(volatile uint8_t *)(object+8u)=(uint8_t)classification;
  (void)opencfw_em9305_controller_transport_count(classification);
  uint32_t total=(uint32_t)length+1u;
  *(volatile uint16_t *)(object+106u)=(uint16_t)total;
  uint8_t indicator;
  if (selected==2u) indicator=classification==2u?0x84u:0x81u;
  else if (classification==2u) indicator=4u;
  else if (classification==1u) indicator=2u;
  else indicator=5u;
  *(volatile uint8_t *)(data-1u)=indicator;
  uint32_t bytes=*(volatile uint16_t *)(uintptr_t)0x8018ceu;
  *(volatile uint32_t *)(uintptr_t)0x8018d0u=(uint32_t)(data-1u);
  if (bytes>255u) bytes=255u;
  *(volatile uint16_t *)(uintptr_t)0x8018ccu=(uint16_t)bytes;
  (void)opencfw_em9305_pal_transport_write(1u,data-1u,bytes);
  return 0u;
 }
 return 1u;
}
/* Native0x3047b0..0x3047c0: receive idle-state query. */
uint32_t opencfw_em9305_controller_transport_idle(void)
{
 return *(volatile uint8_t *)(uintptr_t)0x8018bcu==1u;
}
/* Native0x3047c0..0x3047d4: LL event producer kick. */
uint32_t opencfw_em9305_ll_event_kick(uint32_t incoming)
{
 (void)incoming;
 uint32_t busy=*(volatile uint32_t *)(uintptr_t)0x801868u;
 if (busy!=0u) return busy;
 return opencfw_em9305_controller_transport_poll(0u);
}

/* Native LL callback installations: exact store order and conditional defaults.
 * Callback prototypes remain unqualified until their native bodies are owned. */
extern uint32_t opencfw_em9305_dispatch_32e3bc(void); /*0x32e3bc*/
extern uint32_t opencfw_em9305_dispatch_32e3e0(uint32_t,uint32_t); /*0x32e3e0*/
extern uint32_t opencfw_em9305_dispatch_32ef10(uintptr_t,uintptr_t); /*0x32ef10*/
extern void opencfw_em9305_dispatch_32f0a0(void); /*0x32f0a0*/
extern uint32_t opencfw_em9305_dispatch_32f64c(uintptr_t,uintptr_t); /*0x32f64c*/
extern uint32_t opencfw_em9305_dispatch_32f70c(uintptr_t); /*0x32f70c*/
extern uint32_t opencfw_em9305_dispatch_330440(uintptr_t request,uintptr_t input); /*native330440*/
extern void opencfw_em9305_dispatch_3304f0(void); /*0x3304f0*/
extern uint32_t opencfw_em9305_dispatch_3305b0(uintptr_t request,uintptr_t input); /*native3305b0*/
extern void opencfw_em9305_dispatch_330664(void); /*0x330664*/
extern void opencfw_em9305_dispatch_330848(void); /*0x330848*/
extern uintptr_t opencfw_em9305_dispatch_331a8c(void); /*0x331a8c*/
extern uint32_t opencfw_em9305_dispatch_332278(uintptr_t request,uintptr_t input); /* native 0x332278 */
extern uint32_t opencfw_em9305_dispatch_332394(uintptr_t request,uintptr_t input); /* native 0x332394 */
extern void opencfw_em9305_dispatch_3324e0(void); /*0x3324e0*/
extern uint32_t opencfw_em9305_dispatch_3327f4(uintptr_t); /* native packet ABI */
uint32_t opencfw_em9305_ll_callback_pair(uintptr_t first,uintptr_t second)
{
 *(volatile uint32_t *)(uintptr_t)0x805b14u=(uint32_t)second;
 *(volatile uint32_t *)(uintptr_t)0x805b10u=(uint32_t)first;
 return (uint32_t)first;
}
/* Native0x30a7bc. */
uint32_t opencfw_em9305_ll_seed_30a7bc(void)
{
 (void)opencfw_em9305_ll_callback_pair((uintptr_t)&opencfw_em9305_dispatch_32e3e0,(uintptr_t)&opencfw_em9305_dispatch_32e3bc);
 if (*(volatile uint32_t *)(uintptr_t)0x805730u==0u) {
  *(volatile uint32_t *)(uintptr_t)0x805730u=(uint32_t)(uintptr_t)&opencfw_em9305_dispatch_32ef10;
  *(volatile uint32_t *)(uintptr_t)0x8057c0u=(uint32_t)(uintptr_t)&opencfw_em9305_dispatch_32f0a0;
 }
 *(volatile uint32_t *)(uintptr_t)0x8058d0u=(uint32_t)(uintptr_t)&opencfw_em9305_dispatch_331a8c;
 return 0x8058d0u;
}
/* Native0x30a800. */
uint32_t opencfw_em9305_ll_seed_30a800(void)
{
 (void)opencfw_em9305_ll_callback_pair((uintptr_t)&opencfw_em9305_dispatch_32e3e0,(uintptr_t)&opencfw_em9305_dispatch_32e3bc);
 *(volatile uint32_t *)(uintptr_t)0x8057c0u=(uint32_t)(uintptr_t)&opencfw_em9305_dispatch_3304f0;
 *(volatile uint32_t *)(uintptr_t)0x805730u=(uint32_t)(uintptr_t)&opencfw_em9305_dispatch_330440;
 *(volatile uint32_t *)(uintptr_t)0x8058d0u=(uint32_t)(uintptr_t)&opencfw_em9305_dispatch_331a8c;
 return 0x8058d0u;
}
/* Native0x30a860. */
uint32_t opencfw_em9305_ll_seed_30a860(void)
{
 if (*(volatile uint32_t *)(uintptr_t)0x805738u==0u) {
  *(volatile uint32_t *)(uintptr_t)0x805738u=(uint32_t)(uintptr_t)&opencfw_em9305_dispatch_332278;
  *(volatile uint32_t *)(uintptr_t)0x8057c8u=(uint32_t)(uintptr_t)&opencfw_em9305_dispatch_332394;
 }
 return 0x805738u;
}
/* Native0x30a884. */
uint32_t opencfw_em9305_ll_seed_30a884(void)
{
 if (*(volatile uint32_t *)(uintptr_t)0x80572cu==0u) {
  *(volatile uint32_t *)(uintptr_t)0x80572cu=(uint32_t)(uintptr_t)&opencfw_em9305_dispatch_32f64c;
  *(volatile uint32_t *)(uintptr_t)0x8057bcu=(uint32_t)(uintptr_t)&opencfw_em9305_dispatch_32f70c;
 }
 return 0x80572cu;
}
/* Native0x30a8a8. */
uint32_t opencfw_em9305_ll_seed_30a8a8(void)
{
 *(volatile uint32_t *)(uintptr_t)0x8057dcu=(uint32_t)(uintptr_t)&opencfw_em9305_dispatch_3327f4;
 *(volatile uint32_t *)(uintptr_t)0x80574cu=(uint32_t)(uintptr_t)&opencfw_em9305_dispatch_3324e0;
 *(volatile uint32_t *)(uintptr_t)0x805750u=(uint32_t)(uintptr_t)&opencfw_em9305_dispatch_3324e0;
 *(volatile uint32_t *)(uintptr_t)0x8057e0u=(uint32_t)(uintptr_t)&opencfw_em9305_dispatch_3327f4;
 return 0x80574cu;
}
/* Native0x30a8cc. */
uint32_t opencfw_em9305_ll_seed_30a8cc(void)
{
 (void)opencfw_em9305_ll_callback_pair((uintptr_t)&opencfw_em9305_dispatch_32e3e0,(uintptr_t)&opencfw_em9305_dispatch_32e3bc);
 *(volatile uint32_t *)(uintptr_t)0x8057c0u=(uint32_t)(uintptr_t)&opencfw_em9305_dispatch_3304f0;
 *(volatile uint32_t *)(uintptr_t)0x805730u=(uint32_t)(uintptr_t)&opencfw_em9305_dispatch_3305b0;
 *(volatile uint32_t *)(uintptr_t)0x8058d0u=(uint32_t)(uintptr_t)&opencfw_em9305_dispatch_331a8c;
 return 0x8058d0u;
}
/* Native0x30a90c. */
uint32_t opencfw_em9305_ll_seed_30a90c(void)
{
 *(volatile uint32_t *)(uintptr_t)0x8057d0u=(uint32_t)(uintptr_t)&opencfw_em9305_dispatch_330848;
 *(volatile uint32_t *)(uintptr_t)0x805740u=(uint32_t)(uintptr_t)&opencfw_em9305_dispatch_330664;
 *(volatile uint32_t *)(uintptr_t)0x805744u=(uint32_t)(uintptr_t)&opencfw_em9305_dispatch_330664;
 *(volatile uint32_t *)(uintptr_t)0x8057d4u=(uint32_t)(uintptr_t)&opencfw_em9305_dispatch_330848;
 return 0x805740u;
}

/* Native0x30c078..0x30c094: register the LL poll handler and configure transport. */
uint32_t opencfw_em9305_ll_transport_register(uint32_t first,uint32_t second)
{
 uint32_t handler=opencfw_em9305_controller_wsf_register((uintptr_t)&opencfw_em9305_controller_transport_poll);
 return opencfw_em9305_controller_transport_configure(handler,first,second);
}
/* Native0x3335c8..0x3335d8: native idle predicate translated to status1/2. */
uint32_t opencfw_em9305_controller_transport_status(void)
{
 uint32_t idle=opencfw_em9305_controller_transport_idle();
 return (idle==0u)+1u;
}

/* Further native LL callback constructors; indirect ABI remains unqualified. */
extern void opencfw_em9305_dispatch_32e4c4(void); /*0x32e4c4*/
extern void opencfw_em9305_dispatch_330c60(void); /*0x330c60*/
extern void opencfw_em9305_dispatch_330ce0(void); /*0x330ce0*/
extern void opencfw_em9305_dispatch_330fa0(void); /*0x330fa0*/
extern void opencfw_em9305_dispatch_331074(void); /*0x331074*/
extern uint32_t opencfw_em9305_dispatch_331100(uintptr_t); /*0x331100*/
extern uint32_t opencfw_em9305_dispatch_331204(uintptr_t,uintptr_t); /*0x331204*/
extern void opencfw_em9305_dispatch_331334(void); /*0x331334*/
extern void opencfw_em9305_dispatch_3316e0(void); /*0x3316e0*/
extern uint32_t opencfw_em9305_dispatch_331814(uintptr_t); /*0x331814*/
extern uint32_t opencfw_em9305_dispatch_331868(uintptr_t,uintptr_t); /* native command ABI */
extern uint32_t opencfw_em9305_dispatch_33194c(uintptr_t,uintptr_t); /* native command ABI */
extern uint32_t opencfw_em9305_dispatch_3319bc(uintptr_t); /* native packet ABI */
extern uint32_t opencfw_em9305_dispatch_331aec(uintptr_t,uintptr_t); /*0x331aec*/
extern uint32_t opencfw_em9305_dispatch_331b3c(uintptr_t); /*0x331b3c*/
/* Native0x30ad80. */
uint32_t opencfw_em9305_ll_seed_30ad80(void)
{
 *(volatile uint32_t *)(uintptr_t)0x8057b0u=(uint32_t)(uintptr_t)&opencfw_em9305_dispatch_331334;
 *(volatile uint32_t *)(uintptr_t)0x80571cu=(uint32_t)(uintptr_t)&opencfw_em9305_dispatch_32e4c4;
 return 0x80571cu;
}
/* Native0x30ada0. */
uint32_t opencfw_em9305_ll_seed_30ada0(void)
{
 *(volatile uint32_t *)(uintptr_t)0x8057b0u=(uint32_t)(uintptr_t)&opencfw_em9305_dispatch_331334;
 *(volatile uint32_t *)(uintptr_t)0x805720u=(uint32_t)(uintptr_t)&opencfw_em9305_dispatch_331204;
 return 0x805720u;
}
/* Native0x30adc0. */
uint32_t opencfw_em9305_ll_seed_30adc0(void)
{
 *(volatile uint32_t *)(uintptr_t)0x8057e8u=(uint32_t)(uintptr_t)&opencfw_em9305_dispatch_331814;
 *(volatile uint32_t *)(uintptr_t)0x805758u=(uint32_t)(uintptr_t)&opencfw_em9305_dispatch_3316e0;
 return 0x805758u;
}
/* Native0x30ae24. */
uint32_t opencfw_em9305_ll_seed_30ae24(void)
{
 *(volatile uint32_t *)(uintptr_t)0x8057b4u=(uint32_t)(uintptr_t)&opencfw_em9305_dispatch_3319bc;
 *(volatile uint32_t *)(uintptr_t)0x805724u=(uint32_t)(uintptr_t)&opencfw_em9305_dispatch_33194c;
 return 0x805724u;
}
/* Native0x30ae50. */
uint32_t opencfw_em9305_ll_seed_30ae50(void)
{
 *(volatile uint32_t *)(uintptr_t)0x8057e4u=(uint32_t)(uintptr_t)&opencfw_em9305_dispatch_331b3c;
 *(volatile uint32_t *)(uintptr_t)0x805754u=(uint32_t)(uintptr_t)&opencfw_em9305_dispatch_331aec;
 return 0x805754u;
}
/* Native0x30ae70. */
uint32_t opencfw_em9305_ll_seed_30ae70(void)
{
 *(volatile uint32_t *)(uintptr_t)0x8057ccu=(uint32_t)(uintptr_t)&opencfw_em9305_dispatch_330ce0;
 *(volatile uint32_t *)(uintptr_t)0x80573cu=(uint32_t)(uintptr_t)&opencfw_em9305_dispatch_330c60;
 return 0x80573cu;
}
/* Native0x30ad58..0x30ad80: capability gate before callback installation. */
uint32_t opencfw_em9305_ll_seed_30ad58(void)
{
 uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
 uint32_t capability=*(volatile uint8_t *)(config+4u);
 if (capability<10u) return capability;
 *(volatile uint32_t *)(uintptr_t)0x8057f0u=0u;
 *(volatile uint32_t *)(uintptr_t)0x805760u=(uint32_t)(uintptr_t)&opencfw_em9305_dispatch_330fa0;
 return 0x805760u;
}
/* Native0x30ade0..0x30ae04: preserve installed provider. */
uint32_t opencfw_em9305_ll_seed_30ade0(void)
{
 if (*(volatile uint32_t *)(uintptr_t)0x80578cu==0u) {
  *(volatile uint32_t *)(uintptr_t)0x80578cu=(uint32_t)(uintptr_t)&opencfw_em9305_dispatch_331074;
  *(volatile uint32_t *)(uintptr_t)0x80581cu=(uint32_t)(uintptr_t)&opencfw_em9305_dispatch_331100;
 }
 return 0x80578cu;
}
/* Native0x30ae04..0x30ae24: R0 returns the original provider value. */
uint32_t opencfw_em9305_ll_seed_30ae04(void)
{
 uint32_t installed=*(volatile uint32_t *)(uintptr_t)0x805724u;
 if (installed==0u) {
  *(volatile uint32_t *)(uintptr_t)0x8057b4u=0u;
  *(volatile uint32_t *)(uintptr_t)0x805724u=(uint32_t)(uintptr_t)&opencfw_em9305_dispatch_331868;
 }
 return installed;
}
/* Native0x30ae44..0x30ae50. */
uint32_t opencfw_em9305_ll_event_callback_set(uintptr_t callback)
{
 *(volatile uint32_t *)(uintptr_t)0x805880u=(uint32_t)callback;
 return (uint32_t)callback;
}

extern uint32_t opencfw_em9305_dispatch_331cbc(uint32_t); /*0x331cbc*/
extern uint32_t opencfw_em9305_dispatch_32fe3c(uintptr_t); /*0x32fe3c*/
extern uint32_t opencfw_em9305_ll_dispatch_initialize(uint32_t); /*0x331ac0*/
/* Native0x30b6c0..0x30b6cc. */
uint32_t opencfw_em9305_ll_dispatch_callback_set(uintptr_t callback)
{
 *(volatile uint32_t *)(uintptr_t)0x805b0cu=(uint32_t)callback;
 return (uint32_t)callback;
}
/* Native0x30ac6c..0x30acc4: initialize dispatch records and transport hooks. */
uint32_t opencfw_em9305_ll_dispatch_records_initialize(uint32_t handler)
{
 (void)opencfw_em9305_controller_transport_callbacks(0u,
  (uintptr_t)&opencfw_em9305_dispatch_331a40,
  (uintptr_t)&opencfw_em9305_dispatch_331c20,
  (uintptr_t)&opencfw_em9305_dispatch_331cdc);
 (void)opencfw_em9305_controller_transport_hook((uintptr_t)&opencfw_em9305_dispatch_331cbc);
 (void)opencfw_em9305_memset((void *)(uintptr_t)0x80585cu,0u,108u);
 *(volatile uint8_t *)(uintptr_t)0x80585cu=(uint8_t)handler;
 (void)opencfw_em9305_memset((void *)(uintptr_t)0x8056e8u,0u,52u);
 uint32_t result=opencfw_em9305_ll_dispatch_callback_set((uintptr_t)&opencfw_em9305_dispatch_32fe3c);
 return opencfw_em9305_ll_dispatch_initialize(result);
}
extern uint32_t opencfw_em9305_dispatch_32fccc(uint32_t,uintptr_t,uintptr_t); /*0x32fccc*/
extern uint32_t opencfw_em9305_dispatch_32fc8c(void); /*0x32fc8c*/
extern uint32_t opencfw_em9305_dispatch_331abc(uint32_t); /*0x331abc*/
extern uintptr_t opencfw_em9305_dispatch_331aa4(void); /*0x331aa4*/
extern uint32_t opencfw_em9305_dispatch_32f85c(uintptr_t,uintptr_t); /*0x32f85c*/
extern uint32_t opencfw_em9305_dispatch_32fc88(void); /*0x32fc88*/
/* Native0x30c2ac..0x30c2bc. */
uint32_t opencfw_em9305_ll_dispatch_active(uint32_t active)
{
 uint32_t selected=active!=0u;
 *(volatile uint8_t *)(uintptr_t)0x805aafu=(uint8_t)selected;
 return selected;
}
/* Native0x30c2c8..0x30c2d4. */
uint32_t opencfw_em9305_ll_auxiliary_pair(uintptr_t first,uintptr_t second)
{
 *(volatile uint32_t *)(uintptr_t)0x805b3cu=(uint32_t)second;
 *(volatile uint32_t *)(uintptr_t)0x805b38u=(uint32_t)first;
 return (uint32_t)first;
}
/* Native0x30acc4..0x30ad20. */
uint32_t opencfw_em9305_ll_seed_30acc4(void)
{
 (void)opencfw_em9305_ll_auxiliary_pair((uintptr_t)&opencfw_em9305_dispatch_32fccc,(uintptr_t)&opencfw_em9305_dispatch_32fc8c);
 *(volatile uint32_t *)(uintptr_t)0x8058c8u=(uint32_t)(uintptr_t)&opencfw_em9305_dispatch_331abc;
 *(volatile uint32_t *)(uintptr_t)0x8058d4u=(uint32_t)(uintptr_t)&opencfw_em9305_dispatch_331aa4;
 *(volatile uint32_t *)(uintptr_t)0x805858u=(uint32_t)(uintptr_t)&opencfw_em9305_ll_dispatch_active;
 *(volatile uint32_t *)(uintptr_t)0x805728u=(uint32_t)(uintptr_t)&opencfw_em9305_dispatch_32f85c;
 *(volatile uint32_t *)(uintptr_t)0x8057b8u=(uint32_t)(uintptr_t)&opencfw_em9305_dispatch_32fc88;
 return 0x8057b8u;
}
/* Native0x30ad20..0x30ad30. */
uint32_t opencfw_em9305_ll_pack_typed_halfword(uintptr_t destination,uint32_t value)
{
 *(volatile uint8_t *)(destination+1u)=(uint8_t)value;
 *(volatile uint8_t *)(destination+2u)=(uint8_t)(value>>8u);
 *(volatile uint8_t *)destination=1u;
 return 3u;
}
/* Native0x30ad30..0x30ad40. */
uint32_t opencfw_em9305_ll_pack_halfword(uintptr_t destination,uint32_t value)
{
 *(volatile uint8_t *)(destination+1u)=(uint8_t)(value>>8u);
 *(volatile uint8_t *)destination=(uint8_t)value;
 return 2u;
}
/* Native0x30ad40..0x30ad48. */
uint32_t opencfw_em9305_ll_pack_byte(uintptr_t destination,uint32_t value)
{
 *(volatile uint8_t *)destination=(uint8_t)value;
 return 1u;
}
/* Native0x30ad48..0x30ad58 duplicates the preceding halfword contract. */
uint32_t opencfw_em9305_ll_pack_halfword_secondary(uintptr_t destination,uint32_t value)
{
 return opencfw_em9305_ll_pack_halfword(destination,value);
}

/* Native0x30aa38..0x30ac40: construct LL feature bytes from installed providers.
 * This is a typed native field projection, not an embedded executable/data blob. */
uint32_t opencfw_em9305_ll_features_initialize(void)
{
 uintptr_t out=0x805885u,providers=0x80571cu,feature=0x8058a7u;
 (void)opencfw_em9305_memset((void *)out,0u,64u);
 *(volatile uint16_t *)(out+27u)=0x7883u;
 uint32_t primary=*(volatile uint32_t *)(providers+20u);
 *(volatile uint8_t *)(out+41u)=16u;
 *(volatile uint8_t *)(out+22u)=4u;
 *(volatile uint8_t *)(out+15u)=2u;
 *(volatile uint16_t *)(out+25u)=0xc017u;
 *(volatile uint8_t *)(out+14u)=40u;
 *(volatile uint8_t *)(out+5u)=192u;
 uint32_t bits1=0u,bits0=0u,flags27=0x83u;
 if (primary!=0u) {
  bits1=8u;bits0=1u;flags27=0xb7u;
  *(volatile uint8_t *)(out+35u)=8u;
  *(volatile uint8_t *)(out+10u)=4u;
  *(volatile uint16_t *)(out+33u)=496u;
  *(volatile uint8_t *)(out+27u)=(uint8_t)flags27;
  *(volatile uint8_t *)(out+15u)=34u;
  *(volatile uint8_t *)(out+2u)=128u;
  *(volatile uint8_t *)out=32u;
 }
 uint32_t value=*(volatile uint32_t *)(providers+32u),flags26;
 if (value!=0u) {
  *(volatile uint8_t *)(out+26u)=204u;
  if (primary!=0u) {
   flags27|=8u;
   *(volatile uint8_t *)(out+26u)=252u;
   *(volatile uint8_t *)(out+27u)=(uint8_t)flags27;
   flags26=255u;
  } else flags26=207u;
 } else flags26=195u;
 value=*(volatile uint32_t *)(providers+44u);
 if (value!=0u) {
  *(volatile uint8_t *)(out+26u)=(uint8_t)flags26;
  *(volatile uint8_t *)(out+25u)=247u;
 }
 value=*(volatile uint32_t *)(providers+28u);
 if (value!=0u && primary!=0u) {
  flags27|=64u;
  *(volatile uint8_t *)(out+32u)=48u;
  *(volatile uint8_t *)(out+28u)=127u;
  *(volatile uint8_t *)(out+27u)=(uint8_t)flags27;
 }
 value=*(volatile uint32_t *)(providers+8u);
 uint32_t bits5=0u;
 if (value!=0u) {
  uint32_t next1=bits1|6u,next0=bits0|120u;
  bits5=4u;
  *(volatile uint8_t *)(feature+1u)=(uint8_t)next1;
  *(volatile uint8_t *)feature=(uint8_t)next0;
  if (primary!=0u) {
   bits1|=7u;bits0|=0xfffffff8u;
   *(volatile uint8_t *)(feature+1u)=(uint8_t)bits1;
   *(volatile uint8_t *)feature=(uint8_t)bits0;
  } else {bits1=next1;bits0=next0;}
 }
 uint32_t extended=*(volatile uint32_t *)(providers+56u);
 if (extended!=0u) *(volatile uint8_t *)feature=(uint8_t)(bits0|6u);
 uint32_t scan=*(volatile uint32_t *)(providers+12u);
 if (scan!=0u) *(volatile uint8_t *)(out+7u)=12u;
 value=*(volatile uint32_t *)(providers+60u);
 *(volatile uint8_t *)(feature+4u)=128u;
 uint32_t bits2;
 if (value!=0u) {
  bits1|=240u;bits2=255u;
  *(volatile uint8_t *)(feature+2u)=1u;
  *(volatile uint8_t *)(feature+1u)=(uint8_t)bits1;
 } else bits2=254u;
 value=*(volatile uint32_t *)(providers+48u);
 uint32_t bits3=0u;
 if (value!=0u) {
  bits3=3u;bits5|=3u;
  *(volatile uint8_t *)(feature+3u)=3u;
  *(volatile uint8_t *)(feature+2u)=(uint8_t)bits2;
  *(volatile uint8_t *)(feature+5u)=(uint8_t)bits5;
 }
 value=*(volatile uint32_t *)(providers+36u);
 uint32_t next3=bits3;
 if (value!=0u) {
  next3=bits3|96u;
  *(volatile uint8_t *)(feature+3u)=(uint8_t)next3;
  if (primary!=0u) {bits3|=0xffffffe0u;*(volatile uint8_t *)(feature+3u)=(uint8_t)bits3;}
  else bits3=next3;
 }
 next3=bits3;
 value=*(volatile uint32_t *)(providers+52u);
 if (value!=0u) *(volatile uint8_t *)(feature+3u)=(uint8_t)(next3|28u);
 value=*(volatile uint32_t *)(providers+40u);
 if (value!=0u) *(volatile uint8_t *)(feature+4u)=255u;
 value=*(volatile uint32_t *)(providers+64u);
 uint32_t bits6;
 if (value!=0u) {bits5|=0xffffffe0u;bits6=255u;*(volatile uint8_t *)(feature+6u)=31u;}
 else bits6=224u;
 value=*(volatile uint32_t *)(providers+68u);
 uint32_t bits7;
 if (value!=0u) {bits7=19u;*(volatile uint8_t *)(feature+7u)=19u;*(volatile uint8_t *)(feature+6u)=(uint8_t)bits6;}
 else bits7=16u;
 *(volatile uint8_t *)(feature+5u)=(uint8_t)(bits5|24u);
 if (extended!=0u) {bits7|=4u;*(volatile uint8_t *)(feature+7u)=(uint8_t)bits7;}
 value=*(volatile uint32_t *)(providers+72u);
 *(volatile uint8_t *)(feature+11u)=0u;
 *(volatile uint8_t *)(feature+10u)=2u;
 uint32_t bits8;
 if (value!=0u) {bits8=7u;bits7|=0xffffff80u;*(volatile uint8_t *)(feature+8u)=7u;*(volatile uint8_t *)(feature+7u)=(uint8_t)bits7;}
 else bits8=0u;
 value=*(volatile uint32_t *)(providers+76u);
 if (value!=0u) {bits8|=24u;*(volatile uint8_t *)(feature+8u)=(uint8_t)bits8;}
 value=*(volatile uint32_t *)(providers+80u);
 uint32_t bits9;
 if (value!=0u) {bits9=255u;*(volatile uint8_t *)(feature+9u)=3u;}
 else bits9=252u;
 value=*(volatile uint32_t *)(providers+84u);
 if (value!=0u) {bits8|=224u;*(volatile uint8_t *)(feature+8u)=(uint8_t)bits8;}
 uint32_t bits10=250u;
 if (scan!=0u) {
  bits7|=96u;bits10=255u;
  *(volatile uint8_t *)(feature+10u)=7u;
  *(volatile uint8_t *)(feature+9u)=(uint8_t)bits9;
  *(volatile uint8_t *)(feature+7u)=(uint8_t)bits7;
 }
 value=*(volatile uint32_t *)(providers+112u);
 uint32_t provider68=*(volatile uint32_t *)(providers+104u);
 if (value!=0u) *(volatile uint8_t *)(feature+10u)=(uint8_t)bits10;
 uint32_t provider10=*(volatile uint32_t *)(providers+16u);
 uint32_t result=provider10==0u?0xffffffe4u:0xffffffe7u;
 *(volatile uint8_t *)(out+13u)=12u;
 *(volatile uint8_t *)(out+47u)=3u;
 *(volatile uint8_t *)(out+45u)=(uint8_t)(provider68==0u?65u:125u);
 *(volatile uint8_t *)(out+46u)=(uint8_t)result;
 return result;
}

/* Native0x30c0e8..0x30c150: ordered LL provider construction chain. */
uint32_t opencfw_em9305_ll_providers_initialize(uint32_t incoming)
{
 (void)incoming;
 uint32_t result;
 result=opencfw_em9305_ll_seed_30ae70();
 result=opencfw_em9305_ll_seed_30a840();
 result=opencfw_em9305_ll_seed_30a800();
 result=opencfw_em9305_ll_seed_30a70c();
 result=opencfw_em9305_ll_seed_30a860();
 result=opencfw_em9305_ll_seed_30a7bc();
 result=opencfw_em9305_ll_seed_30ae04();
 result=opencfw_em9305_ll_seed_30ae24();
 result=opencfw_em9305_ll_seed_30ae50();
 result=opencfw_em9305_ll_seed_30a90c();
 result=opencfw_em9305_ll_seed_30a8cc();
 result=opencfw_em9305_ll_seed_30a8a8();
 result=opencfw_em9305_ll_seed_30a76c();
 result=opencfw_em9305_ll_seed_30adc0();
 result=opencfw_em9305_ll_seed_30ad58();
 result=opencfw_em9305_ll_seed_30a884();
 result=opencfw_em9305_ll_seed_30a77c();
 result=opencfw_em9305_ll_seed_30a72c();
 result=opencfw_em9305_ll_seed_30a74c();
 result=opencfw_em9305_ll_seed_30a79c();
 result=opencfw_em9305_ll_seed_30acc4();
 result=opencfw_em9305_ll_seed_30ade0();
 result=opencfw_em9305_ll_seed_30ad80();
 result=opencfw_em9305_ll_seed_30ada0();
 return result;
}

extern uint32_t opencfw_em9305_ll_handler_lower(uint32_t,uint32_t); /*0x30a930*/
extern uint32_t opencfw_em9305_ll_received_event(uintptr_t); /*0x30cd80*/
/* Native0x30ac40..0x30ac6c: drain queued messages before processing events. */
uint32_t opencfw_em9305_ll_handler(uint32_t events,uint32_t handler)
{
 if ((events&16u)!=0u) {
  volatile uint8_t queued_handler;
  for (;;) {
   uintptr_t message=opencfw_em9305_wsf_event_remove(0x805878u,(uintptr_t)&queued_handler);
   if (message==0u) break;
   (void)opencfw_em9305_ll_received_event(message);
  }
 }
 return opencfw_em9305_ll_handler_lower(events,handler);
}
/* Native0x30c0d4..0x30c0e8: LL handler registration and record setup. */
uint32_t opencfw_em9305_ll_handler_initialize(void)
{
 uint32_t handler=opencfw_em9305_controller_wsf_register((uintptr_t)&opencfw_em9305_ll_handler);
 return opencfw_em9305_ll_dispatch_records_initialize(handler);
}

extern uint32_t opencfw_em9305_ll_received_event_active(uintptr_t); /*0x30a564*/
/* Native0x30cd80..0x30cd94: ownership-aware received-message routing. */
uint32_t opencfw_em9305_ll_received_event(uintptr_t message)
{
 if (*(volatile uint8_t *)(uintptr_t)0x805adcu!=0u)
  return opencfw_em9305_ll_received_event_active(message);
 return opencfw_em9305_wsf_event_release(message);
}
extern uint32_t opencfw_em9305_ll_queued_event(uintptr_t); /*0x30cd6c*/
extern uint32_t opencfw_em9305_ll_command_primary(uintptr_t,uintptr_t); /*0x32e5d4*/
/* Native0x30a930..0x30aa38: queues, command provider chain and elapsed maximum.
 * Native LD.AB/ST.AB access the old base before writeback. The command
 * descriptor's unused stack byte and callback ABI remain unqualified. */
uint32_t opencfw_em9305_ll_handler_lower(uint32_t events,uint32_t handler)
{
 (void)handler;
 uint32_t started=opencfw_em9305_pal_current_time(),previous=0u,result=started;
 if (started!=0u) {previous=opencfw_em9305_pal_current_time();result=previous;}
 if ((events&1u)!=0u) {
  volatile uint8_t queued_handler;
  for (;;) {
   uintptr_t message=opencfw_em9305_wsf_event_remove(0x805860u,(uintptr_t)&queued_handler);
   result=(uint32_t)message;
   if (message==0u) break;
   result=opencfw_em9305_ll_queued_event(message);
  }
 }
 if ((events&2u)!=0u) {
  volatile uint8_t queued_handler;
  for (;;) {
   uintptr_t message=opencfw_em9305_wsf_event_remove(0x805868u,(uintptr_t)&queued_handler);
   result=(uint32_t)message;
   if (message==0u) break;
   uint32_t high=*(volatile uint8_t *)(message+1u);
   uint32_t parameter_length=*(volatile uint8_t *)(message+2u);
   uint32_t low=*(volatile uint8_t *)message;
   uint16_t opcode=(uint16_t)((high<<8u)+low);
   volatile uint8_t command[4] __attribute__((aligned(4)));
   command[2]=(uint8_t)parameter_length;
   *(volatile uint16_t *)command=opcode;
   uintptr_t parameters=message+3u;
   uint32_t accepted=opencfw_em9305_ll_command_primary((uintptr_t)command,parameters);
   if (accepted==0u) {
    for (uint32_t index=0u;index<35u;index++) {
     uintptr_t callback=*(volatile uint32_t *)(uintptr_t)(0x80571cu+index*4u);
     if (callback!=0u) {
      accepted=((uint32_t (*)(uintptr_t,uintptr_t))callback)((uintptr_t)command,parameters);
      if (accepted!=0u) break;
     }
    }
    if (accepted==0u) {
     uintptr_t payload=opencfw_em9305_ll_event_allocate(15u,4u);
     if (payload!=0u) {
      uint32_t current=*(volatile uint16_t *)command;
      *(volatile uint8_t *)(payload+1u)=1u;
      *(volatile uint8_t *)(payload+2u)=(uint8_t)current;
      *(volatile uint8_t *)payload=1u;
      uintptr_t event=payload-2u;
      *(volatile uint8_t *)(event+5u)=(uint8_t)(current>>8u);
      (void)opencfw_em9305_ll_event_send(event);
     }
    }
   }
   result=opencfw_em9305_wsf_event_release(message);
  }
 }
 result=0u; /* Native delay slot even when event bit2 is clear. */
 if ((events&4u)!=0u) {
  *(volatile uint8_t *)(uintptr_t)0x805884u=0u;
  result=opencfw_em9305_ll_event_kick(0u);
  uintptr_t callback=*(volatile uint32_t *)(uintptr_t)0x805880u;
  result=(uint32_t)callback;
  if (callback!=0u) result=((uint32_t (*)(uintptr_t))callback)(callback);
 }
 result=16u; /* Native bit3 branch delay slot. */
 if ((events&8u)!=0u) {
  uintptr_t payload=opencfw_em9305_ll_event_allocate(16u,1u);
  result=(uint32_t)payload;
  if (payload!=0u) {
   uint32_t value=*(volatile uint8_t *)(uintptr_t)0x805701u;
   *(volatile uint8_t *)payload=(uint8_t)value;
   result=opencfw_em9305_ll_event_send(payload-2u);
  }
 }
 if (started!=0u) {
  result=opencfw_em9305_pal_current_time();
  if (result!=0u) {
   uint32_t now=opencfw_em9305_pal_current_time();
   result=opencfw_em9305_pal_elapsed_raw(now,previous);
   uint32_t maximum=*(volatile uint16_t *)(uintptr_t)0x805838u;
   if (maximum<result) *(volatile uint16_t *)(uintptr_t)0x805838u=(uint16_t)result;
  }
 }
 return result;
}

extern uint32_t opencfw_em9305_ll_queued_event_active(uintptr_t); /*0x30a484*/
/* Native0x30cd6c..0x30cd80: queue message release or active processing. */
uint32_t opencfw_em9305_ll_queued_event(uintptr_t message)
{
 if (*(volatile uint8_t *)(uintptr_t)0x805ab4u!=0u)
  return opencfw_em9305_ll_queued_event_active(message);
 return opencfw_em9305_wsf_event_release(message);
}

/* Native0x303fac..0x303fb8: retain the base configuration pointer. */
uint32_t opencfw_em9305_ll_memory_configuration_set(uintptr_t configuration)
{
 *(volatile uint32_t *)(uintptr_t)0x805c18u=(uint32_t)configuration;
 return (uint32_t)configuration;
}
extern uint32_t opencfw_em9305_ll_memory_3033c0(uint32_t,uintptr_t,uint32_t);
extern uint32_t opencfw_em9305_ll_memory_303340(uint32_t,uintptr_t,uint32_t);
extern uint32_t opencfw_em9305_ll_memory_303380(uint32_t,uintptr_t,uint32_t);
/* Native0x30c1e8..0x30c228: sequential memory providers, wrapping size sum. */
uint32_t opencfw_em9305_ll_base_memory_initialize(uintptr_t configuration,uint32_t first_count,uint32_t second_count,uint32_t third_count,uintptr_t base,uint32_t available)
{
 (void)opencfw_em9305_ll_memory_configuration_set(configuration);
 uint32_t first=opencfw_em9305_ll_memory_3033c0(first_count,base,available);
 base+=first;available-=first;
 uint32_t third=opencfw_em9305_ll_memory_303340(third_count,base,available);
 base+=third;available-=third;
 uint32_t second=opencfw_em9305_ll_memory_303380(second_count,base,available);
 return second+third+first;
}
/* Native0x30c1c8..0x30c1d4: install the LL capability/configuration object. */
uint32_t opencfw_em9305_ll_configuration_set(uintptr_t configuration)
{
 *(volatile uint32_t *)(uintptr_t)0x805cacu=(uint32_t)configuration;
 return (uint32_t)configuration;
}
extern uint32_t opencfw_em9305_ll_memory_307158(uintptr_t,uint32_t);
extern uint32_t opencfw_em9305_ll_memory_3071a4(uintptr_t,uint32_t);
extern uint32_t opencfw_em9305_ll_memory_30705c(uintptr_t,uint32_t);
extern uint32_t opencfw_em9305_ll_memory_3070fc(uintptr_t,uint32_t);
extern uint32_t opencfw_em9305_ll_memory_3071f0(uintptr_t,uint32_t);
extern uint32_t opencfw_em9305_ll_memory_307210(uintptr_t,uint32_t);
extern uint32_t opencfw_em9305_ll_memory_30723c(uintptr_t,uint32_t);
/* Native0x30c228..0x30c2ac. Actual native tail aliases bind directly to source
 * providers at0x307xxx; no executable native addresses are invoked. */
uint32_t opencfw_em9305_ll_capability_memory_initialize(uintptr_t configuration,uintptr_t base,uint32_t available)
{
 (void)opencfw_em9305_ll_configuration_set(configuration);
 uint32_t total=0u,used;
 if (*(volatile uint8_t *)(configuration+34u)!=0u) {
  used=opencfw_em9305_ll_memory_307158(base,available);
  total+=used;base+=used;available-=used;
 }
 used=opencfw_em9305_ll_memory_3071a4(base,available);
 total+=used;base+=used;available-=used;
 used=opencfw_em9305_ll_memory_30705c(base,available);
 total+=used;base+=used;available-=used;
 used=opencfw_em9305_ll_memory_3070fc(base,available);
 total+=used;base+=used;available-=used;
 used=opencfw_em9305_ll_memory_3071f0(base,available);
 total+=used;base+=used;available-=used;
 used=opencfw_em9305_ll_memory_307210(base,available);
 total+=used;base+=used;available-=used;
 used=opencfw_em9305_ll_memory_30723c(base,available);
 return total+used;
}

uint32_t opencfw_em9305_ll_common_initialize(uint32_t); /*0x30c038*/
uint32_t opencfw_em9305_ll_auxiliary_initialize(uint32_t); /*0x30c1d4*/
extern uint32_t opencfw_em9305_ll_radio_initialize(uintptr_t); /*0x30c150*/
/* Native0x30bfec..0x30c038: consume two regions then initialize common/radio. */
uint32_t opencfw_em9305_ll_memory_construct(uintptr_t descriptor)
{
 uint32_t available=*(volatile uint32_t *)(descriptor+16u);
 uintptr_t base=*(volatile uint32_t *)(descriptor+12u);
 uint32_t third=*(volatile uint8_t *)(descriptor+6u);
 uint32_t second=*(volatile uint8_t *)(descriptor+5u);
 uint32_t first=*(volatile uint8_t *)(descriptor+4u);
 uintptr_t configuration=*(volatile uint32_t *)descriptor;
 uint32_t first_used=opencfw_em9305_ll_base_memory_initialize(configuration,first,second,third,base,available);
 base=*(volatile uint32_t *)(descriptor+12u);
 available=*(volatile uint32_t *)(descriptor+16u);
 base+=first_used;available-=first_used;
 uintptr_t capability=*(volatile uint32_t *)(descriptor+8u);
 *(volatile uint32_t *)(descriptor+12u)=(uint32_t)base;
 *(volatile uint32_t *)(descriptor+16u)=available;
 uint32_t second_used=opencfw_em9305_ll_capability_memory_initialize(capability,base,available);
 base=*(volatile uint32_t *)(descriptor+12u);
 available=*(volatile uint32_t *)(descriptor+16u);
 base+=second_used;available-=second_used;
 *(volatile uint32_t *)(descriptor+12u)=(uint32_t)base;
 *(volatile uint32_t *)(descriptor+16u)=available;
 uint32_t result=opencfw_em9305_ll_common_initialize(available);
 (void)opencfw_em9305_ll_auxiliary_initialize(result);
 (void)opencfw_em9305_ll_radio_initialize(*(volatile uint32_t *)(descriptor+8u));
 return second_used+first_used;
}
extern uint32_t opencfw_em9305_ll_special_mode_initialize(uint32_t); /*0x30cb7c*/
/* Native0x30c098..0x30c0c8: actual LL initialization entry. */
uint32_t opencfw_em9305_controller_ll_init(uintptr_t descriptor)
{
 uint32_t consumed=opencfw_em9305_ll_memory_construct(descriptor);
 uintptr_t config=*(volatile uint32_t *)(descriptor+8u);
 uint32_t second=*(volatile uint16_t *)(config+44u);
 /* Native0x30c0aa is the call delay slot: first is loaded before the call. */
 uint32_t first=*(volatile uint16_t *)(config+38u);
 uint32_t transport=opencfw_em9305_ll_transport_register(first,second);
 (void)opencfw_em9305_ll_providers_initialize(transport);
 (void)opencfw_em9305_ll_handler_initialize();
 (void)opencfw_em9305_ll_features_initialize();
 uint32_t status=opencfw_em9305_pal_status();
 if (status==2u) (void)opencfw_em9305_ll_special_mode_initialize(status);
 return consumed;
}

/* Native LL memory children: pointer writes occur even on capacity failure.
 * Counts are full-width for sizing, byte-truncated for stored metadata;
 * successful consumed sizes return only their low halfword. */
/* Native0x303340. */
uint32_t opencfw_em9305_ll_memory_303340(uint32_t count,uintptr_t base,uint32_t available)
{
 *(volatile uint8_t *)(uintptr_t)0x80160au=0u;
 *(volatile uint8_t *)(uintptr_t)0x80160bu=0u;
 uint32_t aligned=opencfw_em9305_controller_align_pointer((uint32_t)base);
 uint32_t required=aligned+count*12u-(uint32_t)base;
 *(volatile uint32_t *)(uintptr_t)0x805bfcu=aligned;
 if (available<required) return 0u;
 *(volatile uint8_t *)(uintptr_t)0x80160bu=(uint8_t)count;
 return (uint16_t)required;
}
/* Native0x303380. */
uint32_t opencfw_em9305_ll_memory_303380(uint32_t count,uintptr_t base,uint32_t available)
{
 *(volatile uint8_t *)(uintptr_t)0x801610u=0u;
 *(volatile uint8_t *)(uintptr_t)0x801611u=0u;
 uint32_t aligned=opencfw_em9305_controller_align_pointer((uint32_t)base);
 uint32_t required=aligned+count*72u-(uint32_t)base;
 *(volatile uint32_t *)(uintptr_t)0x805c00u=aligned;
 if (available<required) return 0u;
 *(volatile uint8_t *)(uintptr_t)0x801611u=(uint8_t)count;
 return (uint16_t)required;
}
/* Native0x3033c0. */
uint32_t opencfw_em9305_ll_memory_3033c0(uint32_t count,uintptr_t base,uint32_t available)
{
 *(volatile uint8_t *)(uintptr_t)0x801639u=0u;
 *(volatile uint8_t *)(uintptr_t)0x80163bu=0u;
 *(volatile uint8_t *)(uintptr_t)0x80163au=0u;
 uint32_t aligned=opencfw_em9305_controller_align_pointer((uint32_t)base);
 uint32_t required=aligned+count*8u-(uint32_t)base;
 *(volatile uint32_t *)(uintptr_t)0x805c04u=aligned;
 if (available<required) return 0u;
 *(volatile uint8_t *)(uintptr_t)0x80163bu=(uint8_t)count;
 return (uint16_t)required;
}

extern uint32_t opencfw_em9305_ll_memory_32d524(uintptr_t,uint32_t);
/* Native0x307158..0x3071a4: optional912-byte records then lower memory provider. */
uint32_t opencfw_em9305_ll_memory_307158(uintptr_t base,uint32_t available)
{
 uint32_t aligned=opencfw_em9305_controller_align_pointer((uint32_t)base);
 uintptr_t configuration=*(volatile uint32_t *)(uintptr_t)0x805cacu;
 uint32_t count=*(volatile uint8_t *)(configuration+34u);
 uint32_t end=aligned+count*912u;
 uint32_t required=end-(uint32_t)base;
 *(volatile uint32_t *)(uintptr_t)0x805c70u=aligned;
 if (available<required) return 0u;
 uint32_t additional=opencfw_em9305_ll_memory_32d524(end,available-required);
 if (additional==0u) return 0u;
 uint32_t consumed=end+additional-(uint32_t)base;
 *(volatile uint16_t *)(uintptr_t)0x805b1au=912u;
 return consumed;
}
/* Native0x3071a4..0x3071f0: nine independently aligned capability buffers.
 * Native writes all pointers before capacity rejection. Configuration/stride
 * are re-read each iteration, preserving volatile product state dependence. */
uint32_t opencfw_em9305_ll_memory_3071a4(uintptr_t base,uint32_t available)
{
 uint32_t cursor=(uint32_t)base;
 for (uint32_t index=0u;index<9u;index++) {
  cursor=opencfw_em9305_controller_align_pointer(cursor);
  uintptr_t configuration=*(volatile uint32_t *)(uintptr_t)0x805cacu;
  uintptr_t cell=index<3u?0x803b5cu+index*4u:0x803d58u+(index-3u)*4u;
  *(volatile uint32_t *)cell=cursor;
  uint32_t stride=*(volatile uint16_t *)(configuration+32u);
  cursor+=stride;
 }
 uint32_t consumed=cursor-(uint32_t)base;
 return consumed>available?0u:consumed;
}
extern uint32_t opencfw_em9305_ll_memory_31bc28(uintptr_t,uint32_t);
/* Native0x3071f0..0x307210: preserve unaligned original region end. */
uint32_t opencfw_em9305_ll_memory_3071f0(uintptr_t base,uint32_t available)
{
 uint32_t end=(uint32_t)base+available;
 uint32_t aligned=opencfw_em9305_controller_align_pointer((uint32_t)base);
 uint32_t used=opencfw_em9305_ll_memory_31bc28(aligned,end-aligned);
 return used==0u?0u:aligned+used-(uint32_t)base;
}

/* Native0x30705c..0x3070fc: main2824-byte records and three buffer arrays.
 * Configuration/count/stride are re-read after each pointer store; zero counts
 * can terminate subsequent array construction. Capacity is checked last. */
uint32_t opencfw_em9305_ll_memory_30705c(uintptr_t base,uint32_t available)
{
 uint32_t cursor=opencfw_em9305_controller_align_pointer((uint32_t)base);
 uintptr_t configuration=*(volatile uint32_t *)(uintptr_t)0x805cacu;
 uint32_t count=*(volatile uint8_t *)(configuration+12u);
 *(volatile uint32_t *)(uintptr_t)0x805c38u=cursor;
 cursor+=count*2824u;
 if (count!=0u) {
  uint32_t index=0u;
  do {
   cursor=opencfw_em9305_controller_align_pointer(cursor);
   configuration=*(volatile uint32_t *)(uintptr_t)0x805cacu;
   *(volatile uint32_t *)(uintptr_t)(0x8028b4u+index*4u)=cursor;
   index+=1u;
   count=*(volatile uint8_t *)(configuration+12u);
   uint32_t stride=*(volatile uint16_t *)(configuration+16u);
   cursor+=stride;
  } while (index<count);
  if (count!=0u) {
   index=0u;
   do {
    cursor=opencfw_em9305_controller_align_pointer(cursor);
    configuration=*(volatile uint32_t *)(uintptr_t)0x805cacu;
    *(volatile uint32_t *)(uintptr_t)(0x80519cu+index*4u)=cursor;
    index+=1u;
    count=*(volatile uint8_t *)(configuration+12u);
    uint32_t stride=*(volatile uint16_t *)(configuration+16u);
    cursor+=stride;
   } while (index<count);
   if (count!=0u) {
    index=0u;
    do {
     cursor=opencfw_em9305_controller_align_pointer(cursor);
     configuration=*(volatile uint32_t *)(uintptr_t)0x805cacu;
     *(volatile uint32_t *)(uintptr_t)(0x802850u+index*4u)=cursor;
     index+=1u;
     count=*(volatile uint8_t *)(configuration+12u);
     cursor+=8u;
    } while (index<count);
   }
  }
 }
 uint32_t consumed=cursor-(uint32_t)base;
 if (available<consumed) return 0u;
 *(volatile uint16_t *)(uintptr_t)0x805b1cu=2824u;
 return consumed;
}
/* Native0x3070fc..0x307158:256-byte and512-byte capability regions. */
uint32_t opencfw_em9305_ll_memory_3070fc(uintptr_t base,uint32_t available)
{
 uint32_t aligned=opencfw_em9305_controller_align_pointer((uint32_t)base);
 uintptr_t configuration=*(volatile uint32_t *)(uintptr_t)0x805cacu;
 *(volatile uint32_t *)(uintptr_t)0x805c40u=aligned;
 uint32_t first_count=*(volatile uint8_t *)(configuration+58u);
 uint32_t second_base=opencfw_em9305_controller_align_pointer(aligned+(first_count<<8u));
 configuration=*(volatile uint32_t *)(uintptr_t)0x805cacu;
 uint32_t second_count=*(volatile uint8_t *)(configuration+57u);
 uint32_t required=second_base+(second_count<<9u)-(uint32_t)base;
 *(volatile uint32_t *)(uintptr_t)0x805c3cu=second_base;
 if (available<required) return 0u;
 *(volatile uint32_t *)(uintptr_t)0x805b28u=0x02000100u;
 return required;
}

/* Native0x307210..0x30723c: capability halfword-sized region. */
uint32_t opencfw_em9305_ll_memory_307210(uintptr_t base,uint32_t available)
{
 uint32_t aligned=opencfw_em9305_controller_align_pointer((uint32_t)base);
 uintptr_t configuration=*(volatile uint32_t *)(uintptr_t)0x805cacu;
 *(volatile uint32_t *)(uintptr_t)0x805cecu=aligned;
 uint32_t size=*(volatile uint16_t *)(configuration+26u);
 uint32_t consumed=aligned+size-(uint32_t)base;
 return consumed>available?0u:consumed;
}
/* Native0x30723c..0x3072d0: two-stage record regions and spare-buffer queue.
 * All native pointer/queue writes precede final capacity rejection. */
uint32_t opencfw_em9305_ll_memory_30723c(uintptr_t base,uint32_t available)
{
 uint32_t cursor=(uint32_t)base,index=0u;
 uintptr_t row=0x80517cu;
 for (;;) {
  uintptr_t configuration=*(volatile uint32_t *)(uintptr_t)0x805cacu;
  uint32_t count=*(volatile uint8_t *)(configuration+13u);
  uint32_t first=opencfw_em9305_controller_align_pointer(cursor);
  cursor=first;
  if (index>=count) break;
  *(volatile uint32_t *)(row+4u)=first;
  uint32_t second=opencfw_em9305_controller_align_pointer(first+144u);
  *(volatile uint32_t *)row=second;
  row+=12u;cursor=second+3868u;index+=1u;
 }
 uintptr_t configuration=*(volatile uint32_t *)(uintptr_t)0x805cacu;
 *(volatile uint32_t *)(uintptr_t)0x805ce4u=cursor;
 *(volatile uint32_t *)(uintptr_t)0x805198u=0u;
 uint32_t count=*(volatile uint8_t *)(configuration+30u);
 uint32_t stride=*(volatile uint16_t *)(configuration+26u);
 *(volatile uint32_t *)(uintptr_t)0x805194u=0u;
 cursor+=stride;
 if (count!=0u) {
  index=0u;
  do {
   uint32_t aligned=opencfw_em9305_controller_align_pointer(cursor);
   configuration=*(volatile uint32_t *)(uintptr_t)0x805cacu;
   *(volatile uint32_t *)(uintptr_t)0x805ce8u=aligned;
   stride=*(volatile uint16_t *)(configuration+26u);
   (void)opencfw_em9305_wsf_queue_append(0x805194u,aligned);
   configuration=*(volatile uint32_t *)(uintptr_t)0x805cacu;
   index+=1u;
   count=*(volatile uint8_t *)(configuration+30u);
   cursor=aligned+stride;
  } while (index<count);
 }
 uint32_t consumed=cursor-(uint32_t)base;
 return consumed>available?0u:consumed;
}

/* Native0x31bc28..0x31bc7c:132-byte queue blocks, partial writes on failure. */
uint32_t opencfw_em9305_ll_memory_31bc28(uintptr_t base,uint32_t available)
{
 uint32_t cursor=(uint32_t)base,index=0u;
 *(volatile uint32_t *)(uintptr_t)0x8028ccu=0u;
 *(volatile uint32_t *)(uintptr_t)0x8028c8u=0u;
 *(volatile uint32_t *)(uintptr_t)0x805cd0u=0u;
 for (;;) {
  uintptr_t configuration=*(volatile uint32_t *)(uintptr_t)0x805cacu;
  uint32_t count=*(volatile uint8_t *)(configuration+42u);
  if (index>=count) return cursor-(uint32_t)base;
  uint32_t aligned=opencfw_em9305_controller_align_pointer(cursor);
  cursor=aligned+132u;
  if (available<cursor-(uint32_t)base) return 0u;
  (void)opencfw_em9305_wsf_queue_append(0x8028c8u,aligned);
  index+=1u;
 }
}
/* Native0x32d524..0x32d598: custom-opcode-sized queue blocks.
 * The 0x06/0x1e instruction is preserved by native_config_product; this source
 * makes no unqualified multiplication/high-word arithmetic substitution. */
uint32_t opencfw_em9305_ll_memory_32d524(uintptr_t base,uint32_t available)
{
 uintptr_t configuration=*(volatile uint32_t *)(uintptr_t)0x805cacu;
 uint32_t length=*(volatile uint16_t *)(configuration+38u);
 uint32_t product=opencfw_em9305_native_config_product(0x12f69u,length);
 *(volatile uint32_t *)(uintptr_t)0x805cd4u=0u;
 uint32_t bytes=(((product+0x1ed0aau)>>18u)&~7u)+16u;
 *(volatile uint32_t *)(uintptr_t)0x8056e0u=0u;
 *(volatile uint32_t *)(uintptr_t)0x8056dcu=0u;
 uint32_t cursor=(uint32_t)base,index=0u;
 for (;;) {
  uint32_t count=*(volatile uint8_t *)(configuration+35u);
  if (index>=count) return cursor-(uint32_t)base;
  uint32_t aligned=opencfw_em9305_controller_align_pointer(cursor);
  cursor=aligned+bytes;
  if (available<cursor-(uint32_t)base) return 0u;
  (void)opencfw_em9305_wsf_queue_append(0x8056dcu,aligned);
  configuration=*(volatile uint32_t *)(uintptr_t)0x805cacu;
  index+=1u;
 }
}

/* Native0x304360..0x30436a: install the auxiliary callback, retaining R0. */
uint32_t opencfw_em9305_auxiliary_callback_install(uintptr_t callback)
{
 *(volatile uint32_t *)(uintptr_t)0x801640u=(uint32_t)callback;
 return (uint32_t)callback;
}
/* These callback bodies remain explicit source contracts. */
extern void opencfw_em9305_auxiliary_callback_333a00(void);
extern void opencfw_em9305_auxiliary_handler_312ca0(void);
/* Native0x312d80..0x312da4: reset record then install handler and callback.
 * The handler byte store occupies the call delay slot and precedes install. */
uint32_t opencfw_em9305_auxiliary_record_initialize(uint32_t handler)
{
 (void)opencfw_em9305_memset((void *)(uintptr_t)0x805f04u,0u,36u);
 *(volatile uint8_t *)(uintptr_t)0x805f05u=(uint8_t)handler;
 return opencfw_em9305_auxiliary_callback_install(
  (uintptr_t)&opencfw_em9305_auxiliary_callback_333a00);
}
/* Native0x30c1d4..0x30c1e8: registration followed by auxiliary record init.
 * Incoming R0 is replaced before registration; callback ABI remains unqualified. */
uint32_t opencfw_em9305_ll_auxiliary_initialize(uint32_t unused)
{
 (void)unused;
 uint32_t handler=opencfw_em9305_controller_wsf_register(
  (uintptr_t)&opencfw_em9305_auxiliary_handler_312ca0);
 return opencfw_em9305_auxiliary_record_initialize(handler);
}

/* Native0x333a00..0x333a30: enqueue completion only in state 2.
 * BMSK bit 1 retains two bits; the four-entry ring is not a two-entry ring. */
void opencfw_em9305_auxiliary_callback_333a00(void)
{
 uintptr_t root=0x805f04u;
 if (*(volatile uint8_t *)root==2u) {
  uint32_t index=*(volatile uint32_t *)(root+4u);
  *(volatile uint8_t *)(root+12u+index)=1u;
  *(volatile uint32_t *)(root+4u)=(index+1u)&3u;
  (void)opencfw_em9305_wsf_event_post(*(volatile uint8_t *)(root+1u),1u);
 }
}
/* Native0x333a30..0x333a60: enqueue idle only in state 1. */
void opencfw_em9305_auxiliary_callback_333a30(void)
{
 uintptr_t root=0x805f04u;
 if (*(volatile uint8_t *)root==1u) {
  uint32_t index=*(volatile uint32_t *)(root+4u);
  *(volatile uint8_t *)(root+12u+index)=0u;
  *(volatile uint32_t *)(root+4u)=(index+1u)&3u;
  (void)opencfw_em9305_wsf_event_post(*(volatile uint8_t *)(root+1u),1u);
 }
}

/* Remaining auxiliary child bodies are source contracts, not stock jumps. */
extern uint32_t opencfw_em9305_auxiliary_elapsed_303f8c(uint32_t,uint32_t);
extern uint32_t opencfw_em9305_auxiliary_prepare_303ef0(uintptr_t);
extern uint32_t opencfw_em9305_auxiliary_start_303f50(uintptr_t);
extern uint32_t opencfw_em9305_auxiliary_ready_303f68(void);
extern uint32_t opencfw_em9305_auxiliary_signal_304394(void);
uint32_t opencfw_em9305_auxiliary_stop_333780(void);
extern uint32_t opencfw_em9305_auxiliary_arm_333690(void);
extern uint32_t opencfw_em9305_auxiliary_expire_3339cc(void);
void opencfw_em9305_auxiliary_callback_333a30(void);
/* Native0x312ca0..0x312d80: drain four-entry auxiliary events and track elapsed.
 * Child contracts with ambient native argument registers retain ABI gates. */
void opencfw_em9305_auxiliary_handler_312ca0(void)
{
 uintptr_t root=0x805f04u;
 uint32_t started=opencfw_em9305_pal_current_time();
 for (;;) {
  uint32_t read=*(volatile uint32_t *)(root+8u);
  if (read==*(volatile uint32_t *)(root+4u)) break;
  uint32_t event=*(volatile uint8_t *)(root+12u+read);
  uintptr_t object=*(volatile uint32_t *)(root+16u);
  *(volatile uint32_t *)(root+8u)=(read+1u)&3u;
  if (object==0u) goto clear_state;
  uint32_t state=*(volatile uint8_t *)root;
  if (state==0u) {
   if (event==3u) goto arm;
   goto check_object;
  }
  if (state==2u) {
   if (event==2u) {
    if (opencfw_em9305_auxiliary_ready_303f68()!=0u) {
     (void)opencfw_em9305_auxiliary_signal_304394();
     goto check_object;
    }
   } else if (event==1u) {
    (void)opencfw_em9305_auxiliary_stop_333780();
    uintptr_t callback=*(volatile uint32_t *)(object+28u);
    *(volatile uint8_t *)root=3u;
    if (callback!=0u) ((void (*)(uintptr_t))callback)(object);
    goto callback_done;
   } else continue;
   (void)opencfw_em9305_auxiliary_stop_333780();
   uintptr_t callback=*(volatile uint32_t *)(object+32u);
   *(volatile uint8_t *)root=3u;
   if (callback!=0u) ((void (*)(uintptr_t))callback)(object);
callback_done:
   if (*(volatile uint32_t *)(root+16u)==0u) goto clear_state;
   goto arm;
  }
  if (state!=1u) continue;
  if (event==3u) {
   (void)opencfw_em9305_pal_timer_disarm();
   goto arm;
  }
  if (event==2u) {
   (void)opencfw_em9305_auxiliary_stop_333780();
   uintptr_t callback=*(volatile uint32_t *)(object+32u);
   *(volatile uint8_t *)root=3u;
   if (callback!=0u) ((void (*)(uintptr_t))callback)(object);
   if (*(volatile uint32_t *)(root+16u)==0u) goto clear_state;
   goto arm;
  }
  if (event!=0u) continue;
  *(volatile uint8_t *)root=2u;
  uint32_t now=opencfw_em9305_pal_current_time();
  if (opencfw_em9305_auxiliary_elapsed_303f8c(
      *(volatile uint32_t *)(object+8u),now+25u)==0u &&
      *(volatile uint8_t *)(object+27u)==0u) {
   (void)opencfw_em9305_auxiliary_expire_3339cc();
  } else {
   (void)opencfw_em9305_auxiliary_prepare_303ef0(object);
   if (opencfw_em9305_auxiliary_start_303f50(object)!=0u)
    opencfw_em9305_auxiliary_callback_333a00();
  }
  goto check_object;
arm:
  *(volatile uint8_t *)root=1u;
  if (opencfw_em9305_auxiliary_arm_333690()==0u)
   opencfw_em9305_auxiliary_callback_333a30();
check_object:
  if (*(volatile uint32_t *)(root+16u)!=0u) continue;
clear_state:
  *(volatile uint8_t *)root=0u;
 }
 uint32_t elapsed=opencfw_em9305_auxiliary_elapsed_303f8c(
  opencfw_em9305_pal_current_time(),started);
 if (*(volatile uint16_t *)(root+24u)<elapsed)
  *(volatile uint16_t *)(root+24u)=(uint16_t)elapsed;
}

/* Native0x303f8c..0x303f94: wrapping subtraction followed by signed MAX zero. */
uint32_t opencfw_em9305_auxiliary_elapsed_303f8c(uint32_t current,uint32_t previous)
{
 uint32_t difference=current-previous;
 return (difference&0x80000000u)!=0u?0u:difference;
}
/* Native0x303f50..0x303f5c: incoming object is unused. */
uint32_t opencfw_em9305_auxiliary_start_303f50(uintptr_t unused)
{
 (void)unused;
 return *(volatile uint8_t *)(uintptr_t)0x8016beu;
}
/* Native0x303f68..0x303f74: current auxiliary object, not a boolean cell. */
uint32_t opencfw_em9305_auxiliary_ready_303f68(void)
{ return *(volatile uint32_t *)(uintptr_t)0x80163cu; }
/* Native0x304394..0x3043ac: return zero when no object, otherwise flag address. */
uint32_t opencfw_em9305_auxiliary_signal_304394(void)
{
 if (*(volatile uint32_t *)(uintptr_t)0x80163cu==0u) return 0u;
 *(volatile uint8_t *)(uintptr_t)0x8016beu=1u;
 return 0x8016beu;
}

/* Native0x3339cc..0x333a00: expire events only for states 1 and 2.
 * The unsigned state-minus-one gate also excludes state zero. */
uint32_t opencfw_em9305_auxiliary_expire_3339cc(void)
{
 uintptr_t root=0x805f04u;
 uint32_t adjusted=(uint32_t)*(volatile uint8_t *)root-1u;
 if (adjusted>=2u) return adjusted;
 (void)opencfw_em9305_pal_timer_disarm();
 uint32_t index=*(volatile uint32_t *)(root+4u);
 *(volatile uint8_t *)(root+12u+index)=2u;
 *(volatile uint32_t *)(root+4u)=(index+1u)&3u;
 return opencfw_em9305_wsf_event_post(*(volatile uint8_t *)(root+1u),1u);
}

extern uint32_t opencfw_em9305_auxiliary_select_314d94(uint32_t);
/* Native0x303ef0..0x303f50: choose the product provider and prepare object.
 * 0x30fd2c is an authenticated J [blink] no-op; no guessed hardware action. */
uint32_t opencfw_em9305_auxiliary_prepare_303ef0(uintptr_t object)
{
 uintptr_t root=0x80163cu;
 uint32_t active=*(volatile uint8_t *)(root+129u);
 *(volatile uint8_t *)(root+130u)=0u;
 *(volatile uint32_t *)root=(uint32_t)object;
 if (active!=0u || *(volatile uint8_t *)(root+129u)!=0u) {
  uint32_t current=*(volatile uint8_t *)(root+128u);
  uint32_t requested=*(volatile uint8_t *)(object+26u);
  if (current!=requested) {
   uintptr_t callback=*(volatile uint32_t *)(root+current*24u+20u);
   *(volatile uint8_t *)(root+129u)=0u;
   (void)((uint32_t (*)(uintptr_t))callback)(callback);
   if (*(volatile uint8_t *)(root+129u)==0u)
    (void)opencfw_em9305_auxiliary_select_314d94(
     *(volatile uint8_t *)(object+26u));
  }
 } else {
  (void)opencfw_em9305_auxiliary_select_314d94(
   *(volatile uint8_t *)(object+26u));
 }
 uint32_t requested=*(volatile uint8_t *)(object+26u);
 uintptr_t record=root+requested*24u;
 uintptr_t callback=*(volatile uint32_t *)(record+8u);
 if (callback!=0u) return ((uint32_t (*)(uintptr_t))callback)(object);
 return (uint32_t)record;
}

/* Native0x314d94..0x314db8: provider callback followed by selection flags.
 * The indirect call retains its own address in native R0; ABI unqualified.
 * 0x30fd6c is authenticated J[blink], so the final return is the index. */
uint32_t opencfw_em9305_auxiliary_select_314d94(uint32_t index)
{
 uintptr_t callback=*(volatile uint32_t *)(uintptr_t)(0x80164cu+index*24u);
 (void)((uint32_t (*)(uintptr_t))callback)(callback);
 *(volatile uint8_t *)(uintptr_t)0x8016bcu=(uint8_t)index;
 *(volatile uint8_t *)(uintptr_t)0x8016bdu=1u;
 return index;
}

/* Native0x333a60..0x333a94: request transition from idle or waiting states. */
uint32_t opencfw_em9305_auxiliary_transition_333a60(void)
{
 uintptr_t root=0x805f04u;
 uint32_t state=*(volatile uint8_t *)root;
 if (state!=0u && state!=1u) return state;
 if (state==1u) (void)opencfw_em9305_pal_timer_disarm();
 uint32_t index=*(volatile uint32_t *)(root+4u);
 *(volatile uint8_t *)(root+12u+index)=3u;
 *(volatile uint32_t *)(root+4u)=(index+1u)&3u;
 return opencfw_em9305_wsf_event_post(*(volatile uint8_t *)(root+1u),1u);
}

/* Native0x303f80..0x303f8c: configured auxiliary guard interval. */
uint32_t opencfw_em9305_auxiliary_guard_interval(void)
{
 uintptr_t configuration=*(volatile uint32_t *)(uintptr_t)0x805c18u;
 return *(volatile uint16_t *)(configuration+6u);
}
/* Native0x333780..0x333804: remove current object, reinsert deferred object.
 * Preserve path-specific R0 for the newly recovered313354 caller.
 * BN tests subtraction sign bit. */
uint32_t opencfw_em9305_auxiliary_stop_333780(void)
{
 uintptr_t root=0x805f04u;
 uintptr_t current=*(volatile uint32_t *)(root+16u);
 uintptr_t next=*(volatile uint32_t *)(current+4u);
 *(volatile uint32_t *)(root+16u)=(uint32_t)next;
 if (next!=0u) *(volatile uint32_t *)next=0u;
 else *(volatile uint32_t *)(root+20u)=0u;
 uintptr_t deferred=*(volatile uint32_t *)(root+28u);
 if (deferred==0u) return (uint32_t)next;
 uint32_t now=opencfw_em9305_pal_current_time();
 uint32_t deadline=now+opencfw_em9305_auxiliary_guard_interval();
 *(volatile uint32_t *)(deferred+8u)=deadline;
 uint32_t remaining=opencfw_em9305_auxiliary_elapsed_303f8c(
  *(volatile uint32_t *)(root+32u),deadline);
 if (remaining==0u) {
  uintptr_t callback=*(volatile uint32_t *)(deferred+32u);
  uint32_t result=0u;
  if (callback!=0u) result=((uint32_t (*)(uintptr_t,uintptr_t))callback)(deferred,callback);
  *(volatile uint32_t *)(root+28u)=0u;
  return result;
 }
 next=*(volatile uint32_t *)(root+16u);
 if (next==0u) {
  *(volatile uint32_t *)(root+20u)=(uint32_t)deferred;
  *(volatile uint32_t *)(root+16u)=(uint32_t)deferred;
  *(volatile uint32_t *)(deferred+4u)=0u;
  *(volatile uint32_t *)deferred=0u;
  *(volatile uint32_t *)(root+28u)=0u;
 } else {
  uint32_t end=*(volatile uint32_t *)(deferred+8u)+
   *(volatile uint32_t *)(deferred+16u);
  uint32_t next_time=*(volatile uint32_t *)(next+8u);
  if (((next_time-end)&0x80000000u)!=0u) {
   uint32_t pending=*(volatile uint32_t *)(root+28u);
   if (pending!=0u) return pending;
  } else {
   uintptr_t previous=*(volatile uint32_t *)next;
   *(volatile uint32_t *)(deferred+4u)=(uint32_t)next;
   *(volatile uint32_t *)deferred=(uint32_t)previous;
   *(volatile uint32_t *)next=(uint32_t)deferred;
   if (previous!=0u) *(volatile uint32_t *)(previous+4u)=(uint32_t)deferred;
   else *(volatile uint32_t *)(root+16u)=(uint32_t)deferred;
   *(volatile uint32_t *)(root+28u)=0u;
  }
 }
 return opencfw_em9305_auxiliary_transition_333a60();
}

/* Native0x310110..0x310128: timer deadline, callback, then channel0 enable. */
uint32_t opencfw_em9305_auxiliary_timer_schedule(uint32_t deadline,uintptr_t callback)
{
 *(volatile uint32_t *)(uintptr_t)0xf0181cu=deadline;
 *(volatile uint32_t *)(uintptr_t)0x805e6cu=(uint32_t)callback;
 return opencfw_em9305_pal_timer_channel(0u,1u);
}
/* Native0x333690..0x3336d8: sample head before critical-entry delay slot,
 * test signed-clamped delay against guard+25, then schedule and exit. */
uint32_t opencfw_em9305_auxiliary_arm_333690(void)
{
 uintptr_t object=*(volatile uint32_t *)(uintptr_t)0x805f14u;
 (void)opencfw_em9305_wsf_critical_enter();
 uint32_t now=opencfw_em9305_pal_current_time();
 uint32_t guard=opencfw_em9305_auxiliary_guard_interval();
 uint32_t remaining=opencfw_em9305_auxiliary_elapsed_303f8c(
  *(volatile uint32_t *)(object+8u),now);
 uint32_t threshold=guard+25u;
 if (remaining>=threshold) {
  uint32_t deadline=*(volatile uint32_t *)(object+8u)-guard;
  (void)opencfw_em9305_auxiliary_timer_schedule(deadline,
   (uintptr_t)&opencfw_em9305_auxiliary_callback_333a30);
 }
 uint32_t ready=remaining>=threshold;
 (void)opencfw_em9305_wsf_critical_exit();
 return ready;
}

/* Native0x314538..0x314548: source callback registry, secondary before primary. */
uint32_t opencfw_em9305_common_callback_register(uint32_t index,uintptr_t primary,uintptr_t secondary)
{
 uintptr_t slot=0x801534u+index*8u;
 *(volatile uint32_t *)(slot+4u)=(uint32_t)secondary;
 *(volatile uint32_t *)slot=(uint32_t)primary;
 return index;
}
uint32_t opencfw_em9305_common_callback_3152bc(uintptr_t);
uint32_t opencfw_em9305_common_callback_3151cc(uint32_t);
extern uint32_t opencfw_em9305_common_callback_3152fc(uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_common_callback_3153fc(uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_common_callback_31481c(uintptr_t,uintptr_t);
extern void opencfw_em9305_common_callback_314888(uintptr_t,uintptr_t);
uint32_t opencfw_em9305_common_callback_314728(uint32_t);
/* Native0x302e90..0x302ea4: callback pair slot3. */
uint32_t opencfw_em9305_common_init_302e90(void)
{ return opencfw_em9305_common_callback_register(3u,
 (uintptr_t)&opencfw_em9305_common_callback_3152bc,
 (uintptr_t)&opencfw_em9305_common_callback_3151cc); }
/* Native0x302ea4..0x302ec8: ordered slot7 then slot8. */
uint32_t opencfw_em9305_common_init_302ea4(void)
{
 (void)opencfw_em9305_common_callback_register(7u,
  (uintptr_t)&opencfw_em9305_common_callback_3152fc,0u);
 return opencfw_em9305_common_callback_register(8u,
  (uintptr_t)&opencfw_em9305_common_callback_3153fc,0u);
}
/* Native0x302ec8..0x302ed8: slot6. */
uint32_t opencfw_em9305_common_init_302ec8(void)
{ return opencfw_em9305_common_callback_register(6u,
 (uintptr_t)&opencfw_em9305_common_callback_31481c,0u); }
/* Native0x302ed8..0x302f00: slot12 then clear28-byte record. */
uintptr_t opencfw_em9305_common_init_302ed8(void)
{
 (void)opencfw_em9305_common_callback_register(12u,
  (uintptr_t)&opencfw_em9305_common_callback_314888,
  (uintptr_t)&opencfw_em9305_common_callback_314728);
 return (uintptr_t)opencfw_em9305_memset((void *)(uintptr_t)0x801518u,0u,28u);
}

extern uint32_t opencfw_em9305_common_init_303f94(uint32_t);
extern uint32_t opencfw_em9305_common_init_3032cc(uint32_t);
extern uint32_t opencfw_em9305_common_init_3102fc(uint32_t);
extern uint32_t opencfw_em9305_common_init_303d18(uint32_t);
extern uint32_t opencfw_em9305_common_init_302ff4(uint32_t);
extern uint32_t opencfw_em9305_common_init_303008(uint32_t);
extern uint32_t opencfw_em9305_common_init_303650(uint32_t);
extern uint32_t opencfw_em9305_common_init_302f80(uint32_t);
extern uint32_t opencfw_em9305_common_init_303d2c(uint32_t);
/* Native0x30c038..0x30c074: thirteen ordered common providers.
 * Unreduced children retain incoming R0 as an explicit source contract. */
uint32_t opencfw_em9305_ll_common_initialize(uint32_t value)
{
 value=opencfw_em9305_common_init_303f94(value);
 value=opencfw_em9305_common_init_3032cc(value);
 value=opencfw_em9305_common_init_3102fc(value);
 value=opencfw_em9305_common_init_303d18(value);
 value=opencfw_em9305_common_init_302ff4(value);
 value=opencfw_em9305_common_init_302e90();
 value=opencfw_em9305_common_init_303008(value);
 value=opencfw_em9305_common_init_302ec8();
 value=opencfw_em9305_common_init_303650(value);
 value=opencfw_em9305_common_init_302ea4();
 value=(uint32_t)opencfw_em9305_common_init_302ed8();
 value=opencfw_em9305_common_init_302f80(value);
 return opencfw_em9305_common_init_303d2c(value);
}

extern uint32_t opencfw_em9305_common_callback_3148cc(uintptr_t,uintptr_t);
uint32_t opencfw_em9305_common_callback_31472c(uint32_t,uintptr_t);
uint32_t opencfw_em9305_common_callback_3153bc(uintptr_t,uintptr_t);
uint32_t opencfw_em9305_common_callback_3151d4(uint32_t,uintptr_t);
extern uint32_t opencfw_em9305_common_callback_3149d4(uintptr_t,uintptr_t);
uint32_t opencfw_em9305_common_callback_314754(uint32_t);
/* Native0x302ff4..0x303008: callback pair slot4; incoming R0 replaced. */
uint32_t opencfw_em9305_common_init_302ff4(uint32_t unused)
{
 (void)unused;
 return opencfw_em9305_common_callback_register(4u,
  (uintptr_t)&opencfw_em9305_common_callback_3148cc,
  (uintptr_t)&opencfw_em9305_common_callback_31472c);
}
/* Native0x303008..0x30301c: callback pair slot5. */
uint32_t opencfw_em9305_common_init_303008(uint32_t unused)
{
 (void)unused;
 return opencfw_em9305_common_callback_register(5u,
  (uintptr_t)&opencfw_em9305_common_callback_3153bc,
  (uintptr_t)&opencfw_em9305_common_callback_3151d4);
}
/* Native0x303d18..0x303d2c: callback pair slot2. */
uint32_t opencfw_em9305_common_init_303d18(uint32_t unused)
{
 (void)unused;
 return opencfw_em9305_common_callback_register(2u,
  (uintptr_t)&opencfw_em9305_common_callback_3149d4,
  (uintptr_t)&opencfw_em9305_common_callback_314754);
}

extern uint32_t opencfw_em9305_common_callback_3154e0(uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_common_callback_315534(uint32_t);
extern uint32_t opencfw_em9305_common_callback_315490(uintptr_t,uintptr_t);
/* Native0x303d2c..0x303d58: ordered pair slots0 and1, shared secondary. */
uint32_t opencfw_em9305_common_init_303d2c(uint32_t unused)
{
 (void)unused;
 (void)opencfw_em9305_common_callback_register(0u,
  (uintptr_t)&opencfw_em9305_common_callback_3154e0,
  (uintptr_t)&opencfw_em9305_common_callback_315534);
 return opencfw_em9305_common_callback_register(1u,
  (uintptr_t)&opencfw_em9305_common_callback_315490,
  (uintptr_t)&opencfw_em9305_common_callback_315534);
}
/* Native0x303f94..0x303fac: hook30fd38 is J[blink], then clear132 bytes. */
uint32_t opencfw_em9305_common_init_303f94(uint32_t unused)
{
 (void)unused;
 return (uint32_t)(uintptr_t)opencfw_em9305_memset(
  (void *)(uintptr_t)0x80163cu,0u,132u);
}

void opencfw_em9305_common_callback_31537c(uintptr_t,uintptr_t);
uint32_t opencfw_em9305_common_callback_3151d0(uint32_t);
/* Native0x302f80..0x302fa8: slot13 then clear shared28-byte record. */
uint32_t opencfw_em9305_common_init_302f80(uint32_t unused)
{
 (void)unused;
 (void)opencfw_em9305_common_callback_register(13u,
  (uintptr_t)&opencfw_em9305_common_callback_31537c,
  (uintptr_t)&opencfw_em9305_common_callback_3151d0);
 return (uint32_t)(uintptr_t)opencfw_em9305_memset(
  (void *)(uintptr_t)0x801518u,0u,28u);
}

extern uint32_t opencfw_em9305_common_callback_314908(uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_common_callback_31497c(uintptr_t);
/* Native0x303650..0x303674: slot9 followed by slot15. */
uint32_t opencfw_em9305_common_init_303650(uint32_t unused)
{
 (void)unused;
 (void)opencfw_em9305_common_callback_register(9u,
  (uintptr_t)&opencfw_em9305_common_callback_314908,0u);
 return opencfw_em9305_common_callback_register(15u,
  (uintptr_t)&opencfw_em9305_common_callback_31497c,0u);
}

/* Native0x3102fc..0x310314: ordered halfword masks, native address return. */
uint32_t opencfw_em9305_common_init_3102fc(uint32_t unused)
{
 (void)unused;
 *(volatile uint16_t *)(uintptr_t)0x8012ecu=15u;
 *(volatile uint16_t *)(uintptr_t)0x8012eeu=15u;
 return 0x8012eeu;
}
/* Native0x30436c..0x304384: four callbacks in native reverse store order. */
uintptr_t opencfw_em9305_common_provider_register(uint32_t index,uintptr_t a,uintptr_t b,uintptr_t c,uintptr_t d)
{
 uintptr_t slot=0x801644u+index*24u;
 *(volatile uint32_t *)(slot+12u)=(uint32_t)d;
 *(volatile uint32_t *)(slot+8u)=(uint32_t)c;
 *(volatile uint32_t *)(slot+4u)=(uint32_t)b;
 *(volatile uint32_t *)slot=(uint32_t)a;
 return slot;
}
/* Native0x304384..0x304394: fifth provider callback. */
uintptr_t opencfw_em9305_common_provider_extra(uint32_t index,uintptr_t callback)
{
 uintptr_t slot=0x801654u+index*24u;
 *(volatile uint32_t *)slot=(uint32_t)callback;
 return slot;
}

extern uint32_t opencfw_em9305_common_hardware_31028c(uint32_t);
uint32_t opencfw_em9305_common_callback_3143f4(uintptr_t);
extern void opencfw_em9305_common_callback_314548(void);
extern uint32_t opencfw_em9305_common_callback_314408(uintptr_t);
uint32_t opencfw_em9305_common_callback_314580(uint32_t);
extern void opencfw_em9305_common_callback_314558(void);
extern void opencfw_em9305_common_callback_314568(void);
uint32_t opencfw_em9305_common_callback_314584(uint32_t);
uint32_t opencfw_em9305_common_callback_31446c(uint32_t);
/* Native0x3032cc..0x303340: hardware init, provider slots1/2/3,
 * extra slot1 callback, then clear the176-byte common callback registry. */
uint32_t opencfw_em9305_common_init_3032cc(uint32_t incoming)
{
 (void)opencfw_em9305_common_hardware_31028c(incoming);
 (void)opencfw_em9305_common_provider_register(1u,
  (uintptr_t)&opencfw_em9305_common_callback_314408,
  (uintptr_t)&opencfw_em9305_common_callback_3143f4,
  (uintptr_t)&opencfw_em9305_common_callback_314548,
  (uintptr_t)&opencfw_em9305_common_callback_314580);
 (void)opencfw_em9305_common_provider_register(2u,
  (uintptr_t)&opencfw_em9305_common_callback_314408,
  (uintptr_t)&opencfw_em9305_common_callback_3143f4,
  (uintptr_t)&opencfw_em9305_common_callback_314558,
  (uintptr_t)&opencfw_em9305_common_callback_314580);
 (void)opencfw_em9305_common_provider_register(3u,0u,
  (uintptr_t)&opencfw_em9305_common_callback_3143f4,
  (uintptr_t)&opencfw_em9305_common_callback_314568,
  (uintptr_t)&opencfw_em9305_common_callback_314584);
 (void)opencfw_em9305_common_provider_extra(1u,
  (uintptr_t)&opencfw_em9305_common_callback_31446c);
 return (uint32_t)(uintptr_t)opencfw_em9305_memset(
  (void *)(uintptr_t)0x801534u,0u,176u);
}

extern uint32_t opencfw_em9305_common_radio_mask_312094(uint32_t);
extern uint32_t opencfw_em9305_common_irq_mask_310ba4(uint32_t,uint32_t);
extern uint32_t opencfw_em9305_common_timer_mask_310bd0(uint32_t,uint32_t);
extern uint32_t opencfw_em9305_common_calibrate_311ffc(uint32_t,uint32_t);
extern uint32_t opencfw_em9305_common_limit_310314(uint32_t);
/* Native0x31028c..0x3102fc: common radio record and ordered MMIO init.
 * Resident ROM0x103b0c remains an explicit native ABI facade. */
uint32_t opencfw_em9305_common_hardware_31028c(uint32_t unused)
{
 (void)unused;
 (void)opencfw_em9305_memset((void *)(uintptr_t)0x805e78u,0u,80u);
 (void)((uint32_t (*)(uint32_t))(uintptr_t)0x103b0cu)(3u);
 (void)opencfw_em9305_common_radio_mask_312094(255u);
 *(volatile uint32_t *)(uintptr_t)0xf04044u=72u;
 *(volatile uint8_t *)(uintptr_t)0xf01845u=1u;
 (void)opencfw_em9305_common_irq_mask_310ba4(1u,1u);
 *(volatile uint8_t *)(uintptr_t)0xf01844u=2u;
 (void)opencfw_em9305_common_irq_mask_310ba4(0u,1u);
 *(volatile uint8_t *)(uintptr_t)0xf01847u=0u;
 (void)opencfw_em9305_common_irq_mask_310ba4(3u,1u);
 (void)opencfw_em9305_common_timer_mask_310bd0(1u,1u);
 uint32_t result=opencfw_em9305_common_calibrate_311ffc(600u,1u);
 *(volatile uint8_t *)(uintptr_t)0x805e78u=1u;
 return opencfw_em9305_common_limit_310314(result);
}

/* Native0x310ba4..0x310bd0: low-nibble IRQ mask with native IRQ window. */
uint32_t opencfw_em9305_common_irq_mask_310ba4(uint32_t index,uint32_t enable)
{
 uint32_t mask=1u,flags;
 __asm__ volatile("asl %0,%0,%1" : "+r"(mask) : "r"(index));
 mask&=15u;
 __asm__ volatile("clri %0\n\tsync" : "=r"(flags) :: "memory");
 uint32_t prior=*(volatile uint8_t *)(uintptr_t)0xf0183eu;
 uint32_t result=mask;
 if (enable!=0u) {
  result=mask|prior;
  *(volatile uint8_t *)(uintptr_t)0xf0183eu=(uint8_t)result;
 } else {
  *(volatile uint8_t *)(uintptr_t)0xf0183eu=(uint8_t)(prior&~mask);
 }
 __asm__ volatile("seti %0" :: "r"(flags) : "memory");
 return result;
}
/* Native0x310bd0..0x310c08: timer high-byte mask and updated word return. */
uint32_t opencfw_em9305_common_timer_mask_310bd0(uint32_t index,uint32_t enable)
{
 uint32_t mask=0x10000u,flags;
 __asm__ volatile("asl %0,%0,%1" : "+r"(mask) : "r"(index));
 mask&=0xff0000u;
 __asm__ volatile("clri %0\n\tsync" : "=r"(flags) :: "memory");
 uint32_t word=*(volatile uint32_t *)(uintptr_t)0xf01818u;
 word=enable!=0u?word|mask:word&~mask;
 *(volatile uint32_t *)(uintptr_t)0xf01818u=word;
 __asm__ volatile("seti %0" :: "r"(flags) : "memory");
 return word;
}

/* Native0x312094..0x3120a0: BMSK bit8 retains nine bits, halfword store. */
uint32_t opencfw_em9305_common_radio_mask_312094(uint32_t value)
{
 value&=0x1ffu;
 *(volatile uint16_t *)(uintptr_t)0xf0404cu=(uint16_t)value;
 return value;
}
extern uint32_t opencfw_em9305_common_packet_limit_3047fc(uint32_t);
/* Native0x310314..0x310328: lower result byte and untruncated return. */
uint32_t opencfw_em9305_common_limit_310314(uint32_t incoming)
{
 uint32_t result=opencfw_em9305_common_packet_limit_3047fc(incoming);
 *(volatile uint8_t *)(uintptr_t)0x8012b8u=(uint8_t)result;
 return result;
}

extern uint32_t opencfw_em9305_packet_default_30f65c(uint32_t);
extern uint32_t opencfw_em9305_packet_revision_3119b0(uintptr_t);
/* Native0x3047fc..0x30482c: signed byte result with revision-dependent clamp.
 * Probe failure returns revision output, not the default provider value. */
uint32_t opencfw_em9305_common_packet_limit_3047fc(uint32_t incoming)
{
 uint8_t revision=0u;
 (void)incoming;
 uint32_t probed=opencfw_em9305_controller_available_level();
 uint32_t fallback=opencfw_em9305_packet_default_30f65c(probed);
 uint32_t status=opencfw_em9305_packet_revision_3119b0((uintptr_t)&revision);
 uint32_t result=revision;
 if (status!=0u) {
  result=fallback;
  if (revision!=10u) {
   uint32_t low=fallback&255u;
   result=low<6u?low:6u;
  }
 }
 uint32_t low=result&255u;
 return (low&128u)!=0u?low|0xffffff00u:low;
}

/* Product byte lookup at native0x3344e0: exact extent/classification unresolved. */
extern const uint8_t opencfw_em9305_packet_default_table[256];
/* Native0x30f65c..0x30f668: truncate index, load signed table byte. */
uint32_t opencfw_em9305_packet_default_30f65c(uint32_t index)
{
 uint32_t byte=opencfw_em9305_packet_default_table[index&255u];
 return (byte&128u)!=0u?byte|0xffffff00u:byte;
}

/* Native revision lookup data0x333ff0:68 records of3 bytes.
 * SHA256 36a707ec3cbeaefa3000faf479f1bfe8e61a7ffdc1f9716da3886078505c822c; exact bounded lookup extent. */
static const uint8_t opencfw_em9305_revision_table[204]={
 0xc7u,0x00u,0x00u,0xdfu,0x00u,0x01u,0xdfu,0x00u,0x01u,0xdfu,0x00u,0x01u,
 0xdfu,0x00u,0x01u,0xdfu,0x00u,0x01u,0xdfu,0x00u,0x01u,0xdfu,0x00u,0x01u,
 0xdfu,0x00u,0x01u,0xdfu,0x00u,0x01u,0xdfu,0x00u,0x01u,0xdfu,0x00u,0x01u,
 0xdfu,0x00u,0x01u,0xdfu,0x00u,0x01u,0xdfu,0x00u,0x01u,0xdfu,0x00u,0x01u,
 0xdfu,0x00u,0x01u,0xdfu,0x00u,0x01u,0xdfu,0x00u,0x01u,0xdfu,0x00u,0x01u,
 0xdfu,0x00u,0x01u,0xdfu,0x00u,0x01u,0xdfu,0x00u,0x01u,0xdfu,0x00u,0x01u,
 0xdfu,0x00u,0x01u,0xe8u,0x00u,0x03u,0xe8u,0x00u,0x03u,0xe8u,0x00u,0x03u,
 0xe8u,0x00u,0x03u,0xe8u,0x00u,0x03u,0xe8u,0x00u,0x03u,0xe8u,0x00u,0x03u,
 0xe8u,0x00u,0x03u,0xe8u,0x00u,0x03u,0xf1u,0x00u,0x08u,0xf1u,0x00u,0x08u,
 0xf1u,0x00u,0x08u,0xf1u,0x00u,0x08u,0xf1u,0x00u,0x08u,0xf1u,0x00u,0x08u,
 0xf1u,0x00u,0x08u,0xf1u,0x00u,0x08u,0xf1u,0x00u,0x08u,0xf4u,0x00u,0x0cu,
 0xf4u,0x00u,0x0cu,0xf4u,0x00u,0x0cu,0xf7u,0x00u,0x11u,0xf7u,0x00u,0x11u,
 0xf7u,0x00u,0x11u,0xfau,0x00u,0x19u,0xfau,0x00u,0x19u,0xfau,0x00u,0x19u,
 0xfdu,0x00u,0x25u,0xfdu,0x00u,0x25u,0xfdu,0x00u,0x25u,0x00u,0x01u,0x2eu,
 0x00u,0x01u,0x2eu,0x00u,0x01u,0x2eu,0x03u,0x04u,0x2fu,0x03u,0x04u,0x2fu,
 0x03u,0x04u,0x2fu,0x04u,0x04u,0x39u,0x05u,0x05u,0x3bu,0x06u,0x07u,0x3du,
 0x08u,0x08u,0x3eu,0x08u,0x08u,0x3eu,0x0au,0x0du,0x3fu,0x0au,0x0du,0x3fu,
};
/* Native0x3119b0..0x3119f0: reverse68-record silicon revision search.
 * XBFU immediate176 is retained as native instruction, not guessed extraction. */
uint32_t opencfw_em9305_packet_revision_3119b0(uintptr_t output)
{
 uint32_t key=*(volatile uint32_t *)(uintptr_t)0xf00420u;
 __asm__ volatile("xbfu %0,%0,176" : "+r"(key));
 uint32_t last=0u;
 for (uint32_t remaining=68u;remaining!=0u;) {
  remaining-=1u;
  uint32_t offset=(remaining&255u)*3u;
  uint32_t byte=opencfw_em9305_revision_table[offset+2u];
  last=(byte&128u)!=0u?byte|0xffffff00u:byte;
  if (key==last) {
   *(volatile uint8_t *)output=opencfw_em9305_revision_table[offset];
   return 1u;
  }
 }
 return key==last;
}

/* Native0x311ffc..0x312094: table calibration with exact native extraction
 * and packing instructions. MMIO sampling and wrapping arithmetic preserved. */
uint32_t opencfw_em9305_common_calibrate_311ffc(uint32_t first,uint32_t second)
{
 uintptr_t table=*(volatile uint32_t *)(uintptr_t)0x80fd54u;
 uint32_t control=*(volatile uint32_t *)(uintptr_t)0xf04004u;
 uint32_t flags=*(volatile uint32_t *)(uintptr_t)0xf0440cu;
 uint32_t channel=control&3u,field=control;
 __asm__ volatile("xbfu %0,%0,40" : "+r"(field));
 uintptr_t a=(flags&256u)==0u?table+field*2u+72u:
  table+field*8u+channel*2u;
 uint32_t adjusted_first=(uint32_t)*(volatile uint16_t *)a+first;
 uintptr_t b=(flags&512u)==0u?table+channel*2u+64u:
  table+channel*8u+field*2u+32u;
 uint32_t adjusted_second=second+(uint32_t)*(volatile uint16_t *)b-600u;
 uint32_t invalid=(adjusted_first+0xffffeda8u)<0xfffff001u;
 invalid|=(int32_t)adjusted_second<1;
 invalid|=(int32_t)adjusted_second>4095;
 if (invalid==0u) {
  uint32_t shifted_first=adjusted_first-600u,packed;
  __asm__ volatile("vpack2hl %0,%1,%2" : "=r"(packed) :
   "r"(adjusted_second),"r"(shifted_first));
  *(volatile uint32_t *)(uintptr_t)0xf04410u=packed;
 }
 return 1u&~invalid;
}

extern uint32_t opencfw_em9305_common_activate_310580(uint32_t);
/* Native3151cc/3151d0/314728 tail through30fab4 to310580.
 * Argument/return R0 preserved; lower activation body remains explicit. */
uint32_t opencfw_em9305_common_callback_3151cc(uint32_t value)
{ return opencfw_em9305_common_activate_310580(value); }
uint32_t opencfw_em9305_common_callback_3151d0(uint32_t value)
{ return opencfw_em9305_common_activate_310580(value); }
uint32_t opencfw_em9305_common_callback_314728(uint32_t value)
{ return opencfw_em9305_common_activate_310580(value); }

extern uint32_t opencfw_em9305_common_radio_restore_312410(uint32_t);
extern uint32_t opencfw_em9305_common_radio_control_311f90(uint32_t,uint32_t);
/* Native0x310580..0x3105b8: activate common radio record once.
 * Incoming R0 is overwritten even on the already-active path. */
uint32_t opencfw_em9305_common_activate_310580(uint32_t unused)
{
 (void)unused;
 uintptr_t root=0x805e78u;
 if (*(volatile uint8_t *)root==1u) return 1u;
 uint32_t masked=opencfw_em9305_common_timer_mask_310bd0(1u,0u);
 (void)opencfw_em9305_common_radio_restore_312410(masked);
 uint32_t first=*(volatile uint8_t *)(uintptr_t)0x805ea4u;
 uint32_t second=*(volatile uint8_t *)(uintptr_t)0x805ea5u;
 uint32_t result=second;
 if ((first|second)!=0u)
  result=opencfw_em9305_common_radio_control_311f90(0u,0u);
 *(volatile uint8_t *)root=1u;
 return result;
}

/* Native0x311f90..0x311fb0: control word preserves original input bits. */
uint32_t opencfw_em9305_common_radio_control_311f90(uint32_t first,uint32_t second)
{
 uint32_t word=first;
 if (first!=0u) word|=4u;
 if (second!=0u) word|=2u|8u;
 *(volatile uint32_t *)(uintptr_t)0xf040a4u=word;
 return word;
}
/* Native0x312410..0x312430: radio restore and ordered AUX writes. */
uint32_t opencfw_em9305_common_radio_restore_312410(uint32_t unused)
{
 (void)unused;
 uint32_t first=4u,second=8u;
 *(volatile uint8_t *)(uintptr_t)0xf04400u=4u;
 __asm__ volatile("sr %0,[1666]" :: "r"(first) : "memory");
 __asm__ volatile("sr %0,[1666]" :: "r"(second) : "memory");
 *(volatile uint8_t *)(uintptr_t)0x805fb8u=1u;
 return first;
}

/* Native0x314754..0x314758: shared activation tail. */
uint32_t opencfw_em9305_common_callback_314754(uint32_t value)
{ return opencfw_em9305_common_activate_310580(value); }
/* Native0x31472c..0x314754: activation then pending and completion callbacks.
 * Dynamic callback register ABI beyond explicit arguments remains unqualified. */
uint32_t opencfw_em9305_common_callback_31472c(uint32_t value,uintptr_t object)
{
 (void)opencfw_em9305_common_activate_310580(value);
 uintptr_t pending=*(volatile uint32_t *)(uintptr_t)0x8015e0u;
 if (pending!=0u) {
  uintptr_t callback=*(volatile uint32_t *)(object+112u);
  *(volatile uint32_t *)(uintptr_t)0x8015e0u=0u;
  (void)((uint32_t (*)(uint32_t,uintptr_t,uint32_t))callback)(value,pending,2u);
 }
 uintptr_t callback=*(volatile uint32_t *)(object+104u);
 return ((uint32_t (*)(uint32_t,uintptr_t))callback)(value,callback);
}
/* Native0x3151d4..0x3151fc: alternate pending/completion offsets. */
uint32_t opencfw_em9305_common_callback_3151d4(uint32_t value,uintptr_t object)
{
 (void)opencfw_em9305_common_activate_310580(value);
 uintptr_t pending=*(volatile uint32_t *)(uintptr_t)0x8015e0u;
 if (pending!=0u) {
  uintptr_t callback=*(volatile uint32_t *)(object+116u);
  *(volatile uint32_t *)(uintptr_t)0x8015e0u=0u;
  (void)((uint32_t (*)(uint32_t,uintptr_t,uint32_t))callback)(value,pending,2u);
 }
 uintptr_t callback=*(volatile uint32_t *)(object+108u);
 return ((uint32_t (*)(uint32_t,uintptr_t))callback)(value,callback);
}

/* Native0x314580..0x314584 tail to30fabc J[blink]: preserves input R0. */
uint32_t opencfw_em9305_common_callback_314580(uint32_t value)
{ return value; }
/* Native0x3143f4..0x314408: dispatch secondary callback by record byte.
 * Tail-call argument registers R0/R1/R2 preserved explicitly; wider ABI gated. */
uint32_t opencfw_em9305_common_callback_3143f4(uintptr_t object)
{
 uintptr_t record=*(volatile uint32_t *)(object+44u);
 uint32_t index=*(volatile uint8_t *)record;
 uintptr_t callback=*(volatile uint32_t *)(uintptr_t)(0x801538u+index*8u);
 if (callback==0u) return (uint32_t)object;
 return ((uint32_t (*)(uintptr_t,uintptr_t,uintptr_t))callback)(object,record,callback);
}

/* Native0x31446c..0x314470 ->30fae8 J[blink]. */
uint32_t opencfw_em9305_common_callback_31446c(uint32_t value)
{ return value; }
/* Native0x314584..0x314594: no-op30fabc, then R0=0 through no-op31055c. */
uint32_t opencfw_em9305_common_callback_314584(uint32_t unused)
{ (void)unused; return 0u; }

extern uint32_t opencfw_em9305_common_channel_callback_314ea4(uint32_t,uint32_t,uint32_t,uint32_t);
extern uint32_t opencfw_em9305_common_channel_callback_314fa4(void);
extern uint32_t opencfw_em9305_common_channel_start_314db8(uintptr_t,uintptr_t,uint32_t,uint32_t);
/* Native0x3152bc..0x3152fc: configure scan channel then start/signalling. */
uint32_t opencfw_em9305_common_callback_3152bc(uintptr_t object)
{
 uintptr_t record=*(volatile uint32_t *)(object+44u),root=0x8015c4u;
 *(volatile uint32_t *)(root+20u)=4u;
 *(volatile uint32_t *)(root+12u)=(uint32_t)(uintptr_t)&opencfw_em9305_common_channel_callback_314ea4;
 uint32_t channel=*(volatile uint8_t *)(record+126u);
 *(volatile uint32_t *)(root+8u)=(uint32_t)(uintptr_t)&opencfw_em9305_common_channel_callback_314fa4;
 *(volatile uint8_t *)(root+2u)=0u;
 *(volatile uint8_t *)root=0u;
 *(volatile uint8_t *)(root+1u)=(uint8_t)channel;
 uint32_t result=opencfw_em9305_common_channel_start_314db8(object,record,0u,1u);
 if (result!=0u) result=opencfw_em9305_auxiliary_signal_304394();
 return result;
}

extern uint32_t opencfw_em9305_common_radio_prepare_30fb4c(uintptr_t);
extern uint32_t opencfw_em9305_common_radio_bind_30fc10(uintptr_t);
extern uint32_t opencfw_em9305_common_channel_callback_3151a0(uint32_t);
extern uint32_t opencfw_em9305_common_radio_finish_3045c0(uint32_t);
/* Native0x31537c..0x3153bc: radio bind and product descriptor notification.
 * Native return is path-dependent; current callback consumer discards it. */
void opencfw_em9305_common_callback_31537c(uintptr_t object,uintptr_t input)
{
 uintptr_t record=*(volatile uint32_t *)(object+44u),root=0x8015c4u;
 (void)opencfw_em9305_common_radio_prepare_30fb4c(input);
 uint32_t timestamp=*(volatile uint32_t *)(object+8u);
 *(volatile uint32_t *)(root+8u)=(uint32_t)(uintptr_t)&opencfw_em9305_common_channel_callback_3151a0;
 *(volatile uint32_t *)(root+16u)=timestamp;
 (void)opencfw_em9305_common_radio_bind_30fc10(root+8u);
 uintptr_t callback=*(volatile uint32_t *)(record+100u);
 *(volatile uint8_t *)root=0u;
 uint32_t result=((uint32_t (*)(uintptr_t,uintptr_t))callback)(object,callback);
 if (opencfw_em9305_auxiliary_start_303f50(result)!=0u) {
  uint32_t current=opencfw_em9305_auxiliary_ready_303f68();
  if (current!=0u) (void)opencfw_em9305_common_radio_finish_3045c0(current);
 }
}

/* Native0x30fc10..0x30fc20: exact16-byte radio binding record copy. */
uint32_t opencfw_em9305_common_radio_bind_30fc10(uintptr_t source)
{
 return (uint32_t)(uintptr_t)opencfw_em9305_memcpy(
  (void *)(uintptr_t)0x805cf4u,(const void *)source,16u);
}

extern uint32_t opencfw_em9305_radio_setup_31230c(uint32_t);
extern uint32_t opencfw_em9305_radio_mode_312290(uint32_t);
/* Native0x310450..0x310454: actual radio setup tail. */
uint32_t opencfw_em9305_radio_setup_310450(uint32_t value)
{ return opencfw_em9305_radio_setup_31230c(value); }
/* Native0x310474..0x310480: radio timestamp/control word store. */
uint32_t opencfw_em9305_radio_timestamp_310474(uint32_t value)
{
 *(volatile uint32_t *)(uintptr_t)0xf04034u=value;
 return value;
}
/* Native0x310570..0x310580: exact product flag gate for radio mode tail. */
uint32_t opencfw_em9305_radio_mode_310570(uint32_t value)
{
 if (*(volatile uint8_t *)(uintptr_t)0x805ec5u!=1u) return value;
 return opencfw_em9305_radio_mode_312290(value);
}

extern uint32_t opencfw_em9305_radio_configure_3104d8(uint32_t,uint32_t);
extern uint32_t opencfw_em9305_radio_status_310284(uint32_t);
extern uint32_t opencfw_em9305_radio_transform_33322c(uintptr_t);
extern uint32_t opencfw_em9305_radio_finish_310454(uint32_t);
/* Native0x30fb4c..0x30fc10: full product radio preparation and transform.
 * Stack/ambient callback ABI beyond represented registers remains gated. */
uint32_t opencfw_em9305_common_radio_prepare_30fb4c(uintptr_t record)
{
 (void)opencfw_em9305_radio_setup_310450(*(volatile uint32_t *)(record+4u));
 (void)opencfw_em9305_radio_timestamp_310474(*(volatile uint32_t *)(record+8u));
 uint32_t byte=*(volatile uint8_t *)(record+2u);
 (void)opencfw_em9305_radio_mode_310570((byte&128u)!=0u?byte|0xffffff00u:byte);
 uintptr_t root=0x805d1cu;
 uint32_t mode=*(volatile uint8_t *)(record+12u),first;
 if (mode==2u) {
  *(volatile uint16_t *)(root+10u)=257u;
  *(volatile uint16_t *)(root+2u)=1028u;
  *(volatile uint16_t *)(root+4u)=2056u;
  first=1u;
 } else if (mode==3u) {
  uint32_t a=*(volatile uint8_t *)(record+14u)==1u?16u:64u;
  first=a==16u?3u:4u;
  uint32_t flag=*(volatile uint8_t *)(record+15u);
  *(volatile uint8_t *)(root+2u)=(uint8_t)a;
  *(volatile uint8_t *)(root+10u)=(uint8_t)first;
  *(volatile uint8_t *)(root+4u)=80u;
  *(volatile uint8_t *)(root+5u)=80u;
  if (flag==1u) {
   *(volatile uint8_t *)(root+3u)=16u;
   *(volatile uint8_t *)(root+11u)=3u;
  } else {
   *(volatile uint8_t *)(root+11u)=4u;
   *(volatile uint8_t *)(root+3u)=64u;
  }
 } else {
  *(volatile uint16_t *)(root+10u)=0u;
  *(volatile uint16_t *)(root+4u)=2056u;
  *(volatile uint16_t *)(root+2u)=2056u;
  first=0u;
 }
 uint32_t secondary=*(volatile uint8_t *)(record+13u),second;
 if (secondary==2u) {
  *(volatile uint16_t *)root=24u;
  second=1u;
  *(volatile uint8_t *)(root+21u)=1u;
 } else {
  second=secondary==3u?2u:0u;
  *(volatile uint8_t *)(root+21u)=(uint8_t)second;
  *(volatile uint16_t *)root=secondary==3u?336u:40u;
 }
 uint32_t result=opencfw_em9305_radio_configure_3104d8(first,second);
 result=opencfw_em9305_radio_status_310284(result);
 *(volatile uint8_t *)(record+2u)=(uint8_t)result;
 (void)opencfw_em9305_radio_transform_33322c(record+20u);
 return opencfw_em9305_radio_finish_310454(*(volatile uint8_t *)(record+1u));
}

/* Native0x3119f0..0x311a00: query level then signed table mapping. */
uint32_t opencfw_em9305_radio_default_3119f0(void)
{ return opencfw_em9305_packet_default_30f65c(opencfw_em9305_controller_available_level()); }
/* Native0x311a00..0x311a20: fresh query or signed stored product byte. */
uint32_t opencfw_em9305_radio_status_311a00(uint32_t query)
{
 uint32_t value;
 if (query!=0u) value=opencfw_em9305_radio_default_3119f0();
 else {
  uintptr_t record=*(volatile uint32_t *)(uintptr_t)0x80fd44u;
  value=*(volatile uint8_t *)(record+1u);
 }
 value&=255u;
 return (value&128u)!=0u?value|0xffffff00u:value;
}
/* Native0x310284..0x31028c: stored product status tail, incoming replaced. */
uint32_t opencfw_em9305_radio_status_310284(uint32_t unused)
{ (void)unused; return opencfw_em9305_radio_status_311a00(0u); }

/* Native0x311a20..0x311a40: signed clamps then low-byte shifted range. */
uint32_t opencfw_em9305_radio_mode_index_311a20(uint32_t first,uint32_t second)
{
 int32_t a=(int32_t)first,b=(int32_t)second;
 int32_t selected=a>=10?10:(a<=-58?-57:a);
 if (b>10) b=10;
 if (b<selected) selected=b;
 return ((uint32_t)selected+57u)&255u;
}
/* Native0x312290..0x3122c0: product mode fields and revision table mapping.
 * Table address wraps like native; out-of-range contract is not invented. */
uint32_t opencfw_em9305_radio_mode_312290(uint32_t mode)
{
 uint32_t limit=opencfw_em9305_radio_default_3119f0();
 uintptr_t record=*(volatile uint32_t *)(uintptr_t)0x80fd44u;
 *(volatile uint8_t *)(record+2u)=(uint8_t)limit;
 *(volatile uint8_t *)record=(uint8_t)mode;
 uint32_t index=opencfw_em9305_radio_mode_index_311a20(mode,limit);
 uint32_t byte=opencfw_em9305_revision_table[index*3u];
 *(volatile uint8_t *)(record+4u)=(uint8_t)index;
 *(volatile uint8_t *)(record+3u)=(uint8_t)byte;
 return (byte&128u)!=0u?byte|0xffffff00u:byte;
}

/* Native0x31230c..0x312330: setup word and conditional alternating marker. */
uint32_t opencfw_em9305_radio_setup_31230c(uint32_t value)
{
 *(volatile uint32_t *)(uintptr_t)0xf0400cu=value;
 uint32_t control=*(volatile uint32_t *)(uintptr_t)0xf04004u;
 if ((control&6u)!=0u) return value;
 uint32_t marker=(value&1u)!=0u?85u:170u;
 *(volatile uint8_t *)(uintptr_t)0xf04008u=(uint8_t)marker;
 return marker;
}
/* Native0x312330..0x312344: product enable bit4, original R0 return. */
uint32_t opencfw_em9305_radio_enable_312330(uint32_t value)
{
 uint32_t control=*(volatile uint32_t *)(uintptr_t)0xf04050u;
 control&=~16u;
 if (value!=0u) control|=16u;
 *(volatile uint32_t *)(uintptr_t)0xf04050u=control;
 return value;
}

extern uint32_t opencfw_em9305_radio_apply_3120a0(uint32_t,uint32_t);
/* Native0x3104d8..0x31055c: original input bytes, encoded mode record,
 * then tail-call apply with mapped second in R0 and mapped first in R1. */
uint32_t opencfw_em9305_radio_configure_3104d8(uint32_t first,uint32_t second)
{
 uintptr_t root=0x805e98u;
 *(volatile uint8_t *)(root+1u)=(uint8_t)second;
 *(volatile uint8_t *)root=(uint8_t)first;
 uint32_t mapped_first=first==1u?1u:(first==3u?3u:(first==4u?2u:0u));
 *(volatile uint8_t *)(root+9u)=(uint8_t)mapped_first;
 *(volatile uint16_t *)(root+2u)=2u;
 uint32_t mapped_second,word;
 if (second==1u) { mapped_second=1u;word=0x18000au; }
 else if (second==2u || second==4u) {mapped_second=2u;word=0x1500034u;}
 else if (second==3u) {mapped_second=3u;word=0x900034u;}
 else {mapped_second=0u;word=0x280013u;}
 *(volatile uint8_t *)(root+10u)=(uint8_t)mapped_second;
 *(volatile uint32_t *)(root+4u)=word;
 return opencfw_em9305_radio_apply_3120a0(mapped_second,mapped_first);
}

extern uint32_t opencfw_em9305_radio_finish_probe_311958(uint32_t);
extern uint32_t opencfw_em9305_radio_finish_apply_3122c0(uint32_t);
extern uint32_t opencfw_em9305_radio_finish_mode_312344(uint32_t,uint32_t);
/* Native0x310454..0x310474: preserve original selector across two children,
 * then apply product flag truth value as native second argument. */
uint32_t opencfw_em9305_radio_finish_310454(uint32_t selector)
{
 uint32_t result=opencfw_em9305_radio_finish_probe_311958(selector);
 (void)opencfw_em9305_radio_finish_apply_3122c0(result);
 uint32_t enabled=*(volatile uint8_t *)(uintptr_t)0x805ea0u!=0u;
 return opencfw_em9305_radio_finish_mode_312344(selector,enabled);
}

/* Native0x311958..0x31197c: unsigned channel remap and low-byte return. */
uint32_t opencfw_em9305_radio_finish_probe_311958(uint32_t value)
{
 uint32_t mapped=value;
 if (value<=10u) mapped=value+1u;
 else if (value<=36u) mapped=value+2u;
 else if (value==37u) mapped=0u;
 else if (value==38u) mapped=12u;
 return mapped&255u;
}

/* Native0x3122c0..0x3122f0: signed MIN39 product lookup and MMIO apply. */
uint32_t opencfw_em9305_radio_finish_apply_3122c0(uint32_t selector)
{
 uintptr_t table=*(volatile uint32_t *)(uintptr_t)0x80fd4cu;
 uint32_t index=(int32_t)selector>39?39u:selector;
 uintptr_t address=(uint32_t)table+index+80u;
 uint32_t nibble=*(volatile uint8_t *)address&15u;
 uint32_t encoded=(nibble<<10u)+index;
 *(volatile uint32_t *)(uintptr_t)0xf04424u=encoded;
 uint32_t control=*(volatile uint32_t *)(uintptr_t)0xf04888u;
 control&=~1u;
 *(volatile uint32_t *)(uintptr_t)0xf04888u=control;
 return control;
}

/* Native0x310498..0x3104b0: product flags then swapped truth-value controls. */
uint32_t opencfw_em9305_radio_flags_310498(uint32_t first,uint32_t second)
{
 *(volatile uint8_t *)(uintptr_t)0x805ea5u=(uint8_t)second;
 *(volatile uint8_t *)(uintptr_t)0x805ea4u=(uint8_t)first;
 return opencfw_em9305_common_radio_control_311f90(second!=0u,first!=0u);
}
/* Native0x310560..0x310570:16-byte source-owned copy. */
uint32_t opencfw_em9305_radio_copy_310560(uintptr_t source)
{ return (uint32_t)(uintptr_t)opencfw_em9305_memcpy((void *)(uintptr_t)0x805ea8u,(const void *)source,16u); }
extern uint32_t opencfw_em9305_radio_data_3104bc(uintptr_t);
extern uint32_t opencfw_em9305_radio_byte_31048c(uint32_t);
extern uint32_t opencfw_em9305_radio_byte_3104b0(uint32_t);
/* Native0x33322c..0x333268: flags and optional product data transform. */
uint32_t opencfw_em9305_radio_transform_33322c(uintptr_t record)
{
 uint32_t second=*(volatile uint8_t *)(record+25u);
 uint32_t first=*(volatile uint8_t *)(record+24u);
 *(volatile uint8_t *)(uintptr_t)0x805d3au=(uint8_t)second;
 (void)opencfw_em9305_radio_flags_310498(first,second);
 uint32_t result=*(volatile uint8_t *)(record+24u);
 if (result==0u) {
  result=*(volatile uint8_t *)(record+25u);
  if (result==0u) return result;
 }
 (void)opencfw_em9305_radio_copy_310560(record);
 (void)opencfw_em9305_radio_data_3104bc(record+16u);
 (void)opencfw_em9305_radio_byte_31048c(*(volatile uint8_t *)(record+40u));
 return opencfw_em9305_radio_byte_3104b0(*(volatile uint8_t *)(record+41u));
}

/* Native0x31048c..0x310498: byte store with untruncated return. */
uint32_t opencfw_em9305_radio_byte_31048c(uint32_t value)
{ *(volatile uint8_t *)(uintptr_t)0x805ea6u=(uint8_t)value;return value; }
/* Native0x3104b0..0x3104bc: second byte store with untruncated return. */
uint32_t opencfw_em9305_radio_byte_3104b0(uint32_t value)
{ *(volatile uint8_t *)(uintptr_t)0x805ea7u=(uint8_t)value;return value; }
/* Native0x3104bc..0x3104cc: exact8-byte data copy. */
uint32_t opencfw_em9305_radio_data_3104bc(uintptr_t source)
{
 return (uint32_t)(uintptr_t)opencfw_em9305_memcpy(
  (void *)(uintptr_t)0x805ebdu,(const void *)source,8u);
}

extern uint32_t opencfw_em9305_common_channel_callback_3151fc(uint32_t,uint32_t,uint32_t,uint32_t,uint32_t);
extern void opencfw_em9305_common_channel_callback_315260(void);
/* Native0x3153bc..0x3153fc: alternate radio bind and descriptor callback.
 * Native indirect callback retains its own address as R1. */
uint32_t opencfw_em9305_common_callback_3153bc(uintptr_t object,uintptr_t input)
{
 uintptr_t record=*(volatile uint32_t *)(object+44u),root=0x8015c4u;
 (void)opencfw_em9305_common_radio_prepare_30fb4c(input);
 uint32_t timestamp=*(volatile uint32_t *)(object+8u);
 uint32_t context=*(volatile uint32_t *)(record+100u);
 *(volatile uint32_t *)(root+12u)=(uint32_t)(uintptr_t)&opencfw_em9305_common_channel_callback_3151fc;
 *(volatile uint32_t *)(root+8u)=(uint32_t)(uintptr_t)&opencfw_em9305_common_channel_callback_315260;
 *(volatile uint32_t *)(root+16u)=timestamp;
 *(volatile uint32_t *)(root+20u)=context;
 (void)opencfw_em9305_common_radio_bind_30fc10(root+8u);
 uintptr_t callback=*(volatile uint32_t *)(input+104u);
 *(volatile uint8_t *)root=0u;
 return ((uint32_t (*)(uintptr_t,uintptr_t))callback)(object,callback);
}

/* Native 0x310340/0x31034c: callback stores retain the input in R0.
 * Source relocations replace stock code addresses; callback bodies remain imports. */
extern void opencfw_em9305_radio_callback_333268(void);
extern void opencfw_em9305_radio_callback_3330d8(void);
uintptr_t opencfw_em9305_radio_callback_store_310340(uintptr_t callback)
{ *(volatile uint32_t *)(uintptr_t)0x805e7cu=(uint32_t)callback;return callback; }
uintptr_t opencfw_em9305_radio_callback_store_31034c(uintptr_t callback)
{ *(volatile uint32_t *)(uintptr_t)0x805e80u=(uint32_t)callback;return callback; }
/* Native 0x30fac0..0x30fadc: ordered callback registration. */
uintptr_t opencfw_em9305_radio_callback_setup_30fac0(void)
{
 (void)opencfw_em9305_radio_callback_store_31034c((uintptr_t)&opencfw_em9305_radio_callback_333268);
 return opencfw_em9305_radio_callback_store_310340((uintptr_t)&opencfw_em9305_radio_callback_3330d8);
}
/* Native 0x310480..0x31048c: enable byte with full-width return. */
uint32_t opencfw_em9305_radio_enable_310480(uint32_t value)
{ *(volatile uint8_t *)(uintptr_t)0x805ea0u=(uint8_t)value;return value; }
/* Native 0x314548/0x314558/0x314568: registry callbacks.
 * Last 0x30fae0 tail targets native 0x31055c, an authenticated j_s blink.
 * Registry uses void callbacks; native incidental R0 values are not exposed. */
void opencfw_em9305_common_callback_314548(void)
{ (void)opencfw_em9305_radio_callback_setup_30fac0();(void)opencfw_em9305_radio_enable_310480(1u); }
void opencfw_em9305_common_callback_314558(void)
{ (void)opencfw_em9305_radio_callback_setup_30fac0();(void)opencfw_em9305_radio_enable_310480(0u); }
void opencfw_em9305_common_callback_314568(void)
{ (void)opencfw_em9305_radio_callback_setup_30fac0();(void)opencfw_em9305_radio_enable_310480(0u); }

extern uint32_t opencfw_em9305_common_channel_callback_3146a4(uint32_t,uint32_t,uint32_t,uint32_t,uint32_t);
extern uint32_t opencfw_em9305_common_channel_callback_3146c4(uint32_t);
/* Product template 0x3343f8: exact 20-byte data contract, not executable bytes. */
extern const uint8_t opencfw_em9305_radio_template_3343f8[20];
extern uint32_t opencfw_em9305_radio_record_30fc28(uintptr_t);
extern uint32_t opencfw_em9305_radio_request_30faec(uintptr_t,uint32_t);
/* Native 0x31481c..0x314888: radio binding and stack descriptor request.
 * Delay slots preserve timestamp-before-copy and request selector 257. */
uint32_t opencfw_em9305_common_callback_31481c(uintptr_t object,uintptr_t input)
{
 uintptr_t record=*(volatile uint32_t *)(object+44u),root=0x8015c4u;
 uint8_t descriptor[20];
 (void)opencfw_em9305_common_radio_prepare_30fb4c(input);
 *(volatile uint32_t *)(root+12u)=(uint32_t)(uintptr_t)&opencfw_em9305_common_channel_callback_3146a4;
 *(volatile uint32_t *)(root+8u)=(uint32_t)(uintptr_t)&opencfw_em9305_common_channel_callback_3146c4;
 *(volatile uint32_t *)(root+20u)=*(volatile uint32_t *)(record+128u);
 *(volatile uint32_t *)(root+16u)=*(volatile uint32_t *)(object+8u);
 (void)opencfw_em9305_common_radio_bind_30fc10(root+8u);
 *(volatile uint8_t *)root=0u;
 if (*(volatile uint32_t *)(record+100u)!=0u)
  (void)opencfw_em9305_memcpy(descriptor,opencfw_em9305_radio_template_3343f8,20u);
 else (void)opencfw_em9305_memset(descriptor,0,20u);
 (void)opencfw_em9305_radio_record_30fc28((uintptr_t)descriptor);
 return opencfw_em9305_radio_request_30faec(0x8013f0u,257u);
}

/* Native 0x30fc28..0x30fc68: exact descriptor copy followed by mode MMIO.
 * Native R0 remains 0xf0440d on every return; byte writes retain order. */
uint32_t opencfw_em9305_radio_record_30fc28(uintptr_t source)
{
 (void)opencfw_em9305_memcpy((void *)(uintptr_t)0x805d04u,(const void *)source,20u);
 uint8_t mode=*(volatile uint8_t *)source;
 volatile uint8_t *control=(volatile uint8_t *)(uintptr_t)0xf0440du;
 if (mode==2u) { *control=0u;control[-1]=0u; }
 else if (mode==3u) { *control=0u;control[-1]=1u; }
 else { *control=3u;control[-1]=3u; }
 return 0xf0440du;
}

extern uint32_t opencfw_em9305_common_channel_callback_3146d4(uint32_t,uint32_t,uint32_t,uint32_t);
/* Native 0x314888..0x3148cc: bind record with preserved primary callback,
 * notify descriptor, and conditionally finish the auxiliary transaction.
 * Native return register is path dependent; registry consumer discards it. */
void opencfw_em9305_common_callback_314888(uintptr_t object,uintptr_t input)
{
 uintptr_t record=*(volatile uint32_t *)(object+44u),root=0x8015c4u;
 (void)opencfw_em9305_common_radio_prepare_30fb4c(input);
 uint32_t timestamp=*(volatile uint32_t *)(object+8u);
 uint32_t context=*(volatile uint32_t *)(record+100u);
 *(volatile uint32_t *)(root+12u)=(uint32_t)(uintptr_t)&opencfw_em9305_common_channel_callback_3146d4;
 *(volatile uint32_t *)(root+16u)=timestamp;
 *(volatile uint32_t *)(root+20u)=context;
 (void)opencfw_em9305_common_radio_bind_30fc10(root+8u);
 uintptr_t callback=*(volatile uint32_t *)(record+104u);
 *(volatile uint8_t *)root=0u;
 uint32_t result=((uint32_t (*)(uintptr_t,uintptr_t))callback)(object,callback);
 if (opencfw_em9305_auxiliary_start_303f50(result)!=0u) {
  uint32_t current=opencfw_em9305_auxiliary_ready_303f68();
  if (current!=0u) (void)opencfw_em9305_common_radio_finish_3045c0(current);
 }
}

/* Native 0x3146d4..0x314728: radio completion callback. Native indirect
 * calls retain their own address in R3; R2 is the original first input.
 * The incoming third argument is overwritten before use. */
uint32_t opencfw_em9305_common_channel_callback_3146d4(
 uint32_t first,uint32_t second,uint32_t unused,uint32_t fourth)
{
 (void)unused;
 uintptr_t root=0x8015c4u;
 uint8_t count=*(volatile uint8_t *)root;
 *(volatile uint8_t *)root=(uint8_t)(count+1u);
 uint32_t current=opencfw_em9305_auxiliary_ready_303f68();
 if (current==0u) return current;
 current=opencfw_em9305_auxiliary_ready_303f68();
 uintptr_t record=*(volatile uint32_t *)((uintptr_t)current+44u);
 uint32_t pending=*(volatile uint32_t *)(root+28u);
 uintptr_t callback=*(volatile uint32_t *)(record+108u);
 *(volatile uint32_t *)(record+116u)=fourth;
 *(volatile uint32_t *)(root+28u)=0u;
 *(volatile uint8_t *)(record+120u)=(uint8_t)second;
 uint32_t result=((uint32_t (*)(uint32_t,uint32_t,uint32_t,uintptr_t))callback)(current,pending,first,callback);
 callback=*(volatile uint32_t *)(record+112u);
 if (callback!=0u)
  result=((uint32_t (*)(uint32_t,uint32_t,uint32_t,uintptr_t))callback)(current,first,second,callback);
 result=opencfw_em9305_auxiliary_start_303f50(result);
 if (result!=0u) {
  result=opencfw_em9305_common_activate_310580(result);
  result=opencfw_em9305_common_radio_finish_3045c0(result);
 }
 return result;
}

extern uint32_t opencfw_em9305_common_channel_callback_314758(uint32_t,uint32_t,uint32_t,uint32_t,uint32_t);
extern void opencfw_em9305_common_channel_callback_3147b4(void);
/* Native 0x3148cc..0x314908: prepare and bind a fixed context of four,
 * then invoke the input descriptor callback after the delayed byte clear. */
uint32_t opencfw_em9305_common_callback_3148cc(uintptr_t object,uintptr_t input)
{
 (void)opencfw_em9305_common_radio_prepare_30fb4c(input);
 uintptr_t root=0x8015c4u;
 uint32_t timestamp=*(volatile uint32_t *)(object+8u);
 *(volatile uint32_t *)(root+12u)=(uint32_t)(uintptr_t)&opencfw_em9305_common_channel_callback_314758;
 *(volatile uint32_t *)(root+8u)=(uint32_t)(uintptr_t)&opencfw_em9305_common_channel_callback_3147b4;
 *(volatile uint32_t *)(root+20u)=4u;
 *(volatile uint32_t *)(root+16u)=timestamp;
 (void)opencfw_em9305_common_radio_bind_30fc10(root+8u);
 uintptr_t callback=*(volatile uint32_t *)(input+100u);
 *(volatile uint8_t *)root=0u;
 return ((uint32_t (*)(uintptr_t,uintptr_t))callback)(object,callback);
}

/* Native 0x314758..0x3147b4: five-input completion callback.
 * Native R2/R3 inputs are dead. Required indirect callbacks preserve address
 * in R3. Current object is dereferenced without a native null guard. */
uint32_t opencfw_em9305_common_channel_callback_314758(
 uint32_t first,uint32_t second,uint32_t unused2,uint32_t unused3,uint32_t fifth)
{
 (void)unused2;(void)unused3;
 uint32_t current=opencfw_em9305_auxiliary_ready_303f68();
 uintptr_t root=0x8015c4u;
 uint8_t count=*(volatile uint8_t *)root;
 uintptr_t record=*(volatile uint32_t *)((uintptr_t)current+44u);
 *(volatile uint8_t *)(record+125u)=(uint8_t)fifth;
 *(volatile uint8_t *)(record+124u)=(uint8_t)second;
 if (count==0u) *(volatile uint8_t *)root=1u;
 uint32_t pending=*(volatile uint32_t *)(root+28u);
 uintptr_t callback=*(volatile uint32_t *)(record+112u);
 *(volatile uint32_t *)(root+28u)=0u;
 uint32_t result=((uint32_t (*)(uint32_t,uint32_t,uint32_t,uintptr_t))callback)(current,pending,first,callback);
 callback=*(volatile uint32_t *)(record+116u);
 if (callback!=0u)
  result=((uint32_t (*)(uint32_t,uint32_t,uint32_t,uintptr_t))callback)(current,first,second,callback);
 result=opencfw_em9305_auxiliary_start_303f50(result);
 if (result!=0u) {
  result=0x51u;
  if (first<7u && ((0x51u>>first)&1u)!=0u)
   result=opencfw_em9305_common_activate_310580(result);
  result=opencfw_em9305_common_radio_finish_3045c0(result);
 }
 return result;
}

extern uint32_t opencfw_em9305_common_channel_callback_314a88(uint32_t,uint32_t,uint32_t,uint32_t,uint32_t);
/* Native 0x314908..0x31497c: callback sourced from a runtime cell,
 * distinct context offset and request object from 0x31481c. */
uint32_t opencfw_em9305_common_callback_314908(uintptr_t object,uintptr_t input)
{
 uintptr_t record=*(volatile uint32_t *)(object+44u),root=0x8015c4u;
 uint8_t descriptor[20];
 (void)opencfw_em9305_common_radio_prepare_30fb4c(input);
 uint32_t primary=*(volatile uint32_t *)(uintptr_t)0x805c14u;
 *(volatile uint32_t *)(root+12u)=(uint32_t)(uintptr_t)&opencfw_em9305_common_channel_callback_314a88;
 *(volatile uint32_t *)(root+8u)=primary;
 *(volatile uint32_t *)(root+20u)=*(volatile uint32_t *)(record+108u);
 *(volatile uint32_t *)(root+16u)=*(volatile uint32_t *)(object+8u);
 (void)opencfw_em9305_common_radio_bind_30fc10(root+8u);
 primary=*(volatile uint32_t *)(uintptr_t)0x805c14u;
 *(volatile uint8_t *)root=0u;
 if (primary!=0u)
  (void)opencfw_em9305_memcpy(descriptor,opencfw_em9305_radio_template_3343f8,20u);
 else (void)opencfw_em9305_memset(descriptor,0u,20u);
 (void)opencfw_em9305_radio_record_30fc28((uintptr_t)descriptor);
 return opencfw_em9305_radio_request_30faec(0x8016f8u,257u);
}

extern uint32_t opencfw_em9305_radio_record_request_30fc68(uintptr_t,uint32_t);
/* Native 0x31497c..0x3149d4: temporarily prepare descriptor +4 from +72,
 * then restore it. STB.AB accesses root before advancing by eight.
 * ADD1 shifts its second operand: record + (0x3c << 1). */
uint32_t opencfw_em9305_common_callback_31497c(uintptr_t object)
{
 uintptr_t original=*(volatile uint32_t *)(object+44u),root=0x8015c4u;
 uint8_t descriptor[20];
 *(volatile uint8_t *)root=1u;
 uintptr_t record=*(volatile uint32_t *)(object+44u);
 uint32_t temporary=*(volatile uint32_t *)(record+72u);
 uint32_t saved=*(volatile uint32_t *)(record+4u);
 *(volatile uint32_t *)(record+4u)=temporary;
 record=*(volatile uint32_t *)(object+44u);
 (void)opencfw_em9305_common_radio_prepare_30fb4c(record);
 record=*(volatile uint32_t *)(object+44u);
 uint32_t primary=*(volatile uint32_t *)(uintptr_t)0x805c14u;
 *(volatile uint32_t *)(record+4u)=saved;
 *(volatile uint32_t *)(root+8u)=primary;
 *(volatile uint32_t *)(root+16u)=*(volatile uint32_t *)(object+8u);
 (void)opencfw_em9305_common_radio_bind_30fc10(root+8u);
 (void)opencfw_em9305_memset(descriptor,0u,20u);
 (void)opencfw_em9305_radio_record_30fc28((uintptr_t)descriptor);
 return opencfw_em9305_radio_record_request_30fc68(original+120u,2u);
}

extern uint32_t opencfw_em9305_radio_schedule_314370(uintptr_t,uintptr_t,uint32_t,uint32_t);
extern uint32_t opencfw_em9305_common_channel_callback_314c04(uint32_t,uint32_t,uint32_t,uint32_t,uint32_t);
extern uint32_t opencfw_em9305_common_channel_callback_314d18(uint32_t);
extern const uint8_t opencfw_em9305_radio_template_3343a8[20];
/* Native 0x3149d4..0x314a88: timing-adjusted preparation and scheduling.
 * Second input survives helper calls. Optional callback keeps its address R1. */
uint32_t opencfw_em9305_common_callback_3149d4(uintptr_t object,uintptr_t input)
{
 uintptr_t record=*(volatile uint32_t *)(object+44u),root=0x8015c4u;
 uint8_t descriptor[20];
 uint32_t now=*(volatile uint32_t *)(uintptr_t)0xf01808u;
 uint32_t timestamp=*(volatile uint32_t *)(object+8u);
 uint32_t result=opencfw_em9305_auxiliary_elapsed_303f8c(timestamp,now);
 if (result==0u) {
  timestamp=*(volatile uint32_t *)(object+8u);
  *(volatile uint32_t *)(root+4u)=timestamp;
  uint32_t guard=opencfw_em9305_auxiliary_guard_interval();
  *(volatile uint32_t *)(object+8u)=guard+now;
  result=opencfw_em9305_auxiliary_elapsed_303f8c(now,*(volatile uint32_t *)(root+4u));
  *(volatile uint32_t *)(record+164u)=result;
 }
 uintptr_t callback=*(volatile uint32_t *)(record+112u);
 if (callback!=0u) (void)((uint32_t (*)(uintptr_t,uintptr_t))callback)(object,callback);
 uint32_t scheduled=opencfw_em9305_radio_schedule_314370(object,record,*(volatile uint32_t *)(object+8u),0u);
 if (scheduled==0u) return opencfw_em9305_auxiliary_signal_304394();
 *(volatile uint32_t *)(root+4u)=*(volatile uint32_t *)(object+8u);
 (void)opencfw_em9305_common_radio_prepare_30fb4c(input);
 *(volatile uint32_t *)(root+20u)=scheduled;
 *(volatile uint32_t *)(root+12u)=(uint32_t)(uintptr_t)&opencfw_em9305_common_channel_callback_314c04;
 *(volatile uint32_t *)(root+8u)=(uint32_t)(uintptr_t)&opencfw_em9305_common_channel_callback_314d18;
 *(volatile uint32_t *)(root+16u)=*(volatile uint32_t *)(object+8u);
 (void)opencfw_em9305_common_radio_bind_30fc10(root+8u);
 *(volatile uint8_t *)root=0u;
 if (*(volatile uint32_t *)(record+104u)!=0u)
  (void)opencfw_em9305_memcpy(descriptor,opencfw_em9305_radio_template_3343a8,20u);
 else (void)opencfw_em9305_memset(descriptor,0u,20u);
 (void)opencfw_em9305_radio_record_30fc28((uintptr_t)descriptor);
 return opencfw_em9305_radio_request_30faec(*(volatile uint32_t *)(record+100u),*(volatile uint8_t *)(record+150u));
}

extern uint32_t opencfw_em9305_common_channel_callback_315000(uint32_t,uint32_t,uint32_t,uint32_t,uint32_t);
extern uint32_t opencfw_em9305_common_channel_callback_315108(void);
extern const uint8_t opencfw_em9305_radio_template_33440c[20];
/* Native 0x3152fc..0x31537c: conditional radio descriptor request.
 * STH.AB writes old root then advances eight; ADD1 yields record+100. */
uint32_t opencfw_em9305_common_callback_3152fc(uintptr_t object,uintptr_t input)
{
 uintptr_t record=*(volatile uint32_t *)(object+44u),root=0x8015c4u;
 uint8_t descriptor[20];
 *(volatile uint32_t *)(root+20u)=4u;
 *(volatile uint32_t *)(root+12u)=(uint32_t)(uintptr_t)&opencfw_em9305_common_channel_callback_315000;
 *(volatile uint32_t *)(root+8u)=(uint32_t)(uintptr_t)&opencfw_em9305_common_channel_callback_315108;
 *(volatile uint16_t *)root=0u;
 uint32_t result=opencfw_em9305_auxiliary_start_303f50((uintptr_t)&opencfw_em9305_common_channel_callback_315108);
 if (result!=0u) return result;
 uintptr_t callback=*(volatile uint32_t *)(record+160u);
 if (callback!=0u) (void)((uint32_t (*)(uintptr_t,uint32_t,uintptr_t))callback)(object,0u,callback);
 (void)opencfw_em9305_common_radio_prepare_30fb4c(input);
 *(volatile uint8_t *)root=0u;
 *(volatile uint32_t *)(root+16u)=*(volatile uint32_t *)(object+8u);
 (void)opencfw_em9305_common_radio_bind_30fc10(root+8u);
 if (*(volatile uint32_t *)(record+116u)!=0u)
  (void)opencfw_em9305_memcpy(descriptor,opencfw_em9305_radio_template_33440c,20u);
 else (void)opencfw_em9305_memset(descriptor,0u,20u);
 (void)opencfw_em9305_radio_record_30fc28((uintptr_t)descriptor);
 return opencfw_em9305_radio_record_request_30fc68(record+100u,2u);
}

/* Native 0x3153fc..0x315490: expanded descriptor callback.
 * ADD2 forms record+160; additional timestamp fields are at +236/+240. */
uint32_t opencfw_em9305_common_callback_3153fc(uintptr_t object,uintptr_t input)
{
 uintptr_t record=*(volatile uint32_t *)(object+44u),root=0x8015c4u;
 uint8_t descriptor[20];
 *(volatile uint32_t *)(root+20u)=4u;
 *(volatile uint32_t *)(root+12u)=(uint32_t)(uintptr_t)&opencfw_em9305_common_channel_callback_315000;
 *(volatile uint32_t *)(root+8u)=(uint32_t)(uintptr_t)&opencfw_em9305_common_channel_callback_315108;
 *(volatile uint16_t *)root=0u;
 uint32_t result=opencfw_em9305_auxiliary_start_303f50((uintptr_t)&opencfw_em9305_common_channel_callback_315108);
 if (result!=0u) return result;
 uintptr_t callback=*(volatile uint32_t *)(record+160u);
 if (callback!=0u) (void)((uint32_t (*)(uintptr_t,uint32_t,uintptr_t))callback)(object,0u,callback);
 (void)opencfw_em9305_common_radio_prepare_30fb4c(input);
 *(volatile uint8_t *)root=0u;
 *(volatile uint32_t *)(root+16u)=*(volatile uint32_t *)(object+8u);
 (void)opencfw_em9305_common_radio_bind_30fc10(root+8u);
 uint32_t enabled=*(volatile uint32_t *)(record+116u);
 if (enabled==0u) enabled=*(volatile uint32_t *)(record+232u);
 if (enabled!=0u)
  (void)opencfw_em9305_memcpy(descriptor,opencfw_em9305_radio_template_33440c,20u);
 else (void)opencfw_em9305_memset(descriptor,0u,20u);
 (void)opencfw_em9305_radio_record_30fc28((uintptr_t)descriptor);
 uint32_t flag=*(volatile uint16_t *)(record+108u);
 uint32_t timestamp=*(volatile uint32_t *)(object+8u);
 *(volatile uint32_t *)(record+236u)=timestamp;
 if (flag!=0u) *(volatile uint32_t *)(record+240u)=timestamp;
 return opencfw_em9305_radio_record_request_30fc68(record+100u,2u);
}

extern uint32_t opencfw_em9305_common_channel_callback_315544(uint32_t,uint32_t);
extern uint32_t opencfw_em9305_common_channel_callback_3155c4(uint32_t);
extern const uint8_t opencfw_em9305_radio_template_334434[20];
/* Native 0x315490..0x3154e0: bind-before-prepare metadata, fixed template,
 * and input descriptor request. No root byte clear appears in this body. */
uint32_t opencfw_em9305_common_callback_315490(uintptr_t object,uintptr_t input)
{
 uintptr_t root=0x8015ccu;
 uint8_t descriptor[20];
 *(volatile uint32_t *)(root+4u)=(uint32_t)(uintptr_t)&opencfw_em9305_common_channel_callback_315544;
 *(volatile uint32_t *)root=(uint32_t)(uintptr_t)&opencfw_em9305_common_channel_callback_3155c4;
 *(volatile uint32_t *)(root+8u)=*(volatile uint32_t *)(object+8u);
 *(volatile uint32_t *)(root+12u)=*(volatile uint32_t *)(input+100u);
 (void)opencfw_em9305_common_radio_prepare_30fb4c(input);
 (void)opencfw_em9305_common_radio_bind_30fc10(root);
 (void)opencfw_em9305_memcpy(descriptor,opencfw_em9305_radio_template_334434,20u);
 (void)opencfw_em9305_radio_record_30fc28((uintptr_t)descriptor);
 return opencfw_em9305_radio_request_30faec(*(volatile uint32_t *)(input+108u),*(volatile uint16_t *)(input+112u));
}

/* Native 0x3154e0..0x315534: zero descriptor then reuses its stack storage
 * for a halfword/word request. Root context at +12 is preserved. */
uint32_t opencfw_em9305_common_callback_3154e0(uintptr_t object,uintptr_t input)
{
 uintptr_t root=0x8015ccu;
 uint32_t descriptor[5];
 *(volatile uint32_t *)(root+4u)=(uint32_t)(uintptr_t)&opencfw_em9305_common_channel_callback_315544;
 *(volatile uint32_t *)root=(uint32_t)(uintptr_t)&opencfw_em9305_common_channel_callback_3155c4;
 *(volatile uint32_t *)(root+8u)=*(volatile uint32_t *)(object+8u);
 (void)opencfw_em9305_common_radio_prepare_30fb4c(input);
 (void)opencfw_em9305_common_radio_bind_30fc10(root);
 (void)opencfw_em9305_memset(descriptor,0u,20u);
 (void)opencfw_em9305_radio_record_30fc28((uintptr_t)descriptor);
 *(volatile uint16_t *)(void *)descriptor=*(volatile uint16_t *)(input+108u);
 descriptor[1]=*(volatile uint32_t *)(input+104u);
 return opencfw_em9305_radio_record_request_30fc68((uintptr_t)descriptor,1u);
}
/* Native 0x315534..0x315544: activation result becomes finish input. */
uint32_t opencfw_em9305_common_callback_315534(uint32_t value)
{ return opencfw_em9305_common_radio_finish_3045c0(opencfw_em9305_common_activate_310580(value)); }

/* Native 0x314408..0x31441c: primary registry dispatch. ADD3 scales
 * record byte by eight; tail callback sees record R1 and own address R2. */
uint32_t opencfw_em9305_common_callback_314408(uintptr_t object)
{
 uintptr_t record=*(volatile uint32_t *)(object+44u);
 uint32_t index=*(volatile uint8_t *)record;
 uintptr_t callback=*(volatile uint32_t *)(0x801534u+index*8u);
 if (callback==0u) return (uint32_t)object;
 return ((uint32_t (*)(uintptr_t,uintptr_t,uintptr_t))callback)(object,record,callback);
}

extern uint32_t opencfw_em9305_radio_completion_303fb8(uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t);
extern uint32_t opencfw_em9305_radio_completion_304140(uint32_t,uint32_t);
/* Native 0x3146a4..0x3146c4: five inputs become six with current object
 * prepended. Delayed R5 assignment precedes completion provider call. */
uint32_t opencfw_em9305_common_channel_callback_3146a4(
 uint32_t first,uint32_t second,uint32_t third,uint32_t fourth,uint32_t fifth)
{
 uint32_t current=opencfw_em9305_auxiliary_ready_303f68();
 return opencfw_em9305_radio_completion_303fb8(current,first,second,third,fourth,fifth);
}
/* Native 0x3146c4..0x3146d4: input and current object completion pair. */
uint32_t opencfw_em9305_common_channel_callback_3146c4(uint32_t first)
{
 uint32_t current=opencfw_em9305_auxiliary_ready_303f68();
 return opencfw_em9305_radio_completion_304140(current,first);
}

/* Exact non-executable descriptor template at 0x3343a8, extent proven by
 * native memcpy length20. SHA256 21fc3f955c14305ed66b2f6064de082e8447f29048da3ab7c5c01090c1b722ab. */
const uint8_t opencfw_em9305_radio_template_3343a8[20]={0x01u,0x00u,0x00u,0x00u,0x00u,0x00u,0x00u,0x00u,0x00u,0x00u,0x00u,0x00u,0x00u,0x00u,0x00u,0x00u,0x00u,0x00u,0x00u,0x00u};

/* Exact non-executable descriptor template at 0x3343f8, extent proven by
 * native memcpy length20. SHA256 21fc3f955c14305ed66b2f6064de082e8447f29048da3ab7c5c01090c1b722ab. */
const uint8_t opencfw_em9305_radio_template_3343f8[20]={0x01u,0x00u,0x00u,0x00u,0x00u,0x00u,0x00u,0x00u,0x00u,0x00u,0x00u,0x00u,0x00u,0x00u,0x00u,0x00u,0x00u,0x00u,0x00u,0x00u};

/* Exact non-executable descriptor template at 0x33440c, extent proven by
 * native memcpy length20. SHA256 21fc3f955c14305ed66b2f6064de082e8447f29048da3ab7c5c01090c1b722ab. */
const uint8_t opencfw_em9305_radio_template_33440c[20]={0x01u,0x00u,0x00u,0x00u,0x00u,0x00u,0x00u,0x00u,0x00u,0x00u,0x00u,0x00u,0x00u,0x00u,0x00u,0x00u,0x00u,0x00u,0x00u,0x00u};

/* Exact non-executable descriptor template at 0x334434, extent proven by
 * native memcpy length20. SHA256 39fe4a43b6be3739483d258fc078a00068fa9b3186c6dfb17c9314eaf0262c96. */
const uint8_t opencfw_em9305_radio_template_334434[20]={0x03u,0x00u,0x00u,0x00u,0x00u,0x00u,0x00u,0x00u,0x00u,0x00u,0x00u,0x00u,0x00u,0x00u,0x00u,0x00u,0x00u,0x00u,0x00u,0x00u};

/* Native 0x3151a0..0x3151cc: count, descriptor completion and optional
 * activation/finish. Descriptor callback retains its own address in R2. */
uint32_t opencfw_em9305_common_channel_callback_3151a0(uint32_t first)
{
 uintptr_t root=0x8015c4u;
 uint8_t count=*(volatile uint8_t *)root;
 *(volatile uint8_t *)root=(uint8_t)(count+1u);
 uint32_t current=opencfw_em9305_auxiliary_ready_303f68();
 uintptr_t record=*(volatile uint32_t *)((uintptr_t)current+44u);
 uintptr_t callback=*(volatile uint32_t *)(record+104u);
 uint32_t result=((uint32_t (*)(uint32_t,uint32_t,uintptr_t))callback)(current,first,callback);
 result=opencfw_em9305_auxiliary_start_303f50(result);
 if (result!=0u) {
  result=opencfw_em9305_common_activate_310580(result);
  result=opencfw_em9305_common_radio_finish_3045c0(result);
 }
 return result;
}

extern uint32_t opencfw_em9305_radio_followup_30fb3c(uint32_t,uint32_t);
/* Native 0x315544..0x3155c4: completion, conditional follow-up, counters.
 * BSET(first,2)==4 accepts only first=0 or4; native callback R3=self. */
uint32_t opencfw_em9305_common_channel_callback_315544(uint32_t first,uint32_t second)
{
 uint8_t descriptor[20];
 uint32_t current=opencfw_em9305_auxiliary_ready_303f68();
 if (current==0u) return current;
 uintptr_t record=*(volatile uint32_t *)((uintptr_t)current+44u);
 uintptr_t callback=*(volatile uint32_t *)(record+104u);
 *(volatile uint8_t *)(record+114u)=(uint8_t)second;
 uint32_t result=((uint32_t (*)(uint32_t,uint32_t,uint32_t,uintptr_t))callback)(current,first,second,callback);
 if ((first|4u)==4u && result!=0u) {
  (void)opencfw_em9305_memcpy(descriptor,opencfw_em9305_radio_template_334434,20u);
  (void)opencfw_em9305_radio_record_30fc28((uintptr_t)descriptor);
  (void)opencfw_em9305_radio_followup_30fb3c(*(volatile uint32_t *)(record+108u),*(volatile uint16_t *)(record+112u));
 } else {
  result=opencfw_em9305_common_activate_310580(result);
  (void)opencfw_em9305_common_radio_finish_3045c0(result);
 }
 uintptr_t counters=0x801848u;
 uint32_t offset=first==4u?4u:first==3u?8u:first==0u?0u:16u;
 volatile uint32_t *counter=(volatile uint32_t *)(counters+offset);
 *counter=*counter+1u;
 return (uint32_t)counters;
}

extern uint32_t opencfw_em9305_radio_adjust_3101f4(uint32_t);
extern uint32_t opencfw_em9305_radio_bits_311fcc(uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_radio_commit_311fb0(uintptr_t);
extern void opencfw_em9305_radio_callback_333480(void);
extern uint32_t opencfw_em9305_radio_schedule_311e60(uint32_t,uint32_t,uintptr_t);
/* Native 0x310374..0x3103e0: parameter adjustment, optional radio bytes,
 * nine-bit mask and scheduled callback. Delay slots pass stack outputs. */
uint32_t opencfw_em9305_radio_followup_driver_310374(uint32_t first,uint32_t second)
{
 uint32_t adjusted=first;uint16_t selector=(uint16_t)second;
 (void)opencfw_em9305_radio_adjust_3101f4(first);
 uintptr_t root=0x805e94u;
 uint8_t enabled=*(volatile uint8_t *)(root+17u);
 uint32_t mode=selector,parameter=adjusted;
 if (enabled!=0u) {
  uint8_t format=*(volatile uint8_t *)(root+19u);
  uint32_t flag;
  if (format==2u) flag=0x80u;
  else flag=*(volatile uint8_t *)(root+18u)==1u?0xffffff80u:0u;
  uint8_t bits=*(volatile uint8_t *)(root+40u);
  *(volatile uint8_t *)(root+40u)=(uint8_t)(flag|(bits&0x7fu));
  (void)opencfw_em9305_radio_bits_311fcc(root+20u,root+36u);
  (void)opencfw_em9305_radio_commit_311fb0(root+36u);
 }
 (void)opencfw_em9305_common_radio_mask_312094(mode);
 uint32_t result=opencfw_em9305_radio_schedule_311e60(parameter,mode,(uintptr_t)&opencfw_em9305_radio_callback_333480);
 *(volatile uint32_t *)root=parameter;
 return result;
}
/* Native 0x30fb3c..0x30fb4c: wrapping increment and selector store before tail. */
uint32_t opencfw_em9305_radio_followup_30fb3c(uint32_t first,uint32_t second)
{
 *(volatile uint16_t *)(uintptr_t)0x805d38u=(uint16_t)second;
 *(volatile uint32_t *)(uintptr_t)0x805d34u=first+1u;
 return opencfw_em9305_radio_followup_driver_310374(first,second);
}

/* Native 0x311fb0..0x311fcc: five sequential source bytes, descending
 * MMIO destinations. LD.AB/ST.AB access old addresses before writeback. */
uint32_t opencfw_em9305_radio_commit_311fb0(uintptr_t source)
{
 for (uint32_t index=0u;index<5u;++index) {
  uint8_t byte=*(volatile uint8_t *)(source+index);
  *(volatile uint8_t *)(uintptr_t)(0xf040a2u-index)=byte;
 }
 return (uint32_t)(source+5u);
}
/* Native 0x311fcc..0x311ffc: sixteen ascending then thirteen descending
 * writes. Native R0 finishes at 0xf04095. */
uint32_t opencfw_em9305_radio_bits_311fcc(uintptr_t first,uintptr_t second)
{
 for (uint32_t index=0u;index<16u;++index) {
  uint8_t byte=*(volatile uint8_t *)(first+index);
  *(volatile uint8_t *)(uintptr_t)(0xf04084u+index)=byte;
 }
 for (uint32_t index=0u;index<13u;++index) {
  uint8_t byte=*(volatile uint8_t *)(second+index);
  *(volatile uint8_t *)(uintptr_t)(0xf040a2u-index)=byte;
 }
 return 0xf04095u;
}

/* Native 0x3101f4..0x310200: stores original first parameter only.
 * R2/R3 supplied by 0x310374 are dead; stack outputs are never modified. */
uint32_t opencfw_em9305_radio_adjust_3101f4(uint32_t first)
{ *(volatile uint32_t *)(uintptr_t)0x805ec8u=first;return first; }

/* Native 0x3155c4..0x315640: activate, descriptor callback, optional
 * follow-up request and counters. Native current-object dereference is
 * unconditional; no null guard is invented. */
uint32_t opencfw_em9305_common_channel_callback_3155c4(uint32_t first)
{
 uint32_t descriptor[5];
 uint32_t current=opencfw_em9305_auxiliary_ready_303f68();
 uintptr_t record=*(volatile uint32_t *)((uintptr_t)current+44u);
 uint32_t activated=opencfw_em9305_common_activate_310580(current);
 uintptr_t callback=*(volatile uint32_t *)(record+100u);
 uint32_t result=((uint32_t (*)(uint32_t,uint32_t,uintptr_t))callback)(activated,first,callback);
 if (first==0u && result!=0u) {
  uintptr_t root=0x8015ccu;
  uint32_t timestamp=*(volatile uint32_t *)(root+8u);
  timestamp+=*(volatile uint16_t *)(record+110u);
  *(volatile uint32_t *)(root+8u)=timestamp;
  (void)opencfw_em9305_common_radio_prepare_30fb4c(record);
  (void)opencfw_em9305_common_radio_bind_30fc10(root);
  (void)opencfw_em9305_memset(descriptor,0u,20u);
  (void)opencfw_em9305_radio_record_30fc28((uintptr_t)descriptor);
  *(volatile uint16_t *)(void *)descriptor=*(volatile uint16_t *)(record+108u);
  descriptor[1]=*(volatile uint32_t *)(record+104u);
  (void)opencfw_em9305_radio_record_request_30fc68((uintptr_t)descriptor,1u);
 } else (void)opencfw_em9305_common_radio_finish_3045c0(result);
 uintptr_t counters=0x801848u;
 volatile uint32_t *counter=(volatile uint32_t *)(counters+(first==0u?12u:16u));
 *counter=*counter+1u;
 return (uint32_t)counters;
}

/* Native 0x304140..0x304184: counter-gated completion. Incoming R0 is
 * overwritten by count+1 before any call; native finish receives that value. */
uint32_t opencfw_em9305_radio_completion_304140(uint32_t unused,uint32_t second)
{
 (void)unused;
 uintptr_t root=0x8015c4u;
 uint8_t count=*(volatile uint8_t *)root;
 uint32_t increment=(uint32_t)count+1u;
 *(volatile uint8_t *)root=(uint8_t)increment;
 if (count!=1u) return 0u;
 if (second!=0u) {
  (void)opencfw_em9305_common_radio_finish_3045c0(increment);
  return 1u;
 }
 uint8_t descriptor[20];
 (void)opencfw_em9305_memset(descriptor,0u,20u);
 (void)opencfw_em9305_radio_record_30fc28((uintptr_t)descriptor);
 (void)opencfw_em9305_radio_followup_30fb3c(0x8013f0u,257u);
 return 0u;
}

/* Native 0x3151fc..0x315260: extended five-input completion.
 * Input R2 is dead; R3 is stored only when counter was zero. Indirect
 * callback's native R3 is its address, retained in the typed call. */
uint32_t opencfw_em9305_common_channel_callback_3151fc(
 uint32_t first,uint32_t second,uint32_t unused,uint32_t fourth,uint32_t fifth)
{
 (void)unused;
 uint32_t current=opencfw_em9305_auxiliary_ready_303f68();
 uintptr_t root=0x8015c4u;
 uint8_t count=*(volatile uint8_t *)root;
 uintptr_t record=*(volatile uint32_t *)((uintptr_t)current+44u);
 *(volatile uint8_t *)(record+133u)=(uint8_t)fifth;
 *(volatile uint8_t *)(record+132u)=(uint8_t)second;
 if (count==0u) {
  *(volatile uint32_t *)(record+128u)=fourth;
  *(volatile uint8_t *)root=1u;
 }
 uint32_t pending=*(volatile uint32_t *)(root+28u);
 uintptr_t callback=*(volatile uint32_t *)(record+116u);
 *(volatile uint32_t *)(root+28u)=0u;
 uint32_t result=((uint32_t (*)(uint32_t,uint32_t,uint32_t,uintptr_t))callback)(current,pending,first,callback);
 callback=*(volatile uint32_t *)(record+120u);
 if (callback!=0u)
  result=((uint32_t (*)(uint32_t,uint32_t,uint32_t,uintptr_t))callback)(current,first,second,callback);
 result=opencfw_em9305_auxiliary_start_303f50(result);
 if (result!=0u) {
  result=0x51u;
  if (first<7u && ((0x51u>>first)&1u)!=0u)
   result=opencfw_em9305_common_activate_310580(result);
  result=opencfw_em9305_common_radio_finish_3045c0(result);
 }
 return result;
}

/* Exact 20-byte non-executable template 0x3343d0, native copy extent.
 * SHA256 21fc3f955c14305ed66b2f6064de082e8447f29048da3ab7c5c01090c1b722ab. */
const uint8_t opencfw_em9305_radio_template_3343d0[20]={1u};
/* Native 0x314fa4..0x315000: completion or counter-selected restart.
 * Native zero-current branch reads absolute address0x2c; preserve this
 * architectural memory-map access rather than adding a null fallback. */
uint32_t opencfw_em9305_common_channel_callback_314fa4(void)
{
 uint32_t current=opencfw_em9305_auxiliary_ready_303f68();
 if (current!=0u) return opencfw_em9305_common_radio_finish_3045c0(current);
 uintptr_t root=0x8015c4u;
 uint8_t count=*(volatile uint8_t *)root;
 uintptr_t record;
 __asm__ volatile("ld %0,[%1]" : "=r"(record) : "r"((uintptr_t)0x2cu) : "memory");
 *(volatile uint8_t *)root=(uint8_t)(count+1u);
 if (count!=2u) {
  if (count!=0u) return current;
  uint32_t followup=*(volatile uint32_t *)(record+104u);
  if (followup!=0u) {
   uint8_t descriptor[20];
   (void)opencfw_em9305_memcpy(descriptor,opencfw_em9305_radio_template_3343d0,20u);
   (void)opencfw_em9305_radio_record_30fc28((uintptr_t)descriptor);
   return opencfw_em9305_radio_followup_30fb3c(*(volatile uint32_t *)(record+104u),36u);
  }
 }
 uint32_t result=opencfw_em9305_common_channel_start_314db8(current,record,0u,0u);
 if (result==0u) return result;
 return opencfw_em9305_common_radio_finish_3045c0(opencfw_em9305_common_activate_310580(result));
}

extern uint32_t opencfw_em9305_channel_timing_312b88(uint32_t,uint32_t,uint32_t);
extern uint32_t opencfw_em9305_channel_continue_314f54(uintptr_t,uintptr_t);
/* Native 0x315108..0x3151a0: counter phases and deferred channel start.
 * Zero current retains architectural descriptor pointer at address0x2c. */
uint32_t opencfw_em9305_common_channel_callback_315108(void)
{
 uint32_t current=opencfw_em9305_auxiliary_ready_303f68();
 if (current!=0u) return opencfw_em9305_common_radio_finish_3045c0(current);
 uintptr_t root=0x8015c4u;
 uint32_t count=*(volatile uint8_t *)root;
 uintptr_t record;
 __asm__ volatile("ld %0,[%1]" : "=r"(record) : "r"((uintptr_t)0x2cu) : "memory");
 uint32_t result;
 if (count==2u) {
  *(volatile uint8_t *)root=3u;
  uint32_t first=*(volatile uint8_t *)(record+13u);
  uint32_t second=*(volatile uint8_t *)(record+177u);
  uint32_t timestamp=*(volatile uint32_t *)(record+180u);
  result=opencfw_em9305_channel_timing_312b88(first,second,14u);
  *(volatile uint32_t *)(root+16u)=result+timestamp+150u;
 } else if (count!=3u) {
  if (count!=0u) return count;
  uint32_t followup=*(volatile uint32_t *)(record+116u);
  if (followup!=0u) {
   uint8_t descriptor[20];
   (void)opencfw_em9305_memcpy(descriptor,opencfw_em9305_radio_template_33440c,20u);
   *(volatile uint8_t *)root=1u;
   (void)opencfw_em9305_radio_record_30fc28((uintptr_t)descriptor);
   return opencfw_em9305_radio_followup_30fb3c(*(volatile uint32_t *)(record+116u),36u);
  }
  uint32_t flag=*(volatile uint8_t *)(record+228u);
  if (flag!=0u) {
   uintptr_t callback=*(volatile uint32_t *)(uintptr_t)0x805c24u;
   if (callback==0u) return flag;
   result=((uint32_t (*)(uint32_t,uintptr_t,uintptr_t))callback)(current,record,callback);
   if (result==0u) return result;
   return opencfw_em9305_common_radio_finish_3045c0(opencfw_em9305_common_activate_310580(result));
  }
  *(volatile uint8_t *)root=3u;
 }
 result=opencfw_em9305_channel_continue_314f54(current,record);
 if (result==0u) return result;
 return opencfw_em9305_common_radio_finish_3045c0(opencfw_em9305_common_activate_310580(result));
}

/* Native 0x314f54..0x314fa4: descriptor continuation. Callback R2 retains
 * its address, ADD2 request points at record+136, success returns zero. */
uint32_t opencfw_em9305_channel_continue_314f54(uintptr_t object,uintptr_t record)
{
 uintptr_t callback=*(volatile uint32_t *)(record+160u);
 if (callback==0u) return 1u;
 uint32_t adjustment=((uint32_t (*)(uintptr_t,uint32_t,uintptr_t))callback)(object,1u,callback);
 if (adjustment==0u) return 1u;
 uintptr_t input=*(volatile uint32_t *)(object+44u);
 (void)opencfw_em9305_common_radio_prepare_30fb4c(input);
 uintptr_t root=0x8015ccu;
 uint32_t timestamp=*(volatile uint32_t *)(root+8u);
 *(volatile uint32_t *)(root+8u)=timestamp+adjustment;
 (void)opencfw_em9305_common_radio_bind_30fc10(root);
 uint8_t descriptor[20];
 (void)opencfw_em9305_memset(descriptor,0u,20u);
 (void)opencfw_em9305_radio_record_30fc28((uintptr_t)descriptor);
 (void)opencfw_em9305_radio_record_request_30fc68(record+136u,2u);
 return 0u;
}

extern uint32_t opencfw_em9305_channel_retry_314594(uintptr_t,uintptr_t);
/* Native 0x314d18..0x314d94: pending completion, counter gate and retry. */
uint32_t opencfw_em9305_common_channel_callback_314d18(uint32_t first)
{
 uint32_t current=opencfw_em9305_auxiliary_ready_303f68();
 uintptr_t record=*(volatile uint32_t *)((uintptr_t)current+44u);
 uintptr_t callback=*(volatile uint32_t *)(record+140u);
 if (callback!=0u) {
  uint32_t flag=*(volatile uint8_t *)(record+148u);
  if (flag!=0u) {
   uint32_t context=*(volatile uint32_t *)(record+132u);
   uint32_t result=((uint32_t (*)(uint32_t,uint32_t,uintptr_t))callback)(context,first,callback);
   if (result!=0u) {
    *(volatile uint8_t *)(record+148u)=0u;
    *(volatile uint32_t *)(record+132u)=0u;
   }
   return result;
  }
 }
 uintptr_t root=0x8015c4u;
 uint32_t count=*(volatile uint8_t *)root;
 *(volatile uint8_t *)root=(uint8_t)(count+1u);
 if (count!=1u) return count;
 if (first!=0u) return opencfw_em9305_common_radio_finish_3045c0(count);
 uint32_t context=*(volatile uint32_t *)(record+104u);
 callback=*(volatile uint32_t *)(record+124u);
 uint32_t result=((uint32_t (*)(uint32_t,uint32_t,uintptr_t))callback)(current,context,callback);
 if (result!=0u) {
  uint8_t descriptor[20];
  (void)opencfw_em9305_memset(descriptor,0u,20u);
  (void)opencfw_em9305_radio_record_30fc28((uintptr_t)descriptor);
  return opencfw_em9305_radio_followup_30fb3c(*(volatile uint32_t *)(record+108u),39u);
 }
 (void)opencfw_em9305_common_activate_310580(result);
 result=opencfw_em9305_channel_retry_314594(current,record);
 if (result!=0u) return opencfw_em9305_common_radio_finish_3045c0(result);
 return result;
}

/* Authenticated resident ROM calls: explicit ABI providers, not firmware
 * implementations. Their bodies and integration qualification remain open. */
extern uint32_t opencfw_em9305_rom_radio_100dd4(uint32_t);
extern uint32_t opencfw_em9305_rom_radio_100ddc(uint32_t,uint32_t);
extern uint32_t opencfw_em9305_rom_radio_101038(uint32_t,uint32_t,uint32_t);
extern uint32_t opencfw_em9305_rom_radio_100fc0(uint32_t,uintptr_t,uint32_t);
extern uint32_t opencfw_em9305_rom_radio_101054(uint32_t,uint32_t);
/* Native 0x311e60..0x311ee0: timer descriptor and ROM channel3 setup.
 * ST.AB writes F04080 before advancing to F04068 for stack descriptor. */
uint32_t opencfw_em9305_radio_schedule_311e60(uint32_t first,uint32_t second,uintptr_t callback)
{
 uintptr_t root=0x8019c4u;
 *(volatile uint32_t *)root=first;
 *(volatile uint32_t *)(root+4u)=(uint32_t)callback;
 *(volatile uint16_t *)(root+12u)=(uint16_t)second;
 *(volatile uint16_t *)(root+14u)=0u;
 (void)opencfw_em9305_rom_radio_100dd4(1u);
 (void)opencfw_em9305_rom_radio_100ddc(3u,0u);
 uint32_t end=first+second-1u;
 uint32_t encoded=(((second<<8u)-256u)&0x1fff00u)|0x80200005u;
 *(volatile uint32_t *)(uintptr_t)0xf04080u=1u;
 uint32_t descriptor[4]={encoded,0xf04068u,end,0u};
 (void)opencfw_em9305_rom_radio_101038(3u,5u,0u);
 (void)opencfw_em9305_rom_radio_100fc0(3u,(uintptr_t)descriptor,0u);
 (void)opencfw_em9305_rom_radio_101054(3u,1u);
 (void)opencfw_em9305_rom_radio_100ddc(3u,1u);
 return 1u;
}

/* Native 0x314594..0x314640: elapsed retry scheduling. Return1 means
 * no retry submitted, while callback handling or descriptor submission returns0. */
uint32_t opencfw_em9305_channel_retry_314594(uintptr_t object,uintptr_t record)
{
 if (opencfw_em9305_auxiliary_start_303f50(object)!=0u) return 1u;
 uint32_t now=opencfw_em9305_pal_current_time();
 uintptr_t root=0x8015c4u;
 uint32_t previous=*(volatile uint32_t *)(root+4u);
 uint32_t elapsed=opencfw_em9305_auxiliary_elapsed_303f8c(now,previous);
 uint32_t accumulated=*(volatile uint32_t *)(record+164u);
 *(volatile uint32_t *)(root+4u)=now;
 *(volatile uint32_t *)(record+164u)=elapsed+accumulated;
 uint32_t guard=opencfw_em9305_auxiliary_guard_interval();
 uint32_t scheduled=opencfw_em9305_radio_schedule_314370(object,record,now,guard);
 if (scheduled==0u) return 1u;
 uintptr_t callback=*(volatile uint32_t *)(record+136u);
 if (callback!=0u) {
  uint32_t result=((uint32_t (*)(uintptr_t,uint32_t,uint32_t,uintptr_t))callback)(object,now,scheduled,callback);
  if (result!=0u) {
   uintptr_t actual=*(volatile uint32_t *)(object+44u);
   *(volatile uint8_t *)(actual+148u)=1u;
   return 0u;
  }
 }
 guard=opencfw_em9305_auxiliary_guard_interval();
 now=*(volatile uint32_t *)(root+4u);
 *(volatile uint32_t *)(root+16u)=guard+now;
 *(volatile uint32_t *)(root+20u)=scheduled;
 (void)opencfw_em9305_common_radio_bind_30fc10(root+8u);
 *(volatile uint8_t *)root=0u;
 uint8_t descriptor[20];
 if (*(volatile uint32_t *)(record+104u)!=0u)
  (void)opencfw_em9305_memcpy(descriptor,opencfw_em9305_radio_template_3343a8,20u);
 else (void)opencfw_em9305_memset(descriptor,0u,20u);
 (void)opencfw_em9305_radio_record_30fc28((uintptr_t)descriptor);
 (void)opencfw_em9305_radio_request_30faec(*(volatile uint32_t *)(record+100u),39u);
 return 0u;
}

uint32_t opencfw_em9305_auxiliary_config_delay_303f74(void)
{
 uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805c18u;
 return *(volatile uint8_t *)(config+2u);
}
extern uint32_t opencfw_em9305_channel_timing_adjust_312c5c(uint32_t);
/* Native 0x314db8..0x314ea4: cycle channel mask and submit radio request.
 * Signed counter byte==3 is the native stop. Root byte1 may wrap. */
uint32_t opencfw_em9305_common_channel_start_314db8(
 uintptr_t object,uintptr_t record,uint32_t third,uint32_t fourth)
{
 if (opencfw_em9305_auxiliary_start_303f50(object)!=0u) return 1u;
 uintptr_t root=0x8015c4u;
 uintptr_t actual=*(volatile uint32_t *)(object+44u);
 uint32_t channel=*(volatile uint8_t *)(root+1u);
 uint32_t attempts=*(volatile uint8_t *)(root+2u);
 for (;;) {
  if ((int8_t)(uint8_t)attempts==3) return 1u;
  int32_t signed_channel=(int8_t)(uint8_t)channel;
  if ((uint32_t)signed_channel>=3u) channel-=3u;
  ++attempts;
  *(volatile uint8_t *)(root+2u)=(uint8_t)attempts;
  *(volatile uint8_t *)(actual+1u)=(uint8_t)(channel+37u);
  uint32_t next=channel+1u;
  *(volatile uint8_t *)(root+1u)=(uint8_t)next;
  uint32_t mask=*(volatile uint8_t *)(record+127u);
  if (((mask>>(channel&31u))&1u)!=0u) break;
  channel=next;
 }
 uint32_t timestamp;
 if (fourth!=0u) {
  (void)opencfw_em9305_common_radio_prepare_30fb4c(actual);
  timestamp=*(volatile uint32_t *)(object+8u);
 } else {
  if ((third|4u)==4u) (void)opencfw_em9305_common_activate_310580((uint32_t)actual);
  (void)opencfw_em9305_common_radio_prepare_30fb4c(actual);
  if (*(volatile uint32_t *)(record+104u)!=0u) {
   uint32_t now=opencfw_em9305_pal_current_time();
   timestamp=now+opencfw_em9305_auxiliary_config_delay_303f74();
  } else {
   uint32_t length=*(volatile uint8_t *)(record+124u);
   uint32_t mode=*(volatile uint8_t *)(actual+12u);
   uint32_t option=*(volatile uint8_t *)(actual+14u);
   uint32_t duration=opencfw_em9305_channel_timing_312b88(mode,option,length);
   duration+=opencfw_em9305_auxiliary_config_delay_303f74();
   duration=opencfw_em9305_channel_timing_adjust_312c5c(duration);
   timestamp=*(volatile uint32_t *)(root+16u)+duration;
  }
 }
 *(volatile uint32_t *)(root+16u)=timestamp;
 *(volatile uint8_t *)root=0u;
 uintptr_t callback=*(volatile uint32_t *)(record+112u);
 if (callback!=0u) (void)((uint32_t (*)(uintptr_t,uint32_t,uintptr_t))callback)(object,timestamp,callback);
 (void)opencfw_em9305_common_radio_bind_30fc10(root+8u);
 uint32_t descriptor[5];
 if (*(volatile uint32_t *)(record+104u)!=0u)
  (void)opencfw_em9305_memcpy(descriptor,opencfw_em9305_radio_template_3343d0,20u);
 else (void)opencfw_em9305_memset(descriptor,0u,20u);
 (void)opencfw_em9305_radio_record_30fc28((uintptr_t)descriptor);
 *(volatile uint16_t *)(void *)descriptor=*(volatile uint8_t *)(record+124u);
 descriptor[1]=*(volatile uint32_t *)(record+100u);
 (void)opencfw_em9305_radio_record_request_30fc68((uintptr_t)descriptor,1u);
 return 0u;
}

/* Native 0x310678..0x31069c: nested critical entry, byte depth with
 * full-width increment return. Re-read depth after CLRI/SYNC as native. */
uint32_t opencfw_em9305_radio_request_enter_310678(void)
{
 volatile uint8_t *depth=(volatile uint8_t *)(uintptr_t)0x805ed4u;
 uint32_t value=*depth;
 if (value==0u) {
  uint32_t irq;
  __asm__ volatile("clri %0\n\tsync" : "=r"(irq) :: "memory");
  value=*depth;
  *(volatile uint32_t *)(uintptr_t)0x805ed0u=irq;
 }
 ++value;*depth=(uint8_t)value;return value;
}
/* Native 0x31069c..0x3106bc: decrement low byte; restore on zero.
 * Return is depth-address when nonzero, saved IRQ when restored. */
uint32_t opencfw_em9305_radio_request_exit_31069c(void)
{
 volatile uint8_t *depth=(volatile uint8_t *)(uintptr_t)0x805ed4u;
 uint8_t value=(uint8_t)(*depth-1u);
 *depth=value;
 if (value!=0u) return 0x805ed4u;
 uint32_t irq=*(volatile uint32_t *)(uintptr_t)0x805ed0u;
 __asm__ volatile("seti %0" :: "r"(irq) : "memory");
 return irq;
}

/* Native 0x333450..0x333480: critical deadline test uses wrapping
 * subtraction's sign bit, not a saturating comparison. */
uint32_t opencfw_em9305_radio_deadline_333450(uint32_t deadline)
{
 (void)opencfw_em9305_radio_request_enter_310678();
 uint32_t now=*(volatile uint32_t *)(uintptr_t)0xf01808u;
 uint32_t delta=deadline-now-10u;
 if ((delta&0x80000000u)==0u) {
  *(volatile uint32_t *)(uintptr_t)0xf01820u=deadline;
  (void)opencfw_em9305_common_timer_mask_310bd0(1u,1u);
 }
 (void)opencfw_em9305_radio_request_exit_31069c();
 return (~delta)>>31u;
}
/* Native 0x3123d0..0x312410: optional control mode then unconditional
 * byte trigger. Incoming R0 dead; return path retains native control R0. */
uint32_t opencfw_em9305_radio_trigger_3123d0(void)
{
 uint32_t value=*(volatile uint8_t *)(uintptr_t)0x8018dcu;
 if (value!=0u) {
  value=*(volatile uint32_t *)(uintptr_t)0x8012e0u;
  uint32_t control=*(volatile uint32_t *)(uintptr_t)0x8012f8u;
  value=(value<<2u)&0x3cu;
  control=((control&0xffffbfc3u)|value)|0x4000u;
  *(volatile uint32_t *)(uintptr_t)0x8012f8u=control;
  *(volatile uint32_t *)(uintptr_t)0xf0484cu=control;
 }
 *(volatile uint8_t *)(uintptr_t)0xf04401u=3u;
 return value;
}
/* Native 0x310600..0x310634: deadline state and callback on failure. */
uint32_t opencfw_em9305_radio_request_state_310600(uint32_t offset)
{
 uintptr_t root=0x805e78u;
 uint32_t base=*(volatile uint32_t *)(root+12u);
 uint32_t lead=*(volatile uint16_t *)(root+34u);
 uint32_t deadline=offset+base-lead-113u;
 *(volatile uint32_t *)(root+16u)=deadline;
 uint32_t result=opencfw_em9305_radio_deadline_333450(deadline);
 if (result!=0u) {
  result=opencfw_em9305_radio_trigger_3123d0();
  *(volatile uint8_t *)root=2u;
  return result;
 }
 uintptr_t callback=*(volatile uint32_t *)(root+8u);
 *(volatile uint8_t *)root=1u;
 return ((uint32_t (*)(uint32_t,uintptr_t))callback)(1u,callback);
}
/* Native 0x310640..0x310654: state2 store before zero-offset tail. */
uint32_t opencfw_em9305_radio_request_base_310640(uint32_t base)
{
 *(volatile uint32_t *)(uintptr_t)0x805e84u=base;
 *(volatile uint8_t *)(uintptr_t)0x805e78u=2u;
 return opencfw_em9305_radio_request_state_310600(0u);
}

/* Native 0x311ef0..0x311f6e: channel2 descriptor. ST.AB stores at
 * F04080 then advances to F04058; stack word order differs from channel3. */
uint32_t opencfw_em9305_radio_schedule_311ef0(uint32_t first,uint32_t second,uintptr_t callback)
{
 uintptr_t root=0x8019d4u;
 *(volatile uint32_t *)root=first;
 *(volatile uint32_t *)(root+4u)=(uint32_t)callback;
 *(volatile uint16_t *)(root+12u)=(uint16_t)second;
 *(volatile uint16_t *)(root+14u)=0u;
 (void)opencfw_em9305_rom_radio_100dd4(1u);
 (void)opencfw_em9305_rom_radio_100ddc(2u,0u);
 uint32_t end=first+second-1u;
 uint32_t encoded=(((second<<8u)-256u)&0x1fff00u)|0x40200005u;
 *(volatile uint32_t *)(uintptr_t)0xf04080u=2u;
 uint32_t descriptor[4]={encoded,end,0xf04058u,0u};
 (void)opencfw_em9305_rom_radio_101038(2u,6u,0u);
 (void)opencfw_em9305_rom_radio_100fc0(2u,(uintptr_t)descriptor,0u);
 (void)opencfw_em9305_rom_radio_101054(2u,1u);
 (void)opencfw_em9305_rom_radio_100ddc(2u,1u);
 return 1u;
}
/* Callback body remains an explicit firmware source import. */
extern uint32_t opencfw_em9305_radio_callback_33354c(uint32_t);
/* Native 0x3105b8..0x310600: optional record bits before channel2 setup. */
uint32_t opencfw_em9305_radio_request_3105b8(uintptr_t first,uint32_t second)
{
 uintptr_t root=0x805ea4u;
 if (*(volatile uint8_t *)root!=0u && *(volatile uint8_t *)(first+1u)!=0u) {
  uint32_t mode=*(volatile uint8_t *)(root+2u);
  uint32_t bits=*(volatile uint8_t *)(root+24u);
  *(volatile uint8_t *)(root+24u)=(uint8_t)((bits&127u)|((mode==1u)?128u:0u));
  (void)opencfw_em9305_radio_bits_311fcc(root+4u,root+20u);
  (void)opencfw_em9305_radio_commit_311fb0(root+20u);
 }
 return opencfw_em9305_radio_schedule_311ef0((uint32_t)first,second,
     (uintptr_t)&opencfw_em9305_radio_callback_33354c);
}
/* Native 0x33354c..0x333582: channel2 completion. R1/R2 retain the
 * callback address in the two distinct indirect-call paths. */
uint32_t opencfw_em9305_radio_callback_33354c(uint32_t status)
{
 (void)opencfw_em9305_pal_hook_three(16u);
 uintptr_t root=0x805e78u;
 if (status!=0u) {
  (void)opencfw_em9305_common_activate_310580(16u);
  uintptr_t callback=*(volatile uint32_t *)(root+8u);
  return ((uint32_t (*)(uint32_t,uintptr_t))callback)(1u,callback);
 }
 uint32_t lead=*(volatile uint16_t *)(root+34u);
 uint32_t captured=*(volatile uint32_t *)(uintptr_t)0xf01848u;
 uintptr_t callback=*(volatile uint32_t *)(root+8u);
 *(volatile uint32_t *)(root+20u)=captured+lead;
 return ((uint32_t (*)(uint32_t,uint32_t,uintptr_t))callback)(0u,lead,callback);
}
/* Exact non-executable 20-byte template at3343bc, native copy extent. */
const uint8_t opencfw_em9305_radio_template_3343bc[20]={1u};
extern uint32_t opencfw_em9305_radio_cancel_30fab8(uint32_t);
/* Native30fab8 unconditional branch to310580, with unchanged incoming R0. */
uint32_t opencfw_em9305_radio_cancel_30fab8(uint32_t value)
{ return opencfw_em9305_common_activate_310580(value); }
/* Native 0x3147b4..0x31481a: required descriptor callback precedes
 * pending-state branches; the zero-current path retains native dereference. */
void opencfw_em9305_common_channel_callback_3147b4(void)
{
 uint32_t current=opencfw_em9305_auxiliary_ready_303f68();
 uintptr_t record=*(volatile uint32_t *)((uintptr_t)current+44u);
 uintptr_t callback=*(volatile uint32_t *)(record+108u);
 uint32_t result=((uint32_t (*)(uint32_t,uint32_t,uintptr_t))callback)(current,current,callback);
 uintptr_t root=0x8015dcu;
 uint32_t pending=*(volatile uint32_t *)(root+4u);
 if (current!=0u) {
  if (pending!=0u) {
   *(volatile uint32_t *)(root+4u)=0u;
   callback=*(volatile uint32_t *)(record+112u);
   result=((uint32_t (*)(uint32_t,uint32_t,uint32_t,uintptr_t))callback)(current,pending,2u,callback);
  }
  result=opencfw_em9305_common_radio_finish_3045c0(result);
 } else if (pending!=0u) {
  uint32_t descriptor[5];
  (void)opencfw_em9305_memcpy(descriptor,opencfw_em9305_radio_template_3343bc,20u);
  (void)opencfw_em9305_radio_record_30fc28((uintptr_t)descriptor);
  result=opencfw_em9305_radio_followup_30fb3c(*(volatile uint32_t *)(root+4u),*(volatile uint16_t *)root);
 } else {
  result=opencfw_em9305_radio_cancel_30fab8(result);
  result=opencfw_em9305_common_radio_finish_3045c0(result);
 }
 callback=*(volatile uint32_t *)(record+120u);
 if (callback!=0u)
  (void)((uint32_t (*)(uint32_t,uint32_t,uint32_t,uintptr_t))callback)(current,current,0u,callback);
 (void)result;
}
extern uint32_t opencfw_em9305_radio_adjust_31199c(uint32_t);
/* Native31199c..3119a8: incoming R0 discarded; delay-slot byte store. */
uint32_t opencfw_em9305_radio_adjust_31199c(uint32_t unused)
{
 (void)unused;
 *(volatile uint8_t *)(uintptr_t)0x8019c0u=1u;
 return 0x8019c0u;
}
/* Native314a88..314c02: five-register completion state machine. LDB.AB
 * reads root's original byte before advancing eight bytes. */
uint32_t opencfw_em9305_common_channel_callback_314a88(
 uint32_t first,uint32_t second,uint32_t third,uint32_t fourth,uint32_t fifth)
{
 uint32_t current=opencfw_em9305_auxiliary_ready_303f68();
 uintptr_t root=0x8015ccu;
 uint32_t state=*(volatile uint8_t *)(root-8u);
 uint32_t result=current,phase=first,buffer=fifth;
 uintptr_t record,callback;
 uint32_t descriptor[5];
 if (state!=0u && state!=3u) return result;
 record=*(volatile uint32_t *)((uintptr_t)current+44u);
 if (state==0u) {
  if ((first-3u)<2u) goto status_pair;
  if (first==1u) goto callback_zero;
  if (first!=0u) goto finish;
  *(volatile uint32_t *)(record+144u)=fourth;
  *(volatile uint32_t *)(record+140u)=third;
  *(volatile uint8_t *)(record+138u)=(uint8_t)second;
  *(volatile uint8_t *)(root-8u)=3u;
  *(volatile uint8_t *)(record+148u)=1u;
  *(volatile uint8_t *)(record+139u)=(uint8_t)fifth;
  callback=*(volatile uint32_t *)(record+100u);
  buffer=0x8016f8u;
  result=((uint32_t (*)(uint32_t,uint32_t,uint32_t,uintptr_t))callback)(current,buffer,0u,callback);
  phase=result;
  if (result==0u) goto special;
  goto submit;
 }
 if ((first-3u)<2u) {
  callback=*(volatile uint32_t *)(record+100u);
  result=((uint32_t (*)(uint32_t,uint32_t,uint32_t,uintptr_t))callback)(current,0u,first,callback);
  goto status_pair;
 }
 if (first!=0u) {
  callback=*(volatile uint32_t *)(record+100u);
  result=((uint32_t (*)(uint32_t,uint32_t,uint32_t,uintptr_t))callback)(current,0u,first,callback);
  goto callback_zero;
 }
 *(volatile uint8_t *)(record+139u)=(uint8_t)fifth;
 *(volatile uint8_t *)(record+138u)=(uint8_t)second;
 *(volatile uint8_t *)(record+148u)=0u;
 callback=*(volatile uint32_t *)(record+100u);
 buffer=0x8016f8u;
 result=((uint32_t (*)(uint32_t,uint32_t,uint32_t,uintptr_t))callback)(current,buffer,0u,callback);
 phase=result;
 if (result==0u) goto callback_buffer;
submit:
 (void)opencfw_em9305_radio_adjust_31199c(result);
 (void)opencfw_em9305_common_radio_prepare_30fb4c(record);
 *(volatile uint32_t *)(root+8u)=phase+fourth;
 (void)opencfw_em9305_common_radio_bind_30fc10(root);
 (void)opencfw_em9305_memset(descriptor,0u,20u);
 result=opencfw_em9305_radio_record_30fc28((uintptr_t)descriptor);
 if (state==0u) result=opencfw_em9305_radio_cancel_30fab8(result);
 (void)opencfw_em9305_radio_request_30faec(buffer,257u);
callback_buffer:
 callback=*(volatile uint32_t *)(record+104u);
 result=((uint32_t (*)(uint32_t,uint32_t,uintptr_t))callback)(current,buffer,callback);
 if (phase!=0u && result!=0u) return result;
 goto activate;
status_pair:
 callback=*(volatile uint32_t *)(record+104u);
 result=((uint32_t (*)(uint32_t,uint32_t,uintptr_t))callback)(current,0u,callback);
 if (first==4u) goto activate;
 goto finish;
callback_zero:
 callback=*(volatile uint32_t *)(record+104u);
 result=((uint32_t (*)(uint32_t,uint32_t,uintptr_t))callback)(current,0u,callback);
 goto finish;
special:
 result=*(volatile uint8_t *)(record+136u);
 if (result!=0u) {
  callback=*(volatile uint32_t *)(uintptr_t)0x805c08u;
  if (callback==0u) goto activate;
  result=((uint32_t (*)(uintptr_t,uint32_t,uintptr_t))callback)(record,1u,callback);
 } else {
  result=*(volatile uint8_t *)(record+150u);
  if (result==0u) goto callback_buffer;
  callback=*(volatile uint32_t *)(uintptr_t)0x805c0cu;
  if (callback==0u) goto activate;
  result=((uint32_t (*)(uint32_t,uintptr_t,uint32_t,uint32_t,uint32_t))callback)(current,record,buffer,1u,fourth);
 }
 if (result==0u) return result;
activate:
 result=opencfw_em9305_radio_cancel_30fab8(result);
finish:
 return opencfw_em9305_common_radio_finish_3045c0(result);
}
extern uint32_t opencfw_em9305_radio_packet_check_303404(uint32_t,uintptr_t,uint32_t,uintptr_t);
extern uint32_t opencfw_em9305_radio_request_30fcd8(uintptr_t,uint32_t);
/* Native314c04..314d16: pending six-register callback, then count-based
 * packet checks/submission/retry. No extra guards or packet fields added. */
uint32_t opencfw_em9305_common_channel_callback_314c04(
 uint32_t first,uint32_t second,uint32_t third,uint32_t fourth,uint32_t fifth)
{
 uint32_t current=opencfw_em9305_auxiliary_ready_303f68();
 uintptr_t record=*(volatile uint32_t *)((uintptr_t)current+44u);
 uintptr_t callback=*(volatile uint32_t *)(record+144u);
 uint32_t result=current;
 if (callback!=0u && *(volatile uint8_t *)(record+148u)!=0u) {
  result=((uint32_t (*)(uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t))callback)(
   *(volatile uint32_t *)(record+132u),first,second,third,fourth,fifth);
  if (result!=0u) {
   *(volatile uint8_t *)(record+148u)=0u;
   *(volatile uint32_t *)(record+132u)=0u;
  }
  return result;
 }
 uintptr_t root=0x8015c4u;
 uint32_t count=*(volatile uint8_t *)root;
 *(volatile uint8_t *)root=(uint8_t)(count+1u);
 result=count;
 if (count==2u) {
  result=first-3u;
  if (result<2u) {
   callback=*(volatile uint32_t *)(record+128u);
   result=((uint32_t (*)(uint32_t,uint32_t,uintptr_t))callback)(current,0u,callback);
   if (first==4u) goto activate;
   goto retry;
  }
  if (first!=0u) goto finish;
  result=opencfw_em9305_radio_packet_check_303404(*(volatile uint32_t *)(record+108u),record+76u,0u,record+168u);
  if (result==0u) goto activate;
  callback=*(volatile uint32_t *)(record+128u);
  result=((uint32_t (*)(uint32_t,uint32_t,uintptr_t))callback)(current,*(volatile uint32_t *)(record+108u),callback);
  goto activate;
 }
 if (count!=0u) return result;
 if (first==4u) goto activate;
 if (first==3u) goto retry;
 if (first!=0u) goto finish;
 *(volatile uint8_t *)(record+153u)=(uint8_t)fifth;
 *(volatile uint32_t *)(record+160u)=fourth;
 *(volatile uint32_t *)(record+156u)=third;
 *(volatile uint8_t *)(record+152u)=(uint8_t)second;
 uint32_t checked=opencfw_em9305_radio_packet_check_303404(*(volatile uint32_t *)(record+100u),record+76u,0u,record+168u);
 result=current; /* Delay-slot MOV occurs even when check branches. */
 if (checked==0u) goto activate;
 callback=*(volatile uint32_t *)(record+116u);
 result=((uint32_t (*)(uint32_t,uint32_t,uintptr_t))callback)(current,*(volatile uint32_t *)(record+100u),callback);
 uint32_t submitted=result;
 if (submitted!=0u) {
  uint32_t request[2],descriptor[5];
  *(uint16_t *)(void *)request=*(volatile uint8_t *)(record+149u);
  request[1]=*(volatile uint32_t *)(record+104u);
  (void)opencfw_em9305_memcpy(descriptor,opencfw_em9305_radio_template_3343a8,20u);
  (void)opencfw_em9305_radio_record_30fc28((uintptr_t)descriptor);
  result=opencfw_em9305_radio_request_30fcd8((uintptr_t)request,1u);
 }
 callback=*(volatile uint32_t *)(record+120u);
 if (callback!=0u)
  result=((uint32_t (*)(uint32_t,uint32_t,uintptr_t))callback)(current,*(volatile uint32_t *)(record+100u),callback);
 if (submitted==0u) goto activate;
 return result;
activate:
 (void)opencfw_em9305_radio_cancel_30fab8(result);
retry:
 result=opencfw_em9305_channel_retry_314594(current,record);
 if (result==0u) return result;
finish:
 return opencfw_em9305_common_radio_finish_3045c0(result);
}
/* Native314ea4..314f52: count-gated channel recycle/submission. */
uint32_t opencfw_em9305_common_channel_callback_314ea4(
 uint32_t first,uint32_t unused1,uint32_t unused2,uint32_t fourth)
{
 (void)unused1;(void)unused2;
 uint32_t current=opencfw_em9305_auxiliary_ready_303f68();
 uintptr_t root=0x8015c4u;
 uint32_t count=*(volatile uint8_t *)root;
 uintptr_t record=*(volatile uint32_t *)((uintptr_t)current+44u);
 uint32_t result=count+1u;
 *(volatile uint8_t *)root=(uint8_t)result;
 if (count!=1u) return result;
 if (first!=0u) {
  result=opencfw_em9305_common_channel_start_314db8(current,record,first,0u);
  if (result==0u) return result;
  if (first==4u) result=opencfw_em9305_radio_cancel_30fab8(result);
  return opencfw_em9305_common_radio_finish_3045c0(result);
 }
 *(volatile uint32_t *)(record+128u)=fourth;
 uint32_t checked=opencfw_em9305_radio_packet_check_303404(*(volatile uint32_t *)(record+104u),record+76u,0u,record+132u);
 result=checked;
 if (checked!=0u) {
  uintptr_t callback=*(volatile uint32_t *)(record+116u);
  result=((uint32_t (*)(uint32_t,uint32_t,uintptr_t))callback)(current,*(volatile uint32_t *)(record+104u),callback);
  if (result!=0u) {
   uint32_t descriptor[5];
   (void)opencfw_em9305_memset(descriptor,0u,20u);
   (void)opencfw_em9305_radio_record_30fc28((uintptr_t)descriptor);
   *(uint16_t *)(void *)descriptor=*(volatile uint8_t *)(record+125u);
   descriptor[1]=*(volatile uint32_t *)(record+108u);
   result=opencfw_em9305_radio_request_30fcd8((uintptr_t)descriptor,1u);
   checked=0u;
   goto notify;
  }
 }
 result=opencfw_em9305_common_channel_start_314db8(current,record,0u,0u);
 uint32_t recycled=result;
 if (checked==0u) goto done;
 checked=recycled;
notify:
 {
  uintptr_t callback=*(volatile uint32_t *)(record+120u);
  if (callback!=0u)
   result=((uint32_t (*)(uint32_t,uint32_t))callback)(current,*(volatile uint32_t *)(record+104u));
 }
 if (checked==0u) return result;
 goto activate;
done:
 if (recycled==0u) return result;
activate:
 result=opencfw_em9305_radio_cancel_30fab8(result);
 return opencfw_em9305_common_radio_finish_3045c0(result);
}
/* Native315000..315108: extended descriptor completion, count1 only. */
uint32_t opencfw_em9305_common_channel_callback_315000(
 uint32_t first,uint32_t second,uint32_t unused2,uint32_t fourth,uint32_t fifth)
{
 (void)unused2;
 uint32_t current=opencfw_em9305_auxiliary_ready_303f68();
 uintptr_t root=0x8015c4u;
 uint32_t count=*(volatile uint8_t *)root;
 uintptr_t record=*(volatile uint32_t *)((uintptr_t)current+44u);
 uint32_t result=count+1u;
 *(volatile uint8_t *)root=(uint8_t)result;
 if (count!=1u) return result;
 uintptr_t flag=record+260u;
 uintptr_t callback=*(volatile uint32_t *)(record+152u);
 uintptr_t saved_hook=0u;
 result=first-3u;
 if ((first-3u)<2u || first==1u) {
  result=*(volatile uint8_t *)flag;
  if (result!=0u) {
   result=((uint32_t (*)(uint32_t,uint32_t,uintptr_t))callback)(current,0u,callback);
   goto clear_finish;
  }
  uintptr_t hook=*(volatile uint32_t *)(uintptr_t)0x805c1cu;
  if (hook==0u) goto clear_finish;
  saved_hook=hook;
  goto call_hook;
 }
 if (first!=0u) goto clear_finish;
 result=*(volatile uint8_t *)flag;
 *(volatile uint8_t *)(record+227u)=(uint8_t)second;
 *(volatile uint8_t *)(record+177u)=(uint8_t)fifth;
 *(volatile uint32_t *)(record+180u)=fourth;
 if (result!=0u) {
  result=((uint32_t (*)(uint32_t,uint32_t,uintptr_t))callback)(current,*(volatile uint32_t *)(record+208u),callback);
  goto clear_activate;
 }
 uint32_t index=*(volatile uint8_t *)(record+225u);
 result=(uint32_t)(record+index*4u);
 uint32_t entry=*(volatile uint32_t *)(record+208u+index*4u);
 if (entry!=0u) {
  result=((uint32_t (*)(uint32_t,uint32_t,uintptr_t))callback)(current,entry,callback);
  if (result!=0u) {
   uintptr_t hook=*(volatile uint32_t *)(uintptr_t)0x805c20u;
   if (hook!=0u) {
    result=((uint32_t (*)(uint32_t,uintptr_t,uint32_t,uintptr_t))hook)(current,record,0u,hook);
    *(volatile uint8_t *)flag=0u;
    if (result==0u) return result;
    goto status_finish;
   }
   *(volatile uint8_t *)flag=0u;
   return result;
  }
 }
 entry=*(volatile uint32_t *)(record+116u);
 if (entry==0u) goto clear_activate;
 result=((uint32_t (*)(uint32_t,uint32_t,uintptr_t))callback)(current,entry,callback);
 if (result==0u) goto clear_activate;
 uint32_t descriptor[5];
 (void)opencfw_em9305_memset(descriptor,0u,20u);
 (void)opencfw_em9305_radio_record_30fc28((uintptr_t)descriptor);
 result=opencfw_em9305_radio_request_30fcd8(record+120u,2u);
 callback=*(volatile uint32_t *)(record+156u);
 if (callback!=0u)
  result=((uint32_t (*)(uint32_t,uint32_t,uintptr_t))callback)(current,*(volatile uint32_t *)(record+116u),callback);
 *(volatile uint8_t *)flag=0u;
 return result;
call_hook:
 {
  uintptr_t hook=saved_hook;
  result=((uint32_t (*)(uint32_t,uintptr_t,uint32_t,uintptr_t))hook)(current,record,0u,hook);
  *(volatile uint8_t *)flag=0u;
  if (result==0u) return result;
  goto status_finish;
 }
clear_finish:
 *(volatile uint8_t *)flag=0u;
status_finish:
 if ((first|4u)!=4u) return opencfw_em9305_common_radio_finish_3045c0(result);
 goto activate;
clear_activate:
 *(volatile uint8_t *)flag=0u;
activate:
 result=opencfw_em9305_radio_cancel_30fab8(result);
 return opencfw_em9305_common_radio_finish_3045c0(result);
}
/* Native315260..3152bc: required callback112, then pending followup or
 * callback116/finish. Exact template3343e4 extent is20 non-code bytes. */
const uint8_t opencfw_em9305_radio_template_3343e4[20]={1u};
void opencfw_em9305_common_channel_callback_315260(void)
{
 uint32_t current=opencfw_em9305_auxiliary_ready_303f68();
 uintptr_t record=*(volatile uint32_t *)((uintptr_t)current+44u);
 uintptr_t callback=*(volatile uint32_t *)(record+112u);
 uint32_t result=((uint32_t (*)(uint32_t,uint32_t,uintptr_t))callback)(current,current,callback);
 uintptr_t root=0x8015dcu;
 uint32_t pending=*(volatile uint32_t *)(root+4u);
 if (current!=0u) {
  if (pending!=0u) {
   *(volatile uint32_t *)(root+4u)=0u;
   callback=*(volatile uint32_t *)(record+116u);
   result=((uint32_t (*)(uint32_t,uint32_t,uint32_t,uintptr_t))callback)(current,pending,2u,callback);
  }
  (void)opencfw_em9305_common_radio_finish_3045c0(result);
  return;
 }
 if (pending!=0u) {
  uint32_t descriptor[5];
  (void)opencfw_em9305_memcpy(descriptor,opencfw_em9305_radio_template_3343e4,20u);
  (void)opencfw_em9305_radio_record_30fc28((uintptr_t)descriptor);
  (void)opencfw_em9305_radio_followup_30fb3c(*(volatile uint32_t *)(root+4u),*(volatile uint16_t *)root);
  return;
 }
 result=opencfw_em9305_radio_cancel_30fab8(result);
 (void)opencfw_em9305_common_radio_finish_3045c0(result);
}
/* Native333064..3330d8: descriptor flattening. Selector1 returns the
 * first buffer; two-byte header case prepends bytes in reverse store order.
 * Optional tail-copy count is the low byte of the third halfword. */
uintptr_t opencfw_em9305_radio_flatten_333064(uintptr_t descriptor,uint32_t selector)
{
 uintptr_t first=*(volatile uint32_t *)(descriptor+4u);
 if (selector==1u) return first;
 uint32_t length=*(volatile uint16_t *)descriptor;
 if (length==2u) {
  uintptr_t header=*(volatile uint32_t *)(descriptor+12u);
  uint8_t second=*(volatile uint8_t *)(first+1u);
  uint8_t initial=*(volatile uint8_t *)first;
  *(volatile uint8_t *)(header-1u)=second;
  header-=2u;
  *(volatile uint8_t *)header=initial;
  if (selector>=3u) {
   uint32_t body_length=*(volatile uint16_t *)(descriptor+8u);
   uintptr_t tail=*(volatile uint32_t *)(descriptor+12u)+body_length;
   uint32_t tail_length=*(volatile uint16_t *)(descriptor+16u);
   uintptr_t scratch=0x805d28u;
   (void)opencfw_em9305_memcpy((void *)scratch,(const void *)tail,(uint8_t)tail_length);
   uintptr_t source=*(volatile uint32_t *)(descriptor+20u);
   *(volatile uint8_t *)(scratch+8u)=(uint8_t)tail_length;
   *(volatile uint32_t *)(scratch+4u)=(uint32_t)tail;
   (void)opencfw_em9305_memcpy((void *)tail,(const void *)source,(uint8_t)tail_length);
  }
  return header;
 }
 uintptr_t scratch=0x805d3cu;
 (void)opencfw_em9305_memcpy((void *)scratch,(const void *)first,length);
 length=*(volatile uint16_t *)descriptor;
 uintptr_t source=*(volatile uint32_t *)(descriptor+12u);
 uint32_t following=*(volatile uint16_t *)(descriptor+8u);
 (void)opencfw_em9305_memcpy((void *)(scratch+length),(const void *)source,following);
 return scratch;
}
/* Native303df8..303e38: packed address-kind lookup in eight-byte rows.
 * The high kind bit is ORed with the full incoming third word. */
uint32_t opencfw_em9305_radio_address_match_303df8(uint32_t kind,uint32_t low,uint32_t high)
{
 uint32_t count=*(volatile uint8_t *)(uintptr_t)0x80163au;
 if (count==0u) return 0u;
 uintptr_t row=*(volatile uint32_t *)(uintptr_t)0x805c04u;
 uint32_t packed=((kind!=0u)?0x10000u:0u)|high;
 for (uint32_t index=1u;;++index) {
  uint32_t actual_high=*(volatile uint32_t *)(row+4u);
  uint32_t actual_low=*(volatile uint32_t *)row;
  row+=8u;
  uint32_t difference=(actual_high^packed)|(actual_low^low);
  uint32_t equal=(difference==0u);
  if (index>=count || equal!=0u) return equal;
 }
}
/* Native303e38..303e50: clear both bytes, return second address. */
uint32_t opencfw_em9305_radio_address_reset_303e38(void)
{
 *(volatile uint8_t *)(uintptr_t)0x801639u=0u;
 *(volatile uint8_t *)(uintptr_t)0x80163au=0u;
 return 0x80163au;
}
uint32_t opencfw_em9305_radio_address_status_303e50(void)
{ return *(volatile uint8_t *)(uintptr_t)0x80163bu; }
/* Native303e5c..303e68: delayed byte load. */
uint32_t opencfw_em9305_radio_address_mode_303e5c(void)
{ return *(volatile uint8_t *)(uintptr_t)0x801639u; }
/* Native303e68..303ec0: remove matched row by copying the final row;
 * preserves high-word-first load/store order and byte count decrement. */
uint32_t opencfw_em9305_radio_address_remove_303e68(uint32_t kind,uint32_t low,uint32_t high)
{
 volatile uint8_t *count_cell=(volatile uint8_t *)(uintptr_t)0x80163au;
 uint32_t count=*count_cell;
 if (count==0u) return 0u;
 uint32_t packed=((kind!=0u)?0x10000u:0u)|high;
 uintptr_t base=*(volatile uint32_t *)(uintptr_t)0x805c04u;
 uintptr_t row=base;
 for (uint32_t index=0u;index<count;++index,row+=8u) {
  uint32_t actual_high=*(volatile uint32_t *)(row+4u);
  uint32_t actual_low=*(volatile uint32_t *)row;
  if (((actual_high^packed)|(actual_low^low))!=0u) continue;
  if (count>=2u) {
   uintptr_t end=base+count*8u;
   uint32_t last_high=*(volatile uint32_t *)(end-4u);
   uint32_t last_low=*(volatile uint32_t *)(end-8u);
   *(volatile uint32_t *)(row+4u)=last_high;
   *(volatile uint32_t *)row=last_low;
  }
  *count_cell=(uint8_t)(count-1u);
  return 1u;
 }
 return 0u;
}
/* Native303ec0..303ecc: disable mode, return byte address. */
uint32_t opencfw_em9305_radio_address_disable_303ec0(void)
{
 *(volatile uint8_t *)(uintptr_t)0x801639u=0u;
 return 0x801639u;
}
/* Native303ecc..303ef0: clear current object before optional provider
 * callback; index uses24-byte provider rows and callback address in R1. */
uint32_t opencfw_em9305_auxiliary_release_303ecc(void)
{
 uintptr_t root=0x80163cu;
 uint32_t object=*(volatile uint32_t *)root;
 if (object==0u) return object;
 uint32_t index=*(volatile uint8_t *)((uintptr_t)object+26u);
 *(volatile uint32_t *)root=0u;
 uintptr_t callback=*(volatile uint32_t *)(root+index*24u+12u);
 if (callback==0u) return object;
 return ((uint32_t (*)(uint32_t,uintptr_t))callback)(object,callback);
}
extern uint32_t opencfw_em9305_radio_resolve_303bdc(uint32_t,uint32_t,uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_radio_resolve_303890(uint32_t,uint32_t,uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_radio_known_303978(uint32_t,uint32_t);
extern uint32_t opencfw_em9305_radio_kind_303a18(uint32_t,uint32_t,uint32_t);
extern uint32_t opencfw_em9305_radio_identity_303954(uint32_t,uint32_t,uint32_t,uintptr_t);
/* Native314470..314538: descriptor address classification. Optional
 * resolver/identity bodies remain distinct genuine source imports. */
uint32_t opencfw_em9305_radio_classify_314470(uint32_t mode,uint32_t resolve,uintptr_t kind_cell,uintptr_t descriptor)
{
 uint32_t high=*(volatile uint32_t *)(descriptor+4u);
 uint32_t kind=*(volatile uint8_t *)kind_cell;
 uint32_t low=*(volatile uint32_t *)descriptor;
 uint32_t active=(kind!=0u);
 uint32_t random=((high&0xc000u)==0x4000u);
 uint32_t classification=2u;
 if (mode!=0u && (active&random)!=0u) {
  if (resolve==0u)
   return (opencfw_em9305_radio_resolve_303890(low,high,kind_cell,descriptor)!=0u)?2u:0u;
  if (opencfw_em9305_radio_resolve_303bdc(low,high,kind_cell,descriptor)!=0u) return classification;
  return (opencfw_em9305_radio_known_303978(low,high)==0u)+1u;
 }
 if (mode==0u && (active&random)!=0u) return classification;
 uint32_t lookup=opencfw_em9305_radio_kind_303a18(active,low,high)&254u;
 if (lookup!=2u) return classification;
 uint8_t identity;
 high=*(volatile uint32_t *)(descriptor+4u);
 low=*(volatile uint32_t *)descriptor;
 kind=(mode==0u)?lookup:*(volatile uint8_t *)kind_cell;
 uint32_t matched=opencfw_em9305_radio_identity_303954(
  kind,low,high,(uintptr_t)&identity);
 if (mode==0u) matched=*(volatile uint8_t *)kind_cell;
 return (matched==0u)?3u:((identity==0u)+2u);
}
/* Native31441c..31445c:72-byte identity rows, full kind input shifted16
 * (unlike the boolean-normalizing address filter lookup). */
uintptr_t opencfw_em9305_radio_identity_find_31441c(uint32_t kind,uint32_t low,uint32_t high)
{
 uint32_t count=*(volatile uint8_t *)(uintptr_t)0x801610u;
 if (count==0u) return 0u;
 uintptr_t row=*(volatile uint32_t *)(uintptr_t)0x805c00u;
 uint32_t packed=(kind<<16u)|high;
 for (uint32_t index=0u;index<count;++index,row+=72u) {
  uint32_t actual_high=*(volatile uint32_t *)(row+36u);
  uint32_t actual_low=*(volatile uint32_t *)(row+32u);
  if (((actual_high^packed)|(actual_low^low))==0u) return row;
 }
 return 0u;
}
uint32_t opencfw_em9305_radio_identity_exists_31445c(uint32_t kind,uint32_t low,uint32_t high)
{ return opencfw_em9305_radio_identity_find_31441c(kind,low,high)!=0u; }
/* Native303954..30396c writes output only for a matching identity. */
uint32_t opencfw_em9305_radio_identity_303954(uint32_t kind,uint32_t low,uint32_t high,uintptr_t output)
{
 uintptr_t row=opencfw_em9305_radio_identity_find_31441c(kind,low,high);
 if (row!=0u) *(volatile uint8_t *)output=*(volatile uint8_t *)(row+67u);
 return row!=0u;
}
uint32_t opencfw_em9305_radio_identity_status_30396c(void)
{ return *(volatile uint8_t *)(uintptr_t)0x801611u; }
/* Native303978..3039a0: four-row exclusion lookup, returns0 on match. */
uint32_t opencfw_em9305_radio_known_303978(uint32_t low,uint32_t high)
{
 uintptr_t row=0x801618u;
 for (uint32_t index=1u;;++index,row+=8u) {
  uint32_t actual_high=*(volatile uint32_t *)(row+4u);
  uint32_t actual_low=*(volatile uint32_t *)row;
  uint32_t difference=(actual_high^high)|(actual_low^low);
  if (difference==0u || index>=4u) return difference!=0u;
 }
}
/* Native303a18..303a40: identity kind from pair40/44 and flag64. */
uint32_t opencfw_em9305_radio_kind_303a18(uint32_t kind,uint32_t low,uint32_t high)
{
 uintptr_t row=opencfw_em9305_radio_identity_find_31441c(kind,low,high);
 if (row==0u) return 0u;
 uint32_t upper=*(volatile uint32_t *)(row+44u);
 uint32_t lower=*(volatile uint32_t *)(row+40u);
 if ((upper|lower)!=0u) return 3u;
 return (*(volatile uint8_t *)(row+64u)==0u)+1u;
}
/* Native3039f0..303a18: sibling pair48/52 and flag65. */
uint32_t opencfw_em9305_radio_peer_kind_3039f0(uint32_t kind,uint32_t low,uint32_t high)
{
 uintptr_t row=opencfw_em9305_radio_identity_find_31441c(kind,low,high);
 if (row==0u) return 0u;
 uint32_t upper=*(volatile uint32_t *)(row+52u);
 uint32_t lower=*(volatile uint32_t *)(row+48u);
 if ((upper|lower)!=0u) return 3u;
 return (*(volatile uint8_t *)(row+65u)==0u)+1u;
}
/* Native303a40/303a60: copy nonzero identity pairs only on match. */
uint32_t opencfw_em9305_radio_peer_pair_303a40(uint32_t kind,uint32_t low,uint32_t high,uintptr_t output)
{
 uintptr_t row=opencfw_em9305_radio_identity_find_31441c(kind,low,high);
 if (row==0u) return 0u;
 uint32_t upper=*(volatile uint32_t *)(row+52u);
 uint32_t lower=*(volatile uint32_t *)(row+48u);
 if ((upper|lower)==0u) return 0u;
 *(volatile uint32_t *)output=lower;
 *(volatile uint32_t *)(output+4u)=upper;
 return 1u;
}
uint32_t opencfw_em9305_radio_identity_pair_303a60(uint32_t kind,uint32_t low,uint32_t high,uintptr_t output)
{
 uintptr_t row=opencfw_em9305_radio_identity_find_31441c(kind,low,high);
 if (row==0u) return 0u;
 uint32_t upper=*(volatile uint32_t *)(row+44u);
 uint32_t lower=*(volatile uint32_t *)(row+40u);
 if ((upper|lower)==0u) return 0u;
 *(volatile uint32_t *)output=lower;
 *(volatile uint32_t *)(output+4u)=upper;
 return 1u;
}
/* Native3039d0..3039f0: consume byte44 flag once. */
uint32_t opencfw_em9305_radio_identity_consume_3039d0(uint32_t kind,uint32_t low,uint32_t high)
{
 uintptr_t row=opencfw_em9305_radio_identity_find_31441c(kind,low,high);
 if (row==0u) return 0u;
 uint32_t flag=*(volatile uint8_t *)(row+68u);
 *(volatile uint8_t *)(row+68u)=0u;
 return flag!=0u;
}
/* Native3039a0..3039d0: five-register identity comparison, flag65 must
 * be clear. Input pair is compared with row56/60 after lookup. */
uint32_t opencfw_em9305_radio_identity_compare_3039a0(
 uint32_t expected_low,uint32_t expected_high,uint32_t kind,uint32_t low,uint32_t high)
{
 uintptr_t row=opencfw_em9305_radio_identity_find_31441c(kind,low,high);
 if (row==0u) return 0u;
 if (*(volatile uint8_t *)(row+65u)!=0u) return 0u;
 uint32_t upper=*(volatile uint32_t *)(row+60u);
 uint32_t lower=*(volatile uint32_t *)(row+56u);
 return ((upper^expected_high)|(lower^expected_low))==0u;
}
/* Native303c9c..303ca8: delayed store leaves original input in R0. */
uint32_t opencfw_em9305_radio_identity_control_303c9c(uint32_t value)
{
 *(volatile uint32_t *)(uintptr_t)0x80160cu=value;
 return value;
}
/* Native303ca8..303cc0: matching identity byte67 setter. */
uint32_t opencfw_em9305_radio_identity_set_303ca8(uint32_t kind,uint32_t low,uint32_t high,uint32_t value)
{
 uintptr_t row=opencfw_em9305_radio_identity_find_31441c(kind,low,high);
 if (row!=0u) *(volatile uint8_t *)(row+67u)=(uint8_t)value;
 return row!=0u;
}
/* Native303cc0..303cd8: source high-first loads, destination high-first
 * stores for matching peer pair48/52. */
uint32_t opencfw_em9305_radio_peer_set_303cc0(uint32_t kind,uint32_t low,uint32_t high,uintptr_t source)
{
 uintptr_t row=opencfw_em9305_radio_identity_find_31441c(kind,low,high);
 if (row!=0u) {
  uint32_t upper=*(volatile uint32_t *)(source+4u);
  uint32_t lower=*(volatile uint32_t *)source;
  *(volatile uint32_t *)(row+52u)=upper;
  *(volatile uint32_t *)(row+48u)=lower;
 }
 return row!=0u;
}
/* Exact non-executable20-byte template native334420. */
const uint8_t opencfw_em9305_radio_template_334420[20]={1u};
/* Native303cd8..303d18: store pending fields before current-object
 * query, submit only descriptor type5 with zero phase byte. */
uint32_t opencfw_em9305_radio_request_start_303cd8(uint32_t first,uint32_t second)
{
 uintptr_t root=0x8015c4u;
 *(volatile uint16_t *)(root+24u)=(uint16_t)second;
 *(volatile uint32_t *)(root+28u)=first;
 uintptr_t current=opencfw_em9305_auxiliary_ready_303f68();
 uintptr_t record=*(volatile uint32_t *)(current+44u);
 uint32_t result=*(volatile uint8_t *)record;
 if (result!=5u) return result;
 result=*(volatile uint8_t *)root;
 if (result!=0u) return result;
 uint32_t descriptor[5];
 (void)opencfw_em9305_memcpy(descriptor,opencfw_em9305_radio_template_334420,20u);
 (void)opencfw_em9305_radio_record_30fc28((uintptr_t)descriptor);
 return opencfw_em9305_radio_request_30faec(first,second);
}
/* Native303d58..303da4: current object request, record type4 and phase0
 * select30fc68; other states select30fcd8. Incoming R0 is dead. */
uint32_t opencfw_em9305_radio_request_current_303d58(uint32_t unused,uint32_t selector)
{
 (void)unused;
 uintptr_t current=opencfw_em9305_auxiliary_ready_303f68();
 uintptr_t record=*(volatile uint32_t *)(current+44u);
 uint32_t phase=*(volatile uint8_t *)(uintptr_t)0x8015c4u;
 uint32_t type=*(volatile uint8_t *)record;
 uint32_t descriptor[5];
 (void)opencfw_em9305_memcpy(descriptor,opencfw_em9305_radio_template_334420,20u);
 (void)opencfw_em9305_radio_record_30fc28((uintptr_t)descriptor);
 if (type==4u && phase==0u) return opencfw_em9305_radio_record_request_30fc68(current,selector);
 return opencfw_em9305_radio_request_30fcd8(current,selector);
}
/* Native303da4..303dec: deduplicated address insert, count is published
 * before high/low row writes, preserving native behavior. */
uint32_t opencfw_em9305_radio_address_add_303da4(uint32_t kind,uint32_t low,uint32_t high)
{
 if (opencfw_em9305_radio_address_match_303df8(kind,low,high)!=0u) return 1u;
 volatile uint8_t *count_cell=(volatile uint8_t *)(uintptr_t)0x80163au;
 uint32_t count=*count_cell;
 uint32_t limit=*(volatile uint8_t *)(uintptr_t)0x80163bu;
 if (count>=limit) return 0u;
 uintptr_t row=*(volatile uint32_t *)(uintptr_t)0x805c04u+count*8u;
 uint32_t packed=high|((kind!=0u)?0x10000u:0u);
 *count_cell=(uint8_t)(count+1u);
 *(volatile uint32_t *)(row+4u)=packed;
 *(volatile uint32_t *)row=low;
 return 1u;
}
uint32_t opencfw_em9305_radio_address_enable_303dec(void)
{
 *(volatile uint8_t *)(uintptr_t)0x801639u=1u;
 return 0x801639u;
}
extern uint32_t opencfw_em9305_radio_random_bytes_310038(uintptr_t,uint32_t);
extern uint32_t opencfw_em9305_radio_hash24_314640(uintptr_t,uint32_t);
/* Native31467c..3146a4: construct address in R0/R1 from random22+set
 * bit22 and a24-bit hash. Lower hash packing remains a true import. */
uint64_t opencfw_em9305_radio_private_address_31467c(uintptr_t key)
{
 uint32_t random;
 (void)opencfw_em9305_radio_random_bytes_310038((uintptr_t)&random,4u);
 random=(random&0x003fffffu)|0x00400000u;
 uint32_t hashed=opencfw_em9305_radio_hash24_314640(key,random);
 uint32_t low=hashed|(random<<24u);
 uint32_t high=random>>8u;
 return ((uint64_t)high<<32u)|low;
}
extern uint32_t opencfw_em9305_rom_random_10a7f8(uintptr_t,uint32_t,uintptr_t);
/* Native310038..310088: resident random call then reversed chunks of8.
 * Byte-truncated counters, initial do-loop and native fatal trap preserved;
 * caller length is compared full-width, without an invented range guard. */
uint32_t opencfw_em9305_radio_random_bytes_310038(uintptr_t output,uint32_t length)
{
 uint32_t remaining=length,done=0u,result;
 do {
  uint8_t scratch[8];
  uint32_t status=opencfw_em9305_rom_random_10a7f8(0x805e40u,2u,(uintptr_t)scratch);
  if (status!=0u) __asm__ volatile("trap_s 0" ::: "memory");
  uint32_t chunk=(uint8_t)remaining;
  if (chunk>8u) chunk=8u;
  uintptr_t destination=output+(uint8_t)done;
  for (uint32_t index=0u;index<chunk;++index)
   *(volatile uint8_t *)(destination+index)=*(volatile uint8_t *)(scratch+chunk-1u-index);
  done+=chunk;
  result=(uint8_t)done;
  remaining-=chunk;
 } while (result<length);
 return result;
}
extern uint32_t opencfw_em9305_rom_cipher_key_1009c0(uintptr_t,uint32_t);
extern uint32_t opencfw_em9305_rom_cipher_block_10090c(uintptr_t,uintptr_t,uint32_t);
/* Native30ff0c..30ff70: reverse key/input bytes, resident block operation
 * under nested critical region, reverse result. ROM bodies are external.
 * Native incidental R0 is stack-output base minus1, retained as integer. */
uint32_t opencfw_em9305_radio_cipher_30ff0c(uintptr_t key,uintptr_t output,uintptr_t input)
{
 uint8_t scratch[48];
 for (uint32_t index=0u;index<16u;++index)
  *(volatile uint8_t *)(scratch+32u+index)=*(volatile uint8_t *)(key+15u-index);
 for (uint32_t index=0u;index<16u;++index)
  *(volatile uint8_t *)(scratch+16u+index)=*(volatile uint8_t *)(input+15u-index);
 (void)opencfw_em9305_radio_request_enter_310678();
 (void)opencfw_em9305_rom_cipher_key_1009c0((uintptr_t)(scratch+32u),0u);
 (void)opencfw_em9305_rom_cipher_block_10090c((uintptr_t)(scratch+16u),(uintptr_t)scratch,0u);
 (void)opencfw_em9305_radio_request_exit_31069c();
 for (uint32_t index=0u;index<16u;++index)
  *(volatile uint8_t *)(output+index)=*(volatile uint8_t *)(scratch+15u-index);
 return (uint32_t)(uintptr_t)scratch-1u;
}
/* Native3045c0..3045e8: provider completion, then required controller
 * callback after flag130 and current-object clear. Incoming R0 is dead. */
uint32_t opencfw_em9305_common_radio_finish_3045c0(uint32_t unused)
{
 (void)unused;
 uintptr_t root=0x80163cu;
 uintptr_t object=*(volatile uint32_t *)root;
 if (object!=0u) {
  uint32_t index=*(volatile uint8_t *)(object+26u);
  uintptr_t callback=*(volatile uint32_t *)(root+index*24u+24u);
  if (callback!=0u) (void)((uint32_t (*)(uintptr_t))callback)(callback);
 }
 uintptr_t callback=*(volatile uint32_t *)(root+4u);
 *(volatile uint8_t *)(root+130u)=1u;
 *(volatile uint32_t *)root=0u;
 return ((uint32_t (*)(uintptr_t))callback)(callback);
}
/* Native3045e8..304604: six-byte address serialization with exact native
 * store order4,0,5,3,2,1; original destination retained in R0. */
uintptr_t opencfw_em9305_radio_address_write_3045e8(uintptr_t output,uint32_t low,uint32_t high)
{
 *(volatile uint8_t *)(output+4u)=(uint8_t)high;
 *(volatile uint8_t *)output=(uint8_t)low;
 *(volatile uint8_t *)(output+5u)=(uint8_t)(high>>8u);
 *(volatile uint8_t *)(output+3u)=(uint8_t)(low>>24u);
 *(volatile uint8_t *)(output+2u)=(uint8_t)(low>>16u);
 *(volatile uint8_t *)(output+1u)=(uint8_t)(low>>8u);
 return output;
}
uintptr_t opencfw_em9305_radio_address_copy_304604(uintptr_t output,uintptr_t input)
{ return (uintptr_t)opencfw_em9305_memcpy((void *)output,(const void *)input,6u); }
/* Native312360..312390: optional control reset, unconditional RX trigger;
 * return is either zero or native RAM control-word address. */
uint32_t opencfw_em9305_radio_receive_trigger_312360(void)
{
 uint32_t result=*(volatile uint8_t *)(uintptr_t)0x8018dcu;
 if (result!=0u) {
  uintptr_t control=0x8012f8u;
  uint32_t value=*(volatile uint32_t *)control;
  value=(value&0xffffbfc3u)|4u;
  *(volatile uint32_t *)control=value;
  *(volatile uint32_t *)(uintptr_t)0xf0484cu=value;
  result=(uint32_t)control;
 }
 *(volatile uint8_t *)(uintptr_t)0xf04401u=1u;
 return result;
}
/* Native312390..3123d0: optional mode control then TX trigger. */
uint32_t opencfw_em9305_radio_transmit_trigger_312390(void)
{
 uint32_t result=*(volatile uint8_t *)(uintptr_t)0x8018dcu;
 if (result!=0u) {
  result=*(volatile uint32_t *)(uintptr_t)0x8012e0u;
  uint32_t control=*(volatile uint32_t *)(uintptr_t)0x8012f8u;
  result=(result<<2u)&0x3cu;
  control=((control&0xffffbfc3u)|result)|0x4000u;
  *(volatile uint32_t *)(uintptr_t)0x8012f8u=control;
  *(volatile uint32_t *)(uintptr_t)0xf0484cu=control;
 }
 *(volatile uint8_t *)(uintptr_t)0xf04400u=1u;
 return result;
}
/* Native312598..3125a4: indexed MMIO halfword store in return delay slot,
 * returning full computed address. Index is not silently bounded. */
uint32_t opencfw_em9305_radio_register_half_312598(uint32_t index,uint32_t value)
{
 uint32_t address=0xf04800u+(index<<2u);
 *(volatile uint16_t *)(uintptr_t)address=(uint16_t)value;
 return address;
}
/* Native311990..31199c:13-bit timing/control store and masked return. */
uint32_t opencfw_em9305_radio_timing_store_311990(uint32_t value)
{
 value&=0x1fffu;
 *(volatile uint32_t *)(uintptr_t)0xf040b4u=value;
 return value;
}
extern uint32_t opencfw_em9305_radio_timing_pair_31197c(uint32_t,uint32_t);
extern uint32_t opencfw_em9305_radio_channel_convert_311878(uint32_t);
/* Native3120a0..312290: complete mode apply outer body. MMIO ST.AB
 * stores use old addresses; table record strides and signed-halfword timing
 * conversion are retained. Packed-timing/channel lower bodies remain imports. */
uint32_t opencfw_em9305_radio_apply_3120a0(uint32_t first,uint32_t second)
{
 uint32_t encoded=((first<<8u)&0x700u)|(second&7u);
 *(volatile uint32_t *)(uintptr_t)0x805fe0u=3u;
 *(volatile uint32_t *)(uintptr_t)0xf04404u=0u;
 uintptr_t root=0x80fd38u;
 uintptr_t table=*(volatile uint32_t *)(root+20u);
 *(volatile uint32_t *)(uintptr_t)0xf04004u=encoded;
 *(volatile uint32_t *)(uintptr_t)0xf04000u=1u;
 *(volatile uint32_t *)(uintptr_t)0xf0402cu=0x10003u;
 uint32_t selected=*(volatile uint8_t *)(uintptr_t)0x8018ddu;
 if (selected!=0u) selected=*(volatile uint32_t *)(uintptr_t)0x8018e0u;
 else selected=0x80032du;
 *(volatile uint32_t *)(uintptr_t)0xf04030u=selected;
 *(volatile uint32_t *)(uintptr_t)0xf0403cu=2u;
 *(volatile uint32_t *)(uintptr_t)0xf04040u=72u;
 *(volatile uint32_t *)(uintptr_t)0xf04048u=0u;
 *(volatile uint32_t *)(uintptr_t)0xf0404cu=0x100ffu;
 *(volatile uint32_t *)(uintptr_t)0xf04050u=31u;
 *(volatile uint32_t *)(uintptr_t)0xf040acu=0x0300000cu;
 *(volatile uint32_t *)(uintptr_t)0xf040bcu=0u;
 *(volatile uint32_t *)(uintptr_t)0xf04400u=0x10000u;
 *(volatile uint32_t *)(uintptr_t)0xf04404u=0u;
 *(volatile uint32_t *)(uintptr_t)0xf04414u=0x015401c2u;
 *(volatile uint32_t *)(uintptr_t)0xf04418u=0u;
 *(volatile uint8_t *)(uintptr_t)0xf0440du=3u;
 (void)opencfw_em9305_common_calibrate_311ffc(600u,600u);
 if (first<=3u) {
  uintptr_t rows=table+184u+first*16u;
  for (uint32_t index=0u;index<3u;++index,rows+=4u) {
   uint32_t value=*(volatile uint16_t *)(rows+2u);
   uint32_t reg=*(volatile uint8_t *)rows;
   (void)opencfw_em9305_radio_register_half_312598(reg,value);
  }
  if (first<2u) {
   uintptr_t timing=*(volatile uint32_t *)(root+32u);
   uint32_t low_offset=*(volatile uint16_t *)(uintptr_t)0x805efeu;
   uint32_t high_offset=*(volatile uint16_t *)(uintptr_t)0x805efcu;
   uint32_t pair_offset=first*6u;
   uint32_t low=*(volatile uint16_t *)(timing+pair_offset+2u);
   uint32_t high=*(volatile uint16_t *)(timing+pair_offset+4u);
   low=(uint32_t)(int32_t)(int16_t)(low+low_offset);
   high=(uint32_t)(int32_t)(int16_t)(high+high_offset);
   (void)opencfw_em9305_radio_timing_pair_31197c(low,high);
   uint32_t value=*(volatile uint16_t *)(timing+pair_offset);
   uint32_t offset=*(volatile uint16_t *)(uintptr_t)0x805fdcu;
   (void)opencfw_em9305_radio_timing_store_311990((uint32_t)(int32_t)(int16_t)(offset+value));
  }
 }
 if (second<=3u) {
  uint32_t value=*(volatile uint16_t *)(table+198u+second*16u);
  uint32_t reg=*(volatile uint8_t *)(table+196u+second*16u);
  (void)opencfw_em9305_radio_register_half_312598(reg,value);
  if (second<2u) *(volatile uint8_t *)(uintptr_t)0xf04009u=(uint8_t)second;
  else *(volatile uint32_t *)(uintptr_t)0xf04008u=0x93cu;
 }
 uintptr_t flag=0x8019c0u;
 if (*(volatile uint8_t *)flag!=0u) {
  *(volatile uint8_t *)flag=0u;
  return (uint32_t)flag;
 }
 uintptr_t descriptor=*(volatile uint32_t *)(root+12u);
 uint32_t channel=*(volatile uint8_t *)descriptor;
 uint32_t result=opencfw_em9305_radio_channel_convert_311878(channel);
 descriptor=*(volatile uint32_t *)(root+12u);
 *(volatile uint8_t *)(descriptor+1u)=(uint8_t)result;
 return result;
}
extern uint32_t opencfw_em9305_radio_channel_prepare_3124e4(uint32_t);
/* Native311878..311958: channel conversion and register drive strength.
 * Revision table is already source-owned as68 three-byte records. */
uint32_t opencfw_em9305_radio_channel_convert_311878(uint32_t channel)
{
 uint32_t level=opencfw_em9305_controller_numeric_level((int32_t)channel);
 level=opencfw_em9305_controller_select_level(level);
 level=opencfw_em9305_packet_default_30f65c(level);
 uint32_t index=opencfw_em9305_radio_mode_index_311a20(channel,level);
 uintptr_t descriptor=*(volatile uint32_t *)(uintptr_t)0x80fd44u;
 *(volatile uint8_t *)(descriptor+4u)=(uint8_t)index;
 (void)opencfw_em9305_radio_channel_prepare_3124e4(index);
 uint32_t control=*(volatile uint32_t *)(uintptr_t)0xf0484cu;
 uint32_t second=opencfw_em9305_revision_table[index*3u+1u];
 control&=0xffffb003u;
 uint32_t enabled=*(volatile uint8_t *)(uintptr_t)0x8018dcu;
 uint32_t third=opencfw_em9305_revision_table[index*3u+2u];
 uint32_t mode=(second<<2u)&0x3cu;
 control=(mode|control)+((third&63u)<<6u);
 *(volatile uint32_t *)(uintptr_t)0x8012f8u=control;
 if (enabled!=0u) {
  control|=0x4000u;
  *(volatile uint32_t *)(uintptr_t)0x8012f8u=control;
 }
 *(volatile uint32_t *)(uintptr_t)0xf0484cu=control;
 uint32_t drive=*(volatile uint32_t *)(uintptr_t)0xf04b88u;
 uint32_t result=(uint32_t)(int32_t)(int8_t)opencfw_em9305_revision_table[index*3u];
 uint32_t bits=drive&120u;
 if ((int32_t)result<7) {
  if (bits!=0x30u) *(volatile uint32_t *)(uintptr_t)0xf04b88u=(drive&0xffffff87u)|0x30u;
  drive=*(volatile uint32_t *)(uintptr_t)0xf04a98u;
  if ((drive&0x30u)!=0x30u) *(volatile uint32_t *)(uintptr_t)0xf04a98u=drive|0x30u;
 } else {
  if (bits!=120u) *(volatile uint32_t *)(uintptr_t)0xf04b88u=drive|120u;
  drive=*(volatile uint32_t *)(uintptr_t)0xf04a98u;
  bits=drive&0x30u;
  if (result<9u) {
   if (bits!=0x10u) *(volatile uint32_t *)(uintptr_t)0xf04a98u=(drive&~0x30u)|0x10u;
  } else if (bits!=0u) *(volatile uint32_t *)(uintptr_t)0xf04a98u=drive&~0x30u;
 }
 return result;
}
/* Native3124e4..31252c: table threshold chooses mode flag, clear bit14
 * only when leaving enabled mode, then publish signed table byte1. */
uint32_t opencfw_em9305_radio_channel_prepare_3124e4(uint32_t index)
{
 uint32_t offset=index*3u;
 int32_t level=(int8_t)opencfw_em9305_revision_table[offset];
 uint32_t enabled=1u;
 if (level<7) {
  uint32_t prior=*(volatile uint8_t *)(uintptr_t)0x8018dcu;
  enabled=0u;
  if (prior!=0u) {
   uint32_t control=*(volatile uint32_t *)(uintptr_t)0x8012f8u;
   control&=~0x4000u;
   *(volatile uint32_t *)(uintptr_t)0x8012f8u=control;
   *(volatile uint32_t *)(uintptr_t)0xf0484cu=control;
  }
 }
 uint32_t value=(uint32_t)(int32_t)(int8_t)opencfw_em9305_revision_table[offset+1u];
 *(volatile uint8_t *)(uintptr_t)0x8018dcu=(uint8_t)enabled;
 *(volatile uint32_t *)(uintptr_t)0x8012e0u=value;
 return value;
}
/* Native31252c..312598: gated control refresh. Read status twice when
 * gate qualifies, and retain native R0 on each early/late path. */
uint32_t opencfw_em9305_radio_control_refresh_31252c(uint32_t selector)
{
 if (*(volatile uint8_t *)(uintptr_t)0x8018dcu==0u) return selector;
 uint32_t status=*(volatile uint32_t *)(uintptr_t)0xf0440cu;
 uint32_t gate=(selector!=0u)?2u:1u;
 if ((status&gate)==0u) return selector;
 status=*(volatile uint32_t *)(uintptr_t)0xf0440cu;
 uint32_t result=*(volatile uint32_t *)(uintptr_t)0x8012f8u;
 uint32_t control=result&0xffffbfc3u;
 uint32_t use_mode=(selector!=0u)?((status&512u)==0u):((status&256u)!=0u);
 if (use_mode!=0u) {
  result=*(volatile uint32_t *)(uintptr_t)0x8012e0u;
  result=(result<<2u)&0x3cu;
  control=(control|result)|0x4000u;
 } else control|=4u;
 *(volatile uint32_t *)(uintptr_t)0x8012f8u=control;
 *(volatile uint32_t *)(uintptr_t)0xf0484cu=control;
 return result;
}
/* Native31197c..311990: preserve the named architectural instruction
 * directly, matching the selected calibration provider's inline-ARC method. */
uint32_t opencfw_em9305_radio_timing_pair_31197c(uint32_t low,uint32_t high)
{
 low&=0x1fffu;high&=0x1fffu;
 uint32_t packed;
 __asm__ volatile("vpack2hl %0,%1,%2" : "=r"(packed) : "r"(high),"r"(low));
 *(volatile uint32_t *)(uintptr_t)0xf040b0u=packed;
 return packed;
}
/* Native314640..31467c: three-byte challenge and13-byte zero tail,
 * in-place cipher, then native VPACK2HL of byte2 and first halfword. */
uint32_t opencfw_em9305_radio_hash24_314640(uintptr_t key,uint32_t challenge)
{
 _Alignas(4) uint8_t block[16];
 (void)opencfw_em9305_memset(block+3u,0u,13u);
 *(volatile uint8_t *)block=(uint8_t)challenge;
 *(volatile uint8_t *)(block+2u)=(uint8_t)(challenge>>16u);
 *(volatile uint8_t *)(block+1u)=(uint8_t)(challenge>>8u);
 (void)opencfw_em9305_radio_cipher_30ff0c(key,(uintptr_t)block,(uintptr_t)block);
 uint32_t half=*(volatile uint16_t *)(void *)block;
 uint32_t byte=*(volatile uint8_t *)(block+2u);
 uint32_t packed;
 __asm__ volatile("vpack2hl %0,%1,%2" : "=r"(packed) : "r"(byte),"r"(half));
 return packed;
}
/* Native31404c..314068: task queue enqueue followed by event bit1. */
uint32_t opencfw_em9305_wsf_task_message_send(uint32_t handler,uintptr_t message)
{
 uintptr_t queue=opencfw_em9305_wsf_task_handlers();
 (void)opencfw_em9305_ll_event_enqueue(queue,handler,message);
 return opencfw_em9305_wsf_task_event_post(handler,1u);
}
/* Native30cb7c..30cba0: incoming R0 is dead; allocate four-byte command. */
uint32_t opencfw_em9305_ll_special_mode_initialize(uint32_t incoming)
{
 (void)incoming;
 uintptr_t event=opencfw_em9305_wsf_event_allocate(4u);
 if (event==0u) return 0u;
 *(volatile uint16_t *)(event+2u)=0xffu;
 uint32_t handler=*(volatile uint8_t *)(uintptr_t)0x805b18u;
 *(volatile uint16_t *)event=0xffu;
 return opencfw_em9305_wsf_task_message_send(handler,event);
}
extern uint32_t opencfw_em9305_ll_event_decode_32dae4(uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_ll_event_mode_32d4b0(uintptr_t);
extern uint32_t opencfw_em9305_ll_event_process_32d380(uintptr_t,uint32_t,uintptr_t,uintptr_t);
/* Native32dae4..32db0c: four-byte header decode, sparse output stores. */
uint32_t opencfw_em9305_ll_event_decode_32dae4(uintptr_t output,uintptr_t input)
{
 uint32_t upper=*(volatile uint8_t *)(input+1u);
 uint32_t lower=*(volatile uint8_t *)input;
 uint32_t word=(upper<<8u)+lower;
 uint32_t kind;
 __asm__ volatile("xbfu %0,%1,0x2c" : "=r"(kind) : "r"(word));
 *(volatile uint16_t *)output=(uint16_t)(word&0xfffu);
 *(volatile uint8_t *)(output+2u)=(uint8_t)kind;
 upper=*(volatile uint8_t *)(input+3u);
 lower=*(volatile uint8_t *)(input+2u);
 *(volatile uint16_t *)(output+4u)=(uint16_t)((upper<<8u)+lower);
 return 4u;
}
/* Native32d4b0..32d524: packet capacity cap with native unsigned arithmetic. */
uint32_t opencfw_em9305_ll_event_mode_32d4b0(uintptr_t record)
{
 uint32_t flags=*(volatile uint8_t *)(record+597u);
 uint32_t mode=*(volatile uint8_t *)(record+76u);
 uint32_t extended=0u;
 if(flags!=0u && (mode==1u || mode==2u)) {
  mode=(mode==1u || (flags&1u)!=0u)?1u:2u;
  extended=(flags&4u)!=0u;
 }
 uint32_t length=*(volatile uint16_t *)(record+580u);
 uint32_t derived=0u;
 if(extended!=0u || mode==3u) {
  if(length>=976u) derived=((length+0x3ffd30u)>>6u)-4u;
 } else if(mode==2u) {
  if(length>=60u) derived=((length+0x3ffd4u)>>2u)-4u;
 } else {
  if(length>=112u) derived=((length+0x7ffb0u)>>3u)-4u;
 }
 uint32_t limit=(uint16_t)derived;
 if(limit<27u) limit=27u;
 uint32_t configured=*(volatile uint16_t *)(record+578u);
 return configured<limit?configured:limit;
}
/* Native30a484..30a564: decoded queued-event ownership and per-link routing.
 * The decoded MPYUW instructions multiply an unsigned link index by912. */
uint32_t opencfw_em9305_ll_queued_event_active(uintptr_t message)
{
 _Alignas(4) uint8_t decoded[8];
 (void)opencfw_em9305_ll_event_decode_32dae4((uintptr_t)decoded,message);
 uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
 uint32_t link=*(volatile uint16_t *)(void *)decoded;
 if(link<*(volatile uint8_t *)(config+34u)) {
  uintptr_t base=*(volatile uint32_t *)(uintptr_t)0x805c70u;
  uintptr_t record=base+link*912u;
  if(*(volatile uint8_t *)record==0u)
   return opencfw_em9305_wsf_event_release(message);
  if(*(volatile uint8_t *)(record+1u)!=3u) {
   uint32_t kind=*(volatile uint8_t *)(decoded+2u);
   if(*(volatile uint32_t *)(uintptr_t)0x805cd8u!=0u || kind!=3u) {
    uint32_t length=*(volatile uint16_t *)(void *)(decoded+4u);
    if((kind==3u || length!=0u) &&
       *(volatile uint16_t *)(config+38u)>=length) {
     (void)opencfw_em9305_wsf_critical_enter();
     uint32_t count=*(volatile uint8_t *)(uintptr_t)0x805ab4u;
     *(volatile uint8_t *)(uintptr_t)0x805ab4u=(uint8_t)(count-1u);
     (void)opencfw_em9305_wsf_critical_exit();
     if(*(volatile uint8_t *)(record+404u)!=0u)
      return opencfw_em9305_ll_event_enqueue(record+352u,
        *(volatile uint8_t *)decoded,message);
     uint32_t mode=opencfw_em9305_ll_event_mode_32d4b0(record);
     (void)opencfw_em9305_ll_event_process_32d380(record,mode,
                                               (uintptr_t)decoded,message);
     uint32_t handler=*(volatile uint8_t *)(uintptr_t)0x805b18u;
     return opencfw_em9305_wsf_event_post(handler,4u);
    }
    if(kind==0u && length==0u)
     *(volatile uint8_t *)(record+381u)=1u;
   }
  }
 }
 (void)opencfw_em9305_wsf_event_release(message);
 uintptr_t callback=*(volatile uint32_t *)(uintptr_t)0x805b10u;
 return ((uint32_t (*)(uint32_t,uint32_t))callback)(
   *(volatile uint16_t *)(void *)decoded,1u);
}
extern uintptr_t opencfw_em9305_ll_segment_header_323d70(uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_ll_segment_notify_3181b4(uintptr_t);
extern uint32_t opencfw_em9305_ll_schedule_notify_313354(uintptr_t);
/* Native333804..33382c: remove a non-head scheduler object, no null guards. */
uintptr_t opencfw_em9305_auxiliary_unlink_333804(uintptr_t object)
{
 uintptr_t root=0x805f04u;
 uintptr_t tail=*(volatile uint32_t *)(root+20u);
 uintptr_t previous=*(volatile uint32_t *)object;
 if(tail!=object) {
  uintptr_t next=*(volatile uint32_t *)(object+4u);
  *(volatile uint32_t *)(previous+4u)=(uint32_t)next;
  next=*(volatile uint32_t *)(object+4u);
  *(volatile uint32_t *)next=(uint32_t)previous;
  return next;
 }
 *(volatile uint32_t *)(root+20u)=(uint32_t)previous;
 if(previous!=0u) *(volatile uint32_t *)(previous+4u)=0u;
 else *(volatile uint32_t *)(root+16u)=0u;
 return object;
}
/* Native313354..3133a0: cancel listed scheduler object, then optional callback. */
uint32_t opencfw_em9305_ll_schedule_notify_313354(uintptr_t object)
{
 uintptr_t root=0x805f04u;
 uintptr_t cursor=root+16u;
 for(;;) {
  uintptr_t entry=*(volatile uint32_t *)cursor;
  if(entry==0u) return 0u;
  cursor=entry+4u;
  if(entry==object) break;
 }
 uintptr_t head=*(volatile uint32_t *)(root+16u);
 uint32_t result=(uint32_t)object;
 if(head!=object) result=(uint32_t)opencfw_em9305_auxiliary_unlink_333804(object);
 else {
  uint32_t state=*(volatile uint8_t *)root;
  if(state==1u) return opencfw_em9305_auxiliary_expire_3339cc();
  if(state==2u) return opencfw_em9305_auxiliary_signal_304394();
  result=opencfw_em9305_auxiliary_stop_333780();
 }
 uintptr_t callback=*(volatile uint32_t *)(object+32u);
 if(callback!=0u) return ((uint32_t (*)(uintptr_t,uintptr_t))callback)(object,callback);
 return result;
}
extern uint32_t opencfw_em9305_ll_received_decode_31bc7c(uintptr_t,uintptr_t);
extern uintptr_t opencfw_em9305_ll_received_resize_3048b0(uintptr_t,uintptr_t);
/* Native304a98..304ac4: release retained fragments, then clear count. */
uint32_t opencfw_em9305_ll_fragment_clear_304a98(void)
{
 uintptr_t cell=0x8019f0u,row=0x8019e8u;
 uint32_t count=*(volatile uint8_t *)cell;
 if(count!=0u) {
  uint32_t done=0u;
  do {
   (void)opencfw_em9305_wsf_event_release(*(volatile uint32_t *)row);
   count=*(volatile uint8_t *)cell;++done;
   *(volatile uint32_t *)row=0u;row+=4u;
   if(done>=count) break;
  } while(1);
 }
 *(volatile uint8_t *)cell=0u;
 return count;
}
/* Native3048b0..304994: retained-fragment assembly and original ownership. */
uintptr_t opencfw_em9305_ll_received_resize_3048b0(uintptr_t message,uintptr_t decoded)
{
 uint32_t count=*(volatile uint8_t *)(uintptr_t)0x8019f0u;
 uint32_t kind=*(volatile uint8_t *)(decoded+2u);
 if(kind!=3u) {
  if((count==0u && kind<2u) || (count!=0u && kind==1u && count<2u)) {
   *(volatile uint8_t *)(uintptr_t)0x8019f0u=(uint8_t)(count+1u);
   *(volatile uint32_t *)(uintptr_t)(0x8019e8u+count*4u)=(uint32_t)message;
   return 0u;
  }
  (void)opencfw_em9305_wsf_event_release(message);
  (void)opencfw_em9305_ll_fragment_clear_304a98();
  return 0u;
 }
 _Alignas(4) uint8_t first[24],second[24];
 uint32_t total=*(volatile uint16_t *)(decoded+4u)+4u;
 uintptr_t row=0x8019e8u;
 if(count!=0u) {
  uint32_t done=0u;
  do {
   uintptr_t fragment=*(volatile uint32_t *)row;row+=4u;
   (void)opencfw_em9305_ll_received_decode_31bc7c((uintptr_t)first,fragment);
   count=*(volatile uint8_t *)(uintptr_t)0x8019f0u;
   uint32_t bytes=*(volatile uint16_t *)(void *)(first+4u);
   ++done;total+=bytes;
   if(done>=count) break;
  } while(1);
 }
 uintptr_t output=opencfw_em9305_wsf_event_allocate((uint16_t)total);
 if(output==0u) {
  (void)opencfw_em9305_wsf_event_release(message);
  (void)opencfw_em9305_ll_fragment_clear_304a98();
  return 0u;
 }
 uintptr_t fragment=*(volatile uint32_t *)(uintptr_t)0x8019e8u;
 (void)opencfw_em9305_ll_received_decode_31bc7c((uintptr_t)first,fragment);
 uint32_t offset=*(volatile uint16_t *)(void *)(first+4u)+4u;
 fragment=*(volatile uint32_t *)(uintptr_t)0x8019e8u;
 (void)opencfw_em9305_memcpy((void *)output,(const void *)fragment,offset);
 count=*(volatile uint8_t *)(uintptr_t)0x8019f0u;
 offset=*(volatile uint16_t *)(void *)(first+4u)+4u;
 if(count>=2u) {
  fragment=*(volatile uint32_t *)(uintptr_t)0x8019ecu;
  (void)opencfw_em9305_ll_received_decode_31bc7c((uintptr_t)second,fragment);
  fragment=*(volatile uint32_t *)(uintptr_t)0x8019ecu;
  uint32_t bytes=*(volatile uint16_t *)(void *)(second+4u);
  (void)opencfw_em9305_memcpy((void *)(output+(uint16_t)offset),
                           (const void *)(fragment+4u),bytes);
  offset+=*(volatile uint16_t *)(void *)(second+4u);
 }
 (void)opencfw_em9305_memcpy((void *)(output+(uint16_t)offset),
  (const void *)(message+4u),*(volatile uint16_t *)(decoded+4u));
 (void)opencfw_em9305_wsf_event_release(message);
 (void)opencfw_em9305_ll_fragment_clear_304a98();
 return output;
}
/* Native316e5c..316e74: receive packet pool queue, skip eight-byte header. */
uintptr_t opencfw_em9305_ll_stream_packet_take_316e5c(void)
{
 uintptr_t node=opencfw_em9305_wsf_queue_remove(0x8028c8u);
 return node!=0u?node+8u:0u;
}
/* Native3175d0..3175f0: two-byte stream header, native sparse fields. */
uint32_t opencfw_em9305_ll_stream_header_3175d0(uintptr_t output,uintptr_t fields)
{
 uint32_t length=*(volatile uint8_t *)(fields+3u);
 uint32_t mode=*(volatile uint8_t *)(fields+1u);
 uint32_t flag=*(volatile uint8_t *)(fields+2u);
 uint32_t kind=*(volatile uint8_t *)fields;
 *(volatile uint8_t *)(output+1u)=(uint8_t)length;
 *(volatile uint8_t *)output=(uint8_t)(kind|((mode<<2u)&28u)|(flag<<5u));
 return 2u;
}
/* Native316f50..316f70: stack field construction for stream header. */
uint32_t opencfw_em9305_ll_stream_segment_header_316f50(uintptr_t output,uint32_t length,uint32_t kind)
{
 uint8_t fields[4];
 *(volatile uint8_t *)(fields+3u)=(uint8_t)length;
 *(volatile uint8_t *)(fields+2u)=0u;
 *(volatile uint8_t *)(fields+1u)=0u;
 *(volatile uint8_t *)fields=(uint8_t)kind;
 return opencfw_em9305_ll_stream_header_3175d0(output,(uintptr_t)fields);
}
/* Native3175f0..31761c: gated receive buffer with ten-byte private prefix. */
uintptr_t opencfw_em9305_ll_receive_buffer_allocate_3175f0(void)
{
 if(*(volatile uint8_t *)(uintptr_t)0x805addu==0u) return 0u;
 uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
 uint32_t capacity=*(volatile uint16_t *)(config+44u);
 uintptr_t allocation=opencfw_em9305_wsf_event_allocate((uint16_t)(capacity+12u));
 return allocation!=0u?allocation+10u:0u;
}
/* Native31761c..317624: restore private prefix before releasing. */
uint32_t opencfw_em9305_ll_receive_buffer_release_31761c(uintptr_t payload)
{ return opencfw_em9305_wsf_event_release(payload-10u); }
/* Native318708..318740: two-byte link segment header. */
uint32_t opencfw_em9305_ll_link_segment_header_318708(uintptr_t output,uintptr_t fields)
{
 uint32_t four=*(volatile uint8_t *)(fields+4u);
 uint32_t one=*(volatile uint8_t *)(fields+1u);
 uint32_t two=*(volatile uint8_t *)(fields+2u);
 uint32_t three=*(volatile uint8_t *)(fields+3u);
 uint32_t zero=*(volatile uint8_t *)fields;
 uint32_t five=*(volatile uint8_t *)(fields+5u);
 *(volatile uint8_t *)output=(uint8_t)(zero|((one<<2u)&4u)|
   ((two<<3u)&8u)|((three<<4u)&16u)|((four<<6u)&64u));
 *(volatile uint8_t *)(output+1u)=(uint8_t)five;
 return 2u;
}
/* Native318740..318878: received link segmentation, one initial iteration. */
extern uint32_t opencfw_em9305_ll_segment_error_32322c(uint32_t);
uint32_t opencfw_em9305_ll_link_process_318740(uintptr_t record,uintptr_t decoded,uintptr_t message)
{
 uint32_t capacity=*(volatile uint16_t *)(record+448u);
 uint32_t total=*(volatile uint16_t *)(decoded+14u);
 uintptr_t packet=opencfw_em9305_ll_stream_packet_take_316e5c();
 if(packet==0u) {
  (void)opencfw_em9305_wsf_event_release(message);
  uintptr_t callback=*(volatile uint32_t *)(uintptr_t)0x805b38u;
  if(callback!=0u && *(volatile uint8_t *)(record+548u)==0u) {
   _Alignas(2) uint16_t id=(uint16_t)*(volatile uint16_t *)decoded;
   _Alignas(2) uint16_t reason=1u;
   (void)((uint32_t (*)(uint32_t,uintptr_t,uintptr_t,uintptr_t))callback)(
     1u,(uintptr_t)&id,(uintptr_t)&reason,callback);
  }
  (void)opencfw_em9305_wsf_critical_enter();
  uint32_t count=*(volatile uint8_t *)(uintptr_t)0x805adcu;
  *(volatile uint8_t *)(uintptr_t)0x805adcu=(uint8_t)(count+1u);
  (void)opencfw_em9305_wsf_critical_exit();
  return opencfw_em9305_ll_segment_error_32322c(7u);
 }
 uint32_t length=*(volatile uint16_t *)(decoded+14u);
 uint32_t limit=capacity<length?capacity:length;
 *(volatile uint8_t *)(packet+11u)=0u;
 *(volatile uint8_t *)(packet+10u)=(uint8_t)limit;
 uint32_t extra=*(volatile uint8_t *)(decoded+3u);
 *(volatile uint16_t *)(packet+8u)=(uint16_t)length;
 uintptr_t payload=message+8u+(extra!=0u?4u:0u);
 *(volatile uint32_t *)packet=(uint32_t)message;
 *(volatile uint32_t *)(packet+4u)=(uint32_t)payload;
 uint32_t done=0u,index=0u;
 do {
  uint32_t active=*(volatile uint8_t *)(record+484u);
  uint32_t remaining=(uint16_t)(total-done);
  uint32_t chunk=remaining<limit?remaining:limit;
  uintptr_t segment=packet+(uint8_t)index*13u;
  uint8_t fields[6];
  fields[0]=(uint8_t)(active!=0u?2u:(limit<remaining));
  *(volatile uint8_t *)(fields+4u)=0u;
  *(volatile uint8_t *)(fields+3u)=0u;
  *(volatile uint8_t *)(fields+2u)=0u;
  *(volatile uint8_t *)(fields+1u)=0u;
  *(volatile uint16_t *)(decoded+14u)=(uint16_t)chunk;
  *(volatile uint8_t *)(fields+5u)=(uint8_t)chunk;
  uint32_t header=opencfw_em9305_ll_link_segment_header_318708(segment+22u,(uintptr_t)fields);
  uintptr_t callback=*(volatile uint32_t *)(uintptr_t)0x8051e0u;
  *(volatile uint8_t *)(segment+20u)=2u;
  uint32_t result=0u;
  if(callback!=0u) result=((uint32_t (*)(uintptr_t,uint32_t,uintptr_t,uintptr_t))callback)(
    record+112u,header,payload,segment+29u);
  *(volatile uint8_t *)(segment+21u)=(uint8_t)(result!=0u?4u:0u);
  payload+=chunk;done+=chunk;++index;
  if((uint16_t)done>=total) break;
 } while(1);
 return opencfw_em9305_ll_event_enqueue(record+396u,
   *(volatile uint8_t *)decoded,packet);
}
/* Native32fc88..32fc8c: actual zero-return hook, not an invented stub. */
uint32_t opencfw_em9305_dispatch_32fc88(void) { return 0u; }
extern uintptr_t opencfw_em9305_ll_link_pending_30858c(void);
/* Native31ba54..31ba78: consume pending state0/1 queue after four-byte prefix. */
uintptr_t opencfw_em9305_ll_pending_packet_take_31ba54(uintptr_t state)
{
 uint32_t value=*(volatile uint8_t *)state;
 if(value!=0u && value!=1u) return 0u;
 volatile uint8_t handler;
 return opencfw_em9305_wsf_event_remove(state+4u,(uintptr_t)&handler);
}
extern uint32_t opencfw_em9305_ll_link_restart_308614(uint32_t);
extern uint32_t opencfw_em9305_ll_link_dispatch_331d94(uintptr_t);
/* Native331d94..331dc0: optional packet accounting, release and restart. */
uint32_t opencfw_em9305_ll_link_dispatch_331d94(uintptr_t message)
{
 uint32_t enabled=*(volatile uint8_t *)(uintptr_t)0x80583cu;
 if(enabled!=0u) {
  uint32_t bytes=*(volatile uint8_t *)(message+2u);
  uint32_t packets=*(volatile uint32_t *)(uintptr_t)0x805840u;
  uint32_t total=*(volatile uint32_t *)(uintptr_t)0x805844u;
  *(volatile uint32_t *)(uintptr_t)0x805840u=packets+1u;
  *(volatile uint32_t *)(uintptr_t)0x805844u=total+bytes;
  (void)opencfw_em9305_wsf_event_release(message);
  (void)opencfw_em9305_ll_link_restart_308614(1u);
 }
 return enabled!=0u;
}
/* Native308614..308630: protected byte counter increment, exit R0 return. */
uint32_t opencfw_em9305_ll_link_restart_308614(uint32_t increment)
{
 (void)opencfw_em9305_wsf_critical_enter();
 uint32_t count=*(volatile uint8_t *)(uintptr_t)0x805addu;
 *(volatile uint8_t *)(uintptr_t)0x805addu=(uint8_t)(count+increment);
 return opencfw_em9305_wsf_critical_exit();
}
/* Native32fc8c..32fccc: pending-link release/restart, dispatch or event kick. */
uint32_t opencfw_em9305_dispatch_32fc8c(void)
{
 if(*(volatile uint8_t *)(uintptr_t)0x805854u!=0u) {
  uintptr_t pending=opencfw_em9305_ll_link_pending_30858c();
  if(pending!=0u) {
   (void)opencfw_em9305_wsf_event_release(pending);
   return opencfw_em9305_ll_link_restart_308614(1u);
  }
 }
 if(*(volatile uint8_t *)(uintptr_t)0x80583cu!=0u) {
  uintptr_t pending=opencfw_em9305_ll_link_pending_30858c();
  if(pending!=0u) return opencfw_em9305_ll_link_dispatch_331d94(pending);
 }
 return opencfw_em9305_ll_event_kick(0u);
}
extern uintptr_t opencfw_em9305_ll_primary_pending_30853c(void);
extern uint32_t opencfw_em9305_ll_primary_send_32f794(uint32_t,uint32_t,uint32_t);
/* Native32f794..32f7f8: fixed259-byte generated packet burst and busy flag. */
uint32_t opencfw_em9305_ll_primary_send_32f794(uint32_t id,uint32_t length,uint32_t count)
{
 if(*(volatile uint8_t *)(uintptr_t)0x80570cu!=0u) return id;
 *(volatile uint8_t *)(uintptr_t)0x80570cu=1u;
 uint32_t result=id;
 if(count!=0u) {
  uint32_t remaining=(uint8_t)(count-1u)+1u;
  uint32_t upper;
  __asm__ volatile("xbfu %0,%1,104" : "=r"(upper) : "r"(id));
  do {
   uintptr_t packet=opencfw_em9305_wsf_event_allocate(259u);
   result=(uint32_t)packet;
   if(packet==0u) break;
   *(volatile uint8_t *)(packet+3u)=(uint8_t)(length>>8u);
   *(volatile uint8_t *)(packet+2u)=(uint8_t)length;
   *(volatile uint8_t *)(packet+1u)=(uint8_t)upper;
   *(volatile uint8_t *)packet=(uint8_t)id;
   uint32_t value=*(volatile uint8_t *)(uintptr_t)0x80570du;
   *(volatile uint8_t *)(uintptr_t)0x80570du=(uint8_t)(value+1u);
   (void)opencfw_em9305_memset((void *)(packet+4u),value,length);
   result=opencfw_em9305_ll_queued_event(packet);
   --remaining;
   if(remaining==0u) break;
  } while(1);
 }
 *(volatile uint8_t *)(uintptr_t)0x80570cu=0u;
 return result;
}
/* Native32f7f8..32f85c: fixed259-byte generated packet burst and busy flag. */
uint32_t opencfw_em9305_ll_link_send_32f7f8(uint32_t id,uint32_t length,uint32_t count)
{
 if(*(volatile uint8_t *)(uintptr_t)0x805848u!=0u) return id;
 *(volatile uint8_t *)(uintptr_t)0x805848u=1u;
 uint32_t result=id;
 if(count!=0u) {
  uint32_t remaining=(uint8_t)(count-1u)+1u;
  uint32_t upper;
  __asm__ volatile("xbfu %0,%1,104" : "=r"(upper) : "r"(id));
  do {
   uintptr_t packet=opencfw_em9305_wsf_event_allocate(259u);
   result=(uint32_t)packet;
   if(packet==0u) break;
   *(volatile uint8_t *)(packet+3u)=(uint8_t)(length>>8u);
   *(volatile uint8_t *)(packet+2u)=(uint8_t)length;
   *(volatile uint8_t *)(packet+1u)=(uint8_t)upper;
   *(volatile uint8_t *)packet=(uint8_t)id;
   uint32_t value=*(volatile uint8_t *)(uintptr_t)0x805849u;
   *(volatile uint8_t *)(uintptr_t)0x805849u=(uint8_t)(value+1u);
   (void)opencfw_em9305_memset((void *)(packet+4u),value,length);
   result=opencfw_em9305_ll_received_event(packet);
   --remaining;
   if(remaining==0u) break;
  } while(1);
 }
 *(volatile uint8_t *)(uintptr_t)0x805848u=0u;
 return result;
}
/* Native308570..30858c: primary packet credit, critical-exit R0. */
uint32_t opencfw_em9305_ll_primary_credit_308570(uint32_t increment)
{
 (void)opencfw_em9305_wsf_critical_enter();
 uint32_t count=*(volatile uint8_t *)(uintptr_t)0x805ab5u;
 *(volatile uint8_t *)(uintptr_t)0x805ab5u=(uint8_t)(count+increment);
 return opencfw_em9305_wsf_critical_exit();
}
/* Native331d60..331d94: primary packet16-bit byte count and ownership. */
uint32_t opencfw_em9305_ll_primary_account_331d60(uintptr_t message)
{
 uint32_t enabled=*(volatile uint8_t *)(uintptr_t)0x805702u;
 if(enabled!=0u) {
  uint32_t high=*(volatile uint8_t *)(message+3u);
  uint32_t low=*(volatile uint8_t *)(message+2u);
  uint32_t count=*(volatile uint32_t *)(uintptr_t)0x805704u;
  uint32_t total=*(volatile uint32_t *)(uintptr_t)0x805708u;
  *(volatile uint32_t *)(uintptr_t)0x805704u=count+1u;
  *(volatile uint32_t *)(uintptr_t)0x805708u=total+(uint16_t)((high<<8u)+low);
  (void)opencfw_em9305_wsf_event_release(message);
  (void)opencfw_em9305_ll_primary_credit_308570(1u);
 }
 return enabled!=0u;
}
/* Native32e3bc..32e3e0: primary accounting or shared controller event kick. */
uint32_t opencfw_em9305_dispatch_32e3bc(void)
{
 if(*(volatile uint8_t *)(uintptr_t)0x805702u!=0u) {
  uintptr_t pending=opencfw_em9305_ll_primary_pending_30853c();
  if(pending!=0u) return opencfw_em9305_ll_primary_account_331d60(pending);
 }
 return opencfw_em9305_ll_event_kick(0u);
}
/* Native32e3e0..32e428: primary send or five-byte fallback event. */
uint32_t opencfw_em9305_dispatch_32e3e0(uint32_t first,uint32_t second)
{
 uint32_t length=*(volatile uint16_t *)(uintptr_t)0x80570eu;
 if(length!=0u) {
  uint32_t packets=*(volatile uint32_t *)(uintptr_t)0x805710u;
  uint32_t bytes=*(volatile uint32_t *)(uintptr_t)0x805714u;
  *(volatile uint32_t *)(uintptr_t)0x805710u=packets+1u;
  *(volatile uint32_t *)(uintptr_t)0x805714u=bytes+length;
  return opencfw_em9305_ll_primary_send_32f794(first,length,second);
 }
 uintptr_t event=opencfw_em9305_ll_event_allocate(19u,5u);
 if(event==0u) return 0u;
 *(volatile uint8_t *)(event+4u)=0u;
 *(volatile uint8_t *)(event+3u)=(uint8_t)second;
 *(volatile uint8_t *)(event+1u)=(uint8_t)first;
 *(volatile uint8_t *)event=1u;
 *(volatile uint8_t *)(event+2u)=(uint8_t)(first>>8u);
 return opencfw_em9305_ll_event_send(event-2u);
}
extern uintptr_t opencfw_em9305_ll_link_find_31ab88(uint32_t);
extern uintptr_t opencfw_em9305_ll_stream_find_31ab14(uint32_t);
extern uint32_t opencfw_em9305_ll_link_ready_31825c(uint32_t);
/* Native31b750..31b768: live link state1 and nonzero readiness byte520. */
uint32_t opencfw_em9305_ll_link_state_ready_31b750(uintptr_t record)
{
 if(*(volatile uint8_t *)(record+2u)!=1u) return 0u;
 return *(volatile uint8_t *)(record+520u)!=0u;
}
/* Native31825c..318278: lookup, active flag, then link readiness. */
uint32_t opencfw_em9305_ll_link_ready_31825c(uint32_t id)
{
 uintptr_t record=opencfw_em9305_ll_link_find_31ab88(id);
 if(record==0u || *(volatile uint8_t *)record==0u) return 0u;
 return opencfw_em9305_ll_link_state_ready_31b750(record)!=0u;
}
extern uint32_t opencfw_em9305_ll_stream_process_317680(uintptr_t,uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_ll_link_process_318740(uintptr_t,uintptr_t,uintptr_t);
/* Native31bc7c..31bd18: received header decode; LD.AB consumes old address. */
uint32_t opencfw_em9305_ll_received_decode_31bc7c(uintptr_t output,uintptr_t input)
{
 uint32_t low=*(volatile uint8_t *)input++;
 uint32_t high=*(volatile uint8_t *)input++;
 uint32_t word=(high<<8u)+low;
 *(volatile uint16_t *)output=(uint16_t)(word&0xfffu);
 word=(uint16_t)word;
 uint32_t extra;
 __asm__ volatile("xbfu %0,%1,0xe" : "=r"(extra) : "r"(word));
 uint32_t shifted=word>>12u,kind=shifted&3u;
 *(volatile uint8_t *)(output+3u)=(uint8_t)extra;
 *(volatile uint8_t *)(output+2u)=(uint8_t)kind;
 low=*(volatile uint8_t *)input++;
 high=*(volatile uint8_t *)input++;
 *(volatile uint16_t *)(output+4u)=(uint16_t)(((high<<8u)+low)&0xfffu);
 uint32_t size;
 if(((shifted|2u)&3u)!=2u) {
  *(volatile uint8_t *)(output+16u)=0u;
  *(volatile uint16_t *)(output+14u)=0u;
  *(volatile uint32_t *)(output+8u)=0u;
  size=4u;
 } else {
  uint32_t timestamp=0u;size=8u;
  if(extra!=0u) {
   uint32_t b1=*(volatile uint8_t *)(input+1u);
   uint32_t b0=*(volatile uint8_t *)input;
   uint32_t b2=*(volatile uint8_t *)(input+2u);
   uint32_t b3=*(volatile uint8_t *)(input+3u);
   timestamp=(b1<<8u)+b0+(b2<<16u)+(b3<<24u);input+=4u;size=12u;
  }
  *(volatile uint32_t *)(output+8u)=timestamp;
  low=*(volatile uint8_t *)input++;high=*(volatile uint8_t *)input++;
  *(volatile uint16_t *)(output+12u)=(uint16_t)((high<<8u)+low);
  low=*(volatile uint8_t *)input++;high=*(volatile uint8_t *)input++;
  word=(high<<8u)+low;
  *(volatile uint16_t *)(output+14u)=(uint16_t)(word&0xfffu);
  *(volatile uint8_t *)(output+16u)=(uint8_t)((word&0xc000u)>>14u);
 }
 *(volatile uint32_t *)(output+20u)=(uint32_t)input;
 return size;
}
/* Native31ab14..31ab50: active stream records, 256-byte stride. */
uintptr_t opencfw_em9305_ll_stream_find_31ab14(uint32_t id)
{
 uintptr_t row=*(volatile uint32_t *)(uintptr_t)0x805c40u;
 if(row==0u) return 0u;
 uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
 uint32_t count=*(volatile uint8_t *)(config+58u);
 for(uint32_t i=0u;i<count;++i,row+=256u)
  if(*(volatile uint8_t *)row!=0u && *(volatile uint16_t *)(row+2u)==id) return row;
 return 0u;
}
/* Native31ab88..31abc0: identifier then active flag, 656-byte link records. */
uintptr_t opencfw_em9305_ll_link_find_31ab88(uint32_t id)
{
 uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
 uint32_t count=*(volatile uint8_t *)(config+53u);
 if(count==0u) return 0u;
 uintptr_t row=*(volatile uint32_t *)(uintptr_t)0x805c68u;
 for(uint32_t i=0u;i<count;++i,row+=656u)
  if(*(volatile uint16_t *)(row+8u)==id && *(volatile uint8_t *)row!=0u) return row;
 return 0u;
}
/* Native30a564..30a6b4: received-message length checks and link/stream routing. */
uint32_t opencfw_em9305_ll_received_event_active(uintptr_t message)
{
 _Alignas(4) uint8_t decoded[24];
 (void)opencfw_em9305_ll_received_decode_31bc7c((uintptr_t)decoded,message);
 uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
 uint32_t length=*(volatile uint16_t *)(void *)(decoded+14u);
 if(*(volatile uint16_t *)(config+44u)<length ||
    *(volatile uint8_t *)(uintptr_t)0x805adcu==0u) goto reject;
 uint32_t extra=*(volatile uint8_t *)(decoded+3u);
 uint32_t encoded=*(volatile uint16_t *)(void *)(decoded+4u);
 uint32_t actual=(uint16_t)(encoded-(extra!=0u?8u:4u));
 if(length!=actual) {
  message=opencfw_em9305_ll_received_resize_3048b0(message,(uintptr_t)decoded);
  if(message==0u) return 0u;
  (void)opencfw_em9305_ll_received_decode_31bc7c((uintptr_t)decoded,message);
 }
 uint32_t id=*(volatile uint16_t *)(void *)decoded;
 uintptr_t link=opencfw_em9305_ll_link_find_31ab88(id);
 if(link!=0u) {
  uint32_t ready=opencfw_em9305_ll_link_ready_31825c(
    *(volatile uint16_t *)(link+8u));
  if(ready==0u) return opencfw_em9305_wsf_event_release(message);
  if(*(volatile uint16_t *)(link+448u)==0u) goto reject;
  uint32_t active=*(volatile uint8_t *)(link+10u);
  uint32_t flags=*(volatile uint8_t *)(link+512u);
  if((flags|active)==0u) goto reject;
  if(*(volatile uint8_t *)(link+513u)==0u && active==1u) goto reject;
  uint32_t maximum=*(volatile uint16_t *)(link+(active==0u?486u:488u));
  if(maximum<*(volatile uint16_t *)(void *)(decoded+14u)) goto reject;
  if(*(volatile uint8_t *)(link+484u)!=0u) {
   uintptr_t queue=link+612u;
   (void)opencfw_em9305_ll_event_enqueue(queue,0u,message);
   uint32_t count=*(volatile uint8_t *)(queue+8u)+1u;
   *(volatile uint8_t *)(queue+8u)=(uint8_t)count;
   return count;
  }
  (void)opencfw_em9305_wsf_critical_enter();
  uint32_t count=*(volatile uint8_t *)(uintptr_t)0x805adcu;
  *(volatile uint8_t *)(uintptr_t)0x805adcu=(uint8_t)(count-1u);
  (void)opencfw_em9305_wsf_critical_exit();
  return opencfw_em9305_ll_link_process_318740(link,(uintptr_t)decoded,message);
 }
 uintptr_t stream=opencfw_em9305_ll_stream_find_31ab14(id);
 if(stream==0u) return opencfw_em9305_wsf_event_release(message);
 uintptr_t descriptor=*(volatile uint32_t *)(stream+4u);
 if(*(volatile uint16_t *)(descriptor+6u)<
    *(volatile uint16_t *)(void *)(decoded+14u)) goto reject;
 (void)opencfw_em9305_wsf_critical_enter();
 uint32_t count=*(volatile uint8_t *)(uintptr_t)0x805adcu;
 *(volatile uint8_t *)(uintptr_t)0x805adcu=(uint8_t)(count-1u);
 (void)opencfw_em9305_wsf_critical_exit();
 descriptor=*(volatile uint32_t *)(stream+4u);
 if(*(volatile uint8_t *)(descriptor+30u)!=0u) {
  (void)opencfw_em9305_ll_event_enqueue(stream+20u,0u,message);
  count=*(volatile uint8_t *)(stream+28u)+1u;
  *(volatile uint8_t *)(stream+28u)=(uint8_t)count;
  return count;
 }
 return opencfw_em9305_ll_stream_process_317680(stream,(uintptr_t)decoded,message);
reject:;
 uint32_t result=opencfw_em9305_wsf_event_release(message);
 uintptr_t callback=*(volatile uint32_t *)(uintptr_t)0x805b10u;
 if(callback!=0u) return ((uint32_t (*)(uint32_t,uint32_t))callback)(
   *(volatile uint16_t *)(void *)decoded,1u);
 return result;
}
/* Native3181b4..318200: conditional segment scheduling, incidental R0. */
uint32_t opencfw_em9305_ll_segment_notify_3181b4(uintptr_t record)
{
 uint32_t result=*(volatile uint8_t *)(record+2u);
 if(result==0u) return result;
 result=*(volatile uint8_t *)(record+5u);
 if((result&4u)==0u) return result;
 result=*(volatile uint16_t *)(record+260u);
 if(result==0u) return result;
 result=*(volatile uint8_t *)(record+628u);
 if(result!=0u) {
  result=*(volatile uint8_t *)(record+635u);
  if(result==17u) return result;
 }
 uint32_t now=opencfw_em9305_pal_current_time();
 uint32_t interval=*(volatile uint16_t *)(record+266u)*1250u;
 uint32_t timestamp=*(volatile uint32_t *)(record+24u);
 uint32_t elapsed=opencfw_em9305_auxiliary_elapsed_303f8c(timestamp,now);
 if(interval>=elapsed) return (uint32_t)(record+16u);
 *(volatile uint8_t *)(record+217u)=1u;
 return opencfw_em9305_ll_schedule_notify_313354(record+16u);
}
extern uint32_t opencfw_em9305_ll_segment_error_32322c(uint32_t);
/* Native30e79c..30e7ac: optional controller callback, own address in R1. */
uint32_t opencfw_em9305_ll_event_callback_30e79c(uintptr_t event)
{
 uintptr_t callback=*(volatile uint32_t *)(uintptr_t)0x805b0cu;
 if(callback==0u) return 0u;
 return ((uint32_t (*)(uintptr_t,uintptr_t))callback)(event,callback);
}
/* Native32322c..32324c: five initialized event bytes; no unused stack copy. */
uint32_t opencfw_em9305_ll_segment_error_32322c(uint32_t error)
{
 _Alignas(4) uint8_t event[5];
 *(volatile uint8_t *)(event+4u)=(uint8_t)error;
 *(volatile uint8_t *)(event+3u)=(uint8_t)error;
 *(volatile uint8_t *)(event+2u)=0u;
 *(volatile uint16_t *)(void *)event=0u;
 return opencfw_em9305_ll_event_callback_30e79c((uintptr_t)event);
}
/* Native323d70..323dc0: compact two/three-byte segment header. Return length. */
uintptr_t opencfw_em9305_ll_segment_header_323d70(uintptr_t output,uintptr_t fields)
{
 uint32_t one=*(volatile uint8_t *)(fields+1u);
 uint32_t three=*(volatile uint8_t *)(fields+3u);
 uint32_t two=*(volatile uint8_t *)(fields+2u);
 uint32_t five=*(volatile uint8_t *)(fields+5u);
 uint32_t four=*(volatile uint8_t *)(fields+4u);
 uint32_t zero=*(volatile uint8_t *)fields;
 *(volatile uint8_t *)(output+1u)=(uint8_t)five;
 *(volatile uint8_t *)output=(uint8_t)(zero|((one<<2u)&4u)|
   ((two<<3u)&8u)|((three<<4u)&16u)|((four<<5u)&32u));
 if(*(volatile uint8_t *)(fields+4u)==0u) return 2u;
 uint32_t six=*(volatile uint8_t *)(fields+6u);
 uint32_t seven=*(volatile uint8_t *)(fields+7u);
 *(volatile uint8_t *)(output+2u)=(uint8_t)((seven&31u)+(six<<6u));
 return 3u;
}
/* Native32d380..32d4b0: queue-backed segment construction and ownership. */
uint32_t opencfw_em9305_ll_event_process_32d380(uintptr_t record,uint32_t capacity,
                                             uintptr_t decoded,uintptr_t message)
{
 uint32_t total=*(volatile uint16_t *)(decoded+4u);
 uintptr_t node=opencfw_em9305_wsf_queue_remove(0x8056dcu);
 if(node==0u) {
  (void)opencfw_em9305_wsf_event_release(message);
  uintptr_t callback=*(volatile uint32_t *)(uintptr_t)0x805b10u;
  (void)((uint32_t (*)(uint32_t,uint32_t))callback)(
    *(volatile uint16_t *)decoded,1u);
  (void)opencfw_em9305_wsf_critical_enter();
  uint32_t count=*(volatile uint8_t *)(uintptr_t)0x805ab4u;
  *(volatile uint8_t *)(uintptr_t)0x805ab4u=(uint8_t)(count+1u);
  (void)opencfw_em9305_wsf_critical_exit();
  return opencfw_em9305_ll_segment_error_32322c(7u);
 }
 uintptr_t packet=node+8u,payload=message+4u;
 uint32_t length=*(volatile uint16_t *)(decoded+4u);
 uint32_t chunk_limit=capacity<length?capacity:length;
 *(volatile uint8_t *)(packet+7u)=0u;
 *(volatile uint32_t *)packet=(uint32_t)payload;
 *(volatile uint16_t *)(packet+4u)=(uint16_t)length;
 *(volatile uint8_t *)(packet+6u)=(uint8_t)chunk_limit;
 if(total!=0u) {
  uint32_t kind=*(volatile uint8_t *)(decoded+2u),done=0u,index=0u;
  do {
   uint32_t remaining=(uint16_t)(total-done);
   uint32_t chunk=remaining<chunk_limit?remaining:chunk_limit;
   _Alignas(4) uint8_t header[8]={0};
   *(volatile uint16_t *)(decoded+4u)=(uint16_t)chunk;
   if(kind==1u) {
    uint32_t pending=*(volatile uint8_t *)(record+381u);
    header[0]=1u;
    if(pending!=0u) {
     *(volatile uint8_t *)(record+381u)=0u;header[0]=2u;
    }
   } else if(kind==0u) {
    *(volatile uint8_t *)(record+381u)=0u;header[0]=2u;
   }
   uintptr_t segment=packet+(uint8_t)index*8u;
   header[5]=(uint8_t)chunk;
   uintptr_t output=opencfw_em9305_ll_segment_header_323d70(segment+10u,(uintptr_t)header);
   uintptr_t callback=*(volatile uint32_t *)(uintptr_t)0x8051e0u;
   *(volatile uint8_t *)(segment+8u)=2u;
   uint32_t result=0u;
   if(callback!=0u) result=((uint32_t (*)(uintptr_t,uintptr_t,uintptr_t,uintptr_t))callback)(
     record+84u,output,payload,segment+12u);
   *(volatile uint8_t *)(segment+9u)=(uint8_t)(result!=0u?4u:0u);
   done+=chunk;
   *(volatile uint8_t *)(decoded+2u)=1u;
   if((uint16_t)done>=total) break;
   kind=1u;payload+=chunk;++index;
  } while(1);
 }
 (void)opencfw_em9305_ll_event_enqueue(record+360u,
   *(volatile uint8_t *)decoded,packet);
 return opencfw_em9305_ll_segment_notify_3181b4(record);
}

/* Native32fccc..32fd18: counted two-halfword pair response, native byte length. */
uint32_t opencfw_em9305_dispatch_32fccc(uint32_t count,uintptr_t first,uintptr_t second)
{
 uintptr_t packet=opencfw_em9305_ll_event_allocate(19u,(uint8_t)(1u+4u*count));
 if(packet==0u) return 0u;
 *(volatile uint8_t *)packet=(uint8_t)count;
 uintptr_t cursor=packet;
 for(uint32_t i=0u;i<count;++i) {
  uint32_t a=*(volatile uint8_t *)(first+2u*i);
  *(volatile uint8_t *)(cursor+1u)=(uint8_t)a;
  a=*(volatile uint8_t *)(first+2u*i+1u);
  *(volatile uint8_t *)(cursor+2u)=(uint8_t)a;
  uint32_t b=*(volatile uint8_t *)(second+2u*i);
  *(volatile uint8_t *)(cursor+3u)=(uint8_t)b;
  b=*(volatile uint8_t *)(second+2u*i+1u);
  *(volatile uint8_t *)(cursor+4u)=(uint8_t)b;
  cursor+=4u;
 }
 return opencfw_em9305_ll_event_send(packet-2u);
}

/* Native32e428..32e454: source-owned command response header and payload. */
uintptr_t opencfw_em9305_ll_response_allocate_32e428(uint32_t length,uint32_t command)
{
 uintptr_t packet=opencfw_em9305_wsf_event_allocate(length+5u);
 if(packet==0u) return 0u;
 *(volatile uint8_t *)(packet+3u)=(uint8_t)command;
 *(volatile uint8_t *)(packet+2u)=1u;
 *(volatile uint8_t *)packet=14u;
 *(volatile uint8_t *)(packet+4u)=(uint8_t)(command>>8u);
 *(volatile uint8_t *)(packet+1u)=(uint8_t)(length+3u);
 return packet+5u;
}
extern uintptr_t opencfw_em9305_ll_information_303278(uintptr_t);
extern uintptr_t opencfw_em9305_ll_information_303284(uintptr_t);
/* Native32fd18..32fe3c: link-test commands and real command-response allocation. */
uint32_t opencfw_em9305_dispatch_32fd18(uintptr_t request,uintptr_t input)
{
 uint32_t command=*(volatile uint16_t *)request;
 uint32_t length;
 if(command==0xffd5u) {
  uint32_t highid=*(volatile uint8_t *)(input+1u);
  uint32_t highlength=*(volatile uint8_t *)(input+3u);
  uint32_t lowid=*(volatile uint8_t *)input;
  uint32_t lowlength=*(volatile uint8_t *)(input+2u);
  uint32_t count=*(volatile uint8_t *)(input+4u);
  (void)opencfw_em9305_ll_link_send_32f7f8((uint16_t)((highid<<8u)+lowid),
       (uint16_t)((highlength<<8u)+lowlength),count);
  command=*(volatile uint16_t *)request; length=1u;
 } else if(command==0xffd6u) length=17u;
 else if(command==0xffd7u) {
  *(volatile uint8_t *)(uintptr_t)0x80583cu=*(volatile uint8_t *)input!=0u;
  length=1u;
 } else if(command==0xffd8u) {
  uint32_t low=*(volatile uint8_t *)input;
  uint32_t high=*(volatile uint8_t *)(input+1u);
  *(volatile uint16_t *)(uintptr_t)0x80584au=(uint16_t)(low+(high<<8u));
  length=1u;
 } else if(command==0xffd9u || command==0xffc1u) length=29u;
 else return 0u;
 uintptr_t response=opencfw_em9305_ll_response_allocate_32e428(length,command);
 if(response==0u) return 1u;
 *(volatile uint8_t *)response=0u;
 uintptr_t payload=response+1u;
 command=*(volatile uint16_t *)request;
 if(command==0xffd6u) {
  static const uint8_t offsets[4]={0u,4u,12u,16u};
  for(uint32_t i=0u;i<4u;++i) {
   uintptr_t src=(uintptr_t)0x805840u+offsets[i];
   *(volatile uint8_t *)(payload+4u*i)=(uint8_t)*(volatile uint32_t *)src;
   *(volatile uint8_t *)(payload+4u*i+1u)=(uint8_t)(*(volatile uint32_t *)src>>8u);
   *(volatile uint8_t *)(payload+4u*i+2u)=(uint8_t)*(volatile uint16_t *)(src+2u);
   *(volatile uint8_t *)(payload+4u*i+3u)=*(volatile uint8_t *)(src+3u);
  }
 } else if(command==0xffc1u || command==0xffd9u) {
  _Alignas(4) uint8_t scratch[28];
  if(command==0xffc1u) opencfw_em9305_ll_information_303278((uintptr_t)scratch);
  else opencfw_em9305_ll_information_303284((uintptr_t)scratch);
  (void)opencfw_em9305_memcpy((void *)payload,scratch,28u);
 }
 (void)opencfw_em9305_ll_event_send(payload-6u);
 return 1u;
}

/* Native303278/303284: exact 28-byte live controller information copies. */
uintptr_t opencfw_em9305_ll_information_303278(uintptr_t output)
{
 return (uintptr_t)opencfw_em9305_memcpy((void *)output,(const void *)(uintptr_t)0x801518u,28u);
}
uintptr_t opencfw_em9305_ll_information_303284(uintptr_t output)
{
 return (uintptr_t)opencfw_em9305_memcpy((void *)output,(const void *)(uintptr_t)0x8016c0u,28u);
}

/* Native32fe3c..32fea4: 35 dynamic handlers and fallback controller event. */
uint32_t opencfw_em9305_dispatch_32fe3c(uintptr_t message)
{
 uintptr_t cursor=(uintptr_t)0x8057acu;
 uint32_t remaining=35u;
 do {
  uintptr_t callback=*(volatile uint32_t *)cursor;
  cursor+=4u;
  if(callback!=0u && ((uint32_t (*)(uintptr_t))callback)(message)!=0u) return 1u;
  --remaining;
 } while(remaining!=0u);
 uint32_t kind=*(volatile uint8_t *)(message+2u);
 if(kind==1u) {
  (void)opencfw_em9305_ll_dispatch_initialize(1u);
  uintptr_t packet=opencfw_em9305_ll_event_allocate(14u,4u);
  if(packet==0u) return 0u;
  *(volatile uint8_t *)(packet+2u)=12u;
  *(volatile uint8_t *)(packet+1u)=3u;
  *(volatile uint8_t *)packet=1u;
  *(volatile uint8_t *)(packet+3u)=*(volatile uint8_t *)(message+3u);
  (void)opencfw_em9305_ll_event_send(packet-2u);
  return 1u;
 }
 if(kind==0u) {
  uintptr_t packet=opencfw_em9305_ll_event_allocate(16u,1u);
  if(packet==0u) return 0u;
  *(volatile uint8_t *)packet=*(volatile uint8_t *)(message+4u);
  (void)opencfw_em9305_ll_event_send(packet-1u);
  return 1u;
 }
 return 0u;
}

/* Native31b71c..31b750: any active 512-byte record in pending state1. */
uint32_t opencfw_em9305_ll_record_pending_31b71c(void)
{
 uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
 uint32_t count=*(volatile uint8_t *)(config+57u);
 if(count==0u) return 0u;
 uintptr_t record=*(volatile uint32_t *)(uintptr_t)0x805c3cu;
 for(uint32_t i=0u;i<count;++i,record+=512u)
  if(*(volatile uint8_t *)record!=0u && *(volatile uint8_t *)(record+1u)==1u) return 1u;
 return 0u;
}
/* Native31aa98..31aad0: active512-byte record id lookup. */
uintptr_t opencfw_em9305_ll_record_find_31aa98(uint32_t id)
{
 uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
 uint32_t count=*(volatile uint8_t *)(config+57u);
 if(count==0u) return 0u;
 uintptr_t record=*(volatile uint32_t *)(uintptr_t)0x805c3cu;
 for(uint32_t i=0u;i<count;++i,record+=512u)
  if(*(volatile uint8_t *)record!=0u && *(volatile uint8_t *)(record+2u)==id) return record;
 return 0u;
}
/* Native31aad0..31ab14: active record association to784-byte controller state. */
uintptr_t opencfw_em9305_ll_record_associated_31aad0(uint32_t index)
{
 uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
 uint32_t count=*(volatile uint8_t *)(config+57u);
 if(count==0u) return 0u;
 uintptr_t record=*(volatile uint32_t *)(uintptr_t)0x805c3cu;
 uintptr_t state=(uintptr_t)0x803d78u+index*784u;
 for(uint32_t i=0u;i<count;++i,record+=512u)
  if(*(volatile uint8_t *)record!=0u && *(volatile uint32_t *)(record+196u)==state) return record;
 return 0u;
}
/* Native31b248..31b278: count inactive256-byte stream records, byte return. */
uint32_t opencfw_em9305_ll_stream_free_count_31b248(void)
{
 uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
 uint32_t count=*(volatile uint8_t *)(config+58u),free_count=0u;
 if(count!=0u) {
  uintptr_t record=*(volatile uint32_t *)(uintptr_t)0x805c40u;
  for(uint32_t i=0u;i<count;++i,record+=256u)
   if(*(volatile uint8_t *)record==0u) ++free_count;
 }
 return (uint8_t)free_count;
}
/* Native316a8c..316ad4: clear first inactive512-byte record and publish id/active. */
uintptr_t opencfw_em9305_ll_record_allocate_316a8c(uint32_t id)
{
 uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
 uint32_t count=*(volatile uint8_t *)(config+57u);
 if(count==0u) return 0u;
 uintptr_t record=*(volatile uint32_t *)(uintptr_t)0x805c3cu;
 for(uint32_t i=0u;i<count;++i,record+=512u) {
  if(*(volatile uint8_t *)record==0u) {
   (void)opencfw_em9305_memset((void *)record,0u,512u);
   *(volatile uint8_t *)(record+2u)=(uint8_t)id;
   *(volatile uint8_t *)record=1u;
   return record;
  }
 }
 return 0u;
}
/* Native331bf8..331c20: four-byte command-status event. */
uint32_t opencfw_em9305_ll_status_event_331bf8(uintptr_t request,uint32_t status)
{
 uintptr_t packet=opencfw_em9305_ll_event_allocate(15u,4u);
 if(packet==0u) return 0u;
 uint32_t command=*(volatile uint16_t *)request;
 *(volatile uint8_t *)(packet+1u)=1u;
 *(volatile uint8_t *)(packet+2u)=(uint8_t)command;
 *(volatile uint8_t *)packet=(uint8_t)status;
 packet-=2u; /* native ST.AB: status at old payload then pointer retreats */
 *(volatile uint8_t *)(packet+5u)=(uint8_t)(command>>8u);
 return opencfw_em9305_ll_event_send(packet);
}

extern uintptr_t opencfw_em9305_ll_record_callback_322618(uint32_t); /* native0x322618 */
/* Native307664..3077b8: validate and configure controller-associated link record. */
uint32_t opencfw_em9305_ll_record_configure_307664(uintptr_t command)
{
 if(opencfw_em9305_ll_record_pending_31b71c()!=0u) return 12u;
 uint32_t id=*(volatile uint8_t *)command;
 if(opencfw_em9305_ll_record_find_31aa98(id)!=0u) return 12u;
 uint32_t index=*(volatile uint16_t *)(command+2u);
 if(index>=7u) return 66u;
 uintptr_t state=(uintptr_t)0x803d78u+index*784u;
 if(*(volatile uint8_t *)state==0u) return 66u;
 if(opencfw_em9305_ll_record_associated_31aad0(index)!=0u) return 17u;
 if(*(volatile uint8_t *)(state+410u)==0u) return 12u;
 uint32_t maximum=*(volatile uint8_t *)(state+424u);
 uint32_t requested=*(volatile uint8_t *)(command+24u);
 if(maximum<requested) return 17u;
 if(requested>=5u) return 13u;
 if(opencfw_em9305_ll_stream_free_count_31b248()<requested) return 13u;
 uint32_t count=*(volatile uint8_t *)(command+24u);
 for(uint32_t i=0u;i<count;++i) {
  uint32_t item=*(volatile uint8_t *)(command+25u+i);
  if(item==0u) return 18u;
  if(item>=5u) return 17u;
  if(*(volatile uint8_t *)(state+424u)<item) return 17u;
 }
 uint32_t mode=*(volatile uint8_t *)(command+4u);
 if(mode!=*(volatile uint8_t *)(state+477u)) return 37u;
 uintptr_t record=opencfw_em9305_ll_record_allocate_316a8c(*(volatile uint8_t *)command);
 if(record==0u) return 13u;
 id=*(volatile uint8_t *)command;
 *(volatile uint32_t *)(state+12u)=(uint32_t)(uintptr_t)&opencfw_em9305_ll_record_callback_322618;
 *(volatile uint32_t *)(record+196u)=(uint32_t)state;
 uint32_t options=*(volatile uint8_t *)(command+21u);
 *(volatile uint8_t *)(record+2u)=(uint8_t)id;
 *(volatile uint8_t *)(record+201u)=(uint8_t)options;
 uint32_t interval=*(volatile uint16_t *)(command+22u);
 *(volatile uint32_t *)(record+224u)=interval*10u;
 count=*(volatile uint8_t *)(command+24u);
 *(volatile uint8_t *)(record+202u)=(uint8_t)count;
 (void)opencfw_em9305_memcpy((void *)(record+203u),(const void *)(command+25u),
                             *(volatile uint8_t *)(command+24u));
 mode=*(volatile uint8_t *)(command+4u);
 *(volatile uint8_t *)(record+484u)=mode!=0u;
 (void)opencfw_em9305_memcpy((void *)(record+228u),(const void *)(command+5u),16u);
 uint32_t handler=*(volatile uint8_t *)(uintptr_t)0x805b18u;
 *(volatile uint16_t *)(record+212u)=(uint16_t)id;
 *(volatile uint8_t *)(record+220u)=(uint8_t)handler;
 *(volatile uint16_t *)(record+214u)=1297u;
 uintptr_t event=opencfw_em9305_wsf_event_allocate(4u);
 if(event!=0u) {
  *(volatile uint16_t *)(event+2u)=273u;
  id=*(volatile uint8_t *)command;
  handler=*(volatile uint8_t *)(uintptr_t)0x805b18u;
  *(volatile uint16_t *)event=(uint16_t)id;
  (void)opencfw_em9305_wsf_task_message_send(handler,event);
 }
 return 0u;
}
/* Native30b0a4..30b0f0: exact parameter validation envelope. */
uint32_t opencfw_em9305_ll_record_validate_30b0a4(uintptr_t command)
{
 if(*(volatile uint8_t *)command>239u) return 48u;
 if(*(volatile uint16_t *)(command+2u)>=0xf00u) return 48u;
 if(*(volatile uint8_t *)(command+4u)>=2u) return 48u;
 if(*(volatile uint8_t *)(command+21u)>=32u) return 48u;
 uint32_t interval=*(volatile uint16_t *)(command+22u);
 if((uint16_t)(interval-0x4001u)<0xc009u) return 48u;
 uint32_t count=*(volatile uint8_t *)(command+24u);
 if(count-1u>=31u) return 48u;
 return opencfw_em9305_ll_record_configure_307664(command);
}

/* Native322f08..322f2c: fully initialized six-byte record error callback. */
uint32_t opencfw_em9305_ll_record_error_322f08(uint32_t error,uintptr_t record)
{
 _Alignas(2) uint8_t event[6];
 *(volatile uint16_t *)(void *)event=(uint16_t)record;
 event[2]=43u; event[3]=(uint8_t)error; event[4]=(uint8_t)error; event[5]=(uint8_t)record;
 return opencfw_em9305_ll_event_callback_30e79c((uintptr_t)event);
}
/* Native3077b8..3077f4 /30b0f0: release request or exact lookup/state error. */
uint32_t opencfw_em9305_ll_record_release_request_3077b8(uint32_t id)
{
 uintptr_t record=opencfw_em9305_ll_record_find_31aa98(id);
 if(record==0u) return opencfw_em9305_ll_record_error_322f08(66u,record);
 if(*(volatile uint8_t *)(record+3u)!=0u)
  return opencfw_em9305_ll_record_error_322f08(12u,record);
 uintptr_t event=opencfw_em9305_wsf_event_allocate(4u);
 if(event==0u) return 0u;
 *(volatile uint16_t *)(event+2u)=529u;
 uint32_t handler=*(volatile uint8_t *)(uintptr_t)0x805b18u;
 *(volatile uint16_t *)event=(uint16_t)record;
 return opencfw_em9305_wsf_task_message_send(handler,event);
}
/* Native32fea4..32ff20: source-owned record command parameter conversion. */
uint32_t opencfw_em9305_dispatch_32fea4(uintptr_t request,uintptr_t input)
{
 uint32_t command=*(volatile uint16_t *)request;
 if(command==0x206cu) {
  (void)opencfw_em9305_ll_record_release_request_3077b8(*(volatile uint8_t *)input);
  return 1u;
 }
 if(command!=0x206bu) return 0u;
 _Alignas(4) uint8_t converted[32];
 uint32_t high=*(volatile uint8_t *)(input+2u);
 uint32_t low=*(volatile uint8_t *)(input+1u);
 uint32_t id=*(volatile uint8_t *)input;
 uint32_t mode=*(volatile uint8_t *)(input+3u);
 converted[0]=(uint8_t)id; converted[4]=(uint8_t)mode;
 *(volatile uint16_t *)(void *)(converted+2u)=(uint16_t)((high<<8u)+low);
 (void)opencfw_em9305_memcpy(converted+5u,(const void *)(input+4u),16u);
 high=*(volatile uint8_t *)(input+22u);
 low=*(volatile uint8_t *)(input+21u);
 uint32_t flags=*(volatile uint8_t *)(input+20u);
 uint32_t count=*(volatile uint8_t *)(input+23u);
 converted[21]=(uint8_t)flags; converted[24]=(uint8_t)count;
 *(volatile uint16_t *)(void *)(converted+22u)=(uint16_t)((high<<8u)+low);
 (void)opencfw_em9305_memcpy(converted+25u,(const void *)(input+24u),count<4u?count:4u);
 /* Native leaves byte1/padding untouched; validators and setup never consume it. */
 uint32_t status=opencfw_em9305_ll_record_validate_30b0a4((uintptr_t)converted);
 (void)opencfw_em9305_ll_status_event_331bf8(request,status);
 return 1u;
}

/* Native32ff20..3300c8: four controller-event encodings and feature/credit gates. */
uint32_t opencfw_em9305_dispatch_32ff20(uintptr_t message)
{
 uint32_t kind=*(volatile uint8_t *)(message+2u);
 uintptr_t features=(uintptr_t)0x8056e8u;
 uintptr_t packet;
 if(kind==43u) {
  packet=opencfw_em9305_ll_event_allocate(14u,5u);
  if(packet==0u) return 0u;
  uint32_t size=opencfw_em9305_ll_pack_typed_halfword(packet,0x206cu);
  *(volatile uint8_t *)(packet+size)=*(volatile uint8_t *)(message+4u);
  *(volatile uint8_t *)(packet+size+1u)=*(volatile uint8_t *)(message+5u);
 } else if(kind==50u) {
  if((*(volatile uint8_t *)(features+20u)&2u)==0u) return 1u;
  if((*(volatile uint8_t *)(features+7u)&32u)==0u) return 1u;
  uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
  uint32_t outstanding=*(volatile uint8_t *)(uintptr_t)0x805718u;
  if(outstanding>=*(volatile uint8_t *)(config+14u)) return 1u;
  packet=opencfw_em9305_ll_event_allocate(62u,20u);
  if(packet==0u) return 1u;
  *(volatile uint8_t *)packet=34u;
  for(uint32_t i=0u;i<9u;++i)
   *(volatile uint8_t *)(packet+1u+i)=*(volatile uint8_t *)(message+4u+i);
  *(volatile uint8_t *)(packet+10u)=*(volatile uint8_t *)(message+14u);
  *(volatile uint8_t *)(packet+11u)=*(volatile uint8_t *)(message+15u);
  *(volatile uint8_t *)(packet+12u)=(uint8_t)*(volatile uint32_t *)(message+16u);
  *(volatile uint8_t *)(packet+13u)=(uint8_t)(*(volatile uint32_t *)(message+16u)>>8u);
  *(volatile uint8_t *)(packet+14u)=(uint8_t)*(volatile uint16_t *)(message+18u);
  for(uint32_t i=0u;i<5u;++i)
   *(volatile uint8_t *)(packet+15u+i)=*(volatile uint8_t *)(message+20u+i);
  outstanding=*(volatile uint8_t *)(uintptr_t)0x805718u;
  *(volatile uint8_t *)(uintptr_t)0x805718u=(uint8_t)(outstanding+1u);
 } else if(kind==44u) {
  if((*(volatile uint8_t *)(features+19u)&16u)==0u) return 0u;
  if((*(volatile uint8_t *)(features+7u)&32u)==0u) return 0u;
  uint32_t count=*(volatile uint8_t *)(message+20u);
  packet=opencfw_em9305_ll_event_allocate(62u,(uint8_t)(15u+2u*count));
  if(packet==0u) return 0u;
  *(volatile uint8_t *)packet=29u;
  *(volatile uint8_t *)(packet+1u)=*(volatile uint8_t *)(message+4u);
  *(volatile uint8_t *)(packet+2u)=*(volatile uint8_t *)(message+5u);
  *(volatile uint8_t *)(packet+3u)=(uint8_t)*(volatile uint32_t *)(message+8u);
  *(volatile uint8_t *)(packet+4u)=(uint8_t)(*(volatile uint32_t *)(message+8u)>>8u);
  *(volatile uint8_t *)(packet+5u)=(uint8_t)*(volatile uint16_t *)(message+10u);
  for(uint32_t i=0u;i<8u;++i)
   *(volatile uint8_t *)(packet+6u+i)=*(volatile uint8_t *)(message+12u+i);
  *(volatile uint8_t *)(packet+14u)=*(volatile uint8_t *)(message+20u);
  count=*(volatile uint8_t *)(message+20u);
  if(count!=0u) {
   uint32_t i=0u;
   do {
    *(volatile uint8_t *)(packet+15u+2u*i)=*(volatile uint8_t *)(message+22u+2u*i);
    ++i;
    *(volatile uint8_t *)(packet+14u+2u*i)=*(volatile uint8_t *)(message+21u+2u*i);
    count=*(volatile uint8_t *)(message+20u);
   } while(i<count);
  }
 } else if(kind==45u) {
  if((*(volatile uint8_t *)(features+19u)&32u)==0u) return 0u;
  if((*(volatile uint8_t *)(features+7u)&32u)==0u) return 0u;
  packet=opencfw_em9305_ll_event_allocate(62u,3u);
  if(packet==0u) return 0u;
  *(volatile uint8_t *)packet=30u;
  *(volatile uint8_t *)(packet+1u)=*(volatile uint8_t *)(message+4u);
  *(volatile uint8_t *)(packet+2u)=*(volatile uint8_t *)(message+5u);
 } else return 0u;
 (void)opencfw_em9305_ll_event_send(packet-2u);
 return 1u;
}

/* Native322618..322630: detach associated record while retaining lookup R0. */
uintptr_t opencfw_em9305_ll_record_callback_322618(uint32_t index)
{
 uintptr_t record=opencfw_em9305_ll_record_associated_31aad0(index);
 if(record!=0u && *(volatile uint32_t *)(record+196u)!=0u)
  *(volatile uint32_t *)(record+196u)=0u;
 return record;
}

/* Native330568..3305ac: command0x2019 little-endian decode and status event.
 * The associated controller operation30e054 remains an honest lower contract. */
extern uint32_t opencfw_em9305_ll_command_30e054(uint32_t id,uintptr_t first,
                                               uint32_t value,uintptr_t second);
uint32_t opencfw_em9305_dispatch_330568(uintptr_t request,uintptr_t input)
{
 if(*(volatile uint16_t *)request!=0x2019u)
  return opencfw_em9305_dispatch_332278(request,input);
 uint32_t id=*(volatile uint8_t *)input |
             ((uint32_t)*(volatile uint8_t *)(input+1u)<<8u);
 uint32_t value=*(volatile uint8_t *)(input+10u) |
                ((uint32_t)*(volatile uint8_t *)(input+11u)<<8u);
 uint32_t status=opencfw_em9305_ll_command_30e054(id,input+2u,value,input+12u);
 (void)opencfw_em9305_ll_status_event_331bf8(request,status);
 return 1u;
}
/* Native3305ac: unconditional branch preserves the two-argument ABI. */
uint32_t opencfw_em9305_dispatch_3305ac(uintptr_t request,uintptr_t input)
{
 return opencfw_em9305_dispatch_332394(request,input);
}

/* Native332394..33248e: feature-gated controller event conversion.
 * R1 is overwritten immediately by the native feature-mask base. */
extern uint32_t opencfw_em9305_ll_event_fallback_30c2e0(uint32_t id);
uint32_t opencfw_em9305_dispatch_332394(uintptr_t request,uintptr_t input)
{
 (void)input;
 volatile uint8_t *mask=(volatile uint8_t *)(uintptr_t)0x8056e8u;
 volatile uint8_t *message=(volatile uint8_t *)request;
 uint32_t kind=message[2];
 uintptr_t packet;
 if(kind==17u) {
  if((mask[10]&0x80u)==0u) return 0u;
  packet=opencfw_em9305_ll_event_allocate(87u,2u);
  if(packet==0u) return 0u;
  *(volatile uint8_t *)packet=message[4];
  *(volatile uint8_t *)(packet+1u)=message[5];
 } else if(kind==12u) {
  if((mask[5]&0x80u)==0u) return 0u;
  packet=opencfw_em9305_ll_event_allocate(48u,3u);
  if(packet==0u) return 0u;
  *(volatile uint8_t *)packet=message[4];
  *(volatile uint8_t *)(packet+1u)=message[6];
  *(volatile uint8_t *)(packet+2u)=message[7];
 } else if(kind==13u) {
  if((mask[16]&0x10u)==0u || (mask[7]&0x20u)==0u)
   packet=0u;
  else packet=opencfw_em9305_ll_event_allocate(62u,13u);
  if(packet==0u) {
   (void)opencfw_em9305_ll_event_fallback_30c2e0(*(volatile uint16_t *)(request+4u));
   return 0u;
  }
  *(volatile uint8_t *)packet=5u;
  *(volatile uint8_t *)(packet+1u)=message[4];
  *(volatile uint8_t *)(packet+2u)=message[5];
  (void)opencfw_em9305_memcpy((void *)(packet+3u),(const void *)(request+6u),8u);
  *(volatile uint8_t *)(packet+11u)=message[14];
  *(volatile uint8_t *)(packet+12u)=message[15];
 } else if(kind==11u) {
  uint32_t extended=mask[11]&2u;
  if(extended==0u && (mask[0]&0x80u)==0u) return 0u;
  packet=opencfw_em9305_ll_event_allocate(extended!=0u?89u:8u,extended!=0u?5u:4u);
  if(packet==0u) return 0u;
  uint8_t first=message[4];
  if(extended!=0u) message[9]=1u;
  *(volatile uint8_t *)packet=first;
  *(volatile uint8_t *)(packet+1u)=message[6];
  *(volatile uint8_t *)(packet+2u)=message[7];
  *(volatile uint8_t *)(packet+3u)=message[8];
  if(extended!=0u) *(volatile uint8_t *)(packet+4u)=message[9];
 } else return 0u;
 (void)opencfw_em9305_ll_event_send(packet-2u);
 return 1u;
}

/* Native30c2e0..30c33a: validate controller slot and enqueue four-byte command.
 * The three slot accessors retain their native contracts and are unresolved. */
extern uint32_t opencfw_em9305_ll_slot_active_30731c(uint32_t id);
extern uint32_t opencfw_em9305_ll_slot_state_306fdc(uint32_t id);
extern uint32_t opencfw_em9305_ll_slot_flag_307480(uint32_t id,uint32_t mask);
uint32_t opencfw_em9305_ll_event_fallback_30c2e0(uint32_t id)
{
 uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
 if(id>=*(volatile uint8_t *)(config+34u)) return 2u;
 if(opencfw_em9305_ll_slot_active_30731c(id)==0u) return 2u;
 if(opencfw_em9305_ll_slot_state_306fdc(id)!=1u) return 12u;
 if(opencfw_em9305_ll_slot_flag_307480(id,2u)==0u) return 12u;
 uintptr_t message=opencfw_em9305_wsf_event_allocate(4u);
 if(message!=0u) {
  *(volatile uint16_t *)(message+2u)=0x1a01u;
  uint32_t handler=*(volatile uint8_t *)(uintptr_t)0x805b18u;
  *(volatile uint16_t *)message=(uint16_t)id;
  (void)opencfw_em9305_wsf_task_message_send(handler,message);
 }
 return 0u;
}

/* Native306fdc/30731c/307480 use MPYUW (major4/minor0x1f), not
 * the distinct private major6 products. Preserve the named ISA operation. */
static uint32_t opencfw_em9305_slot_offset(uint32_t id)
{
 uint32_t offset;
 __asm__ volatile("mpyuw %0,%1,912" : "=r"(offset) : "r"(id));
 return offset;
}
/* Native30731c..30732e: return slot byte0 after pointer reload. */
uint32_t opencfw_em9305_ll_slot_active_30731c(uint32_t id)
{
 uintptr_t slots=*(volatile uint32_t *)(uintptr_t)0x805c70u;
 uint32_t offset=opencfw_em9305_slot_offset(id);
 return *(volatile uint8_t *)(slots+offset);
}
/* Native306fdc..306fee: return slot byte2, retaining multiply/read order. */
uint32_t opencfw_em9305_ll_slot_state_306fdc(uint32_t id)
{
 uint32_t offset=opencfw_em9305_slot_offset(id);
 uintptr_t slots=*(volatile uint32_t *)(uintptr_t)0x805c70u;
 return *(volatile uint8_t *)(slots+offset+2u);
}
/* Native307480..307498: boolean slot byte13 masked by incoming R1. */
uint32_t opencfw_em9305_ll_slot_flag_307480(uint32_t id,uint32_t mask)
{
 uint32_t offset=opencfw_em9305_slot_offset(id);
 uintptr_t slots=*(volatile uint32_t *)(uintptr_t)0x805c70u;
 return ((uint32_t)*(volatile uint8_t *)(slots+offset+13u)&mask)!=0u;
}

/* Native30e054..30e0d4: preserve id saved in BL delay slot before first child,
 * validate slot state and construct/send the thirty-byte task command. */
extern uint32_t opencfw_em9305_ll_slot_pending_307434(uint32_t id,uint32_t operation);
extern uint32_t opencfw_em9305_ll_slot_callback_3072f0(uint32_t id);
uint32_t opencfw_em9305_ll_command_30e054(uint32_t id,uintptr_t first,
                                       uint32_t value,uintptr_t second)
{
 if(opencfw_em9305_ll_slot_pending_307434(id,24u)!=0u) return 12u;
 if(opencfw_em9305_ll_slot_callback_3072f0(id)!=0u) return 12u;
 uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
 if(id>=*(volatile uint8_t *)(config+34u)) return 2u;
 if(opencfw_em9305_ll_slot_active_30731c(id)==0u) return 2u;
 if(opencfw_em9305_ll_slot_state_306fdc(id)!=0u) return 12u;
 uintptr_t message=opencfw_em9305_wsf_event_allocate(30u);
 if(message!=0u) {
  *(volatile uint16_t *)(message+2u)=0x1801u;
  *(volatile uint16_t *)message=(uint16_t)id;
  (void)opencfw_em9305_memcpy((void *)(message+4u),(const void *)first,8u);
  *(volatile uint16_t *)(message+12u)=(uint16_t)value;
  (void)opencfw_em9305_memcpy((void *)(message+14u),(const void *)second,16u);
  uint32_t handler=*(volatile uint8_t *)(uintptr_t)0x805b18u;
  (void)opencfw_em9305_wsf_task_message_send(handler,message);
 }
 return 0u;
}

/* Native3072f0..30730c: LD.AS scales204 words to816 bytes; optional
 * slot callback receives the original id and its return is forwarded. */
uint32_t opencfw_em9305_ll_slot_callback_3072f0(uint32_t id)
{
 uint32_t offset=opencfw_em9305_slot_offset(id);
 uintptr_t slots=*(volatile uint32_t *)(uintptr_t)0x805c70u;
 uintptr_t callback=*(volatile uint32_t *)(slots+offset+816u);
 if(callback==0u) return 0u;
 return ((uint32_t (*)(uint32_t))callback)(id);
}
/* Source-owned operation-to-pending-bit mapping, native ROM334479..334488.
 * Product data, not executable instructions. Bound to authenticated EM image
 * by slot-pending-map-receipt.json; only indices0..14 are permitted. */
static const uint8_t opencfw_em9305_slot_pending_map[15]={
 17u,1u,0u,19u,1u,1u,2u,3u,1u,1u,4u,21u,5u,6u,7u
};
/* Native307434..307480: sparse operation filter then code or pending-bit test. */
uint32_t opencfw_em9305_ll_slot_pending_307434(uint32_t id,uint32_t operation)
{
 uint32_t index=operation-21u;
 if(index>14u) return 0u;
 if(((0x7ccfu>>index)&1u)==0u) return 0u;
 uint32_t offset=opencfw_em9305_slot_offset(id);
 uintptr_t slots=*(volatile uint32_t *)(uintptr_t)0x805c70u;
 uintptr_t slot=slots+offset;
 uint32_t code=opencfw_em9305_slot_pending_map[index];
 if(*(volatile uint8_t *)(slot+635u)==code) return 1u;
 uint32_t flags=*(volatile uint32_t *)(slot+644u); /* native LD.AS161 */
 return ((flags>>code)&1u)!=0u;
}

extern uint32_t opencfw_em9305_ll_flags_command_30d54c(uint32_t id,uintptr_t flags);
/* Native332490..3324e0: private command0xfff7 builds two normalized flags. */
uint32_t opencfw_em9305_dispatch_332490(uintptr_t request,uintptr_t input)
{
 uint32_t command=*(volatile uint16_t *)request;
 if(command!=0xfff7u) return 0u;
 uint8_t flags[2];
 flags[0]=*(volatile uint8_t *)(input+2u)!=0u;
 flags[1]=*(volatile uint8_t *)(input+3u)==1u;
 uint32_t id=*(volatile uint8_t *)input |
             ((uint32_t)*(volatile uint8_t *)(input+1u)<<8u);
 uint32_t status=opencfw_em9305_ll_flags_command_30d54c(id,(uintptr_t)flags);
 uintptr_t packet=opencfw_em9305_ll_response_allocate_32e428(1u,*(volatile uint16_t *)request);
 if(packet!=0u) {
  *(volatile uint8_t *)packet=(uint8_t)status;
  (void)opencfw_em9305_ll_event_send(packet-5u);
 }
 return 1u;
}

extern uint32_t opencfw_em9305_ll_data_command_30b644(uintptr_t input,uintptr_t output);
extern uint32_t opencfw_em9305_ll_pair_command_30e350(uint32_t id,uint32_t value);
extern uint32_t opencfw_em9305_ll_payload_command_30c33c(uint32_t id,uintptr_t input);
extern uint32_t opencfw_em9305_ll_query_command_30c6d4(uint32_t id,uintptr_t output);
/* Native332278..332394: private-first dispatch with five command response maps. */
uint32_t opencfw_em9305_dispatch_332278(uintptr_t request,uintptr_t input)
{
 if(opencfw_em9305_dispatch_332490(request,input)!=0u) return 1u;
 uint32_t command=*(volatile uint16_t *)request;
 uint32_t status=0u,id=0u,length;
 uintptr_t output=0u;
 if(command==0x2017u) {
  output=input+16u;
  opencfw_em9305_ll_data_command_30b644(input,output);
  length=17u;
 } else if(command==0x201bu || command==0x201au || command==0xc7cu || command==0xc7bu) {
  id=*(volatile uint8_t *)input |
     ((uint32_t)*(volatile uint8_t *)(input+1u)<<8u);
  if(command==0x201bu) status=opencfw_em9305_ll_event_fallback_30c2e0(id);
  else if(command==0x201au) status=opencfw_em9305_ll_payload_command_30c33c(id,input+2u);
  else if(command==0xc7cu) {
   uint32_t value=*(volatile uint8_t *)(input+2u) |
                  ((uint32_t)*(volatile uint8_t *)(input+3u)<<8u);
   status=opencfw_em9305_ll_pair_command_30e350(id,value);
  }
  length=command==0xc7bu?5u:3u;
 } else return 0u;
 uintptr_t packet=opencfw_em9305_ll_response_allocate_32e428(length,*(volatile uint16_t *)request);
 if(packet==0u) return 1u;
 command=*(volatile uint16_t *)request; /* native reload after allocation */
 if(command==0x201au || command==0x201bu || command==0xc7cu) {
  *(volatile uint8_t *)(packet+1u)=(uint8_t)id;
  *(volatile uint8_t *)packet=(uint8_t)status;
  *(volatile uint8_t *)(packet+2u)=(uint8_t)(id>>8u);
 } else if(command==0xc7bu) {
  uint16_t value=0u;
  uint32_t result=opencfw_em9305_ll_query_command_30c6d4(id,(uintptr_t)&value);
  *(volatile uint8_t *)(packet+1u)=(uint8_t)id;
  *(volatile uint8_t *)(packet+3u)=(uint8_t)value;
  *(volatile uint8_t *)packet=(uint8_t)result;
  *(volatile uint8_t *)(packet+2u)=(uint8_t)(id>>8u);
  *(volatile uint8_t *)(packet+4u)=(uint8_t)(value>>8u);
 } else if(command==0x2017u) {
  *(volatile uint8_t *)packet=(uint8_t)status;
  (void)opencfw_em9305_memcpy((void *)(packet+1u),(const void *)output,16u);
 }
 (void)opencfw_em9305_ll_event_send(packet-5u);
 return 1u;
}

/* Native30c33c..30c3a4: state1 flag2 gate and twenty-byte task command. */
uint32_t opencfw_em9305_ll_payload_command_30c33c(uint32_t id,uintptr_t input)
{
 uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
 if(id>=*(volatile uint8_t *)(config+34u)) return 2u;
 if(opencfw_em9305_ll_slot_active_30731c(id)==0u) return 2u;
 if(opencfw_em9305_ll_slot_state_306fdc(id)!=1u) return 12u;
 if(opencfw_em9305_ll_slot_flag_307480(id,2u)==0u) return 12u;
 uintptr_t message=opencfw_em9305_wsf_event_allocate(20u);
 if(message!=0u) {
  *(volatile uint16_t *)(message+2u)=0x1901u;
  *(volatile uint16_t *)message=(uint16_t)id;
  (void)opencfw_em9305_memcpy((void *)(message+4u),(const void *)input,16u);
  uint32_t handler=*(volatile uint8_t *)(uintptr_t)0x805b18u;
  (void)opencfw_em9305_wsf_task_message_send(handler,message);
 }
 return 0u;
}
extern uint32_t opencfw_em9305_ll_slot_apply_308708(uint32_t id,uint32_t value);
/* Native30e350..30e38c: zero-value rejection, named MPYUW10 and child result. */
uint32_t opencfw_em9305_ll_pair_command_30e350(uint32_t id,uint32_t value)
{
 uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
 if(id>=*(volatile uint8_t *)(config+34u)) return 2u;
 if(opencfw_em9305_ll_slot_active_30731c(id)==0u) return 2u;
 if(value==0u) return 18u;
 uint32_t scaled;
 __asm__ volatile("mpyuw %0,%1,10" : "=r"(scaled) : "r"(value));
 return opencfw_em9305_ll_slot_apply_308708(id,scaled)!=0u?0u:30u;
}
/* Native306ea8..306ebc: slot word123→492-byte field. */
uint32_t opencfw_em9305_ll_slot_time_306ea8(uint32_t id)
{
 uint32_t offset=opencfw_em9305_slot_offset(id);
 uintptr_t slots=*(volatile uint32_t *)(uintptr_t)0x805c70u;
 return *(volatile uint32_t *)(slots+offset+492u);
}
/* Native30c6d4..30c714: named MPYDU outputs exactly R2/R3; retained
 * low>>22 | high<<10 arithmetic and sixteen-bit destination. */
uint32_t opencfw_em9305_ll_query_command_30c6d4(uint32_t id,uintptr_t output)
{
 uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
 if(id>=*(volatile uint8_t *)(config+34u)) return 2u;
 if(opencfw_em9305_ll_slot_active_30731c(id)==0u) return 2u;
 uint32_t time=opencfw_em9305_ll_slot_time_306ea8(id);
 register uint32_t low __asm__("r2");
 register uint32_t high __asm__("r3");
 __asm__ volatile("mpydu r2,%2,0x66667" : "=r"(low),"=r"(high) : "r"(time));
 *(volatile uint16_t *)output=(uint16_t)((low>>22u)|(high<<10u));
 return 0u;
}

/* Native30b644..30b654: resident cipher invocation with output/input alias. */
uint32_t opencfw_em9305_ll_data_command_30b644(uintptr_t input,uintptr_t output)
{
 (void)opencfw_em9305_radio_cipher_30ff0c(input,output,output);
 return 0u;
}
extern uint32_t opencfw_em9305_ll_slot_flags_apply_308b74(uint32_t id,uintptr_t flags);
/* Native30d54c..30d580: max/active validation and boolean child status map. */
uint32_t opencfw_em9305_ll_flags_command_30d54c(uint32_t id,uintptr_t flags)
{
 uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
 if(id>=*(volatile uint8_t *)(config+34u)) return 2u;
 if(opencfw_em9305_ll_slot_active_30731c(id)==0u) return 2u;
 return opencfw_em9305_ll_slot_flags_apply_308b74(id,flags)!=0u?0u:12u;
}
/* Native308b74..308ba8: latch two bytes only while the request flag is clear. */
uint32_t opencfw_em9305_ll_slot_flags_apply_308b74(uint32_t id,uintptr_t flags)
{
 uint32_t offset=opencfw_em9305_slot_offset(id);
 uintptr_t slots=*(volatile uint32_t *)(uintptr_t)0x805c70u;
 uintptr_t slot=slots+offset;
 uint32_t busy=*(volatile uint8_t *)(slot+514u);
 if(busy==0u) {
  uint32_t low=*(volatile uint8_t *)flags;
  uint32_t high=*(volatile uint8_t *)(flags+1u);
  *(volatile uint8_t *)(slot+514u)=1u;
  *(volatile uint16_t *)(slot+512u)=(uint16_t)(low|(high<<8u));
 }
 return busy==0u;
}

/* Native317c10..317c40: retain private config-product ISA through selected
 * adapter, arithmetic ASR bit pattern, remainder rounding and min-ten clamp. */
uint32_t opencfw_em9305_ll_slot_adjust_317c10(uintptr_t slot,uint32_t value)
{
 if(value<11u) return value;
 uint32_t first=*(volatile uint16_t *)(slot+260u);
 uint32_t second=*(volatile uint16_t *)(slot+266u);
 uint32_t product=opencfw_em9305_native_config_product(first+4u,second);
 uint32_t shifted=(product>>2u)|((product&0x80000000u)!=0u?0xc0000000u:0u);
 uint32_t offset=shifted+product;
 if((product&3u)!=0u) offset+=1u;
 if(offset>=value) return value;
 value-=offset;
 return value<10u?10u:value;
}
/* Native308708..308780: source arithmetic keeps compact named MPYUW/MPY
 * and private clock operations; no unqualified product substitution. */
uint32_t opencfw_em9305_ll_slot_apply_308708(uint32_t id,uint32_t value)
{
 uint32_t offset=opencfw_em9305_slot_offset(id);
 uintptr_t slots=*(volatile uint32_t *)(uintptr_t)0x805c70u;
 uintptr_t slot=slots+offset;
 uint32_t adjusted=opencfw_em9305_ll_slot_adjust_317c10(slot,value);
 if(adjusted==value) return 0u;
 register uint32_t factor __asm__("r3")=*(volatile uint16_t *)(slot+266u);
 register uint32_t product __asm__("r2")=*(volatile uint16_t *)(slot+846u);
 register uint32_t count __asm__("r1")=*(volatile uint16_t *)(slot+260u)+1u;
 __asm__ volatile("mpyuw_s r2,r2,r3" : "+r"(product) : "r"(factor));
 __asm__ volatile("mpy_s r2,r2,r1" : "+r"(product) : "r"(count));
 uint32_t requested=opencfw_em9305_native_clock_product(value,1000u);
 uint32_t minimum=opencfw_em9305_native_clock_product(product,1250u);
 if(requested<minimum) return 0u;
 uint32_t enabled=*(volatile uint8_t *)(slot+109u);
 *(volatile uint32_t *)(slot+472u)=adjusted;
 *(volatile uint32_t *)(slot+492u)=value;
 if(enabled!=0u) {
  (void)opencfw_em9305_wsf_timer_start_ms(slot+496u,value);
  uint32_t delay=*(volatile uint32_t *)(slot+472u);
  (void)opencfw_em9305_wsf_timer_start_ms(slot+476u,delay);
 }
 return 1u;
}

/* Native304648..304678: all eight ordered byte loads, R0/R1 uint64 ABI. */
uint64_t opencfw_em9305_ll_pack64_304648(uintptr_t input)
{
 volatile uint8_t *p=(volatile uint8_t *)input;
 uint32_t b1=p[1],b5=p[5],b2=p[2],b3=p[3];
 uint32_t b6=p[6],b7=p[7],b0=p[0],b4=p[4];
 uint32_t low=b0|(b1<<8u)|(b2<<16u)|(b3<<24u);
 uint32_t high=b4|(b5<<8u)|(b6<<16u)|(b7<<24u);
 return ((uint64_t)high<<32u)|low;
}
extern uint32_t opencfw_em9305_ll_mask_count_30c414(uint32_t low,uint32_t high);
/* Native30cf88..30d00c: pending/state gate, masked feature words and command. */
uint32_t opencfw_em9305_ll_mask_command_30cf88(uint32_t id,uintptr_t input)
{
 if(opencfw_em9305_ll_slot_pending_307434(id,22u)!=0u) return 12u;
 uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
 if(id>=*(volatile uint8_t *)(config+34u)) return 2u;
 if(opencfw_em9305_ll_slot_active_30731c(id)==0u) return 2u;
 if(opencfw_em9305_ll_slot_state_306fdc(id)!=0u) return 12u;
 uint64_t bits=opencfw_em9305_ll_pack64_304648(input);
 uint32_t allowed_low=*(volatile uint32_t *)(uintptr_t)0x805aa0u;
 uint32_t allowed_high=*(volatile uint32_t *)(uintptr_t)0x805aa4u;
 uint32_t low=(uint32_t)bits&allowed_low;
 uint32_t high=(uint32_t)(bits>>32u)&allowed_high;
 if(opencfw_em9305_ll_mask_count_30c414(low,high)<2u) return 18u;
 uintptr_t message=opencfw_em9305_wsf_event_allocate(12u);
 if(message!=0u) {
  *(volatile uint16_t *)(message+2u)=0x1601u;
  uint32_t handler=*(volatile uint8_t *)(uintptr_t)0x805b18u;
  *(volatile uint32_t *)(message+4u)=low;
  *(volatile uint16_t *)message=(uint16_t)id;
  *(volatile uint32_t *)(message+8u)=high;
  (void)opencfw_em9305_wsf_task_message_send(handler,message);
 }
 return 0u;
}
/* Native33052c..330568: LDB.AB advances the input before mask child call. */
uint32_t opencfw_em9305_dispatch_33052c(uintptr_t request,uintptr_t input)
{
 uint32_t command=*(volatile uint16_t *)request;
 if(command!=0xfff8u) return 0u;
 uint32_t id=*(volatile uint8_t *)input |
             ((uint32_t)*(volatile uint8_t *)(input+1u)<<8u);
 uint32_t status=opencfw_em9305_ll_mask_command_30cf88(id,input+2u);
 uintptr_t packet=opencfw_em9305_ll_response_allocate_32e428(1u,*(volatile uint16_t *)request);
 if(packet!=0u) {
  *(volatile uint8_t *)packet=(uint8_t)status;
  (void)opencfw_em9305_ll_event_send(packet-5u);
 }
 return 1u;
}
extern uint32_t opencfw_em9305_ll_stream_control_decode_332a78(uintptr_t output,uintptr_t input);
extern uint32_t opencfw_em9305_ll_stream_command_30b7ec(uintptr_t header,uintptr_t pairs,uintptr_t controls);
/* Native3305b0..330664: three-entry selection and twelve-byte control stride. */
uint32_t opencfw_em9305_dispatch_3305b0(uintptr_t request,uintptr_t input)
{
 if(opencfw_em9305_dispatch_33052c(request,input)!=0u) return 1u;
 if(*(volatile uint16_t *)request!=0x2043u)
  return opencfw_em9305_dispatch_330440(request,input);
 _Alignas(4) uint8_t header[12];
 _Alignas(4) uint8_t controls[36];
 uint16_t pairs[3][2];
 header[9]=255u;
 header[10]=255u;
 (void)opencfw_em9305_memset(controls,0u,36u);
 header[0]=*(volatile uint8_t *)input;
 header[1]=*(volatile uint8_t *)(input+1u);
 header[2]=*(volatile uint8_t *)(input+2u);
 uint32_t mask=*(volatile uint8_t *)(input+9u);
 *(uint32_t *)(void *)(header+4u)=(uint32_t)(input+3u);
 header[8]=(uint8_t)mask;
 uintptr_t cursor=input+10u;
 uint32_t entries=0u;
 for(uint32_t bit=0u;bit<8u && entries<3u;++bit) {
  if(((mask>>bit)&1u)==0u) continue;
  pairs[entries][0]=(uint16_t)(*(volatile uint8_t *)cursor |
                    ((uint32_t)*(volatile uint8_t *)(cursor+1u)<<8u));
  pairs[entries][1]=(uint16_t)(*(volatile uint8_t *)(cursor+2u) |
                    ((uint32_t)*(volatile uint8_t *)(cursor+3u)<<8u));
  uint32_t length=opencfw_em9305_ll_stream_control_decode_332a78(
                     (uintptr_t)(controls+12u*entries),cursor+4u);
  cursor+=length+4u;
  ++entries;
 }
 uint32_t status=opencfw_em9305_ll_stream_command_30b7ec((uintptr_t)header,
                             (uintptr_t)pairs,(uintptr_t)controls);
 (void)opencfw_em9305_ll_status_event_331bf8(request,status);
 return 1u;
}

/* Native 0x332a78..0x332aba: six little-endian halfwords, high byte
 * loaded before low byte in each pair; the final store is the return delay
 * slot. The native record consumes exactly twelve input bytes. */
uint32_t opencfw_em9305_ll_stream_control_decode_332a78(uintptr_t output,uintptr_t input)
{
 for(uint32_t offset=0;offset<12;offset+=2) {
  uint32_t high=*(volatile uint8_t *)(input+offset+1);
  uint32_t low=*(volatile uint8_t *)(input+offset);
  *(volatile uint16_t *)(output+offset)=(uint16_t)((high<<8)+low);
 }
 return 12;
}

/* Native30e510..30e524: latch companion only when the first byte is clear. */
uint32_t opencfw_em9305_ll_stream_gate_30e510(void)
{
 uint32_t busy=*(volatile uint8_t *)(uintptr_t)0x805a9eu;
 if(busy==0u) *(volatile uint8_t *)(uintptr_t)0x805a9fu=1u;
 return busy==0u;
}
/* Native318200..31825c: negative controller word enables active slot scan. */
uint32_t opencfw_em9305_ll_stream_address_busy_318200(uint32_t kind,uint32_t low,uint32_t high)
{
 uint32_t enabled=*(volatile uint32_t *)(uintptr_t)0x805a88u;
 if((enabled&0x80000000u)==0u) return 0u;
 uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
 uint32_t count=*(volatile uint8_t *)(config+34u);
 if(count==0u) return 0u;
 uintptr_t slot=*(volatile uint32_t *)(uintptr_t)0x805c70u;
 for(uint32_t i=0u;i<count;++i,slot+=912u) {
  if(*(volatile uint8_t *)slot==0u) continue;
  uint32_t shigh=*(volatile uint32_t *)(slot+520u);
  uint32_t slow=*(volatile uint32_t *)(slot+516u);
  if(((shigh^high)|(slow^low))!=0u) continue;
  if(*(volatile uint8_t *)(slot+524u)==kind) return 1u;
 }
 return 0u;
}
extern uint32_t opencfw_em9305_ll_stream_header_valid_332f04(uintptr_t);
extern uint32_t opencfw_em9305_ll_stream_control_valid_332f00(uintptr_t);
extern uint32_t opencfw_em9305_ll_stream_disable_307970(uint32_t);
extern uint32_t opencfw_em9305_ll_stream_enable_307a48(uint32_t);
extern uint32_t opencfw_em9305_ll_stream_configure_307a28(uint32_t,uintptr_t,uintptr_t);
/* Native30b7ec..30b974: guarded three-stream configuration and event265.
 * Selected bits use packed controls; bit1 intentionally has no pair checks.
 * Feature words are captured before the latch call, while header mask and
 * count bytes are reloaded at the native call/store boundaries. */
uint32_t opencfw_em9305_ll_stream_command_30b7ec(uintptr_t header,uintptr_t pairs,uintptr_t controls)
{
 uintptr_t state=0x805a70u;
 uint32_t feature_high=*(volatile uint32_t *)(state+40u);
 uint32_t feature_low=*(volatile uint32_t *)(state+36u);
 uint32_t gate=opencfw_em9305_ll_stream_gate_30e510();
 if(*(volatile uint8_t *)(state+4u)!=0u || gate==0u) return 12u;
 uint32_t mask=*(volatile uint8_t *)(header+8u);
 uint32_t allowed=1u|((feature_low>>7u)&2u)|((feature_low>>9u)&4u);
 if((allowed&mask)!=mask) return 17u;
 if(mask-1u>=7u) return 18u;
 if(opencfw_em9305_ll_stream_header_valid_332f04(header)==0u) return 18u;
 uint32_t flags=*(volatile uint8_t *)(uintptr_t)0x805a99u;
 uint32_t kind=*(volatile uint8_t *)header;
 if((flags&4u)==0u && kind>=2u) return 17u;
 uint32_t maxkind=(feature_high&(1u<<10u))!=0u?4u:1u;
 if(maxkind<kind) return 18u;
 uint32_t skipped=0u;
 for(uint32_t bit=0u;bit<3u;++bit) {
  mask=*(volatile uint8_t *)(header+8u);
  uint32_t packed=bit-skipped;
  if((mask&(1u<<bit))==0u) { ++skipped; continue; }
  if(opencfw_em9305_ll_stream_control_valid_332f00(controls+packed*12u)!=0u) return 18u;
  if(bit==1u) continue;
  uintptr_t pair=pairs+packed*4u;
  uint32_t second=*(volatile uint16_t *)(pair+2u);
  uint32_t first=*(volatile uint16_t *)pair;
  if(first<second || second<4u) return 18u;
 }
 uint32_t packed=0u;
 mask=*(volatile uint8_t *)(header+8u);
 *(volatile uint8_t *)(state+12u)=0u;
 if((mask&1u)==0u) {
  (void)opencfw_em9305_ll_stream_disable_307970(0u);
  (void)opencfw_em9305_ll_stream_configure_307a28(0u,0u,controls);
 } else {
  (void)opencfw_em9305_ll_stream_enable_307a48(0u);
  uint32_t count=*(volatile uint8_t *)(state+12u);
  *(volatile uint8_t *)(state+12u)=(uint8_t)(count+1u);
  (void)opencfw_em9305_ll_stream_configure_307a28(0u,pairs,controls);
  packed=1u;
 }
 mask=*(volatile uint8_t *)(header+8u);
 if((mask&2u)==0u) {
  (void)opencfw_em9305_ll_stream_configure_307a28(1u,0u,controls);
 } else {
  uint32_t offset;
  __asm__ volatile("mpyuw %0,%1,12":"=r"(offset):"r"(packed));
  (void)opencfw_em9305_ll_stream_configure_307a28(1u,0u,controls+offset);
  ++packed;
 }
 mask=*(volatile uint8_t *)(header+8u);
 if((mask&4u)==0u) {
  (void)opencfw_em9305_ll_stream_disable_307970(2u);
  (void)opencfw_em9305_ll_stream_configure_307a28(2u,0u,controls);
 } else {
  (void)opencfw_em9305_ll_stream_enable_307a48(2u);
  uint32_t count=*(volatile uint8_t *)(state+12u);
  *(volatile uint8_t *)(state+12u)=(uint8_t)(count+1u);
  (void)opencfw_em9305_ll_stream_configure_307a28(2u,pairs+packed*4u,controls+packed*12u);
 }
 uint64_t address=opencfw_em9305_controller_pack_address(*(volatile uint32_t *)(header+4u));
 kind=*(volatile uint8_t *)header;
 if(kind==0u && opencfw_em9305_ll_stream_address_busy_318200(
      *(volatile uint8_t *)(header+2u),(uint32_t)address,(uint32_t)(address>>32u))!=0u) return 11u;
 uintptr_t message=opencfw_em9305_wsf_event_allocate(20u);
 if(message==0u) return 0u;
 *(volatile uint32_t *)(message+8u)=(uint32_t)address;
 *(volatile uint32_t *)(message+12u)=(uint32_t)(address>>32u);
 *(volatile uint16_t *)(message+2u)=265u;
 *(volatile uint16_t *)(message+4u)=*(volatile uint16_t *)header;
 uint32_t value=*(volatile uint8_t *)(header+2u);
 mask=*(volatile uint8_t *)(header+8u);
 uint32_t handler=*(volatile uint8_t *)(uintptr_t)0x805b18u;
 *(volatile uint8_t *)(message+6u)=(uint8_t)value;
 *(volatile uint8_t *)(message+16u)=(uint8_t)mask;
 (void)opencfw_em9305_wsf_task_message_send(handler,message);
 return 0u;
}

/* Native30e4dc..30e510: literal kind policy and runtime capability byte. */
uint32_t opencfw_em9305_ll_stream_kind_valid_30e4dc(uint32_t kind)
{
 if(kind==0u || kind==2u || kind==255u) return 1u;
 if(kind==1u || kind==3u)
  return *(volatile uint8_t *)(uintptr_t)0x805a81u!=0u;
 return 0u;
}
/* Native332f04..332f3c: capability width and header kind gate. */
uint32_t opencfw_em9305_ll_stream_header_valid_332f04(uintptr_t header)
{
 uint32_t flags=*(volatile uint8_t *)(uintptr_t)0x805a94u;
 uint32_t first=*(volatile uint8_t *)(header+1u);
 uint32_t maximum=(flags&64u)!=0u?3u:1u;
 if(maximum<first) return 0u;
 uint32_t second=*(volatile uint8_t *)(header+2u);
 if(maximum<second) return 0u;
 if(*(volatile uint8_t *)header>=5u) return 0u;
 return opencfw_em9305_ll_stream_kind_valid_30e4dc(first)!=0u;
}
/* Native30a6b4..30a70c and tail332f00: private product ISA is preserved
 * by the already selected native operation adapters; no guessed scaling. */
uint32_t opencfw_em9305_ll_stream_control_valid_332f00(uintptr_t control)
{
 uint32_t first=*(volatile uint16_t *)control;
 if(first<6u) return 18u;
 uint32_t second=*(volatile uint16_t *)(control+2u);
 if(second<first || second<6u || second>3200u || first>3200u) return 18u;
 uint32_t latency=*(volatile uint16_t *)(control+4u);
 if(latency>499u) return 18u;
 uint32_t timeout=*(volatile uint16_t *)(control+6u);
 uint32_t product=opencfw_em9305_native_config_product(latency+1u,second);
 uint32_t scaled;
 __asm__ volatile("mpyuw %0,%1,%2":"=r"(scaled):"r"(10000u),"r"(timeout));
 uint32_t limit=opencfw_em9305_native_clock_product(product,2500u);
 return timeout>3200u || timeout<10u || scaled<=limit?18u:0u;
}
/* Native3357a8..3357b4: three nonexecutecutable runtime record pointers.
 * Their 704-byte RAM records remain runtime/data ownership frontiers. */
static const uint32_t opencfw_em9305_stream_record_addresses[3]={0x802d20u,0x802fe0u,0x8032a0u};
/* Native307970..307980 and307a48..307a58: latch bit clear/set. */
uint32_t opencfw_em9305_ll_stream_disable_307970(uint32_t bit)
{
 uint32_t value=*(volatile uint8_t *)(uintptr_t)0x802a5eu;
 value&=~(1u<<(bit&31u));
 *(volatile uint8_t *)(uintptr_t)0x802a5eu=(uint8_t)value;
 return value;
}
uint32_t opencfw_em9305_ll_stream_enable_307a48(uint32_t bit)
{
 uint32_t value=*(volatile uint8_t *)(uintptr_t)0x802a5eu;
 value|=1u<<(bit&31u);
 *(volatile uint8_t *)(uintptr_t)0x802a5eu=(uint8_t)value;
 return value;
}
/* Native307a28..307a48: optional pair copy then exact twelve-byte memcpy. */
uint32_t opencfw_em9305_ll_stream_configure_307a28(uint32_t index,uintptr_t pair,uintptr_t control)
{
 uintptr_t record=opencfw_em9305_stream_record_addresses[index];
 if(pair!=0u) {
  uint32_t second=*(volatile uint16_t *)(pair+2u);
  uint32_t first=*(volatile uint16_t *)pair;
  *(volatile uint16_t *)(record+22u)=(uint16_t)second;
  *(volatile uint16_t *)(record+20u)=(uint16_t)first;
 }
 return (uint32_t)(uintptr_t)opencfw_em9305_memcpy((void *)(record+24u),(const void *)control,12u);
}

extern uint32_t opencfw_em9305_ll_connection_begin_30b480(uintptr_t,uintptr_t);
extern void opencfw_em9305_ll_connection_cancel_30b53c(uintptr_t);
extern uint32_t opencfw_em9305_ll_connection_update_30cf40(uintptr_t);
/* Native330440..3304f0: legacy connection dispatcher. Stack padding is
 * deliberately not initialized: only native named fields are populated. */
uint32_t opencfw_em9305_dispatch_330440(uintptr_t request,uintptr_t input)
{
 if(opencfw_em9305_dispatch_33052c(request,input)!=0u) return 1u;
 uint32_t command=*(volatile uint16_t *)request;
 if(command==0x200du) {
  _Alignas(4) uint8_t header[12];
  uint16_t control[6];
  uint32_t b1=*(volatile uint8_t *)(input+1u);
  uint32_t b3=*(volatile uint8_t *)(input+3u);
  uint32_t b12=*(volatile uint8_t *)(input+12u);
  uint32_t b0=*(volatile uint8_t *)input;
  uint32_t b2=*(volatile uint8_t *)(input+2u);
  uint32_t b4=*(volatile uint8_t *)(input+4u);
  uint32_t b5=*(volatile uint8_t *)(input+5u);
  header[5]=(uint8_t)b12;
  *(uint32_t *)(void *)(header+8u)=(uint32_t)(input+6u);
  header[4]=(uint8_t)b4;
  header[6]=(uint8_t)b5;
  *(uint16_t *)(void *)header=(uint16_t)(b0+(b1<<8u));
  *(uint16_t *)(void *)(header+2u)=(uint16_t)(b2+(b3<<8u));
  (void)opencfw_em9305_ll_stream_control_decode_332a78((uintptr_t)control,input+13u);
  uint32_t status=opencfw_em9305_ll_connection_begin_30b480((uintptr_t)header,(uintptr_t)control);
  (void)opencfw_em9305_ll_status_event_331bf8(request,status);
  return 1u;
 }
 if(command==0x2014u) {
  uint32_t status=opencfw_em9305_ll_connection_update_30cf40(input);
  uintptr_t packet=opencfw_em9305_ll_response_allocate_32e428(1u,*(volatile uint16_t *)request);
  if(packet!=0u) {
   if(*(volatile uint16_t *)request==0x2014u) *(volatile uint8_t *)packet=(uint8_t)status;
   (void)opencfw_em9305_ll_event_send(packet-5u);
  }
  return 1u;
 }
 if(command==0x200eu) {
  opencfw_em9305_ll_connection_cancel_30b53c(input);
  return 1u;
 }
 return opencfw_em9305_dispatch_32ef10(request,input);
}
/* Native30e524..30e538: inverse companion latch to30e510. */
uint32_t opencfw_em9305_ll_connection_gate_30e524(void)
{
 uint32_t busy=*(volatile uint8_t *)(uintptr_t)0x805a9fu;
 if(busy==0u) *(volatile uint8_t *)(uintptr_t)0x805a9eu=1u;
 return busy==0u;
}
/* Native30b480..30b53c: validated legacy request, exact sparse message259. */
uint32_t opencfw_em9305_ll_connection_begin_30b480(uintptr_t header,uintptr_t control)
{
 uint32_t flags=*(volatile uint32_t *)(uintptr_t)0x805a94u;
 uintptr_t address_pointer=*(volatile uint32_t *)(header+8u);
 uint32_t maximum=(flags&64u)!=0u?3u:1u;
 uint64_t address=opencfw_em9305_controller_pack_address(address_pointer);
 if(opencfw_em9305_ll_connection_gate_30e524()==0u) return 12u;
 uint32_t first=*(volatile uint16_t *)header;
 if(first>=0x4001u) return 18u;
 uint32_t second=*(volatile uint16_t *)(header+2u);
 if(first<second || second<4u) return 18u;
 uint32_t mode=*(volatile uint8_t *)(header+4u);
 if(mode>=3u) return 18u;
 if(mode==0u && maximum<*(volatile uint8_t *)(header+6u)) return 18u;
 if(maximum<*(volatile uint8_t *)(header+5u)) return 18u;
 if(opencfw_em9305_ll_stream_control_valid_332f00(control)!=0u) return 18u;
 if(opencfw_em9305_ll_stream_kind_valid_30e4dc(*(volatile uint8_t *)(header+5u))==0u) return 18u;
 if(opencfw_em9305_ll_stream_address_busy_318200(*(volatile uint8_t *)(header+6u),
         (uint32_t)address,(uint32_t)(address>>32u))!=0u) return 11u;
 uintptr_t message=opencfw_em9305_wsf_event_allocate(36u);
 if(message==0u) return 0u;
 *(volatile uint16_t *)(message+2u)=259u;
 (void)opencfw_em9305_memcpy((void *)(message+4u),(const void *)control,12u);
 *(volatile uint32_t *)(message+28u)=(uint32_t)(address>>32u);
 *(volatile uint32_t *)(message+24u)=(uint32_t)address;
 uint32_t pair=*(volatile uint32_t *)header;
 uint32_t handler=*(volatile uint8_t *)(uintptr_t)0x805b18u;
 *(volatile uint32_t *)(message+16u)=pair;
 uint32_t address_kind=*(volatile uint8_t *)(header+6u);
 uint32_t local_kind=*(volatile uint8_t *)(header+5u);
 mode=*(volatile uint8_t *)(header+4u);
 *(volatile uint8_t *)(message+32u)=(uint8_t)address_kind;
 *(volatile uint8_t *)(message+21u)=(uint8_t)local_kind;
 *(volatile uint8_t *)(message+22u)=(uint8_t)mode;
 (void)opencfw_em9305_wsf_task_message_send(handler,message);
 return 0u;
}
/* Native30b53c..30b570: no result consumed by the selected dispatcher. */
void opencfw_em9305_ll_connection_cancel_30b53c(uintptr_t input)
{
 (void)input;
 uintptr_t message=opencfw_em9305_wsf_event_allocate(4u);
 if(message==0u) return;
 uint32_t pending=*(volatile uint8_t *)(uintptr_t)0x805a9fu;
 uint32_t handler=*(volatile uint8_t *)(uintptr_t)0x805b18u;
 *(volatile uint8_t *)(message+3u)=2u;
 *(volatile uint8_t *)(message+2u)=(uint8_t)(pending!=0u?9u:3u);
 (void)opencfw_em9305_wsf_task_message_send(handler,message);
}
/* Native3087a0..3087ec: publish words, visit each registered callback,
 * retaining the first result with a nonzero low byte; count is reloaded. */
uint32_t opencfw_em9305_ll_connection_mask_apply_3087a0(uint32_t low,uint32_t high)
{
 uint32_t count=*(volatile uint8_t *)(uintptr_t)0x8027ccu;
 *(volatile uint32_t *)(uintptr_t)0x805aa4u=high;
 *(volatile uint32_t *)(uintptr_t)0x805aa0u=low;
 if(count==0u) return 0u;
 uintptr_t cursor=0x8027d0u;
 uint32_t first=0u,index=0u;
 do {
  uintptr_t callback=*(volatile uint32_t *)cursor;
  cursor+=4u;
  uint32_t result=((uint32_t (*)(uint32_t,uint32_t))callback)(low,high);
  count=*(volatile uint8_t *)(uintptr_t)0x8027ccu;
  ++index;
  if((first&255u)==0u) first=result;
 } while(index<count);
 return first&255u;
}
/* Native30cf40..30cf88: the unsigned MAC byte terms do not overlap;
 * b0+b1*256+b2*65536+b3*16777216 is bounded by UINT32_MAX,
 * so the native add/adc high contribution is zero before b4 is added.
 * The native count operation remains an explicit real provider. */
uint32_t opencfw_em9305_ll_connection_update_30cf40(uintptr_t input)
{
 uint32_t b0=*(volatile uint8_t *)input;
 uint32_t b1=*(volatile uint8_t *)(input+1u);
 uint32_t b2=*(volatile uint8_t *)(input+2u);
 uint32_t b3=*(volatile uint8_t *)(input+3u);
 uint32_t b4=*(volatile uint8_t *)(input+4u);
 uint32_t low=b0+(b1<<8u)+(b2<<16u)+(b3<<24u);
 uint32_t high=b4;
 if(opencfw_em9305_ll_mask_count_30c414(low,high)<2u) return 18u;
 if(high>=32u) return 18u;
 return opencfw_em9305_ll_connection_mask_apply_3087a0(low,high);
}
extern uint32_t opencfw_em9305_dispatch_32f494(uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_ll_connection_parameters_30b1b0(uint32_t,uintptr_t);
extern uint32_t opencfw_em9305_ll_connection_query_30cb28(uint32_t);
extern uint32_t opencfw_em9305_ll_connection_read_30c860(uint32_t);
extern uint32_t opencfw_em9305_ll_connection_modify_30c998(uint32_t,uintptr_t);
extern uint32_t opencfw_em9305_ll_connection_mode_30c944(uint32_t,uint32_t);
extern uint32_t opencfw_em9305_ll_connection_times_30d3c4(uint32_t,uint32_t,uint32_t);
extern uint32_t opencfw_em9305_ll_connection_value_30e38c(uint32_t,uint32_t);
extern uint32_t opencfw_em9305_ll_connection_disconnect_30b570(uint32_t,uint32_t);
extern uint32_t opencfw_em9305_ll_connection_action_30c8c8(uint32_t);
extern uint32_t opencfw_em9305_ll_connection_response_32f34c(uintptr_t,uint32_t,uint32_t,uintptr_t,uint32_t);
/* Native32ef10..32f0a0: exact command table destinations, decoded control
 * records and distinct status-event vs command-response paths. */
uint32_t opencfw_em9305_dispatch_32ef10(uintptr_t request,uintptr_t input)
{
 if(opencfw_em9305_dispatch_32f494(request,input)!=0u) return 1u;
 uint32_t command=*(volatile uint16_t *)request;
 uint32_t status=0u,length=0u,id=0u;
 uintptr_t payload=0u;
 if(command==0x2013u || command==0x2020u) {
  uint16_t control[6];
  uint32_t low=*(volatile uint8_t *)input;
  uint32_t high=*(volatile uint8_t *)(input+1u);
  (void)opencfw_em9305_ll_stream_control_decode_332a78((uintptr_t)control,input+2u);
  id=(uint16_t)(low+(high<<8u));
  if(command==0x2013u) {
   status=opencfw_em9305_ll_connection_parameters_30b1b0(id,(uintptr_t)control);
   (void)opencfw_em9305_ll_status_event_331bf8(request,status);
   return 1u;
  }
  status=opencfw_em9305_ll_connection_modify_30c998(id,(uintptr_t)control);
  length=3u;
 } else if(command==0x206du || command==0x2016u || command==0x041du) {
  uint32_t high=*(volatile uint8_t *)(input+1u);
  uint32_t low=*(volatile uint8_t *)input;
  id=(uint16_t)(low+(high<<8u));
  if(command==0x206du) status=opencfw_em9305_ll_connection_query_30cb28(id);
  else if(command==0x2016u) status=opencfw_em9305_ll_connection_read_30c860(id);
  else status=opencfw_em9305_ll_connection_action_30c8c8(id);
  (void)opencfw_em9305_ll_status_event_331bf8(request,status);
  return 1u;
 } else if(command==0x2021u || command==0x0406u) {
  uint32_t high=*(volatile uint8_t *)(input+1u);
  uint32_t low=*(volatile uint8_t *)input;
  uint32_t value=*(volatile uint8_t *)(input+2u);
  id=(uint16_t)(low+(high<<8u));
  if(command==0x0406u) {
   status=opencfw_em9305_ll_connection_disconnect_30b570(id,value);
   (void)opencfw_em9305_ll_status_event_331bf8(request,status);
   return 1u;
  }
  status=opencfw_em9305_ll_connection_mode_30c944(id,value);
  length=3u;
 } else if(command==0x2022u) {
  uint32_t b0=*(volatile uint8_t *)input;
  uint32_t b1=*(volatile uint8_t *)(input+1u);
  uint32_t b2=*(volatile uint8_t *)(input+2u);
  uint32_t b3=*(volatile uint8_t *)(input+3u);
  uint32_t b4=*(volatile uint8_t *)(input+4u);
  uint32_t b5=*(volatile uint8_t *)(input+5u);
  id=(uint16_t)(b0+(b1<<8u));
  status=opencfw_em9305_ll_connection_times_30d3c4(id,(uint16_t)(b2+(b3<<8u)),(uint16_t)(b4+(b5<<8u)));
  length=3u;
 } else if(command==0x2024u) {
  uint32_t b1=*(volatile uint8_t *)(input+1u);
  uint32_t b3=*(volatile uint8_t *)(input+3u);
  uint32_t b0=*(volatile uint8_t *)input;
  uint32_t b2=*(volatile uint8_t *)(input+2u);
  status=opencfw_em9305_ll_connection_value_30e38c((uint16_t)(b0+(b1<<8u)),(uint16_t)(b2+(b3<<8u)));
  length=1u;
 } else if(command==0x2015u || command==0x1405u || command==0x0c2du) {
  uint32_t low=*(volatile uint8_t *)input;
  uint32_t high=*(volatile uint8_t *)(input+1u);
  id=(uint16_t)(low+(high<<8u));
  length=command==0x2015u?8u:4u;
  if(command==0x0c2du) payload=input+2u;
 } else if(command==0x2023u) length=5u;
 else if(command==0x202fu) length=9u;
 else return 0u;
 (void)opencfw_em9305_ll_connection_response_32f34c(request,status,length,payload,id);
 return 1u;
}
extern uint32_t opencfw_em9305_ll_connection_limits_30c714(uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_ll_connection_capabilities_30c78c(uintptr_t,uintptr_t,uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_ll_connection_remote_features_30bbbc(uint32_t,uintptr_t);
extern uint32_t opencfw_em9305_ll_connection_version_30beb4(uint32_t,uint32_t,uintptr_t);
extern uint32_t opencfw_em9305_ll_connection_quality_30be68(uint32_t,uintptr_t);
/* Native32f34c..32f494: allocation precedes command reload and routing.
 * Unmatched commands send the allocator-owned payload without writes. */
uint32_t opencfw_em9305_ll_connection_response_32f34c(uintptr_t request,uint32_t status,uint32_t length,uintptr_t input,uint32_t id)
{
 uintptr_t packet=opencfw_em9305_ll_response_allocate_32e428(length,*(volatile uint16_t *)request);
 if(packet==0u) return 0u;
 uint32_t command=*(volatile uint16_t *)request;
 if((command>=0x2020u && command<=0x2022u) ||
    (command>=0x205au && command<=0x205cu)) {
  *(volatile uint8_t *)(packet+1u)=(uint8_t)id;
  *(volatile uint8_t *)packet=(uint8_t)status;
  *(volatile uint8_t *)(packet+2u)=(uint8_t)(id>>8u);
 } else if(command==0x2023u) {
  uint8_t info[2];uint16_t limit;
  (void)opencfw_em9305_ll_connection_limits_30c714((uintptr_t)info,(uintptr_t)&limit);
  *(volatile uint8_t *)packet=(uint8_t)status;
  *(volatile uint8_t *)(packet+1u)=info[0];
  uint32_t value=limit;uint32_t second=info[1];
  *(volatile uint8_t *)(packet+3u)=(uint8_t)value;
  *(volatile uint8_t *)(packet+2u)=(uint8_t)second;
  *(volatile uint8_t *)(packet+4u)=(uint8_t)(value>>8u);
 } else if(command==0x2015u) {
  uint32_t result=opencfw_em9305_ll_connection_remote_features_30bbbc(id,packet+3u);
  *(volatile uint8_t *)(packet+1u)=(uint8_t)id;
  *(volatile uint8_t *)(packet+2u)=(uint8_t)(id>>8u);
  *(volatile uint8_t *)packet=(uint8_t)result;
 } else if(command==0x2024u || command==0x2059u || command==0x205du) {
  *(volatile uint8_t *)packet=(uint8_t)status;
 } else if(command==0x0c2du || command==0x1405u) {
  uint8_t value;
  uint32_t result;
  if(command==0x0c2du) {
   value=0u;
   uint32_t selector=input!=0u?*(volatile uint8_t *)input:0u;
   result=opencfw_em9305_ll_connection_version_30beb4(id,selector,(uintptr_t)&value);
  } else result=opencfw_em9305_ll_connection_quality_30be68(id,(uintptr_t)&value);
  *(volatile uint8_t *)(packet+1u)=(uint8_t)id;
  *(volatile uint8_t *)packet=(uint8_t)result;
  *(volatile uint8_t *)(packet+2u)=(uint8_t)(id>>8u);
  *(volatile uint8_t *)(packet+3u)=value;
 } else if(command==0x202fu) {
  uint8_t info[2];uint16_t first,second,third;
  (void)opencfw_em9305_ll_connection_capabilities_30c78c((uintptr_t)info,
      (uintptr_t)&first,(uintptr_t)&second,(uintptr_t)&third);
  *(volatile uint8_t *)packet=(uint8_t)status;
  *(volatile uint8_t *)(packet+1u)=info[0];
  uint32_t a=first,b=second,c=third,d=info[1];
  *(volatile uint8_t *)(packet+3u)=(uint8_t)a;
  *(volatile uint8_t *)(packet+5u)=(uint8_t)b;
  *(volatile uint8_t *)(packet+7u)=(uint8_t)c;
  *(volatile uint8_t *)(packet+2u)=(uint8_t)d;
  *(volatile uint8_t *)(packet+4u)=(uint8_t)(a>>8u);
  *(volatile uint8_t *)(packet+6u)=(uint8_t)(b>>8u);
  *(volatile uint8_t *)(packet+8u)=(uint8_t)(c>>8u);
 }
 return opencfw_em9305_ll_event_send(packet-5u);
}
/* Native30c714..30c724: two ordered halfword copies, second in return slot. */
uint32_t opencfw_em9305_ll_connection_limits_30c714(uintptr_t info,uintptr_t limit)
{
 uint32_t first=*(volatile uint16_t *)(uintptr_t)0x805ab6u;
 *(volatile uint16_t *)info=(uint16_t)first;
 uint32_t second=*(volatile uint16_t *)(uintptr_t)0x805ab8u;
 *(volatile uint16_t *)limit=(uint16_t)second;
 return second;
}
/* Native30c78c..30c7b0: ADD1 shifts its third operand, giving +112.
 * The output reloads are intentional and preserve aliased destinations. */
uint32_t opencfw_em9305_ll_connection_capabilities_30c78c(uintptr_t info,uintptr_t first,uintptr_t second,uintptr_t third)
{
 uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
 uint32_t size=*(volatile uint16_t *)(config+38u);
 if(size>251u) size=251u;
 *(volatile uint16_t *)info=(uint16_t)size;
 *(volatile uint16_t *)first=(uint16_t)((size<<3u)+112u);
 uint32_t value=*(volatile uint16_t *)info;
 *(volatile uint16_t *)second=(uint16_t)value;
 value=*(volatile uint16_t *)first;
 *(volatile uint16_t *)third=(uint16_t)value;
 return value;
}
/* Native306ff0..307008 and307030..307044: signed byte result, named stride. */
uint32_t opencfw_em9305_ll_connection_quality_byte_306ff0(uint32_t id)
{
 uint32_t offset;
 __asm__ volatile("mpyuw %0,%1,912":"=r"(offset):"r"(id));
 uintptr_t slots=*(volatile uint32_t *)(uintptr_t)0x805c70u;
 uint32_t value=*(volatile uint8_t *)(slots+offset+268u);
 return (value&128u)!=0u?value|0xffffff00u:value;
}
uint32_t opencfw_em9305_ll_connection_version_byte_307030(uint32_t id)
{
 uint32_t offset;
 __asm__ volatile("mpyuw %0,%1,912":"=r"(offset):"r"(id));
 uintptr_t slots=*(volatile uint32_t *)(uintptr_t)0x805c70u;
 uint32_t value=*(volatile uint8_t *)(slots+offset+66u);
 return (value&128u)!=0u?value|0xffffff00u:value;
}
/* Native30be68..30bea4: always writes the default0x7f on invalid link. */
uint32_t opencfw_em9305_ll_connection_quality_30be68(uint32_t id,uintptr_t output)
{
 (void)opencfw_em9305_wsf_critical_enter();
 uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
 uint32_t status=2u,value=127u;
 if(id<*(volatile uint8_t *)(config+34u) && opencfw_em9305_ll_slot_active_30731c(id)!=0u) {
  value=opencfw_em9305_ll_connection_quality_byte_306ff0(id);
  status=0u;
 }
 *(volatile uint8_t *)output=(uint8_t)value;
 (void)opencfw_em9305_wsf_critical_exit();
 return status;
}
/* Native30beb4..30bf04: invalid link/selector both write0xe2; selector1
 * writes literal20, selector0 returns the native signed slot byte. */
uint32_t opencfw_em9305_ll_connection_version_30beb4(uint32_t id,uint32_t selector,uintptr_t output)
{
 (void)opencfw_em9305_wsf_critical_enter();
 uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
 uint32_t status=2u,value=0xe2u;
 if(id<*(volatile uint8_t *)(config+34u) && opencfw_em9305_ll_slot_active_30731c(id)!=0u) {
  if(selector>=2u) status=18u;
  else {
   value=selector!=0u?20u:opencfw_em9305_ll_connection_version_byte_307030(id);
   status=0u;
  }
 }
 *(volatile uint8_t *)output=(uint8_t)value;
 (void)opencfw_em9305_wsf_critical_exit();
 return status;
}
/* Native306ebc..306ed4: paired ABI result from scaled word69/70 loads. */
uint64_t opencfw_em9305_ll_connection_feature_words_306ebc(uint32_t id)
{
 uint32_t offset;
 __asm__ volatile("mpyuw %0,%1,912":"=r"(offset):"r"(id));
 uintptr_t slots=*(volatile uint32_t *)(uintptr_t)0x805c70u;
 uint32_t low=*(volatile uint32_t *)(slots+offset+276u);
 uint32_t high=*(volatile uint32_t *)(slots+offset+280u);
 return ((uint64_t)high<<32u)|low;
}
/* Native30bbbc..30bc04: five-byte feature result, untouched on invalid link. */
uint32_t opencfw_em9305_ll_connection_remote_features_30bbbc(uint32_t id,uintptr_t output)
{
 (void)opencfw_em9305_wsf_critical_enter();
 uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
 uint32_t status=2u;
 if(id<*(volatile uint8_t *)(config+34u) && opencfw_em9305_ll_slot_active_30731c(id)!=0u) {
  uint64_t words=opencfw_em9305_ll_connection_feature_words_306ebc(id);
  uint32_t low=(uint32_t)words,high=(uint32_t)(words>>32u);
  *(volatile uint8_t *)(output+4u)=(uint8_t)high;
  *(volatile uint8_t *)output=(uint8_t)low;
  *(volatile uint8_t *)(output+3u)=(uint8_t)(low>>24u);
  *(volatile uint8_t *)(output+2u)=(uint8_t)(low>>16u);
  *(volatile uint8_t *)(output+1u)=(uint8_t)(low>>8u);
  status=0u;
 }
 (void)opencfw_em9305_wsf_critical_exit();
 return status;
}
extern uint32_t opencfw_em9305_ll_private_mask_30d378(uint32_t,uint32_t,uint32_t,uint32_t);
extern uint32_t opencfw_em9305_ll_private_radio_30d8fc(uint32_t,uint32_t,uint32_t);
extern uint32_t opencfw_em9305_ll_private_query_30bde0(uint32_t,uintptr_t);
extern uint32_t opencfw_em9305_ll_private_signed_30cef0(uint32_t,uint32_t);
extern uint32_t opencfw_em9305_ll_private_signed_pair_30dd94(uint32_t,uint32_t,uint32_t);
extern uint32_t opencfw_em9305_ll_private_descriptor_303290(uintptr_t);
/* Native32f494..32f64c: sparse private command table and response suffixes.
 * The 28 descriptor bytes are a genuine query-output contract, not defaults. */
uint32_t opencfw_em9305_dispatch_32f494(uintptr_t request,uintptr_t input)
{
 uint32_t command=*(volatile uint16_t *)request;
 uint8_t query[3]={2u,0u,0u};
 uint32_t status=0u,length=1u;
 if(command==0xffe3u) {
  uint32_t value=*(volatile uint8_t *)input;
  *(volatile uint8_t *)(uintptr_t)0x805702u=(uint8_t)(value!=0u);
 } else if(command==0xffe4u) {
  uint32_t b1=*(volatile uint8_t *)(input+1u),b3=*(volatile uint8_t *)(input+3u);
  uint32_t b0=*(volatile uint8_t *)input,b2=*(volatile uint8_t *)(input+2u);
  uint32_t count=*(volatile uint8_t *)(input+4u);
  status=opencfw_em9305_ll_primary_send_32f794((uint16_t)(b0+(b1<<8u)),(uint16_t)(b2+(b3<<8u)),count);
 } else if(command==0xffe5u) {
  uint32_t high=*(volatile uint8_t *)(input+1u),low=*(volatile uint8_t *)input;
  *(volatile uint16_t *)(uintptr_t)0x80570eu=(uint16_t)(low+(high<<8u));
 } else if(command==0xffe7u) {
  uint32_t high=*(volatile uint8_t *)(input+1u),low=*(volatile uint8_t *)input;
  uint32_t id=(uint16_t)(low+(high<<8u));
  uint64_t mask=opencfw_em9305_ll_pack64_304648(input+2u);
  uint32_t enabled=*(volatile uint8_t *)(input+10u)!=0u;
  status=opencfw_em9305_ll_private_mask_30d378(id,(uint32_t)mask,(uint32_t)(mask>>32u),enabled);
 } else if(command==0xffe9u) length=17u;
 else if(command==0xffeau) {
  uint32_t third=*(volatile uint8_t *)(input+2u);
  uint32_t value=*(volatile uint8_t *)(input+1u);
  uint32_t signed_value=(value&128u)!=0u?value|0xffffff00u:value;
  uint32_t first=*(volatile uint8_t *)input;
  status=opencfw_em9305_ll_private_radio_30d8fc(first,signed_value,third);
 } else if(command==0xffebu || command==0xfff6u || command==0xffddu) {
  uint32_t high=*(volatile uint8_t *)(input+1u),low=*(volatile uint8_t *)input;
  uint32_t id=(uint16_t)(low+(high<<8u));
  if(command==0xffebu) {
   status=opencfw_em9305_ll_private_query_30bde0(id,(uintptr_t)query);
   length=4u;
  } else {
   uint32_t third=0u;
   if(command==0xffddu) third=*(volatile uint8_t *)(input+3u);
   uint32_t value=*(volatile uint8_t *)(input+2u);
   uint32_t signed_value=(value&128u)!=0u?value|0xffffff00u:value;
   status=command==0xfff6u?opencfw_em9305_ll_private_signed_30cef0(id,signed_value):
                         opencfw_em9305_ll_private_signed_pair_30dd94(id,signed_value,third);
  }
 } else if(command==0xfffdu) length=29u;
 else return 0u;
 uintptr_t packet=opencfw_em9305_ll_response_allocate_32e428(length,*(volatile uint16_t *)request);
 if(packet==0u) return 1u;
 *(volatile uint8_t *)packet=(uint8_t)status;
 uintptr_t suffix=packet+1u;
 command=*(volatile uint16_t *)request;
 if(command==0xffe9u) {
  const uint32_t offsets[4]={0u,4u,12u,16u};
  for(uint32_t i=0u;i<4u;++i) {
   uintptr_t source=0x805704u+offsets[i];
   *(volatile uint8_t *)(suffix+4u*i)=(uint8_t)*(volatile uint32_t *)source;
   *(volatile uint8_t *)(suffix+4u*i+1u)=(uint8_t)(*(volatile uint32_t *)source>>8u);
   *(volatile uint8_t *)(suffix+4u*i+2u)=(uint8_t)*(volatile uint16_t *)(source+2u);
   *(volatile uint8_t *)(suffix+4u*i+3u)=*(volatile uint8_t *)(source+3u);
  }
 } else if(command==0xfffdu) {
  uint8_t descriptor[28];
  (void)opencfw_em9305_ll_private_descriptor_303290((uintptr_t)descriptor);
  (void)opencfw_em9305_memcpy((void *)suffix,descriptor,28u);
 } else if(command==0xffebu) {
  *(volatile uint8_t *)suffix=query[0];
  *(volatile uint8_t *)(suffix+1u)=query[1];
  *(volatile uint8_t *)(suffix+2u)=query[2];
 }
 (void)opencfw_em9305_ll_event_send(suffix-6u);
 return 1u;
}
/* Native303290..30329c: full28-byte runtime descriptor copy. The RAM
 * descriptor contents are genuine runtime data, not a zero default. */
uint32_t opencfw_em9305_ll_private_descriptor_303290(uintptr_t output)
{
 return (uint32_t)(uintptr_t)opencfw_em9305_memcpy((void *)output,
               (const void *)(uintptr_t)0x8016dcu,28u);
}

extern void opencfw_em9305_ll_signed_apply_309aa4(uint32_t,uint32_t);
/* Native30cef0..30cf24: validated signed-byte request. The apply child is
 * a genuine unresolved native body; its return does not affect status. */
uint32_t opencfw_em9305_ll_private_signed_30cef0(uint32_t id,uint32_t value)
{
 (void)opencfw_em9305_wsf_critical_enter();
 uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
 uint32_t status=2u;
 if(id<*(volatile uint8_t *)(config+34u) &&
    opencfw_em9305_ll_slot_active_30731c(id)!=0u) {
  (void)opencfw_em9305_ll_signed_apply_309aa4(id,value);
  status=0u;
 }
 (void)opencfw_em9305_wsf_critical_exit();
 return status;
}

/* Native306f44..306f6e: three byte loads, each with a reloaded slot base. */
uint32_t opencfw_em9305_ll_private_query_bytes_306f44(uint32_t id,uintptr_t output)
{
 for(uint32_t index=0u;index<3u;++index) {
  uint32_t offset;
  __asm__ volatile("mpyuw %0,%1,912":"=r"(offset):"r"(id));
  uintptr_t slots=*(volatile uint32_t *)(uintptr_t)0x805c70u;
  uint8_t value=*(volatile uint8_t *)(slots+offset+index+598u);
  *(volatile uint8_t *)(output+index)=value;
 }
 return id;
}
/* Native30bde0..30be2a: private three-byte query with precise status gates. */
uint32_t opencfw_em9305_ll_private_query_30bde0(uint32_t id,uintptr_t output)
{
 (void)opencfw_em9305_wsf_critical_enter();
 uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
 uint32_t status=2u;
 if(id<*(volatile uint8_t *)(config+34u) &&
    opencfw_em9305_ll_slot_active_30731c(id)!=0u) {
  uint32_t flags=*(volatile uint8_t *)(uintptr_t)0x805a96u;
  status=12u;
  if((flags&1u)!=0u && opencfw_em9305_ll_slot_state_306fdc(id)==0u) {
   (void)opencfw_em9305_ll_private_query_bytes_306f44(id,output);
   status=0u;
  }
 }
 (void)opencfw_em9305_wsf_critical_exit();
 return status;
}

extern void opencfw_em9305_ll_signed_pair_apply_309910(uint32_t,uint32_t,uint32_t);
/* Native30dd94..30ddd2: range-gated signed request with selector0..4. */
uint32_t opencfw_em9305_ll_private_signed_pair_30dd94(uint32_t id,uint32_t value,uint32_t selector)
{
 (void)opencfw_em9305_wsf_critical_enter();
 uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
 uint32_t status=2u;
 if(id<*(volatile uint8_t *)(config+34u) &&
    opencfw_em9305_ll_slot_active_30731c(id)!=0u) {
  status=18u;
  if(selector<5u) {
   (void)opencfw_em9305_ll_signed_pair_apply_309910(id,value,selector);
   status=0u;
  }
 }
 (void)opencfw_em9305_wsf_critical_exit();
 return status;
}

extern uint32_t opencfw_em9305_ll_private_mask_apply_308b20(uint32_t,uint32_t,uint32_t,uint32_t);
/* Native30d378..30d3c0: two-word feature mask validation; BMSK26 retains
 * the low27 bits of the high word. There is no critical-section wrapper. */
uint32_t opencfw_em9305_ll_private_mask_30d378(uint32_t id,uint32_t low,uint32_t high,uint32_t enabled)
{
 uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
 if(id>=*(volatile uint8_t *)(config+34u)) return 2u;
 if(opencfw_em9305_ll_slot_active_30731c(id)==0u) return 2u;
 if(((low&0xfff7fb41u)|(high&0x07ffffffu))!=0u) return 18u;
 (void)opencfw_em9305_ll_private_mask_apply_308b20(id,low,high,enabled);
 return 0u;
}

/* Native308b20..308b48: two-word slot-mask update, preserving low/high
 * load-before-low-store ordering and returning the updated low word. */
uint32_t opencfw_em9305_ll_private_mask_apply_308b20(uint32_t id,uint32_t low,uint32_t high,uint32_t enabled)
{
 uint32_t offset;
 __asm__ volatile("mpyuw %0,%1,912":"=r"(offset):"r"(id));
 uintptr_t slots=*(volatile uint32_t *)(uintptr_t)0x805c70u;
 uintptr_t record=slots+offset;
 uint32_t current_low=*(volatile uint32_t *)(record+4u);
 uint32_t current_high=*(volatile uint32_t *)(record+8u);
 uint32_t result=enabled!=0u?current_low|low:current_low&~low;
 *(volatile uint32_t *)(record+4u)=result;
 *(volatile uint32_t *)(record+8u)=enabled!=0u?high|current_high:current_high&~high;
 return result;
}

/* Native310230..31025e: query-dependent signed clamp; upper is signed
 * MIN(product upper, fresh radio query), lower is reloaded only below upper. */
uint32_t opencfw_em9305_ll_signed_clamp_310230(uint32_t value)
{
 int32_t query=(int32_t)opencfw_em9305_radio_status_311a00(1u);
 int32_t upper=(int32_t)*(volatile int8_t *)(uintptr_t)0x8012b8u;
 int32_t ceiling=upper<query?upper:query;
 if(ceiling<(int32_t)value) return (uint32_t)ceiling;
 int32_t lower=(int32_t)*(volatile int8_t *)(uintptr_t)0x8012b9u;
 return (uint32_t)(lower>(int32_t)value?lower:(int32_t)value);
}

/* Native31026c..310280: lower/upper byte outputs, both read before writes. */
uint32_t opencfw_em9305_ll_signed_bounds_31026c(uintptr_t lower,uintptr_t upper)
{
 uint32_t low=*(volatile uint8_t *)(uintptr_t)0x8012b9u;
 uint32_t high=*(volatile uint8_t *)(uintptr_t)0x8012b8u;
 *(volatile uint8_t *)lower=(uint8_t)low;
 *(volatile uint8_t *)upper=(uint8_t)high;
 return (uint32_t)lower;
}
/* Native31b374..31b39a: signed bound classification, lower override last. */
uint32_t opencfw_em9305_ll_signed_classify_31b374(uint32_t value)
{
 uint8_t upper,lower;
 (void)opencfw_em9305_ll_signed_bounds_31026c((uintptr_t)&lower,(uintptr_t)&upper);
 int32_t high=(int32_t)(int8_t)upper,low=(int32_t)(int8_t)lower;
 uint32_t result=high<=(int32_t)value?2u:0u;
 if(low>=(int32_t)value) result=1u;
 return result;
}
/* Native309910..3099c8: signed per-selector update and genuine callbacks.
 * The parent ignores native R0; this body has a void semantic return. */
void opencfw_em9305_ll_signed_pair_apply_309910(uint32_t id,uint32_t value,uint32_t selector)
{
 uint32_t offset;
 __asm__ volatile("mpyuw %0,%1,912":"=r"(offset):"r"(id));
 uintptr_t slots=*(volatile uint32_t *)(uintptr_t)0x805c70u;
 uintptr_t record=slots+offset;
 uint32_t old=*(volatile uint8_t *)(record+66u);
 if(selector==0u) selector=*(volatile uint8_t *)(record+76u);
 uint32_t updated=opencfw_em9305_ll_signed_clamp_310230(value);
 uint32_t difference=updated-old;
 if((difference&255u)==0u) return;
 if(selector==*(volatile uint8_t *)(record+76u)) {
  uint32_t mode=*(volatile uint8_t *)(record+1u);
  *(volatile uint8_t *)(record+66u)=(uint8_t)updated;
  if(mode==2u && (updated&255u)!=old &&
     (*(volatile uint8_t *)(record+548u)&4u)!=0u) {
   uintptr_t callback=*(volatile uint32_t *)(uintptr_t)0x8052c8u;
   if(callback!=0u) {
    uint32_t signed_delta=(difference&128u)!=0u?(difference&255u)|0xffffff00u:difference&255u;
    (void)((uint32_t (*)(uintptr_t,uint32_t,uint32_t,uint32_t,uint32_t))callback)(record,selector,signed_delta,updated,0u);
   }
  }
 }
 uint32_t notify=*(volatile uint8_t *)(record+767u);
 *(volatile uint8_t *)(record+selector+331u)=(uint8_t)updated;
 if(notify!=0u) {
  uintptr_t callback=*(volatile uint32_t *)(uintptr_t)0x805170u;
  if(callback!=0u) {
   uint32_t current=*(volatile uint8_t *)(record+66u);
   uint32_t signed_current=(current&128u)!=0u?current|0xffffff00u:current;
   uint32_t current_selector=*(volatile uint8_t *)(record+76u);
   uint32_t classification=opencfw_em9305_ll_signed_classify_31b374(signed_current);
   uint32_t signed_delta=(difference&128u)!=0u?(difference&255u)|0xffffff00u:difference&255u;
   (void)((uint32_t (*)(uintptr_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t))callback)(record,0u,0u,current_selector,updated,classification,signed_delta);
  }
 }
}

/* Native309aa4..309b74: update default and four selector bytes, with saved
 * old selector bytes and callback-pointer reload after each notification.
 * MPYWHL is retained as the authenticated named DSP operation. */
void opencfw_em9305_ll_signed_apply_309aa4(uint32_t id,uint32_t value)
{
 uint32_t offset;
 __asm__ volatile("mpyuw %0,%1,912":"=r"(offset):"r"(id));
 uintptr_t slots=*(volatile uint32_t *)(uintptr_t)0x805c70u;
 uintptr_t record=slots+offset;
 uint32_t old=*(volatile uint8_t *)(record+66u);
 uint8_t saved[4];
 (void)opencfw_em9305_memcpy(saved,(const void *)(record+332u),4u);
 uint32_t updated=opencfw_em9305_ll_signed_clamp_310230(value);
 uint32_t mode=*(volatile uint8_t *)(record+1u);
 uint32_t byte=updated&255u,replicated;
 __asm__ volatile("mpywhl %0,0x01010101,%1":"=r"(replicated):"r"(byte));
 *(volatile uint8_t *)(record+66u)=(uint8_t)updated;
 *(volatile uint32_t *)(record+332u)=replicated;
 if(mode==2u && byte!=old &&
    (*(volatile uint8_t *)(record+548u)&4u)!=0u) {
  uintptr_t callback=*(volatile uint32_t *)(uintptr_t)0x8052c8u;
  if(callback!=0u) {
   uint32_t selector=*(volatile uint8_t *)(record+76u);
   uint32_t difference=updated-old;
   uint32_t delta=(difference&128u)!=0u?(difference&255u)|0xffffff00u:difference&255u;
   (void)((uint32_t (*)(uintptr_t,uint32_t,uint32_t,uint32_t,uint32_t))callback)(record,selector,delta,updated,0u);
  }
 }
 if(*(volatile uint8_t *)(record+767u)!=0u) {
  uintptr_t callback=*(volatile uint32_t *)(uintptr_t)0x805170u;
  for(uint32_t index=0u;index<4u;++index) {
   if(byte!=saved[index] && callback!=0u) {
    uint32_t difference=updated-saved[index];
    uint32_t classification=opencfw_em9305_ll_signed_classify_31b374(updated);
    uint32_t delta=(difference&128u)!=0u?(difference&255u)|0xffffff00u:difference&255u;
    (void)((uint32_t (*)(uintptr_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t))callback)(record,0u,0u,index,updated,classification,delta);
    callback=*(volatile uint32_t *)(uintptr_t)0x805170u;
   }
  }
 }
}

/* Native30d8fc..30d9b0: private radio mask/channel update and message fanout.
 * Carry-set aliases unsigned LO; EXTBU(third-38)>=220 accepts2..37.
 * Configuration slot count is reloaded on every loop iteration. */
uint32_t opencfw_em9305_ll_private_radio_30d8fc(uint32_t mask,uint32_t gain,uint32_t channel)
{
 if((*(volatile uint8_t *)(uintptr_t)0x805a96u&1u)==0u) return 12u;
 if(mask-1u>=7u || ((channel-38u)&255u)<220u) return 18u;
 for(uint32_t index=0u;index<3u;++index) {
  if((mask&(1u<<index))!=0u) {
   *(volatile uint8_t *)(uintptr_t)(0x805aa9u+index)=(uint8_t)gain;
   *(volatile uint8_t *)(uintptr_t)(0x805aacu+index)=(uint8_t)channel;
  }
 }
 for(uint32_t index=0u;;++index) {
  uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
  uint32_t id=(uint16_t)index;
  if(id>=*(volatile uint8_t *)(config+34u)) return 0u;
  if(opencfw_em9305_ll_slot_active_30731c(id)==0u) continue;
  if(opencfw_em9305_ll_slot_state_306fdc(id)!=1u) continue;
  if(opencfw_em9305_ll_slot_pending_307434(id,33u)!=0u) return 12u;
  uintptr_t message=opencfw_em9305_wsf_event_allocate(6u);
  if(message==0u) continue;
  *(volatile uint16_t *)(message+2u)=0x2101u;
  uint32_t handler=*(volatile uint8_t *)(uintptr_t)0x805b18u;
  *(volatile uint8_t *)(message+5u)=(uint8_t)channel;
  *(volatile uint8_t *)(message+4u)=(uint8_t)mask;
  *(volatile uint16_t *)message=(uint16_t)index;
  (void)opencfw_em9305_wsf_task_message_send(handler,message);
 }
}

/* Native30e38c..30e3e8: connection size/timing limits with exact status48/17.
 * Carry-set is unsigned LO, including the conditional second comparison. */
uint32_t opencfw_em9305_ll_connection_value_30e38c(uint32_t size,uint32_t timing)
{
 if(((size-252u)&65535u)<0xff1fu || timing<328u) return 48u;
 uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
 uint32_t version=*(volatile uint8_t *)(config+4u);
 if(timing>=2121u && version<9u) return 48u;
 if(timing>=17041u && version>=9u) return 48u;
 uint32_t limit=*(volatile uint16_t *)(config+38u);
 if(limit>251u) limit=251u;
 if(limit<size) return 17u;
 *(volatile uint16_t *)(uintptr_t)0x805ab8u=(uint16_t)timing;
 *(volatile uint16_t *)(uintptr_t)0x805ab6u=(uint16_t)size;
 return 0u;
}

/* Native307044..307058: paired slot words544/548 returned in R0/R1. */
uint64_t opencfw_em9305_ll_connection_query_words_307044(uint32_t id)
{
 uint32_t offset;
 __asm__ volatile("mpyuw %0,%1,912":"=r"(offset):"r"(id));
 uintptr_t slots=*(volatile uint32_t *)(uintptr_t)0x805c70u;
 uint32_t low=*(volatile uint32_t *)(slots+offset+544u);
 uint32_t high=*(volatile uint32_t *)(slots+offset+548u);
 return (uint64_t)low|((uint64_t)high<<32u);
}
/* Native30cb28..30cb7a: operation query gated by slot word bit26. */
uint32_t opencfw_em9305_ll_connection_query_30cb28(uint32_t id)
{
 uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
 if(id>=*(volatile uint8_t *)(config+34u)) return 2u;
 if(opencfw_em9305_ll_slot_active_30731c(id)==0u) return 2u;
 uint64_t words=opencfw_em9305_ll_connection_query_words_307044(id);
 if(((uint32_t)words&(1u<<26u))==0u) return 26u;
 uintptr_t message=opencfw_em9305_wsf_event_allocate(6u);
 if(message==0u) return 0u;
 *(volatile uint16_t *)(message+2u)=0x2301u;
 uint32_t handler=*(volatile uint8_t *)(uintptr_t)0x805b18u;
 *(volatile uint16_t *)message=(uint16_t)id;
 *(volatile uint8_t *)(message+4u)=2u;
 (void)opencfw_em9305_wsf_task_message_send(handler,message);
 return 0u;
}

/* Native30c944..30c996: six-byte connection mode command, no critical wrap. */
uint32_t opencfw_em9305_ll_connection_mode_30c944(uint32_t id,uint32_t mode)
{
 uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
 if(id>=*(volatile uint8_t *)(config+34u)) return 2u;
 if(opencfw_em9305_ll_slot_active_30731c(id)==0u) return 2u;
 if(opencfw_em9305_ll_slot_flag_307480(id,1u)==0u) return 12u;
 uintptr_t message=opencfw_em9305_wsf_event_allocate(6u);
 if(message==0u) return 0u;
 *(volatile uint16_t *)(message+2u)=0x1e01u;
 uint32_t handler=*(volatile uint8_t *)(uintptr_t)0x805b18u;
 *(volatile uint8_t *)(message+4u)=(uint8_t)mode;
 *(volatile uint16_t *)message=(uint16_t)id;
 (void)opencfw_em9305_wsf_task_message_send(handler,message);
 return 0u;
}
extern uint32_t opencfw_em9305_ll_connection_parameters_validate_30a6b4(uintptr_t);
/* Native30c998..30c9fe: validated 12-byte controls copied into16-byte message. */
uint32_t opencfw_em9305_ll_connection_modify_30c998(uint32_t id,uintptr_t controls)
{
 uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
 if(id>=*(volatile uint8_t *)(config+34u)) return 2u;
 if(opencfw_em9305_ll_slot_active_30731c(id)==0u) return 2u;
 if(opencfw_em9305_ll_slot_flag_307480(id,1u)==0u) return 12u;
 uint32_t status=opencfw_em9305_ll_connection_parameters_validate_30a6b4(controls);
 if(status!=0u) return status;
 uintptr_t message=opencfw_em9305_wsf_event_allocate(16u);
 if(message==0u) return 0u;
 *(volatile uint16_t *)(message+2u)=0x1d01u;
 *(volatile uint16_t *)message=(uint16_t)id;
 (void)opencfw_em9305_memcpy((void *)(message+4u),(const void *)controls,12u);
 uint32_t handler=*(volatile uint8_t *)(uintptr_t)0x805b18u;
 (void)opencfw_em9305_wsf_task_message_send(handler,message);
 return 0u;
}

/* Native30a6b4..30a70a: interval/latency/timeout validation. Authentic named
 * DSP products preserve ISA semantics; no generic multiply substitution. */
uint32_t opencfw_em9305_ll_connection_parameters_validate_30a6b4(uintptr_t controls)
{
 uint32_t minimum=*(volatile uint16_t *)controls;
 if(minimum<6u) return 18u;
 uint32_t maximum=*(volatile uint16_t *)(controls+2u);
 if(maximum<minimum || maximum<6u || maximum>3200u || minimum>3200u) return 18u;
 uint32_t latency=*(volatile uint16_t *)(controls+4u);
 if(latency>499u) return 18u;
 uint32_t timeout=*(volatile uint16_t *)(controls+6u);
 uint32_t periods=latency+1u,span,required;
 __asm__ volatile("mpywhul %0,%1,%2":"=r"(span):"r"(periods),"r"(maximum));
 uint32_t factor=2500u;
 __asm__ volatile("mpywhl %0,%1,%2":"=r"(required):"r"(span),"r"(factor));
 uint32_t available;
 __asm__ volatile("mpyuw %0,%1,10000":"=r"(available):"r"(timeout));
 if(timeout>3200u || timeout<10u || available<=required) return 18u;
 return 0u;
}

/* Native3073ec..30740e: live-slot byte636 bit2 predicate. */
uint32_t opencfw_em9305_ll_connection_read_ready_3073ec(uint32_t id)
{
 uint32_t offset;
 __asm__ volatile("mpyuw %0,%1,912":"=r"(offset):"r"(id));
 uintptr_t slots=*(volatile uint32_t *)(uintptr_t)0x805c70u;
 uintptr_t record=slots+offset;
 if(*(volatile uint8_t *)record==0u) return 0u;
 return (*(volatile uint8_t *)(record+636u)&4u)>>2u;
}
/* Native309030..309046: set bit2 in slot word636, return record address. */
uint32_t opencfw_em9305_ll_connection_read_mark_309030(uint32_t id)
{
 uint32_t offset;
 __asm__ volatile("mpyuw %0,%1,912":"=r"(offset):"r"(id));
 uintptr_t slots=*(volatile uint32_t *)(uintptr_t)0x805c70u;
 uintptr_t record=slots+offset;
 uint32_t word=*(volatile uint32_t *)(record+636u);
 *(volatile uint32_t *)(record+636u)=word|4u;
 return (uint32_t)record;
}
/* Native30c860..30c8c6: pending read path precedes max-slot validation. */
uint32_t opencfw_em9305_ll_connection_read_30c860(uint32_t id)
{
 if(opencfw_em9305_ll_slot_pending_307434(id,27u)!=0u) {
  if(opencfw_em9305_ll_slot_active_30731c(id)==0u) return 12u;
  if(opencfw_em9305_ll_connection_read_ready_3073ec(id)==0u) return 12u;
  (void)opencfw_em9305_ll_connection_read_mark_309030(id);
  return 0u;
 }
 uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
 if(id>=*(volatile uint8_t *)(config+34u)) return 2u;
 if(opencfw_em9305_ll_slot_active_30731c(id)==0u) return 2u;
 uintptr_t message=opencfw_em9305_wsf_event_allocate(4u);
 if(message==0u) return 0u;
 *(volatile uint16_t *)(message+2u)=0x1b01u;
 uint32_t handler=*(volatile uint8_t *)(uintptr_t)0x805b18u;
 *(volatile uint16_t *)message=(uint16_t)id;
 (void)opencfw_em9305_wsf_task_message_send(handler,message);
 return 0u;
}
/* Native30c8c8..30c916: max/active then pending-operation28 gate. */
uint32_t opencfw_em9305_ll_connection_action_30c8c8(uint32_t id)
{
 uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
 if(id>=*(volatile uint8_t *)(config+34u)) return 2u;
 if(opencfw_em9305_ll_slot_active_30731c(id)==0u) return 2u;
 if(opencfw_em9305_ll_slot_pending_307434(id,28u)!=0u) return 12u;
 uintptr_t message=opencfw_em9305_wsf_event_allocate(4u);
 if(message==0u) return 0u;
 *(volatile uint16_t *)(message+2u)=0x1c01u;
 uint32_t handler=*(volatile uint8_t *)(uintptr_t)0x805b18u;
 *(volatile uint16_t *)message=(uint16_t)id;
 (void)opencfw_em9305_wsf_task_message_send(handler,message);
 return 0u;
}

/* Native3072e0..3072ee and30730c..30731a: optional live callback queries. */
uint32_t opencfw_em9305_ll_disconnect_extra_active_3072e0(uint32_t id)
{
 uintptr_t callback=*(volatile uint32_t *)(uintptr_t)0x8027e8u;
 return callback!=0u?((uint32_t (*)(uint32_t))callback)(id):0u;
}
uint32_t opencfw_em9305_ll_disconnect_extra_pending_30730c(uint32_t id)
{
 uintptr_t callback=*(volatile uint32_t *)(uintptr_t)0x8027ecu;
 return callback!=0u?((uint32_t (*)(uint32_t))callback)(id):0u;
}
/* Native306e54..306e66: lookup callback, authentic missing-provider sentinel. */
uint32_t opencfw_em9305_ll_disconnect_extra_lookup_306e54(uint32_t id)
{
 uintptr_t callback=*(volatile uint32_t *)(uintptr_t)0x8028bcu;
 return callback!=0u?((uint32_t (*)(uint32_t))callback)(id):0xffffu;
}
/* Native30b570..30b620: primary/extra disconnect commands with runtime
 * callback queries and configuration reload before allocation size choice. */
uint32_t opencfw_em9305_ll_connection_disconnect_30b570(uint32_t id,uint32_t reason)
{
 uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
 uint32_t primary=*(volatile uint8_t *)(config+34u);
 uint32_t extra=*(volatile uint8_t *)(config+53u);
 if(id>=primary+extra) return 2u;
 uint32_t ready;
 if(id<primary) {
  ready=opencfw_em9305_ll_slot_active_30731c(id);
  if(ready==0u) return 2u;
 } else ready=opencfw_em9305_ll_disconnect_extra_active_3072e0(id);
 if(ready==0u) {
  if(opencfw_em9305_ll_disconnect_extra_pending_30730c(id)==0u) return 12u;
  uintptr_t message=opencfw_em9305_wsf_event_allocate(8u);
  if(message==0u) return 0u;
  uint32_t lookup=opencfw_em9305_ll_disconnect_extra_lookup_306e54(id);
  *(volatile uint16_t *)(message+2u)=0x2701u;
  *(volatile uint16_t *)message=(uint16_t)lookup;
  uint32_t handler=*(volatile uint8_t *)(uintptr_t)0x805b18u;
  *(volatile uint8_t *)(message+4u)=(uint8_t)reason;
  *(volatile uint16_t *)(message+6u)=(uint16_t)id;
  (void)opencfw_em9305_wsf_task_message_send(handler,message);
  return 0u;
 }
 config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
 primary=*(volatile uint8_t *)(config+34u);
 uintptr_t message=opencfw_em9305_wsf_event_allocate(id<primary?8u:6u);
 if(message==0u) return 0u;
 uint32_t type=0x170fu;
 if(id<primary) {
  *(volatile uint16_t *)(message+6u)=(uint16_t)id;
  type=0x1701u;
 }
 *(volatile uint16_t *)(message+2u)=(uint16_t)type;
 uint32_t handler=*(volatile uint8_t *)(uintptr_t)0x805b18u;
 *(volatile uint8_t *)(message+4u)=(uint8_t)reason;
 *(volatile uint16_t *)message=(uint16_t)id;
 (void)opencfw_em9305_wsf_task_message_send(handler,message);
 return 0u;
}

/* Native30d3c4..30d45a: timing request gated by slot and pending operation31.
 * Product version pointer is freshly reloaded after the pending query. */
uint32_t opencfw_em9305_ll_connection_times_30d3c4(uint32_t id,uint32_t size,uint32_t timing)
{
 uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
 if(id>=*(volatile uint8_t *)(config+34u)) return 2u;
 if(opencfw_em9305_ll_slot_active_30731c(id)==0u) return 2u;
 if(opencfw_em9305_ll_slot_pending_307434(id,31u)!=0u) return 12u;
 if(((size-252u)&65535u)<0xff1fu || timing<328u) return 18u;
 config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
 uint32_t version=*(volatile uint8_t *)(config+4u);
 if(timing>=2121u && version<9u) return 18u;
 if(timing>=17041u && version>=9u) return 18u;
 uintptr_t message=opencfw_em9305_wsf_event_allocate(8u);
 if(message==0u) return 0u;
 *(volatile uint16_t *)(message+2u)=0x1f01u;
 uint32_t handler=*(volatile uint8_t *)(uintptr_t)0x805b18u;
 uint32_t clamped=(int32_t)size<251?size:251u;
 *(volatile uint16_t *)(message+6u)=(uint16_t)timing;
 *(volatile uint16_t *)message=(uint16_t)id;
 *(volatile uint16_t *)(message+4u)=(uint16_t)clamped;
 (void)opencfw_em9305_wsf_task_message_send(handler,message);
 return 0u;
}

/* Native30b1b0..30b22c: legacy controls request; state1 needs feature bit1. */
uint32_t opencfw_em9305_ll_connection_parameters_30b1b0(uint32_t id,uintptr_t controls)
{
 uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
 if(id>=*(volatile uint8_t *)(config+34u)) return 2u;
 if(opencfw_em9305_ll_slot_active_30731c(id)==0u) return 2u;
 if(opencfw_em9305_ll_slot_pending_307434(id,21u)!=0u) return 12u;
 if(opencfw_em9305_ll_slot_state_306fdc(id)==1u &&
    (*(volatile uint8_t *)(uintptr_t)0x805a94u&2u)==0u) return 12u;
 uint32_t status=opencfw_em9305_ll_connection_parameters_validate_30a6b4(controls);
 if(status!=0u) return status;
 uintptr_t message=opencfw_em9305_wsf_event_allocate(16u);
 if(message==0u) return 0u;
 *(volatile uint16_t *)(message+2u)=0x1501u;
 *(volatile uint16_t *)message=(uint16_t)id;
 (void)opencfw_em9305_memcpy((void *)(message+4u),(const void *)controls,12u);
 uint32_t handler=*(volatile uint8_t *)(uintptr_t)0x805b18u;
 (void)opencfw_em9305_wsf_task_message_send(handler,message);
 return 0u;
}

/* Native32f70c..32f76e: event33 relay with two live event-mask gates. */
uint32_t opencfw_em9305_dispatch_32f70c(uintptr_t input)
{
 if(*(volatile uint8_t *)(input+2u)!=0x33u) return 0u;
 if((*(volatile uint8_t *)(uintptr_t)0x8056fcu&4u)==0u) return 0u;
 if((*(volatile uint8_t *)(uintptr_t)0x8056efu&32u)==0u) return 0u;
 uintptr_t output=opencfw_em9305_ll_event_allocate(0x3eu,12u);
 if(output==0u) return 0u;
 output-=2u;
 *(volatile uint8_t *)output=0x23u;
 *(volatile uint8_t *)(output+3u)=*(volatile uint8_t *)(input+4u);
 for(uint32_t index=0u;index<10u;++index)
  *(volatile uint8_t *)(output+4u+index)=*(volatile uint8_t *)(input+6u+index);
 (void)opencfw_em9305_ll_event_send(output);
 return 1u;
}

/* Native32f770..32f792: response status byte only for reloaded command207d. */
uint32_t opencfw_em9305_ll_response_32f770(uintptr_t request,uint32_t status,uint32_t length)
{
 uintptr_t packet=opencfw_em9305_ll_response_allocate_32e428(length,*(volatile uint16_t *)request);
 if(packet==0u) return 0u;
 if(*(volatile uint16_t *)request==0x207du) *(volatile uint8_t *)packet=(uint8_t)status;
 return opencfw_em9305_ll_event_send(packet-5u);
}
extern uint32_t opencfw_em9305_ll_controls_apply_30d524(uintptr_t);
extern uint32_t opencfw_em9305_ll_slot_controls_apply_30e0e0(uint32_t,uintptr_t);
/* Native32f64c..32f70a: paired207d/207e commands, five halfword controls.
 * Input byte-read order is preserved before packing stack controls. */
uint32_t opencfw_em9305_dispatch_32f64c(uintptr_t request,uintptr_t input)
{
 uint32_t command=*(volatile uint16_t *)request;
 if(command!=0x207du && command!=0x207eu) return 0u;
 uint8_t bytes[12];uint16_t controls[5];
 if(command==0x207eu) {
  for(uint32_t i=2u;i<12u;++i) bytes[i]=*(volatile uint8_t *)(input+i);
  bytes[0]=*(volatile uint8_t *)input;
  bytes[1]=*(volatile uint8_t *)(input+1u);
  for(uint32_t i=0u;i<5u;++i) controls[i]=(uint16_t)(bytes[2u+2u*i]+((uint32_t)bytes[3u+2u*i]<<8u));
  uint32_t id=(uint16_t)(bytes[0]+((uint32_t)bytes[1]<<8u));
  uint32_t status=opencfw_em9305_ll_slot_controls_apply_30e0e0(id,(uintptr_t)controls);
  (void)opencfw_em9305_ll_status_event_331bf8(request,status);
 } else {
  bytes[1]=*(volatile uint8_t *)(input+1u);
  bytes[0]=*(volatile uint8_t *)input;
  for(uint32_t i=2u;i<10u;++i) bytes[i]=*(volatile uint8_t *)(input+i);
  for(uint32_t i=0u;i<5u;++i) controls[i]=(uint16_t)(bytes[2u*i]+((uint32_t)bytes[1u+2u*i]<<8u));
  uint32_t status=opencfw_em9305_ll_controls_apply_30d524((uintptr_t)controls);
  (void)opencfw_em9305_ll_response_32f770(request,status,1u);
 }
 return 1u;
}

extern uint32_t opencfw_em9305_ll_controls_validate_32e378(uintptr_t);
/* Native30d524 tail branch to Native308b4c..308b72: validate then snapshot
 * all five input halfwords before publishing the shared controls block. */
uint32_t opencfw_em9305_ll_controls_apply_30d524(uintptr_t controls)
{
 uint32_t status=opencfw_em9305_ll_controls_validate_32e378(controls);
 if(status!=0u) return status;
 uint16_t values[5];
 for(uint32_t i=0u;i<5u;++i) values[i]=*(volatile uint16_t *)(controls+2u*i);
 for(uint32_t i=0u;i<5u;++i) *(volatile uint16_t *)(uintptr_t)(0x805ad0u+2u*i)=values[i];
 return status;
}

/* Native32e378..32e3b8: five-halfword controls domain checks, preserving
 * early returns and conditional compare's unsigned ordering. */
uint32_t opencfw_em9305_ll_controls_validate_32e378(uintptr_t controls)
{
 uint32_t first=*(volatile uint16_t *)controls;
 if(first-1u>499u) return 18u;
 uint32_t second=*(volatile uint16_t *)(controls+2u);
 if(second-1u>499u || first>second) return 18u;
 if(*(volatile uint16_t *)(controls+4u)>499u) return 18u;
 if(*(volatile uint16_t *)(controls+6u)>=second) return 18u;
 uint32_t timeout=*(volatile uint16_t *)(controls+8u);
 if(((timeout-3201u)&65535u)<0xf389u) return 18u;
 return 0u;
}

/* Native30e0e0 tail branch to Native30a39c..30a482: slot controls path.
 * All multiplication instructions retain named authenticated ISA semantics. */
uint32_t opencfw_em9305_ll_slot_controls_apply_30e0e0(uint32_t id,uintptr_t controls)
{
 uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
 if(id>=*(volatile uint8_t *)(config+34u)) return 2u;
 if(opencfw_em9305_ll_slot_active_30731c(id)==0u) return 2u;
 uint32_t status=opencfw_em9305_ll_controls_validate_32e378(controls);
 if(status!=0u) return status;
 uint32_t offset;
 __asm__ volatile("mpyuw %0,%1,912":"=r"(offset):"r"(id));
 uintptr_t base=*(volatile uint32_t *)(uintptr_t)0x805c70u;
 uintptr_t slot=base+offset;
 uint32_t latency=*(volatile uint16_t *)(controls+4u);
 uint32_t maximum=*(volatile uint16_t *)(controls+2u);
 uint32_t interval=*(volatile uint16_t *)(slot+266u);
 uint32_t periods=latency+1u,span;
 __asm__ volatile("mpywhul %0,%1,%2":"=r"(span):"r"(periods),"r"(maximum));
 uint32_t rounded=(interval>>2u)+interval+((interval&3u)!=0u);
 uint32_t timeout=*(volatile uint16_t *)(controls+8u),available;
 __asm__ volatile("mpyuw %0,%1,10":"=r"(available):"r"(timeout));
 uint32_t required;
 __asm__ volatile("mpy %0,%1,%2":"=r"(required):"r"(rounded),"r"(span));
 required<<=1u;
 if(available<required) return 18u;
 if((*(volatile uint8_t *)(uintptr_t)0x805a98u&64u)==0u) return 26u;
 if((*(volatile uint8_t *)(slot+548u)&64u)==0u) return 26u;
 if(*(volatile uint8_t *)(slot+888u)!=0u) return 12u;
 if(*(volatile uint8_t *)(slot+2u)==0u) {
  uint16_t first=*(volatile uint16_t *)controls;
  uint16_t fourth=*(volatile uint16_t *)(controls+6u);
  *(volatile uint16_t *)(uintptr_t)0x805ad4u=(uint16_t)latency;
  *(volatile uint16_t *)(uintptr_t)0x805ad2u=(uint16_t)maximum;
  *(volatile uint16_t *)(uintptr_t)0x805ad8u=(uint16_t)timeout;
  *(volatile uint16_t *)(uintptr_t)0x805ad0u=first;
  *(volatile uint16_t *)(uintptr_t)0x805ad6u=fourth;
 }
 uintptr_t message=opencfw_em9305_wsf_event_allocate(4u);
 if(message==0u) return 0u;
 *(volatile uint16_t *)message=(uint16_t)id;
 __asm__ volatile("mpyuw %0,%1,912":"=r"(offset):"r"(id));
 *(volatile uint16_t *)(message+2u)=0x2901u;
 (void)opencfw_em9305_memcpy((void *)(base+offset+856u),(const void *)controls,10u);
 uint32_t handler=*(volatile uint8_t *)(uintptr_t)0x805b18u;
 (void)opencfw_em9305_wsf_task_message_send(handler,message);
 return 0u;
}
extern uint32_t opencfw_em9305_ll_test_30b1ac(uintptr_t);
extern uint32_t opencfw_em9305_ll_test_30d35c(uint32_t);
extern uint32_t opencfw_em9305_ll_test_30e050(uintptr_t);
extern uint32_t opencfw_em9305_ll_test_30cb24(uint32_t,uint32_t);
extern uint32_t opencfw_em9305_ll_test_30c2dc(uint32_t,uint32_t);
extern uint32_t opencfw_em9305_ll_test_30c2d4(uint32_t,uint32_t);
extern uint32_t opencfw_em9305_ll_test_30bc3c(uintptr_t);
extern uint32_t opencfw_em9305_ll_test_30bd18(uint32_t,uintptr_t);
extern uint32_t opencfw_em9305_ll_test_30bb14(void);
extern uint32_t opencfw_em9305_ll_test_30bb20(void);
extern uint32_t opencfw_em9305_ll_test_30bdc4(void);
extern uint32_t opencfw_em9305_ll_test_30bdd0(void);
extern uint32_t opencfw_em9305_ll_test_30c728(uint32_t,uintptr_t,uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_ll_test_30c2bc(uint32_t,uintptr_t);
extern uint32_t opencfw_em9305_ll_test_30c2d8(uint32_t,uintptr_t);
extern uint32_t opencfw_em9305_ll_test_30c724(uint32_t,uintptr_t);
extern uint32_t opencfw_em9305_ll_test_response_330f08(uintptr_t,uint32_t,uint32_t,uintptr_t);
/* Native32f85c..32fc86: command2060..2075 and three legacy queries.
 * Native scratch outputs stay uninitialized until their genuine providers
 * write them. No invented default response bytes are supplied. */
uint32_t opencfw_em9305_dispatch_32f85c(uintptr_t request,uintptr_t input)
{
 if(opencfw_em9305_dispatch_32fd18(request,input)!=0u) return 1u;
 uint32_t command=*(volatile uint16_t *)request,length=0u,status=0u,id=0u;
 _Alignas(4) uint8_t scratch[36];
 if(command==0x0c15u) length=3u;
 else if(command==0x0c16u) {
  uint32_t high=*(volatile uint8_t *)(input+1u),low=*(volatile uint8_t *)input;
  status=opencfw_em9305_ll_test_30d35c((uint16_t)(low+(high<<8u)));length=1u;
 } else if(command==0x0c83u) {
  uint32_t a=*(volatile uint8_t *)input,b=*(volatile uint8_t *)(input+1u),c=*(volatile uint8_t *)(input+2u);
  *(uint32_t *)(scratch+4u)=(uint32_t)(input+3u);
  scratch[0]=(uint8_t)a;scratch[1]=(uint8_t)b;scratch[2]=(uint8_t)c;
  status=opencfw_em9305_ll_test_30b1ac((uintptr_t)scratch);length=1u;
 } else if(command==0x2060u) length=7u;
 else if(command==0x206eu) {
  uint8_t bytes[13];static const uint8_t order[13]={1,10,0,6,8,9,11,5,7,2,3,4,12};
  for(uint32_t i=0u;i<13u;++i) bytes[order[i]]=*(volatile uint8_t *)(input+order[i]);
  id=bytes[0]+((uint32_t)bytes[1]<<8u);
  *(uint16_t *)scratch=(uint16_t)id;
  *(uint32_t *)(scratch+20u)=(uint32_t)(input+13u);
  scratch[2]=bytes[2];scratch[3]=bytes[3];scratch[4]=bytes[4];scratch[16]=bytes[12];
  *(uint16_t *)(scratch+6u)=(uint16_t)(bytes[5]+((uint32_t)bytes[6]<<8u));
  *(uint16_t *)(scratch+8u)=(uint16_t)(bytes[7]+((uint32_t)bytes[8]<<8u));
  *(uint32_t *)(scratch+12u)=bytes[9]+((uint32_t)bytes[10]<<8u)+((uint32_t)bytes[11]<<16u);
  status=opencfw_em9305_ll_test_30e050((uintptr_t)scratch);
  id=*(volatile uint16_t *)scratch;length=3u;
 } else if(command==0x206fu || command==0x2070u || command==0x2071u) {
  uint32_t high=*(volatile uint8_t *)(input+1u),low=*(volatile uint8_t *)input,arg=*(volatile uint8_t *)(input+2u);
  id=low+(high<<8u);
  if(command==0x206fu) status=opencfw_em9305_ll_test_30cb24((uint16_t)id,arg);
  else if(command==0x2070u) status=opencfw_em9305_ll_test_30c2dc((uint16_t)id,arg);
  else {status=opencfw_em9305_ll_test_30c2d4((uint16_t)id,arg);if(status==0u) *(volatile uint8_t *)(uintptr_t)0x805854u=1u;}
  length=3u;
 } else if(command==0x2061u || command==0x2072u || command==0x2073u || command==0x2075u || command==0x1405u) {
  uint32_t high=*(volatile uint8_t *)(input+1u),low=*(volatile uint8_t *)input;
  id=low+(high<<8u);
  length=command==0x2061u?12u:command==0x2075u?31u:command==0x1405u?4u:15u;
 } else return 0u;
 uintptr_t packet=opencfw_em9305_ll_response_allocate_32e428(length,*(volatile uint16_t *)request);
 if(packet==0u) return 1u;
 command=*(volatile uint16_t *)request;
 if(command==0x2060u) {
  uint32_t first=opencfw_em9305_ll_test_30bb14();
  uint32_t second=opencfw_em9305_ll_test_30bb20();
  uint32_t third=opencfw_em9305_ll_test_30bdc4();
  uint32_t fourth=opencfw_em9305_ll_test_30bdd0();
  *(volatile uint8_t *)(packet+6u)=(uint8_t)fourth;
  *(volatile uint8_t *)(packet+4u)=(uint8_t)third;
  *(volatile uint8_t *)(packet+3u)=(uint8_t)second;
  *(volatile uint8_t *)(packet+1u)=(uint8_t)first;
  *(volatile uint8_t *)packet=(uint8_t)status;
  *(volatile uint8_t *)(packet+5u)=(uint8_t)(third>>8u);
  *(volatile uint8_t *)(packet+2u)=(uint8_t)(first>>8u);
 } else if(command==0x2061u) {
  *(uint16_t *)(scratch+34u)=0u;*(uint32_t *)scratch=0u;*(uint32_t *)(scratch+28u)=0u;
  uint32_t result=opencfw_em9305_ll_test_30c728((uint16_t)id,(uintptr_t)(scratch+34u),(uintptr_t)scratch,(uintptr_t)(scratch+28u));
  uint32_t a=*(uint32_t *)scratch,b=*(uint32_t *)(scratch+28u),c=*(uint16_t *)(scratch+34u);
  *(volatile uint8_t *)packet=(uint8_t)result;
  *(volatile uint8_t *)(packet+1u)=(uint8_t)id;*(volatile uint8_t *)(packet+3u)=(uint8_t)c;
  *(volatile uint8_t *)(packet+9u)=(uint8_t)b;*(volatile uint8_t *)(packet+5u)=(uint8_t)a;
  *(volatile uint8_t *)(packet+2u)=(uint8_t)(id>>8u);
  *(volatile uint8_t *)(packet+11u)=(uint8_t)(b>>16u);*(volatile uint8_t *)(packet+10u)=(uint8_t)(b>>8u);
  *(volatile uint8_t *)(packet+8u)=(uint8_t)(a>>24u);*(volatile uint8_t *)(packet+7u)=(uint8_t)(a>>16u);
  *(volatile uint8_t *)(packet+6u)=(uint8_t)(a>>8u);*(volatile uint8_t *)(packet+4u)=(uint8_t)(c>>8u);
 } else if(command==0x206eu || command==0x206fu) {
  *(volatile uint8_t *)(packet+1u)=(uint8_t)id;*(volatile uint8_t *)packet=(uint8_t)status;*(volatile uint8_t *)(packet+2u)=(uint8_t)(id>>8u);
 } else if(command==0x2070u || command==0x2071u) {
  uint32_t n=opencfw_em9305_ll_pack_byte(packet,status);
  (void)opencfw_em9305_ll_pack_halfword(packet+n,(uint16_t)id);
 } else if(command==0x0c16u || command==0x0c83u) (void)opencfw_em9305_ll_pack_byte(packet,status);
 else if(command==0x0c15u) { (void)opencfw_em9305_ll_test_30bc3c(packet+1u);*(volatile uint8_t *)packet=0u; }
 else if(command==0x1405u) {
  uint32_t result=opencfw_em9305_ll_test_30bd18((uint16_t)id,(uintptr_t)scratch);
  uint32_t value=*(volatile uint8_t *)scratch;
  *(volatile uint8_t *)(packet+1u)=(uint8_t)id;*(volatile uint8_t *)packet=(uint8_t)result;
  *(volatile uint8_t *)(packet+2u)=(uint8_t)(id>>8u);*(volatile uint8_t *)(packet+3u)=(uint8_t)value;
 } else if(command==0x2072u || command==0x2073u) {
  uint32_t result=command==0x2072u?opencfw_em9305_ll_test_30c2bc((uint16_t)id,(uintptr_t)scratch):opencfw_em9305_ll_test_30c2d8((uint16_t)id,(uintptr_t)scratch);
  if(command==0x2073u && result==0u) *(volatile uint8_t *)(uintptr_t)0x805854u=0u;
  (void)opencfw_em9305_ll_test_response_330f08(packet,result,(uint16_t)id,(uintptr_t)scratch);
 } else if(command==0x2075u) {
  uint32_t result=opencfw_em9305_ll_test_30c724((uint16_t)id,(uintptr_t)scratch),words[7];
  for(uint32_t i=0u;i<7u;++i) words[i]=*(uint32_t *)(scratch+4u*i);
  *(volatile uint8_t *)(packet+1u)=(uint8_t)id;*(volatile uint8_t *)packet=(uint8_t)result;*(volatile uint8_t *)(packet+2u)=(uint8_t)(id>>8u);
  for(uint32_t i=0u;i<6u;++i) *(volatile uint8_t *)(packet+3u+4u*i)=(uint8_t)words[i];
  *(volatile uint8_t *)(packet+27u)=(uint8_t)words[6];
  for(uint32_t i=0u;i<6u;++i) {
   *(volatile uint8_t *)(packet+6u+4u*i)=(uint8_t)(words[i]>>24u);
   *(volatile uint8_t *)(packet+5u+4u*i)=(uint8_t)(words[i]>>16u);
   *(volatile uint8_t *)(packet+4u+4u*i)=(uint8_t)(words[i]>>8u);
  }
  *(volatile uint8_t *)(packet+30u)=(uint8_t)(words[6]>>24u);*(volatile uint8_t *)(packet+29u)=(uint8_t)(words[6]>>16u);*(volatile uint8_t *)(packet+28u)=(uint8_t)(words[6]>>8u);
 }
 (void)opencfw_em9305_ll_event_send(packet-5u);
 return 1u;
}
/* Native30bb14..30bb1e,30bb20..30bb2a,30bdc4..30bdce,
 * 30bdd0..30bdda: independent fresh live product pointer getters. */
uint32_t opencfw_em9305_ll_test_30bb14(void)
{
 uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
 return *(volatile uint16_t *)(config+38u);
}
uint32_t opencfw_em9305_ll_test_30bb20(void)
{
 uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
 return *(volatile uint8_t *)(config+35u);
}
uint32_t opencfw_em9305_ll_test_30bdc4(void)
{
 uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
 return *(volatile uint16_t *)(config+44u);
}
uint32_t opencfw_em9305_ll_test_30bdd0(void)
{
 uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
 return *(volatile uint8_t *)(config+42u);
}
/* Native308b14..308b1e: halfword test interval write. */
uint32_t opencfw_em9305_ll_test_interval_308b14(uint32_t value)
{
 *(volatile uint16_t *)(uintptr_t)0x805af4u=(uint16_t)value;
 return 0u;
}
/* Native30d35c..30d376: modulo-halfword interval gate. */
uint32_t opencfw_em9305_ll_test_30d35c(uint32_t value)
{
 if(((value-1u)&65535u)>0xb53fu) return 18u;
 return opencfw_em9305_ll_test_interval_308b14(value);
}
/* Native306f0c..306f42: link then stream quality output; misses leave
 * destination untouched and return2. Stream marker selects127 sentinel. */
uint32_t opencfw_em9305_ll_test_quality_306f0c(uint32_t id,uintptr_t output)
{
 uintptr_t record=opencfw_em9305_ll_link_find_31ab88(id);
 if(record!=0u) {
  uint32_t value=*(volatile uint8_t *)(record+380u);
  *(volatile uint8_t *)output=(uint8_t)value;
  return 0u;
 }
 record=opencfw_em9305_ll_stream_find_31ab14(id);
 if(record==0u) return 2u;
 uintptr_t state=*(volatile uint32_t *)(record+4u);
 uint32_t value=127u;
 if(*(volatile uint8_t *)(state+3u)==0u) value=*(volatile uint8_t *)(record+100u);
 *(volatile uint8_t *)output=(uint8_t)value;
 return 0u;
}
/* Native30bd18..30bd30: primary link/stream query, then slot fallback. */
uint32_t opencfw_em9305_ll_test_30bd18(uint32_t id,uintptr_t output)
{
 if(opencfw_em9305_ll_test_quality_306f0c(id,output)!=0u)
  return opencfw_em9305_ll_connection_quality_30be68(id,output);
 return 0u;
}

/* Native330f08..330f46: three mixed-width reloads per word preserve aliases. */
uint32_t opencfw_em9305_ll_test_response_330f08(uintptr_t packet,uint32_t status,uint32_t id,uintptr_t input)
{
 *(volatile uint8_t *)(packet+1u)=(uint8_t)id;
 *(volatile uint8_t *)packet=(uint8_t)status;
 *(volatile uint8_t *)(packet+2u)=(uint8_t)(id>>8u);
 for(uint32_t index=0u;index<3u;++index) {
  uintptr_t source=input+4u*index,destination=packet+3u+4u*index;
  *(volatile uint8_t *)destination=(uint8_t)*(volatile uint32_t *)source;
  *(volatile uint8_t *)(destination+1u)=(uint8_t)(*(volatile uint32_t *)source>>8u);
  *(volatile uint8_t *)(destination+2u)=(uint8_t)*(volatile uint16_t *)(source+2u);
  *(volatile uint8_t *)(destination+3u)=*(volatile uint8_t *)(source+3u);
 }
 return (uint32_t)packet;
}

/* Native30bc3c tail branch to Native306ed4..306ee6: ordered byte copies. */
uint32_t opencfw_em9305_ll_test_30bc3c(uintptr_t output)
{
 uint32_t low=*(volatile uint8_t *)(uintptr_t)0x805af4u;
 *(volatile uint8_t *)output=(uint8_t)low;
 uint32_t high=*(volatile uint8_t *)(uintptr_t)0x805af5u;
 *(volatile uint8_t *)(output+1u)=(uint8_t)high;
 return 2u;
}
/* Native306a9c..306ab0: stream counters; byte108 return toggles bit0. */
uint32_t opencfw_em9305_ll_test_stream_counters_306a9c(uintptr_t record,uintptr_t output)
{
 uint32_t flag=*(volatile uint8_t *)(record+108u);
 if(flag!=0u) {
  uint32_t second=*(volatile uint32_t *)(record+92u);
  uint32_t first=*(volatile uint32_t *)(record+88u);
  *(volatile uint32_t *)(output+4u)=second;
  *(volatile uint32_t *)output=first;
  uint32_t third=*(volatile uint32_t *)(record+96u);
  *(volatile uint32_t *)(output+8u)=third;
 }
 return flag^1u;
}
/* Native306ae0..306b12: link snapshot, reset-state zero output or status12. */
uint32_t opencfw_em9305_ll_test_link_counters_306ae0(uintptr_t record,uintptr_t output)
{
 if(*(volatile uint8_t *)(record+549u)!=0u) {
  uint32_t first=*(volatile uint32_t *)(record+568u);
  uint32_t second=*(volatile uint32_t *)(record+572u);
  uint32_t third=*(volatile uint32_t *)(record+576u);
  *(volatile uint32_t *)output=first;
  *(volatile uint32_t *)(output+4u)=second;
  *(volatile uint32_t *)(output+8u)=third;
  return 0u;
 }
 if(*(volatile uint8_t *)(record+548u)==0u) return 12u;
 *(volatile uint32_t *)(output+8u)=0u;
 *(volatile uint32_t *)(output+4u)=0u;
 *(volatile uint32_t *)output=0u;
 return 0u;
}
/* Native307498..3074be: first link then stream; misses do not write output. */
uint32_t opencfw_em9305_ll_test_counters_307498(uint32_t id,uintptr_t output)
{
 uintptr_t record=opencfw_em9305_ll_link_find_31ab88(id);
 if(record!=0u) return opencfw_em9305_ll_test_link_counters_306ae0(record,output);
 record=opencfw_em9305_ll_stream_find_31ab14(id);
 if(record!=0u) return opencfw_em9305_ll_test_stream_counters_306a9c(record,output);
 return 2u;
}
/* Native30c2bc..30c2c6: explicitly discard lower query status. */
uint32_t opencfw_em9305_ll_test_30c2bc(uint32_t id,uintptr_t output)
{
 (void)opencfw_em9305_ll_test_counters_307498(id,output);
 return 0u;
}
/* Native317654..31767e: stream counter enable, busy flags read separately. */
uint32_t opencfw_em9305_ll_test_stream_enable_317654(uintptr_t record,uint32_t value)
{
 if(*(volatile uint8_t *)(record+108u)!=0u) return 12u;
 if(*(volatile uint8_t *)(record+109u)!=0u) return 12u;
 *(volatile uint8_t *)(record+116u)=(uint8_t)value;
 *(volatile uint8_t *)(record+110u)=1u;
 *(volatile uint16_t *)(record+108u)=1u;
 *(volatile uint32_t *)(record+88u)=0u;
 *(volatile uint32_t *)(record+92u)=0u;
 *(volatile uint32_t *)(record+96u)=0u;
 return 0u;
}
/* Native30c2d4 tail branch to Native3074c0..307500: link/stream enable. */
uint32_t opencfw_em9305_ll_test_30c2d4(uint32_t id,uint32_t value)
{
 uintptr_t record=opencfw_em9305_ll_link_find_31ab88(id);
 if(record!=0u) {
  *(volatile uint32_t *)(record+576u)=0u;
  *(volatile uint32_t *)(record+572u)=0u;
  *(volatile uint32_t *)(record+568u)=0u;
  *(volatile uint8_t *)(record+580u)=(uint8_t)value;
  *(volatile uint8_t *)(record+549u)=1u;
  *(volatile uint8_t *)(record+581u)=(uint8_t)(value!=0u);
  return 0u;
 }
 record=opencfw_em9305_ll_stream_find_31ab14(id);
 if(record==0u) return 2u;
 return opencfw_em9305_ll_test_stream_enable_317654(record,value);
}
/* Native30c2d8 tail branch to Native307504..307562: query then disable.
 * Link flags are reread after writing caller output to preserve aliases. */
uint32_t opencfw_em9305_ll_test_30c2d8(uint32_t id,uintptr_t output)
{
 uintptr_t record=opencfw_em9305_ll_link_find_31ab88(id);
 if(record!=0u) {
  if(*(volatile uint8_t *)(record+549u)!=0u) {
   uint32_t result=opencfw_em9305_ll_test_link_counters_306ae0(record,output);
   uint32_t pending=*(volatile uint8_t *)(record+548u);
   *(volatile uint8_t *)(record+549u)=0u;
   if(pending!=0u) *(volatile uint8_t *)(record+548u)=0u;
   return result;
  }
  if(*(volatile uint8_t *)(record+548u)==0u) return 12u;
  *(volatile uint8_t *)(record+548u)=0u;
  return 0u;
 }
 record=opencfw_em9305_ll_stream_find_31ab14(id);
 if(record==0u) return 2u;
 uint32_t result=opencfw_em9305_ll_test_stream_counters_306a9c(record,output);
 *(volatile uint8_t *)(record+109u)=1u;
 return result;
}
/* Native31ab50..31ab86: active channel match; ADD2 stride35*4=140. */
uintptr_t opencfw_em9305_ll_test_channel_find_31ab50(uint32_t id)
{
 uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
 uint32_t count=*(volatile uint8_t *)(config+52u);
 if(count==0u) return 0u;
 uintptr_t row=*(volatile uint32_t *)(uintptr_t)0x805c64u;
 for(uint32_t i=0u;i<count;++i,row+=140u)
  if(*(volatile uint8_t *)row!=0u && *(volatile uint8_t *)(row+6u)==id) return row;
 return 0u;
}
/* Native317a10..317a42: stream test mode with two busy and product gates. */
uint32_t opencfw_em9305_ll_test_stream_mode_317a10(uintptr_t record,uint32_t value)
{
 if(*(volatile uint8_t *)(record+108u)!=0u) return 12u;
 if(*(volatile uint8_t *)(record+109u)!=0u) return 12u;
 if(*(volatile uint8_t *)(uintptr_t)0x805adcu==0u) return 7u;
 *(volatile uint8_t *)(record+116u)=(uint8_t)value;
 *(volatile uint32_t *)(record+112u)=0u;
 *(volatile uint16_t *)(record+108u)=1u;
 return 0u;
}
/* Native30c2dc tail branch to Native307564..3075c8: link/stream test mode.
 * Channel pointer is dereferenced only after native gates; no new null guard. */
uint32_t opencfw_em9305_ll_test_30c2dc(uint32_t id,uint32_t value)
{
 uintptr_t record=opencfw_em9305_ll_link_find_31ab88(id);
 if(record==0u) {
  record=opencfw_em9305_ll_stream_find_31ab14(id);
  if(record==0u) return 2u;
  return opencfw_em9305_ll_test_stream_mode_317a10(record,value);
 }
 uintptr_t channel=opencfw_em9305_ll_test_channel_find_31ab50(*(volatile uint8_t *)(record+11u));
 if(*(volatile uint8_t *)(record+512u)==0u && *(volatile uint8_t *)(record+10u)==0u) return 17u;
 if(*(volatile uint8_t *)(record+513u)==0u && *(volatile uint8_t *)(record+10u)==1u) return 17u;
 if(value>=3u) return 18u;
 uint32_t setting=*(volatile uint32_t *)(channel+48u);
 *(volatile uint32_t *)(record+564u)=0u;
 *(volatile uint8_t *)(record+556u)=(uint8_t)value;
 *(volatile uint8_t *)(record+548u)=1u;
 *(volatile uint32_t *)(record+552u)=setting;
 return 0u;
}
/* Native30c724 tail branch to Native3081a4..3081d8: 28-byte link/stream
 * record snapshot; failure leaves caller scratch bytes untouched. */
uint32_t opencfw_em9305_ll_test_30c724(uint32_t id,uintptr_t output)
{
 uintptr_t record=opencfw_em9305_ll_link_find_31ab88(id);
 if(record!=0u) {
  (void)opencfw_em9305_memcpy((void *)output,(const void *)(record+584u),28u);
  return 0u;
 }
 record=opencfw_em9305_ll_stream_find_31ab14(id);
 if(record==0u) return 2u;
 uintptr_t state=*(volatile uint32_t *)(record+4u);
 if(*(volatile uint8_t *)(state+3u)!=0u) return 2u;
 (void)opencfw_em9305_memcpy((void *)output,(const void *)(record+60u),28u);
 return 0u;
}
/* Native30c728 tail branch to Native3081dc..3082ac: link/stream timing
 * query. Named MPYW/MPYWHL preserve native arithmetic. Store order differs
 * across stream phase branches and channel values reload after first store. */
uint32_t opencfw_em9305_ll_test_30c728(uint32_t id,uintptr_t first,uintptr_t second,uintptr_t third)
{
 uintptr_t record=opencfw_em9305_ll_link_find_31ab88(id);
 if(record!=0u) {
  uintptr_t channel=opencfw_em9305_ll_test_channel_find_31ab50(*(volatile uint8_t *)(record+11u));
  uint32_t mode=*(volatile uint8_t *)(record+10u);
  if(mode<2u && *(volatile uint8_t *)(record+512u+mode)==0u) return 12u;
  if(*(volatile uint8_t *)(record+624u)==0u) return 12u;
  uint32_t periods=*(volatile uint16_t *)(record+14u);
  uint32_t stride=*(volatile uint8_t *)(record+512u+(mode!=0u));
  uint32_t value,operand=periods-1u;
  __asm__ volatile("mpyw %0,%1,%2":"=r"(value):"r"(operand),"r"(stride));
  *(volatile uint16_t *)first=(uint16_t)value;
  uint32_t ticks=*(volatile uint16_t *)(channel+20u);
  uint32_t anchor=*(volatile uint32_t *)(channel+48u),factor=(uint32_t)-1250;
  __asm__ volatile("mpywhl %0,%1,%2":"=r"(value):"r"(ticks),"r"(factor));
  *(volatile uint32_t *)second=value+anchor;
 } else {
  record=opencfw_em9305_ll_stream_find_31ab14(id);
  if(record==0u) return 2u;
  uintptr_t state=*(volatile uint32_t *)(record+4u);
  if(*(volatile uint8_t *)(state+3u)!=1u) return 12u;
  uint32_t phase=*(volatile uint8_t *)(state+30u);
  if(phase==1u) {
   if(*(volatile uint8_t *)(record+32u)==0u) return 17u;
   uint32_t start=*(volatile uint32_t *)(state+16u);
   uint32_t end=*(volatile uint32_t *)(state+304u);
   uint32_t periods=*(volatile uint32_t *)(state+32u);
   uint32_t stride=*(volatile uint8_t *)(state+24u),delta=end-start,value,span;
   __asm__ volatile("mpywhl %0,%1,%2":"=r"(value):"r"(delta),"r"(stride));
   periods-=1u;
   __asm__ volatile("mpyw %0,%1,%2":"=r"(span):"r"(periods),"r"(stride));
   *(volatile uint32_t *)second=value;
   *(volatile uint16_t *)first=(uint16_t)span;
  } else {
   if(phase!=0u) return 17u;
   uint32_t remaining=*(volatile uint32_t *)(state+36u);
   uint32_t periods=*(volatile uint32_t *)(state+32u);
   if((remaining|periods)==0u) return 12u;
   uint32_t start=*(volatile uint32_t *)(state+16u);
   uint32_t end=*(volatile uint32_t *)(state+304u);
   uint32_t stride=*(volatile uint8_t *)(state+24u),delta=end-start,value,span;
   periods-=1u;
   __asm__ volatile("mpyw %0,%1,%2":"=r"(span):"r"(periods),"r"(stride));
   __asm__ volatile("mpywhl %0,%1,%2":"=r"(value):"r"(delta),"r"(stride));
   *(volatile uint16_t *)first=(uint16_t)span;
   *(volatile uint32_t *)second=value;
  }
 }
 *(volatile uint32_t *)third=0u;
 return 0u;
}
extern uint32_t opencfw_em9305_ll_test_action_31b7e4(uintptr_t);
extern uint32_t opencfw_em9305_ll_test_action_31b8a8(uintptr_t);
/* Native30cb24 tail branch to Native30843c..308538: link mask actions and
 * stream role action. Genuine children own scratch fields beyond id/+16. */
uint32_t opencfw_em9305_ll_test_30cb24(uint32_t id,uint32_t mask)
{
 _Alignas(4) uint8_t scratch[36];
 uintptr_t record=opencfw_em9305_ll_link_find_31ab88(id);
 if(record!=0u) {
  if(mask==0u || (mask&~3u)!=0u) return 18u;
  if((mask&1u)!=0u && *(volatile uint8_t *)(record+528u)==255u) return 12u;
  if((mask&2u)!=0u && *(volatile uint8_t *)(record+532u)==255u) return 12u;
  if((mask&1u)!=0u) {
   *(uint32_t *)(scratch+16u)=(uint32_t)(record+528u);
   *(volatile uint32_t *)(uintptr_t)0x805cb0u=(uint32_t)(record+528u);
   *(uint16_t *)scratch=*(volatile uint16_t *)(record+8u);
   (void)opencfw_em9305_ll_test_action_31b7e4((uintptr_t)scratch);
   *(volatile uint8_t *)(record+528u)=255u;
   *(volatile uint32_t *)(uintptr_t)0x805cb0u=0u;
  }
  if((mask&2u)!=0u) {
   *(uint32_t *)(scratch+16u)=(uint32_t)(record+532u);
   *(uint16_t *)scratch=*(volatile uint16_t *)(record+8u);
   (void)opencfw_em9305_ll_test_action_31b8a8((uintptr_t)scratch);
   *(volatile uint8_t *)(record+532u)=255u;
  }
  return 0u;
 }
 record=opencfw_em9305_ll_stream_find_31ab14(id);
 if(record==0u) return 2u;
 if((mask&1u)!=0u && *(volatile uint8_t *)(record+36u)==255u) return 12u;
 if((mask&2u)!=0u && *(volatile uint8_t *)(record+44u)==255u) return 12u;
 uintptr_t state=*(volatile uint32_t *)(record+4u);
 *(uint16_t *)scratch=*(volatile uint16_t *)(record+2u);
 if(*(volatile uint8_t *)(state+3u)!=0u) {
  if(*(volatile uint8_t *)(record+36u)==255u) return 12u;
  *(volatile uint32_t *)(uintptr_t)0x805cb0u=(uint32_t)(record+36u);
  *(uint32_t *)(scratch+16u)=(uint32_t)(record+36u);
  (void)opencfw_em9305_ll_test_action_31b7e4((uintptr_t)scratch);
  *(volatile uint8_t *)(record+36u)=255u;
  *(volatile uint32_t *)(uintptr_t)0x805cb0u=0u;
 } else {
  if(*(volatile uint8_t *)(record+44u)==255u) return 12u;
  *(uint32_t *)(scratch+16u)=(uint32_t)(record+44u);
  (void)opencfw_em9305_ll_test_action_31b8a8((uintptr_t)scratch);
  *(volatile uint8_t *)(record+44u)=255u;
 }
 return 0u;
}
/* Native31b7e4..31b7f8: marked first action forwards to required callback.
 * Non-one markers are returned directly; callback presence is native-required. */
uint32_t opencfw_em9305_ll_test_action_31b7e4(uintptr_t request)
{
 uintptr_t slot=*(volatile uint32_t *)(request+16u);
 uint32_t marker=*(volatile uint8_t *)slot;
 if(marker!=1u) return marker;
 uint32_t id=*(volatile uint16_t *)(slot+2u);
 uintptr_t callback=*(volatile uint32_t *)(uintptr_t)0x8027fcu;
 return ((uint32_t (*)(uint32_t,uint32_t))callback)(id,0u);
}
/* Native31b8a8..31b914: second action uses slot+4 marker/queue. Drain each
 * queued event before incrementing the protected released-event counter. */
uint32_t opencfw_em9305_ll_test_action_31b8a8(uintptr_t request)
{
 uintptr_t queue=*(volatile uint32_t *)(request+16u)+4u;
 uint32_t marker=*(volatile uint8_t *)queue;
 if(marker!=0u && marker!=1u) return marker;
 uint8_t handler;
 if(marker==1u) {
  uint32_t id=*(volatile uint16_t *)(queue+10u);
  uintptr_t callback=*(volatile uint32_t *)(uintptr_t)0x8027fcu;
  (void)((uint32_t (*)(uint32_t,uint32_t))callback)(id,1u);
 }
 for(;;) {
  uintptr_t event=opencfw_em9305_wsf_event_remove(queue,(uintptr_t)&handler);
  if(event==0u) return 0u;
  (void)opencfw_em9305_wsf_event_release(event);
  (void)opencfw_em9305_wsf_critical_enter();
  uint32_t count=*(volatile uint8_t *)(uintptr_t)0x805addu;
  *(volatile uint8_t *)(uintptr_t)0x805addu=(uint8_t)(count+1u);
  (void)opencfw_em9305_wsf_critical_exit();
 }
}

/* Native32385c..323878: four-byte packet header, retaining source reloads
 * after each destination store for overlapping metadata/destination buffers. */
uint32_t opencfw_em9305_ll_packet_header_32385c(uintptr_t packet,uintptr_t metadata)
{
 uint32_t kind=*(volatile uint8_t *)(metadata+2u);
 uint32_t handler=*(volatile uint16_t *)metadata;
 uint32_t upper=((kind<<12u)|handler)>>8u;
 *(volatile uint8_t *)packet=(uint8_t)handler;
 *(volatile uint8_t *)(packet+1u)=(uint8_t)upper;
 uint32_t low=*(volatile uint8_t *)(metadata+4u);
 *(volatile uint8_t *)(packet+2u)=(uint8_t)low;
 uint32_t high=*(volatile uint8_t *)(metadata+5u);
 *(volatile uint8_t *)(packet+3u)=(uint8_t)high;
 return 4u;
}
/* Native3252dc..325322: take the primary queue and rewrite its native header. */
uintptr_t opencfw_em9305_ll_primary_take_3252dc(uintptr_t record)
{
 uint8_t handler;
 uintptr_t packet=opencfw_em9305_wsf_event_remove(record+368u,(uintptr_t)&handler);
 if(packet!=0u) {
  uint32_t kind=*(volatile uint8_t *)(packet+2u)&3u;
  uint32_t queue_handler=handler;
  uint32_t count=*(volatile uint8_t *)(packet+3u);
  _Alignas(2) uint8_t metadata[6];
  *(uint16_t *)metadata=(uint16_t)queue_handler;
  *(uint16_t *)(metadata+4u)=(uint16_t)count;
  metadata[2]=(uint8_t)(kind==1u?1u:kind==2u?2u:3u);
  (void)opencfw_em9305_ll_packet_header_32385c(packet,(uintptr_t)metadata);
 }
 return packet;
}
/* Native30853c..30856e: reverse primary scan. A zero configured count
 * underflows natively; no invented empty-count guard is added here. */
uintptr_t opencfw_em9305_ll_primary_pending_30853c(void)
{
 uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
 uintptr_t base=*(volatile uint32_t *)(uintptr_t)0x805c70u;
 uint32_t index=*(volatile uint8_t *)(config+34u);
 do {
  --index;
  uint32_t offset;
  uint32_t stride=912u;
  __asm__ volatile("mpywhl %0,%1,%2":"=r"(offset):"r"(index),"r"(stride));
  uintptr_t record=base+offset;
  if(*(volatile uint8_t *)record!=0u) {
   uintptr_t packet=opencfw_em9305_ll_primary_take_3252dc(record);
   if(packet!=0u) return packet;
   base=*(volatile uint32_t *)(uintptr_t)0x805c70u;
  }
 } while(index!=0u);
 return 0u;
}
/* Native317624..317650: enabled stream or state-zero/one consumes queue. */
uintptr_t opencfw_em9305_ll_stream_take_317624(uintptr_t record)
{
 if(*(volatile uint8_t *)(record+108u)==0u) {
  uint32_t state=*(volatile uint8_t *)(record+44u);
  if(state!=0u && state!=1u) return 0u;
 }
 uint8_t handler;
 return opencfw_em9305_wsf_event_remove(record+48u,(uintptr_t)&handler);
}
/* Native30858c..308612: forward link scan followed by eligible streams.
 * Limits are reread on every iteration; config pointers reload after a
 * child returns zero, while the record base reloads every iteration. */
uintptr_t opencfw_em9305_ll_link_pending_30858c(void)
{
 if(*(volatile uint32_t *)(uintptr_t)0x805c68u!=0u) {
  uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
  for(uint32_t index=0u;index<*(volatile uint8_t *)(config+53u);++index) {
   uintptr_t base=*(volatile uint32_t *)(uintptr_t)0x805c68u;
   uint32_t offset,stride=656u;
   __asm__ volatile("mpywhl %0,%1,%2":"=r"(offset):"r"(index),"r"(stride));
   uintptr_t record=base+offset;
   if(*(volatile uint8_t *)record!=0u && *(volatile uint8_t *)(record+532u)==0u) {
    uintptr_t packet=opencfw_em9305_ll_pending_packet_take_31ba54(record+532u);
    if(packet!=0u) return packet;
    config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
   }
  }
 }
 if(*(volatile uint32_t *)(uintptr_t)0x805c40u==0u) return 0u;
 uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
 for(uint32_t index=0u;index<*(volatile uint8_t *)(config+58u);++index) {
  uintptr_t base=*(volatile uint32_t *)(uintptr_t)0x805c40u;
  uintptr_t record=base+(index<<8u);
  if(*(volatile uint8_t *)record!=0u) {
   uintptr_t state=*(volatile uint32_t *)(record+4u);
   if(*(volatile uint8_t *)(state+3u)==0u && *(volatile uint8_t *)(record+44u)==0u) {
    uintptr_t packet=opencfw_em9305_ll_stream_take_317624(record);
    if(packet!=0u) return packet;
    config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
   }
  }
 }
 return 0u;
}

/* Native30b1ac tail to Native306b70..306b7c: byte increment wraps before
 * unsigned LO comparison. Accepted original markers are 255, zero and one. */
uint32_t opencfw_em9305_ll_test_30b1ac(uintptr_t request)
{
 uint32_t marker=(uint8_t)(*(volatile uint8_t *)(request+1u)+1u);
 return marker<3u?0u:18u;
}

extern uint32_t opencfw_em9305_ll_test_submit_31bb20(uintptr_t,uintptr_t,uint32_t);
/* Native30e050 tail to Native309b84..309cb6: construct the complete native
 * 36-byte test descriptor. Side-effecting reads on rejected role paths are
 * retained; submit owns the remaining scheduling policy. */
uint32_t opencfw_em9305_ll_test_30e050(uintptr_t request)
{
 _Alignas(4) uint8_t descriptor[36];
 uint32_t submit_context;
 (void)opencfw_em9305_memset(descriptor,0u,36u);
 uint32_t parameter=*(volatile uint8_t *)(request+3u);
 if(parameter>=2u && parameter!=255u) return 18u;
 if(*(volatile uint8_t *)(request+4u)==3u && *(volatile uint8_t *)(request+16u)!=0u) return 18u;
 uintptr_t record=opencfw_em9305_ll_link_find_31ab88(*(volatile uint16_t *)request);
 if(record!=0u) {
  if(*(volatile uint8_t *)(record+10u)==1u && *(volatile uint8_t *)(record+3u)==1u) return 12u;
  uintptr_t channel=opencfw_em9305_ll_test_channel_find_31ab50(*(volatile uint8_t *)(record+11u));
  uint32_t mode=*(volatile uint8_t *)(record+10u);
  uint32_t id=*(volatile uint16_t *)(record+8u);
  uint32_t role=*(volatile uint8_t *)(request+2u);
  uint32_t counter=*(volatile uint32_t *)(record+36u);
  *(uint16_t *)descriptor=(uint16_t)id;
  descriptor[2]=(uint8_t)role;
  uint32_t anchor=*(volatile uint32_t *)(record+16u);
  uint32_t timing=*(volatile uint32_t *)(record+(mode==1u?496u:492u));
  *(uint32_t *)(descriptor+12u)=anchor;
  *(uint32_t *)(descriptor+8u)=counter+1u;
  *(uint32_t *)(descriptor+4u)=timing;
  uintptr_t base=*(volatile uint32_t *)(uintptr_t)0x805c70u;
  submit_context=*(volatile uint32_t *)(channel+36u);
  uint32_t index=*(volatile uint16_t *)(record+6u);
  if(role!=0u && role!=1u) return 12u;
  uint32_t timer_high=*(volatile uint32_t *)(uintptr_t)0x805b44u;
  uint32_t timer_low=*(volatile uint32_t *)(uintptr_t)0x805b40u;
  uint32_t offset;
  __asm__ volatile("mpyuw %0,%1,912":"=r"(offset):"r"(index));
  *(uint32_t *)(descriptor+16u)=(uint32_t)(record+(role==0u?528u:532u));
  if(role==0u) {
   *(uint32_t *)(descriptor+24u)=timer_high;
   *(uint32_t *)(descriptor+20u)=timer_low;
   *(uint32_t *)(descriptor+32u)=*(volatile uint32_t *)(base+offset+520u);
   *(uint32_t *)(descriptor+28u)=*(volatile uint32_t *)(base+offset+516u);
  } else {
   *(uint32_t *)(descriptor+32u)=timer_high;
   *(uint32_t *)(descriptor+28u)=timer_low;
   *(uint32_t *)(descriptor+24u)=*(volatile uint32_t *)(base+offset+520u);
   *(uint32_t *)(descriptor+20u)=*(volatile uint32_t *)(base+offset+516u);
  }
 } else {
  record=opencfw_em9305_ll_stream_find_31ab14(*(volatile uint16_t *)request);
  if(record==0u) return 2u;
  uintptr_t state=*(volatile uint32_t *)(record+4u);
  uint32_t id=*(volatile uint16_t *)(record+2u);
  uint32_t role=*(volatile uint8_t *)(request+2u);
  *(uint16_t *)descriptor=(uint16_t)id;
  uint32_t timing=*(volatile uint32_t *)(state+16u);
  uint32_t counter=*(volatile uint32_t *)(state+32u);
  uint32_t stride=*(volatile uint8_t *)(state+24u);
  *(uint32_t *)(descriptor+4u)=timing;
  uint32_t anchor=*(volatile uint32_t *)(state+40u);
  uint32_t span;
  ++counter;
  __asm__ volatile("mpywhl %0,%1,%2":"=r"(span):"r"(counter),"r"(stride));
  submit_context=*(volatile uint32_t *)(state+304u);
  descriptor[2]=(uint8_t)role;
  *(uint32_t *)(descriptor+12u)=anchor;
  *(uint32_t *)(descriptor+8u)=span;
  if(role==1u) {
   if(*(volatile uint8_t *)(state+3u)!=0u) return 12u;
   *(uint32_t *)(descriptor+16u)=(uint32_t)(record+44u);
  } else {
   if(role!=0u || *(volatile uint8_t *)(state+3u)!=1u) return 12u;
   *(uint32_t *)(descriptor+16u)=(uint32_t)(record+36u);
  }
 }
 return opencfw_em9305_ll_test_submit_31bb20((uintptr_t)descriptor,request,submit_context);
}

extern uint32_t opencfw_em9305_ll_test_schedule_first_31b7fc(uintptr_t,uintptr_t,uint32_t);
extern uint32_t opencfw_em9305_ll_test_schedule_second_31b918(uintptr_t,uintptr_t);
/* Native31bb20..31bbac: submit by role, sentinel and requested marker.
 * Callbacks may mutate request/descriptor state, requiring the native reloads. */
uint32_t opencfw_em9305_ll_test_submit_31bb20(uintptr_t descriptor,uintptr_t request,uint32_t context)
{
 uint32_t role=*(volatile uint8_t *)(request+2u);
 if(role!=0u && role!=1u) return 0u;
 uintptr_t slot=*(volatile uint32_t *)(descriptor+16u);
 if(*(volatile uint8_t *)slot!=255u) return 12u;
 if(*(volatile uint8_t *)(request+3u)==255u) return 0u;
 if(role==1u) {
  (void)opencfw_em9305_ll_test_action_31b8a8(descriptor);
  slot=*(volatile uint32_t *)(descriptor+16u);
  uint32_t marker=*(volatile uint8_t *)(request+3u);
  *(volatile uint8_t *)slot=(uint8_t)marker;
  if(*(volatile uint8_t *)(request+3u)==255u) return 0u;
  return opencfw_em9305_ll_test_schedule_second_31b918(descriptor,request);
 }
 *(volatile uint32_t *)(uintptr_t)0x805cb0u=(uint32_t)slot;
 (void)opencfw_em9305_ll_test_action_31b7e4(descriptor);
 uint32_t marker=*(volatile uint8_t *)(request+3u);
 slot=*(volatile uint32_t *)(descriptor+16u);
 *(volatile uint32_t *)(uintptr_t)0x805cb0u=0u;
 *(volatile uint8_t *)slot=(uint8_t)marker;
 if(*(volatile uint8_t *)(request+3u)==255u) return 0u;
 return opencfw_em9305_ll_test_schedule_first_31b7fc(descriptor,request,context);
}

/* Native31b918..31b9aa: prepare the second-role native scheduling callback.
 * Scratch padding remains unspecified; only authenticated fields are written. */
uint32_t opencfw_em9305_ll_test_schedule_second_31b918(uintptr_t descriptor,uintptr_t request)
{
 uintptr_t slot=*(volatile uint32_t *)(descriptor+16u);
 uint32_t marker=*(volatile uint8_t *)slot;
 if(marker==0u) {
  *(volatile uint32_t *)(slot+8u)=0u;
  *(volatile uint32_t *)(slot+4u)=0u;
  *(volatile uint8_t *)(slot+12u)=0u;
  return 0u;
 }
 if(marker==255u) return 0u;
 if(marker!=1u) return 18u;
 uintptr_t callback=*(volatile uint32_t *)(uintptr_t)0x8027f8u;
 uint32_t id=*(volatile uint16_t *)descriptor;
 *(volatile uint32_t *)(slot+8u)=0u;
 *(volatile uint32_t *)(slot+4u)=0u;
 *(volatile uint16_t *)(slot+14u)=(uint16_t)id;
 if(callback==0u) return 18u;
 uint32_t high=*(volatile uint32_t *)(descriptor+24u);
 uint32_t low=*(volatile uint32_t *)(descriptor+20u);
 uint32_t span=*(volatile uint32_t *)(descriptor+8u);
 uint32_t type=*(volatile uint8_t *)(request+4u);
 uint32_t interval=*(volatile uint16_t *)(request+6u);
 uint32_t length=*(volatile uint16_t *)(request+8u);
 uint32_t flag=*(volatile uint8_t *)(request+16u);
 uint32_t data=*(volatile uint32_t *)(request+20u);
 uint32_t anchor=*(volatile uint32_t *)(descriptor+12u);
 uint32_t other_low=*(volatile uint32_t *)(descriptor+28u);
 uint32_t other_high=*(volatile uint32_t *)(descriptor+32u);
 _Alignas(4) uint8_t fields[52];
 *(uint32_t *)(fields+28u)=0u;
 fields[48]=0u;
 *(uint32_t *)(fields+36u)=high;
 *(uint32_t *)(fields+32u)=low;
 fields[16]=(uint8_t)flag;
 *(uint32_t *)(fields+20u)=data;
 *(uint32_t *)(fields+24u)=anchor;
 *(uint32_t *)(fields+44u)=other_high;
 *(uint32_t *)(fields+40u)=other_low;
 id=*(volatile uint16_t *)(slot+14u);
 fields[0]=1u;
 *(uint32_t *)(fields+4u)=span;
 fields[8]=(uint8_t)type;
 *(uint16_t *)(fields+10u)=(uint16_t)interval;
 *(uint16_t *)(fields+12u)=(uint16_t)length;
 uint32_t result=((uint32_t (*)(uint32_t,uintptr_t))callback)(id,(uintptr_t)fields);
 if(result!=0u) return 0u;
 *(volatile uint8_t *)slot=255u;
 return 13u;
}

extern uint32_t opencfw_em9305_ll_test_complete_31bad0(uint32_t,uint32_t,uint32_t,uintptr_t,uint32_t);
extern uint32_t opencfw_em9305_ll_test_timer_31c490(uint32_t,uint32_t);
/* Native31b7fc..31b8a4: first-role callback, cached slot, reload descriptor
 * id after a successful callback before timer handoff. Timer return ignored. */
uint32_t opencfw_em9305_ll_test_schedule_first_31b7fc(uintptr_t descriptor,uintptr_t request,uint32_t context)
{
 uintptr_t slot=*(volatile uint32_t *)(descriptor+16u);
 uint32_t marker=*(volatile uint8_t *)slot;
 if(marker==0u || marker==255u) return 0u;
 if(marker!=1u) return 18u;
 uint32_t id=*(volatile uint16_t *)descriptor;
 *(volatile uint16_t *)(slot+2u)=(uint16_t)id;
 uintptr_t callback=*(volatile uint32_t *)(uintptr_t)0x8027f8u;
 if(callback==0u) return 18u;
 uint32_t high=*(volatile uint32_t *)(descriptor+24u);
 uint32_t low=*(volatile uint32_t *)(descriptor+20u);
 uint32_t span=*(volatile uint32_t *)(descriptor+8u);
 uint32_t type=*(volatile uint8_t *)(request+4u);
 uint32_t interval=*(volatile uint16_t *)(request+6u);
 uint32_t length=*(volatile uint16_t *)(request+8u);
 uint32_t flag=*(volatile uint8_t *)(request+16u);
 uint32_t data=*(volatile uint32_t *)(request+20u);
 uint32_t anchor=*(volatile uint32_t *)(descriptor+12u);
 uint32_t other_low=*(volatile uint32_t *)(descriptor+28u);
 uint32_t other_high=*(volatile uint32_t *)(descriptor+32u);
 _Alignas(4) uint8_t fields[52];
 *(uint32_t *)(fields+28u)=(uint32_t)(uintptr_t)&opencfw_em9305_ll_test_complete_31bad0;
 fields[48]=0u;
 *(uint32_t *)(fields+36u)=high;
 *(uint32_t *)(fields+32u)=low;
 fields[16]=(uint8_t)flag;
 *(uint32_t *)(fields+20u)=data;
 *(uint32_t *)(fields+24u)=anchor;
 *(uint32_t *)(fields+44u)=other_high;
 *(uint32_t *)(fields+40u)=other_low;
 id=*(volatile uint16_t *)(slot+2u);
 fields[0]=0u;
 *(uint32_t *)(fields+4u)=span;
 fields[8]=(uint8_t)type;
 *(uint16_t *)(fields+10u)=(uint16_t)interval;
 *(uint16_t *)(fields+12u)=(uint16_t)length;
 uint32_t result=((uint32_t (*)(uint32_t,uintptr_t))callback)(id,(uintptr_t)fields);
 if(result!=0u) {
  id=*(volatile uint16_t *)descriptor;
  (void)opencfw_em9305_ll_test_timer_31c490(id,context);
  return 0u;
 }
 *(volatile uint8_t *)slot=255u;
 return 13u;
}

/* Native31bad0..31bb1c: release an active matching test packet, otherwise
 * append callback fields to the six-entry product ring and post event128.
 * Native overlapping 20-byte stride / +24 halfword layout is preserved. */
uint32_t opencfw_em9305_ll_test_complete_31bad0(uint32_t id,uint32_t first,uint32_t second,uintptr_t packet,uint32_t length)
{
 uintptr_t active=*(volatile uint32_t *)(uintptr_t)0x805cb0u;
 if(active!=0u && *(volatile uint16_t *)(active+2u)==id)
  return opencfw_em9305_wsf_event_release(packet);
 uintptr_t ring=(uintptr_t)0x8028d0u;
 uint32_t index=*(volatile uint32_t *)ring;
 uint32_t handler=*(volatile uint8_t *)(uintptr_t)0x805b18u;
 uintptr_t row=ring+index*20u;
 uint32_t next=(index+1u)%6u;
 *(volatile uint32_t *)(row+12u)=first;
 *(volatile uint16_t *)(row+24u)=(uint16_t)length;
 *(volatile uint32_t *)(row+20u)=(uint32_t)packet;
 *(volatile uint32_t *)(row+16u)=second;
 *(volatile uint16_t *)(row+8u)=(uint16_t)id;
 *(volatile uint32_t *)ring=next;
 return opencfw_em9305_wsf_event_post(handler,128u);
}

/* Native31c490..31c4fc: first-role timer payload allocation and callback.
 * Fresh config size controls allocation; captured link/stream size controls
 * callback length. Callback is native-required, without an invented guard. */
uint32_t opencfw_em9305_ll_test_timer_31c490(uint32_t id,uint32_t context)
{
 uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
 uint32_t length=*(volatile uint16_t *)(config+44u);
 uintptr_t record=opencfw_em9305_ll_link_find_31ab88(id);
 uintptr_t slot;
 uint32_t timer;
 if(record!=0u) {
  uintptr_t channel=opencfw_em9305_ll_test_channel_find_31ab50(*(volatile uint8_t *)(record+11u));
  slot=record+528u;
  timer=*(volatile uint32_t *)(channel+36u);
 } else {
  record=opencfw_em9305_ll_stream_find_31ab14(id);
  if(record==0u) return 0u;
  uintptr_t state=*(volatile uint32_t *)(record+4u);
  timer=*(volatile uint32_t *)(state+304u);
  if(timer==context) timer=*(volatile uint32_t *)(state+16u)+context;
  length=*(volatile uint16_t *)(state+6u);
  slot=record+36u;
 }
 uint32_t marker=*(volatile uint8_t *)slot;
 if(marker!=1u) return marker;
 config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
 uint32_t bytes=(uint16_t)(*(volatile uint16_t *)(config+44u)+8u);
 uintptr_t allocation=opencfw_em9305_wsf_event_allocate(bytes);
 if(allocation==0u) return 0u;
 uintptr_t callback=*(volatile uint32_t *)(uintptr_t)0x802800u;
 return ((uint32_t (*)(uint32_t,uintptr_t,uint32_t,uint32_t))callback)(id,allocation+12u,length,timer);
}

/* Native331a8c..331aa2: preserve primary packet only on zero account status. */
uintptr_t opencfw_em9305_dispatch_331a8c(void)
{
 uintptr_t packet=opencfw_em9305_ll_primary_pending_30853c();
 if(packet==0u) return 0u;
 return opencfw_em9305_ll_primary_account_331d60(packet)==0u?packet:0u;
}
/* Native331aa4..331aba: analogous link packet accounting contract. */
uintptr_t opencfw_em9305_dispatch_331aa4(void)
{
 uintptr_t packet=opencfw_em9305_ll_link_pending_30858c();
 if(packet==0u) return 0u;
 return opencfw_em9305_ll_link_dispatch_331d94(packet)==0u?packet:0u;
}
/* Native331abc tail30c93c tail308614: replenish link credit and exit critical. */
uint32_t opencfw_em9305_dispatch_331abc(uint32_t credit)
{ return opencfw_em9305_ll_link_restart_308614(credit); }
/* Native331cbc..331cd8: return unchanged input if notification pending;
 * otherwise store its low byte and post event8 to the current handler. */
uint32_t opencfw_em9305_dispatch_331cbc(uint32_t incoming)
{
 if(*(volatile uint8_t *)(uintptr_t)0x805701u!=0u) return incoming;
 uint32_t handler=*(volatile uint8_t *)(uintptr_t)0x80585cu;
 *(volatile uint8_t *)(uintptr_t)0x805701u=(uint8_t)incoming;
 return opencfw_em9305_wsf_event_post(handler,8u);
}

/* Native331a40..331a88: route types0/1/3 to native queues, release others.
 * Handler is loaded after enqueue, preserving queue-child side effects. */
uint32_t opencfw_em9305_dispatch_331a40(uint32_t type,uintptr_t event)
{
 uintptr_t base=(uintptr_t)0x80585cu;
 uintptr_t queue;
 uint32_t bits;
 if(type==0u) { queue=base+12u;bits=2u; }
 else if(type==1u) { queue=base+4u;bits=1u; }
 else if(type==3u) { queue=base+28u;bits=16u; }
 else return opencfw_em9305_wsf_event_release(event);
 (void)opencfw_em9305_ll_event_enqueue(queue,0u,event);
 uint32_t handler=*(volatile uint8_t *)base;
 return opencfw_em9305_wsf_event_post(handler,bits);
}

/* Native331b3c..331bb6: gated two native data events. Enqueue status does
 * not replace the native handled return; exact header/copy order is retained. */
uint32_t opencfw_em9305_dispatch_331b3c(uintptr_t message)
{
 uint32_t type=*(volatile uint8_t *)(message+2u);
 uintptr_t packet;
 if(type==19u) {
  if((*(volatile uint8_t *)(uintptr_t)0x8056f8u&128u)==0u) return 0u;
  if((*(volatile uint8_t *)(uintptr_t)0x8056efu&32u)==0u) return 0u;
  packet=opencfw_em9305_ll_event_allocate(62u,66u);
  if(packet==0u) return 0u;
  *(volatile uint8_t *)(packet+1u)=0u;
  (void)opencfw_em9305_memcpy((void *)(packet+2u),(const void *)(message+5u),32u);
  *(volatile uint8_t *)packet=8u;
  (void)opencfw_em9305_memcpy((void *)(packet+34u),(const void *)(message+37u),32u);
 } else if(type==20u) {
  if((*(volatile uint8_t *)(uintptr_t)0x8056f9u&1u)==0u) return 0u;
  if((*(volatile uint8_t *)(uintptr_t)0x8056efu&32u)==0u) return 0u;
  packet=opencfw_em9305_ll_event_allocate(62u,34u);
  if(packet==0u) return 0u;
  *(volatile uint8_t *)packet=9u;
  *(volatile uint8_t *)(packet+1u)=*(volatile uint8_t *)(message+4u);
  (void)opencfw_em9305_memcpy((void *)(packet+2u),(const void *)(message+5u),32u);
 } else return 0u;
 (void)opencfw_em9305_ll_event_send(packet-2u);
 return 1u;
}

/* Native331c20..331cba: release/account receive events, reload completion
 * callback after release and always post event4 to the refreshed handler. */
uint32_t opencfw_em9305_dispatch_331c20(uint32_t type,uintptr_t event)
{
 if(type==1u) {
  (void)opencfw_em9305_wsf_event_release(event);
  (void)opencfw_em9305_ll_primary_credit_308570(1u);
 } else if(type==3u) {
  uintptr_t callback=*(volatile uint32_t *)(uintptr_t)0x8058c8u;
  if(callback!=0u) {
   (void)opencfw_em9305_wsf_event_release(event);
   callback=*(volatile uint32_t *)(uintptr_t)0x8058c8u;
   (void)((uint32_t (*)(uint32_t))callback)(1u);
  }
 } else if(type==2u) {
  if(*(volatile uint8_t *)event==62u) {
   uint32_t subtype=*(volatile uint8_t *)(event+2u);
   uint32_t index=subtype-11u;
   uintptr_t counter=0u;
   if(index<30u) {
    if(((0x24800015u>>index)&1u)!=0u) counter=0x805718u;
    else if(((0xc00u>>index)&1u)!=0u) counter=0x805719u;
    else if(index==8u) counter=0x805700u;
   }
   if(counter==0u && subtype==2u) counter=0x805718u;
   if(counter!=0u) {
    uint32_t value=*(volatile uint8_t *)counter;
    *(volatile uint8_t *)counter=(uint8_t)(value-1u);
   }
  }
  (void)opencfw_em9305_wsf_event_release(event);
 }
 uint32_t handler=*(volatile uint8_t *)(uintptr_t)0x80585cu;
 return opencfw_em9305_wsf_event_post(handler,4u);
}

/* Native331cdc..331d5c: queued event precedes link then primary callbacks.
 * Busy flag tested once; header bytes captured before aliased output stores. */
uint32_t opencfw_em9305_dispatch_331cdc(uintptr_t type_out,uintptr_t length_out,uintptr_t packet_out)
{
 if(*(volatile uint8_t *)(uintptr_t)0x805884u!=0u) return 0u;
 uint8_t handler;
 uintptr_t packet=opencfw_em9305_wsf_event_remove(0x805870u,(uintptr_t)&handler);
 if(packet!=0u) {
  uint32_t length=*(volatile uint8_t *)(packet+1u);
  *(volatile uint8_t *)(uintptr_t)0x805884u=1u;
  *(volatile uint8_t *)type_out=2u;
  *(volatile uint32_t *)packet_out=(uint32_t)packet;
  *(volatile uint16_t *)length_out=(uint16_t)(length+2u);
  return 1u;
 }
 uint32_t type=3u;
 uintptr_t callback=*(volatile uint32_t *)(uintptr_t)0x8058d4u;
 if(callback!=0u) packet=((uintptr_t (*)(void))callback)();
 if(packet==0u) {
  callback=*(volatile uint32_t *)(uintptr_t)0x8058d0u;
  if(callback==0u) return 0u;
  packet=((uintptr_t (*)(void))callback)();
  if(packet==0u) return 0u;
  type=1u;
 }
 uint32_t low=*(volatile uint8_t *)(packet+2u);
 uint32_t high=*(volatile uint8_t *)(packet+3u);
 *(volatile uint8_t *)(uintptr_t)0x805884u=1u;
 *(volatile uint8_t *)type_out=(uint8_t)type;
 *(volatile uint32_t *)packet_out=(uint32_t)packet;
 *(volatile uint16_t *)length_out=(uint16_t)(low+(high<<8u)+4u);
 return 1u;
}

/* Native30d9f4..30da28: copy all32 bytes only if any scanned byte nonzero. */
uint32_t opencfw_em9305_ll_vendor_key_30d9f4(uintptr_t input)
{
 uint32_t active=0u;
 for(uint32_t i=0u;i<32u;++i) {
  if(*(volatile uint8_t *)(input+i)!=0u) {
   (void)opencfw_em9305_memcpy((void *)(uintptr_t)0x805b60u,(const void *)input,32u);
   active=1u;
   break;
  }
 }
 *(volatile uint8_t *)(uintptr_t)0x805b81u=(uint8_t)active;
 return 0u;
}
/* Native30e040..30e04e tail309b78: fullword mode validation before byte store. */
uint32_t opencfw_em9305_ll_vendor_mode_30e040(uint32_t mode)
{
 if(mode>1u) return 18u;
 *(volatile uint8_t *)(uintptr_t)0x805b83u=(uint8_t)mode;
 return 0u;
}
/* Native331bb8..331bf6: two vendor configuration commands, reload command
 * after child before response allocation and send the five-byte-prefix event. */
uint32_t opencfw_em9305_ll_vendor_dispatch_331bb8(uintptr_t request,uintptr_t input)
{
 uint32_t command=*(volatile uint16_t *)request;
 uint32_t status;
 if(command==0xffe8u) status=opencfw_em9305_ll_vendor_key_30d9f4(input);
 else if(command==0xffecu) status=opencfw_em9305_ll_vendor_mode_30e040(*(volatile uint8_t *)input);
 else return 0u;
 command=*(volatile uint16_t *)request;
 uintptr_t response=opencfw_em9305_ll_response_allocate_32e428(1u,command);
 if(response!=0u) {
  *(volatile uint8_t *)response=(uint8_t)status;
  (void)opencfw_em9305_ll_event_send(response-5u);
 }
 return 1u;
}
extern uint32_t opencfw_em9305_ll_vendor_query_30bb10(void);
extern uint32_t opencfw_em9305_ll_vendor_apply_30bad4(uintptr_t,uintptr_t,uint32_t);
extern uint32_t opencfw_em9305_ll_vendor_apply_30baa0(uintptr_t,uintptr_t);
/* Native331aec..331b38: vendor pre-dispatch then three standard commands. */
uint32_t opencfw_em9305_dispatch_331aec(uintptr_t request,uintptr_t input)
{
 if(opencfw_em9305_ll_vendor_dispatch_331bb8(request,input)!=0u) return 1u;
 uint32_t command=*(volatile uint16_t *)request;
 uint32_t status;
 if(command==0x2025u) status=opencfw_em9305_ll_vendor_query_30bb10();
 else if(command==0x205eu) {
  uint32_t count=*(volatile uint8_t *)(input+64u);
  status=opencfw_em9305_ll_vendor_apply_30bad4(input,input+32u,count);
 } else if(command==0x2026u) status=opencfw_em9305_ll_vendor_apply_30baa0(input,input+32u);
 else return 0u;
 (void)opencfw_em9305_ll_status_event_331bf8(request,status);
 return 1u;
}

/* Native313fc0..313fc8: set and return product scheduler wake cell; incoming
 * address is ignored by native, and callers may overwrite the returned cell. */
uintptr_t opencfw_em9305_wsf_wake_cell_313fc0(uintptr_t incoming)
{
 (void)incoming;
 *(volatile uint8_t *)(uintptr_t)0x80606du=1u;
 return 0x80606du;
}
extern uint32_t opencfw_em9305_ll_vendor_validate_32e328(uintptr_t,uint32_t);
extern uint32_t opencfw_em9305_ll_vendor_defaults_306d7c(void);
/* Native306dcc..306e2a: captured mode controls validation/error behavior;
 * native full validation word controls branching, low byte is recorded. */
uint32_t opencfw_em9305_ll_vendor_start_306dcc(uintptr_t data,uintptr_t key)
{
 if(*(volatile uint8_t *)(uintptr_t)0x805b80u!=0u) return 12u;
 uint32_t mode=*(volatile uint8_t *)(uintptr_t)0x805b83u;
 uint32_t valid=opencfw_em9305_ll_vendor_validate_32e328(data,mode==0u);
 *(volatile uint8_t *)(uintptr_t)0x805b82u=(uint8_t)valid;
 if(valid==0u) return mode==0u?0u:18u;
 *(volatile uint8_t *)(uintptr_t)0x805b80u=1u;
 (void)opencfw_em9305_memcpy((void *)(uintptr_t)0x80527cu,(const void *)data,64u);
 (void)opencfw_em9305_memcpy((void *)(uintptr_t)0x80525cu,(const void *)key,32u);
 uintptr_t wake=opencfw_em9305_wsf_wake_cell_313fc0(0x805258u);
 *(volatile uint8_t *)wake=2u;
 return 0u;
}
/* Native30baa0..30bad0: ordered source/key copies into native96B scratch. */
uint32_t opencfw_em9305_ll_vendor_apply_30baa0(uintptr_t first,uintptr_t second)
{
 _Alignas(4) uint8_t scratch[96];
 (void)opencfw_em9305_memcpy(scratch+32u,(const void *)first,32u);
 (void)opencfw_em9305_memcpy(scratch+64u,(const void *)second,32u);
 (void)opencfw_em9305_memcpy(scratch,(const void *)(uintptr_t)0x805b60u,32u);
 return opencfw_em9305_ll_vendor_start_306dcc((uintptr_t)(scratch+32u),(uintptr_t)scratch);
}
/* Native30bad4..30bb0e: count1 selects actual defaults lower, all other
 * fullword count values retain the three-copy application path. */
uint32_t opencfw_em9305_ll_vendor_apply_30bad4(uintptr_t first,uintptr_t second,uint32_t count)
{
 if(count==1u) return opencfw_em9305_ll_vendor_defaults_306d7c();
 _Alignas(4) uint8_t scratch[96];
 (void)opencfw_em9305_memcpy(scratch+32u,(const void *)first,32u);
 (void)opencfw_em9305_memcpy(scratch+64u,(const void *)second,32u);
 (void)opencfw_em9305_memcpy(scratch,(const void *)(uintptr_t)0x805b60u,32u);
 return opencfw_em9305_ll_vendor_start_306dcc((uintptr_t)(scratch+32u),(uintptr_t)scratch);
}
/* Native30bb10 tail306e2c..306e50: busy gate, mark and wake command1. */
uint32_t opencfw_em9305_ll_vendor_query_30bb10(void)
{
 if(*(volatile uint8_t *)(uintptr_t)0x805b80u!=0u) return 12u;
 *(volatile uint8_t *)(uintptr_t)0x805b80u=1u;
 uintptr_t wake=opencfw_em9305_wsf_wake_cell_313fc0(0x805258u);
 *(volatile uint8_t *)wake=1u;
 return 0u;
}

/* Authenticated nonexecutable default data334348(32B)/334368(64B), read
 * only by native306d7c copy calls. Byte provenance in vendor-default-data.json. */
static const uint8_t opencfw_em9305_vendor_default_key_334348[32]={0xbdu,0x1au,0x3cu,0xcdu,0xa6u,0xb8u,0x99u,0x58u,0x99u,0xb7u,0x40u,0xebu,0x7bu,0x60u,0xffu,0x4au,0x50u,0x3fu,0x10u,0xd2u,0xe3u,0xb3u,0xc9u,0x74u,0x38u,0x5fu,0xc5u,0xa3u,0xd4u,0xf6u,0x49u,0x3fu};
static const uint8_t opencfw_em9305_vendor_default_point_334368[64]={0xe6u,0x9du,0x35u,0x0eu,0x48u,0x01u,0x03u,0xccu,0xdbu,0xfdu,0xf4u,0xacu,0x11u,0x91u,0xf4u,0xefu,0xb9u,0xa5u,0xf9u,0xe9u,0xa7u,0x83u,0x2cu,0x5eu,0x2cu,0xbeu,0x97u,0xf2u,0xd2u,0x03u,0xb0u,0x20u,0x8bu,0xd2u,0x89u,0x15u,0xd0u,0x8eu,0x1cu,0x74u,0x24u,0x30u,0xedu,0x8fu,0xc2u,0x45u,0x63u,0x76u,0x5cu,0x15u,0x52u,0x5au,0xbfu,0x9au,0x32u,0x63u,0x6du,0xebu,0x2au,0x65u,0x49u,0x9cu,0x80u,0xdcu};

/* Native306d7c..306dca: default copy path with native busy flag ordering. */
uint32_t opencfw_em9305_ll_vendor_defaults_306d7c(void)
{
 if(*(volatile uint8_t *)(uintptr_t)0x805b80u!=0u) return 12u;
 *(volatile uint8_t *)(uintptr_t)0x805b80u=1u;
 *(volatile uint8_t *)(uintptr_t)0x805b82u=1u;
 (void)opencfw_em9305_memcpy((void *)(uintptr_t)0x80527cu,opencfw_em9305_vendor_default_point_334368,64u);
 (void)opencfw_em9305_memcpy((void *)(uintptr_t)0x80525cu,opencfw_em9305_vendor_default_key_334348,32u);
 uintptr_t wake=opencfw_em9305_wsf_wake_cell_313fc0(0x805258u);
 *(volatile uint8_t *)wake=2u;
 return 0u;
}
/* Native3333d0..333400: reverse eight source word groups, retaining byte
 * read order within each little-endian word and native final R0 return. */
uint32_t opencfw_em9305_vendor_words_3333d0(uintptr_t destination,uintptr_t source)
{
 uint32_t shifted=0u;
 for(uint32_t i=0u;i<8u;++i) {
  uintptr_t part=source+28u-i*4u;
  uint32_t one=*(volatile uint8_t *)(part+1u);
  uint32_t two=*(volatile uint8_t *)(part+2u);
  uint32_t three=*(volatile uint8_t *)(part+3u);
  uint32_t zero=*(volatile uint8_t *)part;
  shifted=one<<8u;
  *(volatile uint32_t *)(destination+i*4u)=zero+shifted+(two<<16u)+(three<<24u);
 }
 return shifted;
}
extern uint32_t opencfw_em9305_rom_curve_validate_108260(uintptr_t);
/* Native3100c8..3100e8: source point words and resident result==zero gate. */
uint32_t opencfw_em9305_vendor_point_validate_3100c8(uintptr_t source)
{
 _Alignas(4) uint8_t point[64];
 (void)opencfw_em9305_vendor_words_3333d0((uintptr_t)point,source);
 (void)opencfw_em9305_vendor_words_3333d0((uintptr_t)(point+32u),source+32u);
 return opencfw_em9305_rom_curve_validate_108260((uintptr_t)point)==0u;
}
/* Native32e328..32e376: retain dead scratch reversal stores; the native
 * R0 passed to3100c8 is the original input, not the scratch address. */
uint32_t opencfw_em9305_ll_vendor_validate_32e328(uintptr_t data,uint32_t notify)
{
 volatile uint8_t scratch[64] __attribute__((unused));
 for(uint32_t i=0u;i<32u;++i) scratch[i]=*(volatile uint8_t *)(data+31u-i);
 for(uint32_t i=0u;i<32u;++i) scratch[32u+i]=*(volatile uint8_t *)(data+63u-i);
 uint32_t result=opencfw_em9305_vendor_point_validate_3100c8(data);
 if(result==0u && notify!=0u) {
  uint32_t handler=*(volatile uint8_t *)(uintptr_t)0x805b18u;
  (void)opencfw_em9305_wsf_event_post(handler,4096u);
 }
 return result;
}

/* Native331ec0..331efe: rejection predicates precede subtype3 event.
 * Allocation failure remains unhandled; delay-slot writes precede send. */
extern uint32_t opencfw_em9305_packet_gate_3329b0(uintptr_t);
extern uint32_t opencfw_em9305_packet_gate_304ac4(uintptr_t);
uint32_t opencfw_em9305_dispatch_331ec0(uintptr_t packet)
{
 if(opencfw_em9305_packet_gate_3329b0(packet)!=0u) return 1u;
 if(opencfw_em9305_packet_gate_304ac4(packet)!=0u) return 1u;
 if(*(volatile uint8_t *)(packet+2u)!=3u) return 0u;
 uintptr_t event=opencfw_em9305_ll_event_allocate(14u,4u);
 if(event==0u) return 0u;
 *(volatile uint8_t *)(event+1u)=10u;
 *(volatile uint8_t *)(event+2u)=32u;
 event-=2u;
 *(volatile uint8_t *)event=1u;
 *(volatile uint8_t *)(event+5u)=*(volatile uint8_t *)(packet+3u);
 (void)opencfw_em9305_ll_event_send(event);
 return 1u;
}
/* Native3329b0..332a78: vendor packet event serialization. */
uint32_t opencfw_em9305_packet_gate_3329b0(uintptr_t packet)
{
 uint32_t type=*(volatile uint8_t *)(packet+2u);
 uint32_t length,code;
 if(type==0x31u){length=10u;code=0xf3u;}
 else if(type==0x22u){length=15u;code=0xf5u;}
 else if(type==0x15u){length=15u;code=0xf1u;}
 else return 0u;
 uintptr_t event=opencfw_em9305_ll_event_allocate(255u,length);
 if(event==0u) return 0u;
 *(volatile uint8_t *)(event+1u)=255u;
 *(volatile uint8_t *)event=(uint8_t)code;
 *(volatile uint8_t *)(event+2u)=*(volatile uint8_t *)(packet+4u);
 if(type==0x15u){
  uint32_t high=*(volatile uint32_t *)(packet+12u);
  uint32_t low=*(volatile uint32_t *)(packet+8u);
  (void)opencfw_em9305_radio_address_write_3045e8(event+3u,low,high);
  high=*(volatile uint32_t *)(packet+20u);
  low=*(volatile uint32_t *)(packet+16u);
  (void)opencfw_em9305_radio_address_write_3045e8(event+9u,low,high);
 } else {
  uint32_t source=8u,dest=6u;
  if(type==0x22u){
   for(uint32_t i=0u;i<4u;++i)
    *(volatile uint8_t *)(event+3u+i)=*(volatile uint8_t *)(packet+6u+i);
   source=12u;dest=7u;
  }
  *(volatile uint8_t *)(event+dest)=(uint8_t)*(volatile uint32_t *)(packet+source);
  *(volatile uint8_t *)(event+dest+1u)=(uint8_t)(*(volatile uint32_t *)(packet+source)>>8u);
  *(volatile uint8_t *)(event+dest+2u)=(uint8_t)*(volatile uint16_t *)(packet+source+2u);
  *(volatile uint8_t *)(event+dest+3u)=*(volatile uint8_t *)(packet+source+3u);
  if(type==0x22u){source=16u;dest=11u;
   *(volatile uint8_t *)(event+dest)=(uint8_t)*(volatile uint32_t *)(packet+source);
   *(volatile uint8_t *)(event+dest+1u)=(uint8_t)(*(volatile uint32_t *)(packet+source)>>8u);
   *(volatile uint8_t *)(event+dest+2u)=(uint8_t)*(volatile uint16_t *)(packet+source+2u);
   *(volatile uint8_t *)(event+dest+3u)=*(volatile uint8_t *)(packet+source+3u);
  }
 }
 (void)opencfw_em9305_ll_event_send(event-2u);
 return 1u;
}
/* Native304ac4..304af8: subtype64 status event, packer's returned offset. */
uint32_t opencfw_em9305_packet_gate_304ac4(uintptr_t packet)
{
 if(*(volatile uint8_t *)(packet+2u)!=64u) return 0u;
 uintptr_t event=opencfw_em9305_ll_event_allocate(255u,3u);
 if(event==0u) return 0u;
 uint32_t offset=opencfw_em9305_ll_pack_halfword_secondary(event,0xfe82u);
 *(volatile uint8_t *)(event+offset)=*(volatile uint8_t *)(packet+4u);
 (void)opencfw_em9305_ll_event_send(event-2u);
 return 1u;
}

/* Native332200..332278: product-gated event types39/40. */
extern uint32_t opencfw_em9305_packet_event_fill_330e78(uintptr_t,uintptr_t);
uint32_t opencfw_em9305_dispatch_332200(uintptr_t packet)
{
 uint32_t type=*(volatile uint8_t *)(packet+2u);
 if(type!=39u && type!=40u) return 0u;
 uint32_t required=type==39u?1u:2u;
 if((*(volatile uint8_t *)(uintptr_t)0x8056fbu&required)==0u) return 0u;
 if((*(volatile uint8_t *)(uintptr_t)0x8056efu&32u)==0u) return 0u;
 uintptr_t event=opencfw_em9305_ll_event_allocate(62u,type==39u?29u:7u);
 if(event==0u) return 0u;
 if(type==39u) (void)opencfw_em9305_packet_event_fill_330e78(event,packet);
 else {
  *(volatile uint8_t *)event=26u;
  for(uint32_t i=0u;i<6u;++i)
   *(volatile uint8_t *)(event+1u+i)=*(volatile uint8_t *)(packet+4u+i);
 }
 (void)opencfw_em9305_ll_event_send(event-2u);
 return 1u;
}

/* Native330e78..330f08: 29-byte event projection with repeated wide reads. */
uint32_t opencfw_em9305_packet_event_fill_330e78(uintptr_t event,uintptr_t packet)
{
 *(volatile uint8_t *)event=25u;
 *(volatile uint8_t *)(event+1u)=*(volatile uint8_t *)(packet+4u);
 *(volatile uint8_t *)(event+2u)=*(volatile uint8_t *)(packet+6u);
 *(volatile uint8_t *)(event+3u)=*(volatile uint8_t *)(packet+7u);
 for(uint32_t i=0u;i<4u;++i){
  uintptr_t source=packet+8u+i*4u,dest=event+4u+i*3u;
  *(volatile uint8_t *)dest=(uint8_t)*(volatile uint32_t *)source;
  *(volatile uint8_t *)(dest+1u)=(uint8_t)(*(volatile uint32_t *)source>>8u);
  *(volatile uint8_t *)(dest+2u)=(uint8_t)*(volatile uint16_t *)(source+2u);
 }
 for(uint32_t i=0u;i<7u;++i)
  *(volatile uint8_t *)(event+16u+i)=*(volatile uint8_t *)(packet+24u+i);
 for(uint32_t i=0u;i<6u;++i)
  *(volatile uint8_t *)(event+23u+i)=*(volatile uint8_t *)(packet+32u+i);
 return 29u;
}

/* Native332194..332200: commands2066/2067 and fresh command reloads. */
extern uint32_t opencfw_em9305_link_query_30aec4(uint32_t);
extern uint32_t opencfw_em9305_link_mode_30c940(uint32_t,uint32_t);
uint32_t opencfw_em9305_dispatch_332194(uintptr_t request,uintptr_t input)
{
 uint32_t command=*(volatile uint16_t *)request;
 if(command!=0x2066u && command!=0x2067u) return 0u;
 uint32_t high=*(volatile uint8_t *)(input+1u);
 uint32_t low=*(volatile uint8_t *)input;
 uint32_t handle=low+(high<<8u);
 if(command==0x2066u){
  uint32_t status=opencfw_em9305_link_query_30aec4(handle);
  (void)opencfw_em9305_ll_status_event_331bf8(request,status);
  return 1u;
 }
 uint32_t mode=*(volatile uint8_t *)(input+2u);
 uint32_t status=opencfw_em9305_link_mode_30c940(handle,mode);
 uintptr_t response=opencfw_em9305_ll_response_allocate_32e428(3u,*(volatile uint16_t *)request);
 if(response!=0u){
  if(*(volatile uint16_t *)request==0x2067u){
   *(volatile uint8_t *)(response+2u)=0u;
   *(volatile uint8_t *)(response+1u)=(uint8_t)handle;
   *(volatile uint8_t *)response=(uint8_t)status;
  }
  (void)opencfw_em9305_ll_event_send(response-5u);
 }
 return 1u;
}
/* Native306a20..306a7c and308308..308368 link command providers.
 * MPYUW is retained as ISA operation; node/handler fields reload after alloc. */
static uint32_t opencfw_em9305_link_command_native(uint32_t handle,uint32_t mode,uint32_t set)
{
 uintptr_t link=opencfw_em9305_ll_link_find_31ab88(handle);
 if(link==0u) return 2u;
 if(*(volatile uint8_t *)(link+2u)!=0u) return 12u;
 if(*(volatile uint8_t *)(link+3u)==2u) return 12u;
 uintptr_t records=*(volatile uint32_t *)(uintptr_t)0x805c70u;
 if(records==0u) return 2u;
 uint32_t id=*(volatile uint16_t *)(link+6u),offset;
 __asm__ volatile("mpyuw %0,%1,912":"=r"(offset):"r"(id));
 if(*(volatile uint8_t *)(records+offset+2u)==0u) return 12u;
 uintptr_t event=opencfw_em9305_wsf_event_allocate(set?6u:4u);
 if(event!=0u){
  *(volatile uint16_t *)(event+2u)=set?0x2601u:0x2501u;
  uint32_t fresh_id=*(volatile uint16_t *)(link+6u);
  uint32_t handler=*(volatile uint8_t *)(uintptr_t)0x805b18u;
  if(set) *(volatile uint8_t *)(event+4u)=(uint8_t)mode;
  *(volatile uint16_t *)event=(uint16_t)fresh_id;
  (void)opencfw_em9305_wsf_task_message_send(handler,event);
 }
 return 0u;
}
uint32_t opencfw_em9305_link_query_30aec4(uint32_t handle)
{ return opencfw_em9305_link_command_native(handle,0u,0u); }
uint32_t opencfw_em9305_link_mode_30c940(uint32_t handle,uint32_t mode)
{ return opencfw_em9305_link_command_native(handle,mode,1u); }

/* Native3319bc..331a40: subtype5 gated31-byte event. The second
 * six-byte copy starts input+16: native memcpy advances R1 by six. */
uint32_t opencfw_em9305_dispatch_3319bc(uintptr_t packet)
{
 if(*(volatile uint8_t *)(packet+2u)!=5u) return 0u;
 if((*(volatile uint8_t *)(uintptr_t)0x8056f9u&2u)==0u) return 0u;
 if((*(volatile uint8_t *)(uintptr_t)0x8056efu&32u)==0u) return 0u;
 uintptr_t event=opencfw_em9305_ll_event_allocate(62u,31u);
 if(event==0u) return 0u;
 *(volatile uint8_t *)event=10u;
 *(volatile uint8_t *)(event+1u)=*(volatile uint8_t *)(packet+4u);
 for(uint32_t i=0u;i<4u;++i)
  *(volatile uint8_t *)(event+2u+i)=*(volatile uint8_t *)(packet+6u+i);
 (void)opencfw_em9305_radio_address_copy_304604(event+6u,packet+10u);
 (void)opencfw_em9305_radio_address_copy_304604(event+12u,packet+16u);
 (void)opencfw_em9305_radio_address_copy_304604(event+18u,packet+29u);
 for(uint32_t i=0u;i<7u;++i)
  *(volatile uint8_t *)(event+24u+i)=*(volatile uint8_t *)(packet+16u+i);
 (void)opencfw_em9305_ll_event_send(event-2u);
 return 1u;
}

/* Native331814..331868: subtype22 event with post-update send pointer. */
uint32_t opencfw_em9305_dispatch_331814(uintptr_t packet)
{
 if(*(volatile uint8_t *)(packet+2u)!=22u) return 0u;
 if((*(volatile uint8_t *)(uintptr_t)0x8056f9u&8u)==0u) return 0u;
 if((*(volatile uint8_t *)(uintptr_t)0x8056efu&32u)==0u) return 0u;
 uintptr_t event=opencfw_em9305_ll_event_allocate(62u,6u);
 if(event==0u) return 0u;
 *(volatile uint8_t *)event=12u;
 *(volatile uint8_t *)(event+1u)=*(volatile uint8_t *)(packet+4u);
 for(uint32_t i=0u;i<4u;++i)
  *(volatile uint8_t *)(event+2u+i)=*(volatile uint8_t *)(packet+6u+i);
 (void)opencfw_em9305_ll_event_send(event-2u);
 return 1u;
}

/* Native33194c..3319bc: commands202b/202c six-byte scratch response. */
extern uint32_t opencfw_em9305_link_address_30c7d0(uint32_t,uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_link_address_30c72c(uint32_t,uintptr_t,uintptr_t);
uint32_t opencfw_em9305_dispatch_33194c(uintptr_t request,uintptr_t input)
{
 _Alignas(4) uint8_t scratch[8]={0};
 uint32_t command=*(volatile uint16_t *)request;
 if(command!=0x202bu && command!=0x202cu)
  return opencfw_em9305_dispatch_331868(request,input);
 uint32_t selector=*(volatile uint8_t *)input;
 uint32_t status=command==0x202bu?
  opencfw_em9305_link_address_30c7d0(selector,input+1u,(uintptr_t)scratch):
  opencfw_em9305_link_address_30c72c(selector,input+1u,(uintptr_t)scratch);
 uintptr_t response=opencfw_em9305_ll_response_allocate_32e428(7u,*(volatile uint16_t *)request);
 if(response!=0u){
  uint32_t fresh=*(volatile uint16_t *)request;
  if(fresh-0x202bu<2u){
   *(volatile uint8_t *)response=(uint8_t)status;
   (void)opencfw_em9305_radio_address_copy_304604(response+1u,(uintptr_t)scratch);
  }
  (void)opencfw_em9305_ll_event_send(response-5u);
 }
 return 1u;
}
/* Native30c72c/30c7d0: decoded identity lookup, six-byte output. */
static uint32_t opencfw_em9305_link_address_native(uint32_t kind,uintptr_t input,uintptr_t output,uint32_t identity)
{
 if(kind>1u) return 18u;
 uint64_t packed=opencfw_em9305_controller_pack_address(input);
 _Alignas(4) uint32_t pair[2]={0u,0u};
 uint32_t found=identity?
  opencfw_em9305_radio_identity_pair_303a60(kind,(uint32_t)packed,(uint32_t)(packed>>32u),(uintptr_t)pair):
  opencfw_em9305_radio_peer_pair_303a40(kind,(uint32_t)packed,(uint32_t)(packed>>32u),(uintptr_t)pair);
 if(found==0u) return 2u;
 (void)opencfw_em9305_radio_address_write_3045e8(output,pair[0],pair[1]);
 return 0u;
}
uint32_t opencfw_em9305_link_address_30c7d0(uint32_t kind,uintptr_t input,uintptr_t output)
{ return opencfw_em9305_link_address_native(kind,input,output,1u); }
uint32_t opencfw_em9305_link_address_30c72c(uint32_t kind,uintptr_t input,uintptr_t output)
{ return opencfw_em9305_link_address_native(kind,input,output,0u); }
/* Native331868..33194c: generic link command dispatcher. */
extern uint32_t opencfw_em9305_command_30af30(uint32_t,uintptr_t,uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_command_30ca68(uint32_t,uintptr_t);
extern uint32_t opencfw_em9305_command_30b150(void);
extern uint32_t opencfw_em9305_command_30cd94(uint32_t);
extern uint32_t opencfw_em9305_command_30deec(uint32_t);
extern uint32_t opencfw_em9305_command_30ddd4(uint32_t,uintptr_t,uint32_t);
extern uint32_t opencfw_em9305_command_30d45c(uint32_t,uint32_t);
extern uint32_t opencfw_em9305_command_30c918(uintptr_t);
uint32_t opencfw_em9305_dispatch_331868(uintptr_t request,uintptr_t input)
{
 uint32_t command=*(volatile uint16_t *)request,status=0u,length=1u;
 switch(command){
 case 0x2027u:status=opencfw_em9305_command_30af30(*(volatile uint8_t *)input,input+1u,input+7u,input+23u);break;
 case 0x2028u:status=opencfw_em9305_command_30ca68(*(volatile uint8_t *)input,input+1u);break;
 case 0x2029u:status=opencfw_em9305_command_30b150();break;
 case 0x202au:length=2u;break;
 case 0x202du:status=opencfw_em9305_command_30cd94(*(volatile uint8_t *)input);break;
 case 0x202eu:{uint32_t high=*(volatile uint8_t *)(input+1u);uint32_t low=*(volatile uint8_t *)input;status=opencfw_em9305_command_30deec(low+(high<<8u));break;}
 case 0x204eu:{uint32_t extra=*(volatile uint8_t *)(input+7u);uint32_t first=*(volatile uint8_t *)input;status=opencfw_em9305_command_30ddd4(first,input+1u,extra);break;}
 case 0x207cu:{uint32_t second=*(volatile uint8_t *)(input+1u);uint32_t first=*(volatile uint8_t *)input;status=opencfw_em9305_command_30d45c(first,second);break;}
 default:return 0u;
 }
 uintptr_t response=opencfw_em9305_ll_response_allocate_32e428(length,*(volatile uint16_t *)request);
 if(response!=0u){
  uint32_t fresh=*(volatile uint16_t *)request,index=fresh-0x2027u;
  if((index<8u && ((0xc7u>>index)&1u)!=0u)||fresh==0x207cu||fresh==0x204eu)
   *(volatile uint8_t *)response=(uint8_t)status;
  else if(index==3u){
   uint8_t value=0u;
   uint32_t result=opencfw_em9305_command_30c918((uintptr_t)&value);
   *(volatile uint8_t *)(response+2u)=0u;
   *(volatile uint8_t *)response=(uint8_t)result;
   *(volatile uint8_t *)(response+1u)=value;
  }
  (void)opencfw_em9305_ll_event_send(response-5u);
 }
 return 1u;
}
/* Native30cd94/30b150: four ordered busy flags and installed gate. */
static uint32_t opencfw_em9305_command_busy_native(void)
{
 if(*(volatile uint8_t *)(uintptr_t)0x805a74u!=0u) return 1u;
 if(*(volatile uint8_t *)(uintptr_t)0x805a73u!=0u) return 1u;
 if(*(volatile uint8_t *)(uintptr_t)0x805a71u!=0u) return 1u;
 if(*(volatile uint8_t *)(uintptr_t)0x805a72u!=0u) return 1u;
 uintptr_t callback=*(volatile uint32_t *)(uintptr_t)0x80130cu;
 return callback!=0u?((uint32_t (*)(uintptr_t))callback)(callback):0u;
}
uint32_t opencfw_em9305_command_30cd94(uint32_t mode)
{
 if(mode>=2u) return 18u;
 if(opencfw_em9305_command_busy_native()!=0u) return 12u;
 *(volatile uint8_t *)(uintptr_t)0x805a9du=(uint8_t)(mode!=0u);
 return 0u;
}
extern uintptr_t opencfw_em9305_radio_reset_30390c(void);
uint32_t opencfw_em9305_command_30b150(void)
{
 if(opencfw_em9305_command_busy_native()!=0u &&
    *(volatile uint8_t *)(uintptr_t)0x805a9du!=0u) return 12u;
 (void)opencfw_em9305_radio_reset_30390c();
 return 0u;
}

/* Native30390c..303918: byte reset with retained address in R0. */
uintptr_t opencfw_em9305_radio_reset_30390c(void)
{
 *(volatile uint8_t *)(uintptr_t)0x801610u=0u;
 return 0x801610u;
}
/* Native30c918..30c928: preserve original output from BL delay slot. */
uint32_t opencfw_em9305_command_30c918(uintptr_t output)
{
 uint32_t value=opencfw_em9305_radio_identity_status_30396c();
 *(volatile uint8_t *)output=(uint8_t)value;
 return 0u;
}
/* Native325268..325284: fresh handler/time then seconds timer tail. */
uint32_t opencfw_em9305_command_timer_325268(void)
{
 uint32_t handler=*(volatile uint8_t *)(uintptr_t)0x805b18u;
 uint32_t time=*(volatile uint32_t *)(uintptr_t)0x805b58u;
 *(volatile uint8_t *)(uintptr_t)0x8051f0u=(uint8_t)handler;
 return opencfw_em9305_wsf_timer_start_seconds(0x8051e4u,time);
}
/* Native308198..3081a4: store full incoming word before timer tail. */
uint32_t opencfw_em9305_command_time_set_308198(uint32_t value)
{
 *(volatile uint32_t *)(uintptr_t)0x805b58u=value;
 return opencfw_em9305_command_timer_325268();
}
/* Native30deec..30df08: wrapping halfword validation, ignore lower result. */
uint32_t opencfw_em9305_command_30deec(uint32_t value)
{
 if((uint16_t)(value-1u)>0xa1b7u) return 18u;
 (void)opencfw_em9305_command_time_set_308198(value);
 return 0u;
}
/* Native306a90..306a9c: mode-byte store, return0. */
uint32_t opencfw_em9305_link_mode_store_306a90(uint32_t mode)
{
 *(volatile uint8_t *)(uintptr_t)0x805400u=(uint8_t)mode;
 return 0u;
}
/* Native30d45c..30d48c: local gate or installed two-argument provider. */
uint32_t opencfw_em9305_command_30d45c(uint32_t selector,uint32_t mode)
{
 if(mode>=4u) return 18u;
 if(opencfw_em9305_ll_connection_gate_30e524()!=0u)
  return opencfw_em9305_link_mode_store_306a90(mode);
 uintptr_t callback=*(volatile uint32_t *)(uintptr_t)0x801300u;
 if(callback==0u) return 18u;
 return ((uint32_t (*)(uint32_t,uint32_t))callback)(selector,mode);
}
/* Native30ddd4..30de38: two Boolean selectors, gated identity setter. */
uint32_t opencfw_em9305_command_30ddd4(uint32_t kind,uintptr_t input,uint32_t value)
{
 if((kind|value)>1u) return 18u;
 if(opencfw_em9305_command_busy_native()!=0u &&
    *(volatile uint8_t *)(uintptr_t)0x805a9du!=0u) return 12u;
 uint64_t address=opencfw_em9305_controller_pack_address(input);
 uint32_t found=opencfw_em9305_radio_identity_set_303ca8(kind,(uint32_t)address,(uint32_t)(address>>32u),value);
 return found==0u?2u:0u;
}
/* Native30ca68..30cac4: Boolean kind, gated packed-address update. */
extern uint32_t opencfw_em9305_radio_address_update_303b40(uint32_t,uint32_t,uint32_t);
uint32_t opencfw_em9305_command_30ca68(uint32_t kind,uintptr_t input)
{
 if(kind>1u) return 18u;
 if(opencfw_em9305_command_busy_native()!=0u &&
    *(volatile uint8_t *)(uintptr_t)0x805a9du!=0u) return 12u;
 uint64_t address=opencfw_em9305_controller_pack_address(input);
 uint32_t changed=opencfw_em9305_radio_address_update_303b40(kind,(uint32_t)address,(uint32_t)(address>>32u));
 return changed==0u?18u:0u;
}
/* Native303b40..303b7c: remove matched row by last-record replacement. */
uint32_t opencfw_em9305_radio_address_update_303b40(uint32_t kind,uint32_t low,uint32_t high)
{
 uintptr_t row=opencfw_em9305_radio_identity_find_31441c(kind,low,high);
 if(row!=0u){
  uint32_t count=*(volatile uint8_t *)(uintptr_t)0x801610u;
  if(count>=2u){
   uint32_t offset;
   __asm__ volatile("mpyuw %0,%1,72":"=r"(offset):"r"(count));
   uintptr_t records=*(volatile uint32_t *)(uintptr_t)0x805c00u;
   (void)opencfw_em9305_memcpy((void *)row,(const void *)(records+offset-72u),72u);
  }
  *(volatile uint8_t *)(uintptr_t)0x801610u=(uint8_t)(count-1u);
 }
 return row!=0u;
}
/* Native30af30..30af98: five-argument identity insertion descendant. */
extern uint32_t opencfw_em9305_radio_identity_add_303788(uint32_t,uint32_t,uint32_t,uintptr_t,uintptr_t);
uint32_t opencfw_em9305_command_30af30(uint32_t kind,uintptr_t input,uintptr_t first,uintptr_t second)
{
 if(kind>1u) return 18u;
 if(opencfw_em9305_command_busy_native()!=0u &&
    *(volatile uint8_t *)(uintptr_t)0x805a9du!=0u) return 12u;
 uint64_t address=opencfw_em9305_controller_pack_address(input);
 uint32_t inserted=opencfw_em9305_radio_identity_add_303788(kind,(uint32_t)address,(uint32_t)(address>>32u),first,second);
 return inserted==0u?7u:0u;
}
/* Native303788..303844: update/allocate72B identity row, key projections. */
uint32_t opencfw_em9305_radio_identity_add_303788(uint32_t kind,uint32_t low,uint32_t high,uintptr_t first,uintptr_t second)
{
 uintptr_t row=opencfw_em9305_radio_identity_find_31441c(kind,low,high);
 if(row==0u){
  uint32_t count=*(volatile uint8_t *)(uintptr_t)0x801610u;
  uint32_t capacity=*(volatile uint8_t *)(uintptr_t)0x801611u;
  if(count>=capacity) return 0u;
  uintptr_t base=*(volatile uint32_t *)(uintptr_t)0x805c00u;
  *(volatile uint8_t *)(uintptr_t)0x801610u=(uint8_t)(count+1u);
  if(base==0u) return 0u;
  uint32_t offset;
  __asm__ volatile("mpyuw %0,%1,72":"=r"(offset):"r"(count));
  row=base+offset;
 }
 *(volatile uint32_t *)(row+32u)=low;
 *(volatile uint32_t *)(row+36u)=(kind<<16u)|high;
 (void)opencfw_em9305_memcpy((void *)row,(const void *)first,16u);
 *(volatile uint8_t *)(row+64u)=1u;
 for(uint32_t i=0u;i<16u;++i) if(*(volatile uint8_t *)(row+i)!=0u){
  *(volatile uint8_t *)(row+64u)=0u;break;
 }
 (void)opencfw_em9305_memcpy((void *)(row+16u),(const void *)second,16u);
 *(volatile uint8_t *)(row+65u)=1u;
 uint32_t nonzero=0u;
 for(uint32_t i=0u;i<16u;++i) if(*(volatile uint8_t *)(row+16u+i)!=0u){
  nonzero=1u;*(volatile uint8_t *)(row+65u)=0u;break;
 }
 *(volatile uint16_t *)(row+66u)=0u;
 (void)opencfw_em9305_memset((void *)(row+40u),0u,24u);
 if(nonzero){
  uint64_t projected=opencfw_em9305_radio_private_address_31467c(row+16u);
  *(volatile uint32_t *)(row+52u)=(uint32_t)(projected>>32u);
  *(volatile uint32_t *)(row+48u)=(uint32_t)projected;
 }
 return 1u;
}

/* Native331f5c..332036: event41 variable pairs/event42 fixed fields. */
uint32_t opencfw_em9305_dispatch_331f5c(uintptr_t packet)
{
 uint32_t type=*(volatile uint8_t *)(packet+2u);
 if(type!=41u && type!=42u) return 0u;
 if((*(volatile uint8_t *)(uintptr_t)0x8056fbu&(type==41u?4u:8u))==0u) return 0u;
 if((*(volatile uint8_t *)(uintptr_t)0x8056efu&32u)==0u) return 0u;
 uint32_t length=type==41u?(uint8_t)(19u+2u**(volatile uint8_t *)(packet+26u)):3u;
 uintptr_t event=opencfw_em9305_ll_event_allocate(62u,length);
 if(event==0u) return 0u;
 *(volatile uint8_t *)event=type==41u?27u:28u;
 *(volatile uint8_t *)(event+1u)=*(volatile uint8_t *)(packet+4u);
 *(volatile uint8_t *)(event+2u)=*(volatile uint8_t *)(packet+5u);
 if(type==41u){
  for(uint32_t i=0u;i<2u;++i){
   uintptr_t source=packet+8u+4u*i,dest=event+3u+3u*i;
   *(volatile uint8_t *)dest=(uint8_t)*(volatile uint32_t *)source;
   *(volatile uint8_t *)(dest+1u)=(uint8_t)(*(volatile uint32_t *)source>>8u);
   *(volatile uint8_t *)(dest+2u)=(uint8_t)*(volatile uint16_t *)(source+2u);
  }
  for(uint32_t i=0u;i<5u;++i) *(volatile uint8_t *)(event+9u+i)=*(volatile uint8_t *)(packet+16u+i);
  for(uint32_t i=0u;i<5u;++i) *(volatile uint8_t *)(event+14u+i)=*(volatile uint8_t *)(packet+22u+i);
  if(*(volatile uint8_t *)(packet+26u)!=0u){
   uint32_t i=0u;uintptr_t dest=event+19u;
   do {
    uintptr_t source=packet+28u+2u*i;
    *(volatile uint8_t *)dest++=*(volatile uint8_t *)source;
    *(volatile uint8_t *)dest++=*(volatile uint8_t *)(source+1u);
    ++i;
   }while(i<*(volatile uint8_t *)(packet+26u));
  }
 }
 (void)opencfw_em9305_ll_event_send(event-2u);
 return 1u;
}

/* Native3327f4..3328c6: event26 quota,27/29 status,28 gated fields. */
uint32_t opencfw_em9305_dispatch_3327f4(uintptr_t packet)
{
 uint32_t type=*(volatile uint8_t *)(packet+2u);
 uintptr_t event;
 if(type==27u || type==29u){
  event=opencfw_em9305_ll_event_allocate(14u,4u);
  if(event==0u) return 0u;
  *(volatile uint8_t *)event=1u;
  *(volatile uint8_t *)(event+2u)=32u;
  *(volatile uint8_t *)(event+1u)=type==29u?64u:57u;
  *(volatile uint8_t *)(event+3u)=*(volatile uint8_t *)(packet+4u);
 }else if(type==26u || type==28u){
  if(type==26u){
   uintptr_t state=*(volatile uint32_t *)(uintptr_t)0x805cacu;
   uint32_t count=*(volatile uint8_t *)(uintptr_t)0x805700u;
   uint32_t limit=*(volatile uint8_t *)(state+31u);
   if(count>=limit) return 0u;
  }
  uint32_t mask=*(volatile uint8_t *)(uintptr_t)0x8056fau;
  if((mask&(type==26u?4u:2u))==0u) return 0u;
  if((*(volatile uint8_t *)(uintptr_t)0x8056efu&32u)==0u) return 0u;
  event=opencfw_em9305_ll_event_allocate(62u,type==26u?9u:6u);
  if(event==0u) return 0u;
  *(volatile uint8_t *)event=type==26u?19u:18u;
  *(volatile uint8_t *)(event+1u)=*(volatile uint8_t *)(packet+4u);
  *(volatile uint8_t *)(event+2u)=*(volatile uint8_t *)(packet+5u);
  if(type==26u){
   (void)opencfw_em9305_radio_address_copy_304604(event+3u,packet+6u);
   uint32_t count=*(volatile uint8_t *)(uintptr_t)0x805700u;
   *(volatile uint8_t *)(uintptr_t)0x805700u=(uint8_t)(count+1u);
  }else for(uint32_t i=0u;i<3u;++i)
   *(volatile uint8_t *)(event+3u+i)=*(volatile uint8_t *)(packet+6u+i);
 }else return 0u;
 (void)opencfw_em9305_ll_event_send(event-2u);
 return 1u;
}

/* Native332038..332192: packed command2068/2069 and two-byte206a.
 * Stack padding is intentionally not initialized: native does not write it. */
extern uint32_t opencfw_em9305_command_30b230(uintptr_t);
extern uint32_t opencfw_em9305_command_30b2d8(uintptr_t);
extern uint32_t opencfw_em9305_command_30e0e4(uint32_t,uint32_t);
uint32_t opencfw_em9305_dispatch_332038(uintptr_t request,uintptr_t input)
{
 uint32_t command=*(volatile uint16_t *)request,status;
 if(command==0x206au){
  uint32_t second=*(volatile uint8_t *)(input+1u);
  uint32_t first=*(volatile uint8_t *)input;
  status=opencfw_em9305_command_30e0e4(first,second);
 }else if(command==0x2068u || command==0x2069u){
  _Alignas(4) volatile uint8_t scratch[40];
  uint8_t v[20];
  if(command==0x2068u){
   const uint8_t order[]={7,4,6,9,3,5,10,8,0,1,2,11,12,13,14};
   for(uint32_t i=0u;i<15u;++i) v[order[i]]=*(volatile uint8_t *)(input+order[i]);
   scratch[12]=v[10];
   *(volatile uint16_t *)(scratch+8u)=(uint16_t)(v[6]|((uint32_t)v[7]<<8u));
   scratch[0]=v[0];scratch[1]=v[1];scratch[2]=v[2];
   scratch[13]=v[11];scratch[14]=v[12];scratch[15]=v[13];scratch[16]=v[14];
   *(volatile uint16_t *)(scratch+10u)=(uint16_t)(v[8]|((uint32_t)v[9]<<8u));
   *(volatile uint32_t *)(scratch+4u)=v[3]|((uint32_t)v[4]<<8u)|((uint32_t)v[5]<<16u);
   (void)opencfw_em9305_memcpy((void *)(scratch+17u),(const void *)(input+15u),16u);
   status=opencfw_em9305_command_30b230((uintptr_t)scratch);
  }else{
   const uint8_t order[]={7,4,6,10,3,5,12,8,9,11,0,1,2,13,14,15,16,17,18,19};
   for(uint32_t i=0u;i<20u;++i) v[order[i]]=*(volatile uint8_t *)(input+order[i]);
   scratch[26]=v[8];
   *(volatile uint16_t *)(scratch+24u)=(uint16_t)(v[6]|((uint32_t)v[7]<<8u));
   scratch[0]=v[0];scratch[1]=v[1];scratch[2]=v[2];
   for(uint32_t i=0u;i<7u;++i) scratch[32u+i]=v[13u+i];
   *(volatile uint16_t *)(scratch+28u)=(uint16_t)(v[9]|((uint32_t)v[10]<<8u));
   *(volatile uint16_t *)(scratch+30u)=(uint16_t)(v[11]|((uint32_t)v[12]<<8u));
   *(volatile uint32_t *)(scratch+4u)=v[3]|((uint32_t)v[4]<<8u)|((uint32_t)v[5]<<16u);
   (void)opencfw_em9305_memcpy((void *)(scratch+8u),(const void *)(input+20u),16u);
   status=opencfw_em9305_command_30b2d8((uintptr_t)scratch);
  }
 }else return 0u;
 (void)opencfw_em9305_ll_status_event_331bf8(request,status);
 return 1u;
}
/* Native30e0e4 tail30a100..30a132: active-record option update. */
uint32_t opencfw_em9305_command_30e0e4(uint32_t id,uint32_t option)
{
 uintptr_t record=opencfw_em9305_ll_record_find_31aa98(id);
 if(record==0u) return 66u;
 if(*(volatile uint8_t *)(record+3u)!=1u) return 12u;
 if(*(volatile uint8_t *)(record+1u)!=1u) return 12u;
 uint32_t flags=*(volatile uint8_t *)(record+273u);
 *(volatile uint8_t *)(record+290u)=(uint8_t)option;
 *(volatile uint8_t *)(record+273u)=(uint8_t)(flags|2u);
 return 0u;
}
/* Native30b230..30b2d8: packed parameter validation and record apply. */
extern uint32_t opencfw_em9305_radio_record_exists_3072d0(uint32_t);
extern uint32_t opencfw_em9305_radio_record_apply_309cfc(uintptr_t);
uint32_t opencfw_em9305_command_30b230(uintptr_t input)
{
 uintptr_t state=*(volatile uint32_t *)(uintptr_t)0x805cacu;
 uint32_t first=*(volatile uint8_t *)input;
 uint32_t capability=*(volatile uint8_t *)(state+62u);
 if(first>239u) return 18u;
 uint32_t id=*(volatile uint8_t *)(input+1u);
 if(id>239u) return 18u;
 if((uint32_t)(*(volatile uint8_t *)(input+2u)-1u)>=31u) return 18u;
 uint32_t value=*(volatile uint32_t *)(input+4u);
 if(value+0xfff00000u<0xfff00100u) return 18u;
 if(*(volatile uint16_t *)(input+8u)>=4096u) return 18u;
 if((uint16_t)(*(volatile uint16_t *)(input+10u)+0xf05fu)<0xf064u) return 18u;
 if(*(volatile uint8_t *)(input+12u)>=16u) return 18u;
 uint32_t extra=*(volatile uint8_t *)(state+63u);
 uint32_t allowed=((capability!=0u)<<1u)+1u;
 allowed|=extra<<2u;
 uint32_t requested=*(volatile uint8_t *)(input+13u);
 if((requested&((~allowed)|0xffffff00u))!=0u) return 17u;
 if(requested==0u) return 18u;
 if(*(volatile uint8_t *)(input+14u)>=2u) return 18u;
 if(*(volatile uint8_t *)(input+15u)>=2u) return 18u;
 if(*(volatile uint8_t *)(input+16u)>1u) return 18u;
 if(opencfw_em9305_radio_record_exists_3072d0(id)==0u) return 66u;
 return opencfw_em9305_radio_record_apply_309cfc(input);
}
/* Native31aa64..31aa98: active2824-byte record lookup, id first. */
uintptr_t opencfw_em9305_radio_record_find_31aa64(uint32_t id)
{
 uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
 uint32_t count=*(volatile uint8_t *)(config+12u);
 if(count==0u) return 0u;
 uintptr_t row=*(volatile uint32_t *)(uintptr_t)0x805c38u;
 for(uint32_t i=0u;i<count;++i,row+=2824u)
  if(*(volatile uint8_t *)(row+1u)==id && *(volatile uint8_t *)row!=0u) return row;
 return 0u;
}
/* Native3072d0..3072e0: Boolean projection of real record lookup. */
uint32_t opencfw_em9305_radio_record_exists_3072d0(uint32_t id)
{
 return opencfw_em9305_radio_record_find_31aa64(id)!=0u;
}
/* Native30b2d8..30b3f8: extended packed validation, native multiply/remainder. */
extern uint32_t opencfw_em9305_radio_record_available_307410(uint32_t);
extern uint32_t opencfw_em9305_radio_record_extended_apply_309e60(uintptr_t);
uint32_t opencfw_em9305_command_30b2d8(uintptr_t input)
{
 uintptr_t state=*(volatile uint32_t *)(uintptr_t)0x805cacu;
 uint32_t mode=*(volatile uint8_t *)(uintptr_t)0x805a86u;
 uint32_t first=*(volatile uint8_t *)input;
 uint32_t capability=*(volatile uint8_t *)(state+62u);
 if(first>239u) return 48u;
 uint32_t id=*(volatile uint8_t *)(input+1u);
 if(id>239u || (uint32_t)(*(volatile uint8_t *)(input+2u)-1u)>=31u) return 48u;
 uint32_t period=*(volatile uint32_t *)(input+4u);
 if(period+0xfff00000u<0xfff00100u) return 48u;
 uint32_t interval=*(volatile uint16_t *)(input+24u);
 if(interval<((mode&128u)!=0u?2u:4u) || interval>=3201u) return 48u;
 uint32_t count=*(volatile uint8_t *)(input+26u);
 if(count-1u>=31u || *(volatile uint16_t *)(input+28u)>=4096u) return 48u;
 uint32_t size=*(volatile uint16_t *)(input+30u);
 if(size-1u>250u || *(volatile uint8_t *)(input+32u)==0u) return 48u;
 if(*(volatile uint8_t *)(input+33u)>=2u) return 48u;
 uint32_t special=*(volatile uint8_t *)(input+34u);
 if(special>=2u) return 48u;
 uint32_t groups=*(volatile uint8_t *)(input+35u);
 if(groups-1u>=7u) return 48u;
 uint32_t factor=*(volatile uint8_t *)(input+36u);
 if(factor-1u>=15u) return 48u;
 uint32_t option=*(volatile uint8_t *)(input+37u);
 if(option>=16u || *(volatile uint8_t *)(input+38u)>=2u) return 48u;
 uint32_t extra=*(volatile uint8_t *)(state+63u);
 if(special==0u){
  uint32_t product,remainder;
  __asm__ volatile("mpyuw %0,%1,1250":"=r"(product):"r"(interval));
  __asm__ volatile("remu %0,%1,%2":"=r"(remainder):"r"(product),"r"(period));
  if(remainder!=0u) return 48u;
 }
 if(option!=0u || groups>=7u || count>=9u) return 17u;
 if(*(volatile uint16_t *)(state+46u)<size || factor>=5u) return 17u;
 uint32_t product;
 __asm__ volatile("mpyuw %0,%1,%2":"=r"(product):"r"(factor),"r"(groups));
 if(count<product) return 17u;
 if(opencfw_em9305_radio_record_available_307410(id)==0u) return 66u;
 uint32_t allowed=(((capability!=0u)<<1u)+1u)|(extra<<2u);
 uint32_t requested=*(volatile uint8_t *)(input+32u);
 if((requested&((~allowed)|0xffffff00u))!=0u) return 17u;
 return opencfw_em9305_radio_record_extended_apply_309e60(input);
}
/* Native307410..307434: active record availability predicates. */
uint32_t opencfw_em9305_radio_record_available_307410(uint32_t id)
{
 uintptr_t row=opencfw_em9305_radio_record_find_31aa64(id);
 if(row==0u) return 0u;
 if(*(volatile uint8_t *)(row+369u)==0u) return 0u;
 return *(volatile uint8_t *)(row+368u)==1u;
}
/* Native317280..3172c8: active association scan with full-width id. */
uint32_t opencfw_em9305_radio_association_exists_317280(uint32_t id)
{
 uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
 uint32_t count=*(volatile uint8_t *)(config+57u);
 if(count==0u) return 0u;
 uintptr_t base=*(volatile uint32_t *)(uintptr_t)0x805c3cu;
 for(uint32_t i=0u;i<count;++i){
  uintptr_t row=base+i*512u;
  if(*(volatile uint8_t *)row==0u) continue;
  if(*(volatile uint8_t *)(row+3u)!=1u) continue;
  uintptr_t associated=*(volatile uint32_t *)(row+180u);
  if(associated!=0u && *(volatile uint8_t *)(associated+1u)==id) return 1u;
 }
 return 0u;
}
/* Native309cfc..309e60: allocation, stream setup, association callbacks and queue. */
extern void opencfw_em9305_radio_record_configure_32c3bc(uintptr_t,uintptr_t);
extern void opencfw_em9305_radio_record_release_31ac84(uintptr_t);
extern uint32_t opencfw_em9305_radio_record_finish_32c2b0(uintptr_t);
extern uint32_t opencfw_em9305_radio_record_timing_30c40c(uint32_t,uint32_t);
extern uintptr_t opencfw_em9305_radio_stream_allocate_316ad4(uintptr_t);
extern uintptr_t opencfw_em9305_radio_stream_setup_327718(uintptr_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t);
extern void opencfw_em9305_radio_association_callback_3291e4(uint32_t);
extern void opencfw_em9305_radio_association_callback_3291d0(uint32_t);
extern void opencfw_em9305_radio_association_callback_3290c4(uint32_t);
uint32_t opencfw_em9305_radio_record_apply_309cfc(uintptr_t input)
{
 uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
 uint32_t required=*(volatile uint8_t *)(input+2u);
 if(*(volatile uint8_t *)(config+58u)<required) return 13u;
 if(opencfw_em9305_ll_stream_free_count_31b248()<required) return 13u;
 if(opencfw_em9305_ll_record_find_31aa98(*(volatile uint8_t *)input)!=0u) return 12u;
 if(opencfw_em9305_radio_association_exists_317280(*(volatile uint8_t *)(input+1u))==1u) return 66u;
 uintptr_t record=opencfw_em9305_ll_record_allocate_316a8c(*(volatile uint8_t *)input);
 if(record==0u) return 13u;
 config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
 uint32_t requested=*(volatile uint8_t *)(input+12u);
 uint32_t maximum=*(volatile uint8_t *)(config+48u);
 uint32_t id=*(volatile uint8_t *)(input+1u);
 *(volatile uint8_t *)(input+12u)=(uint8_t)(requested<maximum?requested:maximum);
 uintptr_t associated=opencfw_em9305_radio_record_find_31aa64(id);
 (void)opencfw_em9305_radio_record_configure_32c3bc(record,input);
 uint32_t duration=*(volatile uint16_t *)(input+10u);
 uint32_t target=*(volatile uint32_t *)(record+44u),scaled;
 __asm__ volatile("mpyuw %0,%1,1000":"=r"(scaled):"r"(duration));
 if(scaled<target){(void)opencfw_em9305_radio_record_release_31ac84(record);return 17u;}
 (void)opencfw_em9305_radio_record_finish_32c2b0(record);
 if(associated!=0u && (*(volatile uint8_t *)(uintptr_t)0x805a86u&64u)==0u)
  *(volatile uint8_t *)(record+410u)=*(volatile uint8_t *)(associated+2518u);
 uint32_t size=*(volatile uint16_t *)(record+4u);
 uint32_t interval=*(volatile uint16_t *)(record+6u);
 uint32_t timing=opencfw_em9305_radio_record_timing_30c40c(interval,size);
 if(timing>=9u){(void)opencfw_em9305_radio_record_release_31ac84(record);return 18u;}
 for(uint32_t i=0u;i<*(volatile uint8_t *)(input+2u);++i){
  uintptr_t stream=opencfw_em9305_radio_stream_allocate_316ad4(record);
  if(stream==0u){(void)opencfw_em9305_radio_record_release_31ac84(record);return 13u;}
  uint32_t fourth=*(volatile uint32_t *)(uintptr_t)0x805aa4u;
  uint32_t third=*(volatile uint32_t *)(uintptr_t)0x805aa0u;
  uint32_t fifth=*(volatile uint8_t *)(record+292u);
  uint32_t second=*(volatile uint16_t *)(record+348u);
  uint32_t first=*(volatile uint32_t *)(record+344u);
  (void)opencfw_em9305_radio_stream_setup_327718(stream,first,second,third,fourth,fifth);
  if(associated!=0u && (*(volatile uint8_t *)(uintptr_t)0x805a86u&64u)!=0u)
   *(volatile uint8_t *)(record+410u)=*(volatile uint8_t *)(associated+2518u);
 }
 if(associated!=0u){
  *(volatile uint32_t *)(record+180u)=(uint32_t)associated;
  *(volatile uint32_t *)(associated+2804u)=(uint32_t)(uintptr_t)&opencfw_em9305_radio_association_callback_3291e4;
  *(volatile uint32_t *)(associated+2800u)=(uint32_t)(uintptr_t)&opencfw_em9305_radio_association_callback_3291d0;
  *(volatile uint32_t *)(associated+2796u)=(uint32_t)(uintptr_t)&opencfw_em9305_radio_association_callback_3290c4;
 }
 uintptr_t message=opencfw_em9305_wsf_event_allocate(4u);
 if(message!=0u){
  *(volatile uint16_t *)(message+2u)=272u;
  uint32_t id_byte=*(volatile uint8_t *)input;
  uint32_t handler=*(volatile uint8_t *)(uintptr_t)0x805b18u;
  *(volatile uint16_t *)message=(uint16_t)id_byte;
  (void)opencfw_em9305_wsf_task_message_send(handler,message);
 }
 return 0u;
}
/* Native316ad4..316b5c: first free256B stream, publish record slot. */
uintptr_t opencfw_em9305_radio_stream_allocate_316ad4(uintptr_t record)
{
 uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
 uint32_t count=*(volatile uint8_t *)(config+58u);
 if(count==0u) return 0u;
 uintptr_t base=*(volatile uint32_t *)(uintptr_t)0x805c40u,row=0u;
 uint32_t index;
 for(index=0u;index<count;++index){
  uintptr_t candidate=base+index*256u;
  if(*(volatile uint8_t *)candidate==0u){row=candidate;break;}
 }
 if(index==count) return 0u;
 (void)opencfw_em9305_memset((void *)row,0u,256u);
 config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
 uint32_t slot=*(volatile uint8_t *)(record+52u);
 *(volatile uint8_t *)row=1u;
 *(volatile uint32_t *)(row+4u)=(uint32_t)record;
 uint32_t offset=*(volatile uint8_t *)(config+34u);
 uint32_t origin=*(volatile uint8_t *)(config+53u);
 *(volatile uint8_t *)(row+1u)=(uint8_t)(slot+1u);
 *(volatile uint16_t *)(row+2u)=(uint16_t)(origin+index+offset);
 if(*(volatile uint8_t *)(record+3u)!=0u) *(volatile uint8_t *)(row+36u)=255u;
 else {*(volatile uint8_t *)(row+44u)=255u;*(volatile uint8_t *)(row+100u)=127u;}
 slot=*(volatile uint8_t *)(record+52u);
 *(volatile uint8_t *)(record+52u)=(uint8_t)(slot+1u);
 *(volatile uint32_t *)(record+56u+slot*4u)=(uint32_t)row;
 return row;
}

/* Native31ac84..31ace0: record deactivation, child release and queue drain.
 * Native has no defined result contract; all selected consumers discard R0. */
extern void opencfw_em9305_radio_stream_release_31ace0(uintptr_t);
extern void opencfw_em9305_radio_record_queue_step_317320(uintptr_t);
void opencfw_em9305_radio_record_release_31ac84(uintptr_t record)
{
 *(volatile uint8_t *)record=0u;
 for(uint32_t i=0u;i<*(volatile uint8_t *)(record+52u);++i){
  uintptr_t stream=*(volatile uint32_t *)(record+56u+i*4u);
  if(stream==0u) continue;
  uint32_t mode=*(volatile uint8_t *)(record+3u);
  if(mode==0u || mode==1u)
   (void)opencfw_em9305_ll_test_30cb24(*(volatile uint16_t *)(stream+2u),mode==0u?2u:1u);
  opencfw_em9305_radio_stream_release_31ace0(stream);
 }
 if(*(volatile uint8_t *)(record+3u)==1u)
  while(opencfw_em9305_wsf_queue_empty(record+184u)==0u)
   opencfw_em9305_radio_record_queue_step_317320(record);
}
/* Native317320..317334: remove raw queued node then release pool node. */
void opencfw_em9305_radio_record_queue_step_317320(uintptr_t record)
{
 uintptr_t node=opencfw_em9305_wsf_queue_remove(record+184u);
 if(node!=0u) (void)opencfw_em9305_wsf_pool_release(node);
}
/* Native31ace0..31ad64: deactivate stream and drain mode-specific queues. */
extern uintptr_t opencfw_em9305_radio_stream_receive_take_317508(uintptr_t);
extern void opencfw_em9305_radio_stream_queue_step_317980(uintptr_t,uint32_t);
extern void opencfw_em9305_radio_stream_flush_31bd48(uintptr_t,uint32_t);
void opencfw_em9305_radio_stream_release_31ace0(uintptr_t stream)
{
 uintptr_t parent=*(volatile uint32_t *)(stream+4u);
 *(volatile uint8_t *)stream=0u;
 uint32_t mode=*(volatile uint8_t *)(parent+3u);
 if(mode==1u){
  while(opencfw_em9305_wsf_queue_empty(stream+8u)==0u)
   opencfw_em9305_radio_stream_queue_step_317980(stream,1u);
  uint8_t handler;
  uintptr_t event;
  while((event=opencfw_em9305_wsf_event_remove(stream+20u,(uintptr_t)&handler))!=0u)
   (void)opencfw_em9305_wsf_event_release(event);
 }else if(mode==0u){
  uintptr_t payload;
  while((payload=opencfw_em9305_radio_stream_receive_take_317508(stream))!=0u)
   (void)opencfw_em9305_ll_receive_buffer_release_31761c(payload);
  uintptr_t event;
  while((event=opencfw_em9305_ll_stream_take_317624(stream))!=0u){
   (void)opencfw_em9305_wsf_event_release(event);
   (void)opencfw_em9305_wsf_critical_enter();
   uint32_t count=*(volatile uint8_t *)(uintptr_t)0x805addu;
   *(volatile uint8_t *)(uintptr_t)0x805addu=(uint8_t)(count+1u);
   (void)opencfw_em9305_wsf_critical_exit();
  }
  parent=*(volatile uint32_t *)(stream+4u);
  uint32_t option=*(volatile uint8_t *)(parent+30u);
  opencfw_em9305_radio_stream_flush_31bd48(stream+16u,option);
 }
}
/* Native317508..317524: queue event payload plus ten-byte private prefix. */
uintptr_t opencfw_em9305_radio_stream_receive_take_317508(uintptr_t stream)
{
 uint8_t handler;
 uintptr_t event=opencfw_em9305_wsf_event_remove(stream+8u,(uintptr_t)&handler);
 return event!=0u?event+10u:0u;
}
/* Native31bd48..31bd78: mode-specific buffered event release and count clear. */
void opencfw_em9305_radio_stream_flush_31bd48(uintptr_t buffer,uint32_t mode)
{
 if(mode!=0u){
  uintptr_t event=*(volatile uint32_t *)buffer;
  if(event!=0u){
   (void)opencfw_em9305_wsf_event_release(event);
   *(volatile uint32_t *)buffer=0u;
  }
 }else{
  uint8_t handler;
  uintptr_t event;
  while((event=opencfw_em9305_wsf_event_remove(buffer+16u,(uintptr_t)&handler))!=0u)
   (void)opencfw_em9305_wsf_event_release(event);
 }
 *(volatile uint16_t *)(buffer+6u)=0u;
}
/* Native317980..317a10: byte-budget queue consumption and completion. */
extern void opencfw_em9305_radio_packet_complete_31ae74(uintptr_t);
void opencfw_em9305_radio_stream_queue_step_317980(uintptr_t stream,uint32_t budget)
{
 while((uint8_t)budget!=0u){
  uint32_t available=(uint8_t)budget;
  uint8_t handler;
  uintptr_t packet=opencfw_em9305_wsf_event_peek(stream+8u,(uintptr_t)&handler);
  if(packet==0u) return;
  uint32_t unit=*(volatile uint8_t *)(packet+10u);
  uint32_t length=*(volatile uint16_t *)(packet+8u);
  uint32_t needed=opencfw_em9305_radio_record_timing_30c40c(length,unit);
  uint32_t progress=*(volatile uint8_t *)(packet+11u);
  if(needed<=available){progress+=needed;budget-=needed;}
  else {progress+=budget;budget=0u;}
  unit=*(volatile uint8_t *)(packet+10u);
  uint32_t truncated=(uint8_t)progress;
  length=*(volatile uint16_t *)(packet+8u);
  uint32_t product;
  __asm__ volatile("mpyuw %0,%1,%2":"=r"(product):"r"(truncated),"r"(unit));
  *(volatile uint8_t *)(packet+11u)=(uint8_t)progress;
  if(product<length) continue;
  (void)opencfw_em9305_wsf_event_remove(stream+8u,(uintptr_t)&handler);
  (void)*(volatile uint32_t *)packet;
  (void)opencfw_em9305_wsf_event_release(packet);
  opencfw_em9305_radio_packet_complete_31ae74(packet);
  (void)opencfw_em9305_wsf_critical_enter();
  uint32_t count=*(volatile uint8_t *)(uintptr_t)0x805adcu;
  *(volatile uint8_t *)(uintptr_t)0x805adcu=(uint8_t)(count+1u);
  (void)opencfw_em9305_wsf_critical_exit();
  if(*(volatile uint8_t *)(stream+36u)!=0u) continue;
  if(*(volatile uint8_t *)(stream+108u)!=0u) continue;
  count=*(volatile uint8_t *)(stream+16u);
  *(volatile uint8_t *)(stream+16u)=(uint8_t)(count+1u);
 }
}
/* Native31ae74..31ae84: recycle packet's eight-byte allocation node. */
void opencfw_em9305_radio_packet_complete_31ae74(uintptr_t packet)
{
 (void)opencfw_em9305_wsf_queue_append((uintptr_t)0x8028c8u,packet-8u);
}
/* Native3183d4..3183ec: priority bit1,bit0, then bit2. */
uint32_t opencfw_em9305_radio_phy_project_3183d4(uint32_t value)
{
 if((value&2u)!=0u) return 2u;
 if((value&1u)!=0u) return 1u;
 return value&4u;
}
/* Native334488..33448f: bounded data loads in32c3bc and309e60.
 * Authenticated seven non-executable bytes; see phy-projection-data.json. */
const uint8_t opencfw_em9305_radio_phy_values_334488[7]={2u,1u,3u,1u,1u,1u,4u};

/* Native32c3bc..32c4fc: full record parameter and timing configuration. */
extern void opencfw_em9305_radio_encrypt_seed_317334(uintptr_t,uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_radio_phy_duration_31737c(uint32_t,uint32_t,uint32_t);
static uint32_t opencfw_em9305_native_mpywhl(uint32_t a,uint32_t b)
{
 uint32_t result;
 __asm__ volatile("mpywhl %0,%1,%2":"=r"(result):"r"(a),"r"(b));
 return result;
}
void opencfw_em9305_radio_record_configure_32c3bc(uintptr_t record,uintptr_t input)
{
 *(volatile uint8_t *)(record+3u)=1u;
 uint32_t mode=*(volatile uint8_t *)(input+14u);
 uint32_t kind=*(volatile uint8_t *)(input+15u);
 *(volatile uint8_t *)(record+31u)=(uint8_t)mode;
 uint32_t requested=*(volatile uint8_t *)(input+13u);
 *(volatile uint8_t *)(record+30u)=(uint8_t)kind;
 uint32_t projected=opencfw_em9305_radio_phy_project_3183d4(requested)-2u;
 uint32_t phy=1u;
 if((uint8_t)projected<7u) phy=opencfw_em9305_radio_phy_values_334488[(int8_t)projected];
 uint32_t encrypted=*(volatile uint8_t *)(input+16u);
 *(volatile uint8_t *)(record+292u)=(uint8_t)phy;
 *(volatile uint8_t *)(record+484u)=encrypted!=0u;
 if(encrypted!=0u){
  (void)opencfw_em9305_radio_random_bytes_310038(record+485u,8u);
  (void)opencfw_em9305_radio_random_bytes_310038(record+493u,16u);
  opencfw_em9305_radio_encrypt_seed_317334(record+493u,input+17u,record+92u);
 }
 uint32_t period=*(volatile uint32_t *)(input+4u);
 uint32_t length=*(volatile uint16_t *)(input+8u);
 uint32_t remainder=period%1250u;
 *(volatile uint32_t *)(record+8u)=period;
 uint32_t size=length<251u?length:251u;
 *(volatile uint16_t *)(record+6u)=(uint16_t)length;
 *(volatile uint16_t *)(record+4u)=(uint16_t)size;
 *(volatile uint32_t *)(record+16u)=period-remainder;
 if(remainder!=0u) *(volatile uint8_t *)(record+30u)=1u;
 if(remainder!=0u || *(volatile uint8_t *)(record+30u)==1u){
  size=length>210u?251u:length+40u;
  *(volatile uint16_t *)(record+4u)=(uint16_t)size;
 }
 uint32_t timing=opencfw_em9305_radio_record_timing_30c40c(length,(uint16_t)size);
 uint32_t count=*(volatile uint8_t *)(input+12u)+1u;
 uint32_t secure=*(volatile uint8_t *)(record+484u);
 uint32_t live_size=*(volatile uint8_t *)(record+4u);
 uint32_t product=opencfw_em9305_native_mpywhl(timing,count);
 phy=*(volatile uint8_t *)(record+292u);
 uint32_t inputs=*(volatile uint8_t *)(input+2u);
 uint32_t single=*(volatile uint8_t *)(record+31u);
 *(volatile uint8_t *)(record+24u)=(uint8_t)timing;
 *(volatile uint8_t *)(record+27u)=(uint8_t)count;
 *(volatile uint8_t *)(record+25u)=(uint8_t)product;
 uint32_t duration=opencfw_em9305_radio_phy_duration_31737c(phy,live_size,secure);
 uint32_t stride=duration+150u;
 uint32_t groups=(uint8_t)product;
 uint32_t multiplier=single==1u?1u:groups;
 uint32_t number=single==1u?inputs:1u;
 uint32_t first=opencfw_em9305_native_mpywhl(stride,number);
 uint32_t second=opencfw_em9305_native_mpywhl(stride,multiplier);
 *(volatile uint16_t *)(record+28u)=511u;
 *(volatile uint32_t *)(record+48u)=first;
 *(volatile uint32_t *)(record+12u)=second;
 inputs=*(volatile uint8_t *)(input+2u);
 *(volatile uint8_t *)(record+26u)=0u;
 uint32_t a,b;
 if(single==1u){a=stride;b=opencfw_em9305_native_mpywhl(stride,inputs);}
 else {a=opencfw_em9305_native_mpywhl(stride,groups);b=stride;}
 *(volatile uint32_t *)(record+12u)=a;
 *(volatile uint32_t *)(record+48u)=b;
 uint32_t span=a*(inputs-1u)+duration+b*(groups-1u);
 *(volatile uint32_t *)(record+40u)=span;
 uint32_t total=5000u;
 if((uint8_t)timing!=0u){
  period=*(volatile uint32_t *)(record+8u);
  if(period!=0u){
   kind=*(volatile uint8_t *)(record+30u);
   total=*(volatile uint32_t *)(record+16u);
   total+=kind==1u?period+span:span-period;
  }
 }
 *(volatile uint32_t *)(record+44u)=total;
}

/* Native31737c..3173ac: PHY duration with encrypted four-byte addition. */
uint32_t opencfw_em9305_radio_phy_duration_31737c(uint32_t phy,uint32_t length,uint32_t encrypted)
{
 if(encrypted!=0u) length+=4u;
 if(phy==2u) return 44u+(length<<2u);
 if(phy==3u) return (length<<6u)+720u;
 return (length<<3u)+80u;
}
/* Native334b80..334b98: key16 and two4B messages consumed by317334. */
static const uint8_t opencfw_em9305_seed_constants_334b80[24]={49u,71u,73u,66u,0u,0u,0u,0u,0u,0u,0u,0u,0u,0u,0u,0u,50u,71u,73u,66u,51u,71u,73u,66u};
/* Native317334..31737c: four ordered keyed message projections. */
extern uint32_t opencfw_em9305_radio_keyed_message_30fdb8(uintptr_t,uintptr_t,uintptr_t,uint32_t);
void opencfw_em9305_radio_encrypt_seed_317334(uintptr_t key,uintptr_t input,uintptr_t output)
{
 _Alignas(4) uint8_t scratch[48];
 (void)opencfw_em9305_radio_keyed_message_30fdb8((uintptr_t)opencfw_em9305_seed_constants_334b80,(uintptr_t)(scratch+32u),input,16u);
 (void)opencfw_em9305_radio_keyed_message_30fdb8((uintptr_t)(scratch+32u),(uintptr_t)(scratch+16u),(uintptr_t)(opencfw_em9305_seed_constants_334b80+16u),4u);
 (void)opencfw_em9305_radio_keyed_message_30fdb8(key,(uintptr_t)scratch,(uintptr_t)(scratch+16u),16u);
 (void)opencfw_em9305_radio_keyed_message_30fdb8((uintptr_t)scratch,output,(uintptr_t)(opencfw_em9305_seed_constants_334b80+20u),4u);
}

/* Native333584..3335a4: big-endian block doubling. The second source read
 * occurs after the destination write, including for overlapping buffers. */
void opencfw_em9305_radio_block_shift_333584(uintptr_t input,uintptr_t output)
{
 uint32_t carry=0u;
 for (uint32_t i=16u;i!=0u;--i) {
  uint32_t byte=*(volatile uint8_t *)(input+i-1u);
  *(volatile uint8_t *)(output+i-1u)=(uint8_t)(carry+2u*byte);
  carry=*(volatile uint8_t *)(input+i-1u)>>7;
 }
}
/* Native3335d8..3335f4: R1 is dead; native reduction is an immediate. */
void opencfw_em9305_radio_block_reduce_3335d8(uintptr_t input,uintptr_t unused,uintptr_t output)
{
 (void)unused;
 for (uint32_t i=0u;i<3u;++i)
  *(volatile uint32_t *)(output+4u*i)=*(volatile uint32_t *)(input+4u*i);
 uint32_t last=*(volatile uint32_t *)(input+12u);
 *(volatile uint32_t *)(output+12u)=last^0x87000000u;
}
/* Native30fdb8..30ff0c: native scratch layout and cipher call order.
 * Non-16 lengths reverse exactly four bytes; native leaves the other bytes
 * undefined. Current seed callers use only lengths four and sixteen.
 * R0 on return is the reversed-output scratch pointer minus one. */
uint32_t opencfw_em9305_radio_keyed_message_30fdb8(uintptr_t key,uintptr_t output,uintptr_t input,uint32_t length)
{
 _Alignas(4) uint8_t scratch[112];
 uint32_t reversed=length==16u?16u:4u;
 for (uint32_t i=0u;i<reversed;++i)
  *(volatile uint8_t *)(scratch+64u+i)=*(volatile uint8_t *)(input+reversed-1u-i);
 for (uint32_t i=0u;i<16u;++i)
  *(volatile uint8_t *)(scratch+80u+i)=*(volatile uint8_t *)(key+15u-i);
 for (uint32_t i=0u;i<4u;++i) *(volatile uint32_t *)(scratch+4u*i)=0u;
 (void)opencfw_em9305_radio_request_enter_310678();
 (void)opencfw_em9305_rom_cipher_block_10090c((uintptr_t)scratch,(uintptr_t)(scratch+32u),0u);
 (void)opencfw_em9305_radio_request_exit_31069c();
 for (uint32_t round=0u;round<2u;++round) {
  uintptr_t src=(uintptr_t)(scratch+(round==0u?32u:16u));
  uintptr_t dst=(uintptr_t)(scratch+(round==0u?16u:48u));
  if (*(volatile int8_t *)src<0) {
   opencfw_em9305_radio_block_shift_333584(src,(uintptr_t)(scratch+96u));
   opencfw_em9305_radio_block_reduce_3335d8((uintptr_t)(scratch+96u),0x3357c0u,dst);
  } else opencfw_em9305_radio_block_shift_333584(src,dst);
 }
 if (length==16u) {
  for (uint32_t i=0u;i<4u;++i)
   *(volatile uint32_t *)(scratch+4u*i)=*(volatile uint32_t *)(scratch+64u+4u*i)^*(volatile uint32_t *)(scratch+16u+4u*i);
 } else {
  for (uint32_t i=0u;i<16u;++i)
   *(volatile uint8_t *)(scratch+32u+i)=i<(uint8_t)length?*(volatile uint8_t *)(scratch+64u+i):i==(uint8_t)length?0x80u:0u;
  for (uint32_t i=0u;i<4u;++i)
   *(volatile uint32_t *)(scratch+4u*i)=*(volatile uint32_t *)(scratch+32u+4u*i)^*(volatile uint32_t *)(scratch+48u+4u*i);
 }
 (void)opencfw_em9305_radio_request_enter_310678();
 (void)opencfw_em9305_rom_cipher_key_1009c0((uintptr_t)(scratch+80u),0u);
 (void)opencfw_em9305_rom_cipher_block_10090c((uintptr_t)scratch,(uintptr_t)(scratch+32u),0u);
 (void)opencfw_em9305_radio_request_exit_31069c();
 for (uint32_t i=0u;i<16u;++i)
  *(volatile uint8_t *)(output+i)=*(volatile uint8_t *)(scratch+47u-i);
 return (uint32_t)(uintptr_t)(scratch+31u);
}

extern uint32_t opencfw_em9305_radio_access_seed_3189cc(void);
extern uint32_t opencfw_em9305_radio_crc_seed_318960(void);
extern uint32_t opencfw_em9305_radio_access_mix_3188b8(uint32_t,uint32_t);
extern uint32_t opencfw_em9305_radio_channel_transform_30e3fc(uintptr_t);
/* Native32c2b0..32c3bc: ordered record finalization. Genuine seed/channel
 * children and optional queue callback remain external contracts. */
uint32_t opencfw_em9305_radio_record_finish_32c2b0(uintptr_t record)
{
 uint32_t access=opencfw_em9305_radio_access_seed_3189cc();
 *(volatile uint32_t *)(record+344u)=access;
 uint32_t crc=opencfw_em9305_radio_crc_seed_318960();
 *(volatile uint16_t *)(record+348u)=(uint16_t)(crc>>8);
 access=*(volatile uint32_t *)(record+344u);
 *(volatile uint8_t *)(record+408u)=13u;
 access=opencfw_em9305_radio_access_mix_3188b8(access,0u);
 *(volatile uint32_t *)(record+412u)=access;
 uint32_t upper=*(volatile uint32_t *)(uintptr_t)0x805aa4u;
 uint32_t lower=*(volatile uint32_t *)(uintptr_t)0x805aa0u;
 *(volatile uint16_t *)(record+400u)=(uint16_t)(access^(access>>16));
 *(volatile uint8_t *)(record+398u)=1u;
 *(volatile uint32_t *)(record+356u)=upper;
 *(volatile uint32_t *)(record+352u)=lower;
 (void)opencfw_em9305_radio_channel_transform_30e3fc(record+352u);
 uint32_t shifted=(uint32_t)*(volatile uint16_t *)(record+348u)<<8;
 uint32_t secure=*(volatile uint8_t *)(record+484u);
 uint32_t mode=*(volatile uint8_t *)(uintptr_t)0x805a9cu;
 uint32_t phy=*(volatile uint8_t *)(record+292u);
 *(volatile uint16_t *)(record+422u)=0u;
 *(volatile uint8_t *)(record+410u)=(uint8_t)mode;
 *(volatile uint8_t *)(record+420u)=(uint8_t)phy;
 *(volatile uint32_t *)(record+416u)=shifted;
 if (secure==0u) return shifted;
 *(volatile uint8_t *)(record+452u)=1u;
 *(volatile uint16_t *)(record+454u)=513u;
 (void)opencfw_em9305_memcpy((void *)(record+444u),(const void *)(record+485u),8u);
 access=*(volatile uint32_t *)(record+412u);
 uint32_t a=*(volatile uint8_t *)(record+444u);
 uint32_t b=*(volatile uint8_t *)(record+445u);
 uint32_t c=*(volatile uint8_t *)(record+446u);
 uint32_t d=*(volatile uint8_t *)(record+447u);
 *(volatile uint8_t *)(record+444u)=(uint8_t)(a^access);
 *(volatile uint8_t *)(record+445u)=(uint8_t)(b^(access>>8));
 *(volatile uint8_t *)(record+446u)=(uint8_t)(c^(access>>16));
 *(volatile uint8_t *)(record+447u)=(uint8_t)(d^(access>>24));
 (void)opencfw_em9305_memcpy((void *)(record+428u),(const void *)(record+92u),16u);
 uintptr_t callback=*(volatile uint32_t *)(uintptr_t)0x8028c0u;
 *(volatile uint16_t *)(record+468u)=513u;
 if (callback!=0u) {
  uintptr_t base=*(volatile uint32_t *)(uintptr_t)0x805c3cu;
  uint32_t index=(uint32_t)(record-base)>>9;
  return ((uint32_t (*)(uintptr_t,uint32_t,uint32_t))callback)(record+428u,(uint8_t)(index+6u),1u);
 }
 return (uint32_t)(record+428u);
}

/* Native318878/3189cc bounded indices each select32 authenticated data bytes. */
static const uint8_t opencfw_em9305_access_tables_334c6c[64]={8,16,20,24,32,48,52,56,64,68,76,92,88,96,112,120,244,236,232,228,220,204,200,196,188,184,176,160,164,156,140,132,130,134,138,142,162,166,170,174,194,198,202,206,226,230,234,238,17,21,25,29,49,53,57,61,81,85,89,93,113,117,121,125};
/* Native318878..3188b8: PRNG step and bounded access seed projection. */
uint32_t opencfw_em9305_radio_access_raw_318878(void)
{
 uint32_t value=opencfw_em9305_pal_random_step();
 uint32_t bits=opencfw_em9305_access_tables_334c6c[value>>27];
 uint32_t low=value&0x017af5c0u;
 low|=(value&1u)==0u?0x0081020eu:0x02040831u;
 return low|((bits<<24)&0xfd000000u);
}
/* Native3189cc..3189f4. */
uint32_t opencfw_em9305_radio_access_seed_3189cc(void)
{
 uint32_t value=opencfw_em9305_radio_access_raw_318878();
 uint32_t bits=opencfw_em9305_access_tables_334c6c[32u+(value>>27)];
 return (value&0xfd007fffu)+(bits<<15)+0x00800000u;
}
/* Native318960..31896c through native30c478 tail to selected PRNG. */
uint32_t opencfw_em9305_radio_crc_seed_318960(void)
{
 return opencfw_em9305_pal_random_step()&0x00ffffffu;
}
/* Native3188b8..318920: native low-word multiply retained as ISA. */
uint32_t opencfw_em9305_radio_access_mix_3188b8(uint32_t value,uint32_t index)
{
 uint32_t product;
 __asm__ volatile("mpyuw %0,%1,35":"=r"(product):"r"(index));
 uint32_t byte=(uint8_t)(product+42u);
 uint32_t half=byte>>1;
 uint32_t sum=((half&1u)<<23)+(0x01000000u&(byte<<18))+(0x00200000u&(byte<<16))+(0x00100000u&(byte<<16))+(0x00040000u&(byte<<15))+(0x00020000u&(byte<<15));
 uint32_t adjust=((half&1u)<<25)-((product&1u)<<26);
 return value^(adjust|sum);
}
/* Native30e3fc..30e42c: fresh two-word channel mask each iteration and
 * ordered compact channel bytes. Native3027f4 shift index stays0..36. */
uint32_t opencfw_em9305_radio_channel_transform_30e3fc(uintptr_t channels)
{
 uint32_t count=0u,last=0u;
 for (uint32_t index=0u;index<37u;++index) {
  uint32_t low=*(volatile uint32_t *)channels;
  uint32_t high=*(volatile uint32_t *)(channels+4u);
  last=index==0u?low:index<32u?(low>>index)|(high<<(32u-index)):high>>(index-32u);
  if ((last&1u)!=0u) {
   last=(uint32_t)(channels+count);
   count+=1u;
   *(volatile uint8_t *)(channels+8u+count-1u)=(uint8_t)index;
  }
 }
 *(volatile uint8_t *)(channels+45u)=(uint8_t)count;
 return last;
}

/* Native327718..32780c: full stream setup. Its incidental R0 return is
 * an integer/callback result, discarded by native record-apply caller. */
uintptr_t opencfw_em9305_radio_stream_setup_327718(uintptr_t stream,uint32_t access,uint32_t crc,uint32_t lower,uint32_t upper,uint32_t phy)
{
 uintptr_t parent=*(volatile uint32_t *)(stream+4u);
 uint32_t mode=*(volatile uint8_t *)(parent+3u);
 uint32_t id=*(volatile uint8_t *)(stream+1u);
 *(volatile uint8_t *)(stream+176u)=(uint8_t)(12u+(mode==1u));
 access=opencfw_em9305_radio_access_mix_3188b8(access,id);
 *(volatile uint16_t *)(stream+168u)=(uint16_t)(access^(access>>16));
 *(volatile uint32_t *)(stream+124u)=upper;
 *(volatile uint32_t *)(stream+120u)=lower;
 *(volatile uint8_t *)(stream+166u)=1u;
 (void)opencfw_em9305_radio_channel_transform_30e3fc(stream+120u);
 parent=*(volatile uint32_t *)(stream+4u);
 *(volatile uint16_t *)(stream+190u)=0u;
 id=*(volatile uint8_t *)(stream+1u);
 uint32_t secure=*(volatile uint8_t *)(parent+484u);
 uint32_t global_mode=*(volatile uint8_t *)(uintptr_t)0x805a9cu;
 uint32_t packed=(crc<<8)+id;
 *(volatile uint32_t *)(stream+180u)=access;
 *(volatile uint8_t *)(stream+189u)=(uint8_t)phy;
 *(volatile uint8_t *)(stream+188u)=(uint8_t)phy;
 *(volatile uint8_t *)(stream+178u)=(uint8_t)global_mode;
 *(volatile uint32_t *)(stream+184u)=packed;
 if (secure==0u) return packed;
 *(volatile uint32_t *)(stream+220u)=0x02010101u;
 (void)opencfw_em9305_memcpy((void *)(stream+212u),(const void *)(parent+485u),8u);
 uint32_t a=*(volatile uint8_t *)(stream+212u);
 uint32_t b=*(volatile uint8_t *)(stream+213u);
 uint32_t c=*(volatile uint8_t *)(stream+214u);
 uint32_t d=*(volatile uint8_t *)(stream+215u);
 *(volatile uint8_t *)(stream+212u)=(uint8_t)(a^access);
 *(volatile uint8_t *)(stream+213u)=(uint8_t)(b^(access>>8));
 *(volatile uint8_t *)(stream+214u)=(uint8_t)(c^(access>>16));
 *(volatile uint8_t *)(stream+215u)=(uint8_t)(d^(access>>24));
 (void)opencfw_em9305_memcpy((void *)(stream+196u),(const void *)(parent+92u),16u);
 uintptr_t callback=*(volatile uint32_t *)(uintptr_t)0x8028c0u;
 *(volatile uint16_t *)(stream+236u)=513u;
 if (callback!=0u) {
  uint32_t callback_id=*(volatile uint8_t *)(stream+2u);
  return ((uintptr_t (*)(uintptr_t,uint32_t,uint32_t))callback)(stream+196u,callback_id,1u);
 }
 return 513u;
}

/* Native30c3a4..30c40c: restoring division with two-word shifted divisor.
 * Native quotient-mask overflow returns zero. Zero divisor loops forever;
 * the compiler barrier preserves that native nonterminating control path. */
uint32_t opencfw_em9305_radio_unsigned_divide_30c3a4(uint32_t numerator,uint32_t denominator)
{
 if (numerator<denominator) return 0u;
 uint32_t high=0u,low=denominator,mask=1u;
 do {
  high=(high<<1)|(low>>31);
  low<<=1;
  mask<<=1;
  __asm__ volatile("" ::: "memory");
 } while (high==0u && numerator>=low);
 if (mask==0u) return 0u;
 uint32_t remainder_high=0u,quotient=0u;
 for (;;) {
  uint32_t next_high=high>>1;
  low=(low>>1)|(high<<31);
  uint32_t next_mask=mask>>1;
  if (remainder_high>next_high || (remainder_high==next_high && numerator>=low)) {
   uint32_t borrow=numerator<low;
   numerator-=low;
   quotient+=next_mask;
   remainder_high-=next_high+borrow;
  }
  uint32_t old_mask=mask;
  high=next_high;
  mask=next_mask;
  if (old_mask<=3u) return quotient;
 }
}
/* Native30c40c..30c414: wrapping add-minus-one then native division. */
uint32_t opencfw_em9305_radio_record_timing_30c40c(uint32_t length,uint32_t unit)
{
 return opencfw_em9305_radio_unsigned_divide_30c3a4(length+unit-1u,unit);
}

static uint32_t opencfw_em9305_native_div_309f5e(uint32_t a,uint32_t b)
{ uint32_t r; __asm__ volatile("div %0,%1,%2":"=r"(r):"r"(a),"r"(b)); return r; }
static uint32_t opencfw_em9305_native_divu_309fd6(uint32_t a,uint32_t b)
{ uint32_t r; __asm__ volatile("divu %0,%1,%2":"=r"(r):"r"(a),"r"(b)); return r; }
static uint32_t opencfw_em9305_native_mpyw_309f62(uint32_t a,uint32_t b)
{ uint32_t r; __asm__ volatile("mpyw %0,%1,%2":"=r"(r):"r"(a),"r"(b)); return r; }
/* Native309e60..30a0a4: full extended apply, including native arithmetic
 * and unusual timing-failure return (original requested stream count). */
uint32_t opencfw_em9305_radio_record_extended_apply_309e60(uintptr_t input)
{
 uint32_t required=*(volatile uint8_t *)(input+2u);
 if(opencfw_em9305_ll_stream_free_count_31b248()<required) return 13u;
 if(opencfw_em9305_ll_record_find_31aa98(*(volatile uint8_t *)input)!=0u) return 12u;
 if(opencfw_em9305_radio_association_exists_317280(*(volatile uint8_t *)(input+1u))==1u) return 18u;
 uintptr_t record=opencfw_em9305_ll_record_allocate_316a8c(*(volatile uint8_t *)input);
 if(record==0u) return 13u;
 *(volatile uint8_t *)(record+3u)=1u;
 uint32_t single=*(volatile uint8_t *)(input+33u);
 uint32_t mode=*(volatile uint8_t *)(input+34u);
 *(volatile uint8_t *)(record+31u)=(uint8_t)single;
 uint32_t requested=*(volatile uint8_t *)(input+32u);
 *(volatile uint8_t *)(record+30u)=(uint8_t)mode;
 uint32_t projected=opencfw_em9305_radio_phy_project_3183d4(requested)-2u;
 uint32_t phy=1u;
 if((uint8_t)projected<7u) phy=opencfw_em9305_radio_phy_values_334488[(int8_t)projected];
 uint32_t encrypted=*(volatile uint8_t *)(input+38u);
 *(volatile uint8_t *)(record+292u)=(uint8_t)phy;
 *(volatile uint8_t *)(record+484u)=encrypted!=0u;
 if(encrypted!=0u){
  (void)opencfw_em9305_radio_random_bytes_310038(record+485u,8u);
  (void)opencfw_em9305_radio_random_bytes_310038(record+493u,16u);
  opencfw_em9305_radio_encrypt_seed_317334(record+493u,input+8u,record+92u);
 }
 uint32_t groups=*(volatile uint8_t *)(input+35u);
 uint32_t factor=*(volatile uint8_t *)(input+36u);
 uint32_t length=*(volatile uint16_t *)(input+28u);
 uint32_t interval=*(volatile uint16_t *)(input+24u);
 uint32_t size=*(volatile uint16_t *)(input+30u);
 uint32_t option=*(volatile uint8_t *)(input+37u);
 uint32_t period=*(volatile uint32_t *)(input+4u);
 uint32_t count=*(volatile uint8_t *)(input+26u);
 *(volatile uint16_t *)(record+6u)=(uint16_t)length;
 uint32_t product,scaled;
 __asm__ volatile("mpyuw %0,%1,1250":"=r"(scaled):"r"(interval));
 __asm__ volatile("mpyuw %0,%1,%2":"=r"(product):"r"(factor),"r"(groups));
 *(volatile uint16_t *)(record+4u)=(uint16_t)size;
 *(volatile uint32_t *)(record+8u)=period;
 *(volatile uint8_t *)(record+24u)=(uint8_t)groups;
 *(volatile uint8_t *)(record+27u)=(uint8_t)factor;
 *(volatile uint8_t *)(record+26u)=(uint8_t)option;
 *(volatile uint8_t *)(record+25u)=(uint8_t)count;
 *(volatile uint32_t *)(record+16u)=scaled;
 uint32_t original=count;
 if(option==0u && product<count){
  do {original-=groups;count=(uint8_t)original;} while(product<count);
  *(volatile uint8_t *)(record+25u)=(uint8_t)original;
 }
 uint32_t delta=opencfw_em9305_native_div_309f5e(count-product,groups);
 uint32_t extra=opencfw_em9305_native_mpyw_309f62(delta,option);
 *(volatile uint8_t *)(record+194u)=(uint8_t)extra;
 uint32_t tail=option!=0u?opencfw_em9305_native_mpyw_309f62(original-product,option):255u;
 uint32_t secure=*(volatile uint8_t *)(record+484u);
 phy=*(volatile uint8_t *)(record+292u);
 single=*(volatile uint8_t *)(record+31u);
 uint32_t inputs=*(volatile uint8_t *)(input+2u);
 *(volatile uint8_t *)(record+28u)=(uint8_t)tail;
 uint32_t duration=opencfw_em9305_radio_phy_duration_31737c(phy,(uint8_t)size,secure);
 uint32_t stride=duration+150u;
 uint32_t multiplier=inputs,a=stride;
 if(single!=1u){a=opencfw_em9305_native_mpywhl(stride,count);multiplier=1u;}
 *(volatile uint32_t *)(record+12u)=a;
 uint32_t b=opencfw_em9305_native_mpywhl(stride,multiplier);
 uint32_t span=a*(inputs-1u)+duration+b*(count-1u);
 *(volatile uint32_t *)(record+48u)=b;
 *(volatile uint32_t *)(record+40u)=span;
 uint32_t total=5000u;
 if(groups!=0u && period!=0u){
  uint32_t steps=opencfw_em9305_native_divu_309fd6((uint8_t)original,groups)-factor;
  steps=opencfw_em9305_native_mpywhl(steps,option);
  uint32_t aligned=*(volatile uint8_t *)(record+30u);
  if(aligned==1u){period+=scaled;span+=period;}else{span-=period;steps+=1u;}
  total=steps*scaled+span;
 }
 *(volatile uint32_t *)(record+44u)=total;
 (void)opencfw_em9305_radio_record_finish_32c2b0(record);
 uint32_t fresh_size=*(volatile uint16_t *)(record+4u);
 uint32_t fresh_length=*(volatile uint16_t *)(record+6u);
 uint32_t timing=opencfw_em9305_radio_record_timing_30c40c(fresh_length,fresh_size);
 if(timing>=9u) return required;
 if(*(volatile uint8_t *)(input+2u)!=0u){
  uint32_t index=0u;
  do {
   uintptr_t stream=opencfw_em9305_radio_stream_allocate_316ad4(record);
   if(stream==0u){opencfw_em9305_radio_record_release_31ac84(record);return 13u;}
   phy=*(volatile uint8_t *)(record+292u);
   uint32_t crc=*(volatile uint16_t *)(record+348u);
   uint32_t access=*(volatile uint32_t *)(record+344u);
   uint32_t lower=*(volatile uint32_t *)(uintptr_t)0x805aa0u;
   uint32_t upper=*(volatile uint32_t *)(uintptr_t)0x805aa4u;
   (void)opencfw_em9305_radio_stream_setup_327718(stream,access,crc,lower,upper,phy);
   uint32_t fresh=*(volatile uint8_t *)(input+2u);
   ++index;
   if(index>=fresh) break;
  }while(1);
 }
 uintptr_t associated=opencfw_em9305_radio_record_find_31aa64(*(volatile uint8_t *)(input+1u));
 if(associated!=0u){
  *(volatile uint32_t *)(record+180u)=(uint32_t)associated;
  *(volatile uint32_t *)(associated+2804u)=(uint32_t)(uintptr_t)&opencfw_em9305_radio_association_callback_3291e4;
  *(volatile uint32_t *)(associated+2800u)=(uint32_t)(uintptr_t)&opencfw_em9305_radio_association_callback_3291d0;
  *(volatile uint32_t *)(associated+2796u)=(uint32_t)(uintptr_t)&opencfw_em9305_radio_association_callback_3290c4;
 }
 uintptr_t message=opencfw_em9305_wsf_event_allocate(4u);
 if(message!=0u){
  *(volatile uint16_t *)(message+2u)=272u;
  uint32_t id=*(volatile uint8_t *)input;
  uint32_t handler=*(volatile uint8_t *)(uintptr_t)0x805b18u;
  *(volatile uint16_t *)message=(uint16_t)id;
  opencfw_em9305_wsf_task_message_send(handler,message);
 }
 return 0u;
}

/* Native327a4c..327a54: source-owned96-byte clear through selected memset. */
void *opencfw_em9305_radio_association_clear_327a4c(uintptr_t object)
{
 return opencfw_em9305_memset((void *)object,0u,96u);
}
/* Native3291d0..3291e4: association callback's incoming R0 is the id. */
void opencfw_em9305_radio_association_callback_3291d0(uint32_t id)
{
 uintptr_t associated=opencfw_em9305_radio_record_find_31aa64(id);
 (void)opencfw_em9305_radio_association_clear_327a4c(associated+176u);
}
/* Native3291e4..32922c: clear first matching parent-mode1 association.
 * Native does not test active byte0 and missing association can match zero. */
void opencfw_em9305_radio_association_callback_3291e4(uint32_t id)
{
 uintptr_t associated=opencfw_em9305_radio_record_find_31aa64(id);
 uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
 uint32_t count=*(volatile uint8_t *)(config+57u);
 if(count==0u) return;
 uintptr_t record=*(volatile uint32_t *)(uintptr_t)0x805c3cu;
 uintptr_t field=record+180u;
 for(uint32_t i=0u;i<count;++i){
  uint32_t mode=*(volatile uint8_t *)(record+3u);
  if(mode==1u){
   uintptr_t value=*(volatile uint32_t *)field;
   if(value==associated){*(volatile uint32_t *)field=0u;return;}
  }
  field+=512u;record+=512u;
 }
}

struct opencfw_em9305_native_product_pair {uint32_t low,high;};
static struct opencfw_em9305_native_product_pair opencfw_em9305_native_mpydu_329154(uint32_t a,uint32_t b)
{
 register uint32_t low __asm__("r2");
 register uint32_t high __asm__("r3");
 __asm__ volatile("mpydu r2,%2,%3":"=r"(low),"=r"(high):"r"(a),"r"(b));
 struct opencfw_em9305_native_product_pair result={low,high};return result;
}
/* Native3290c4..3291d0: full association update callback, incoming idR0.
 * Native lookup results are used without invented null guards. MPYDU pair
 * and MPYWHL remain genuine target ISA; field access/write order retained. */
void opencfw_em9305_radio_association_callback_3290c4(uint32_t id)
{
 uintptr_t associated=opencfw_em9305_radio_record_find_31aa64(id);
 uintptr_t command=*(volatile uint32_t *)(uintptr_t)0x805c34u;
 uint32_t record_id=*(volatile uint8_t *)(command+4u);
 uintptr_t record=opencfw_em9305_ll_record_find_31aa98(record_id);
 uint32_t secure=*(volatile uint8_t *)(record+484u);
 if(secure!=0u){
  *(volatile uint8_t *)(associated+178u)=57u;
  (void)opencfw_em9305_memcpy((void *)(associated+246u),(const void *)(record+485u),8u);
  (void)opencfw_em9305_memcpy((void *)(associated+254u),(const void *)(record+493u),16u);
  secure=*(volatile uint8_t *)(record+484u);
 }else{*(volatile uint8_t *)(associated+178u)=33u;secure=0u;}
 uint32_t second=*(volatile uint32_t *)(record+48u);
 uint32_t option=*(volatile uint8_t *)(record+26u);
 uint32_t factor=*(volatile uint8_t *)(record+27u);
 uint32_t aligned=*(volatile uint32_t *)(record+16u);
 uint32_t groups=*(volatile uint8_t *)(record+24u);
 uint32_t first=*(volatile uint32_t *)(record+12u);
 uint32_t access=*(volatile uint32_t *)(record+344u);
 uint32_t lower=*(volatile uint32_t *)(record+352u);
 uint32_t time_low=*(volatile uint32_t *)(record+32u);
 uint32_t time_high=*(volatile uint32_t *)(record+36u);
 *(volatile uint32_t *)(associated+196u)=second;
 *(volatile uint8_t *)(associated+200u)=(uint8_t)option;
 *(volatile uint8_t *)(associated+208u)=(uint8_t)factor;
 struct opencfw_em9305_native_product_pair scaled=opencfw_em9305_native_mpydu_329154(aligned,0x001a36e3u);
 uint32_t phy=*(volatile uint8_t *)(record+292u);
 *(volatile uint32_t *)(associated+204u)=first;
 *(volatile uint32_t *)(associated+212u)=access;
 *(volatile uint32_t *)(associated+224u)=lower;
 struct opencfw_em9305_native_product_pair time=opencfw_em9305_native_mpydu_329154(time_low,groups);
 uint32_t high=opencfw_em9305_native_mpywhl(time_high,groups);
 uint32_t streams=*(volatile uint8_t *)(record+52u);
 uint32_t count=*(volatile uint8_t *)(record+25u);
 uint32_t size=*(volatile uint16_t *)(record+4u);
 uint32_t period=*(volatile uint32_t *)(record+8u);
 uint32_t length=*(volatile uint16_t *)(record+6u);
 uint32_t crc=*(volatile uint16_t *)(record+348u);
 uint32_t upper=*(volatile uint32_t *)(record+356u);
 uint32_t mode=*(volatile uint8_t *)(record+30u);
 *(volatile uint8_t *)(associated+232u)=(uint8_t)phy;
 uint32_t timing=(scaled.high<<1)|(scaled.low>>31);
 high+=time.high;
 *(volatile uint8_t *)(associated+176u)=1u;
 *(volatile uint8_t *)(associated+245u)=(uint8_t)secure;
 *(volatile uint8_t *)(associated+192u)=(uint8_t)streams;
 *(volatile uint8_t *)(associated+193u)=(uint8_t)count;
 *(volatile uint8_t *)(associated+194u)=(uint8_t)groups;
 *(volatile uint16_t *)(associated+210u)=(uint16_t)size;
 *(volatile uint32_t *)(associated+216u)=period;
 *(volatile uint16_t *)(associated+220u)=(uint16_t)length;
 *(volatile uint16_t *)(associated+222u)=(uint16_t)crc;
 *(volatile uint32_t *)(associated+228u)=upper;
 *(volatile uint8_t *)(associated+244u)=(uint8_t)mode;
 *(volatile uint32_t *)(associated+236u)=time.low;
 *(volatile uint16_t *)(associated+190u)=(uint16_t)timing;
 *(volatile uint32_t *)(associated+240u)=high;
}
/* Native317680..3177e8: packet ownership, segmentation, timing callback
 * and queue delivery. Local timing pointer is published only during loop. */
uint32_t opencfw_em9305_ll_stream_process_317680(uintptr_t stream,uintptr_t decoded,uintptr_t message)
{
 _Alignas(4) uint32_t timing[2];
 uintptr_t packet=opencfw_em9305_ll_stream_packet_take_316e5c();
 if(packet==0u){
  (void)opencfw_em9305_wsf_event_release(message);
  uintptr_t callback=*(volatile uint32_t *)(uintptr_t)0x805b38u;
  if(callback!=0u && *(volatile uint8_t *)(stream+108u)==0u){
   uint16_t id=*(volatile uint16_t *)decoded,one=1u;
   (void)((uint32_t (*)(uint32_t,uintptr_t,uintptr_t))callback)(1u,(uintptr_t)&id,(uintptr_t)&one);
  }
  (void)opencfw_em9305_wsf_critical_enter();
  uint32_t counter=*(volatile uint8_t *)(uintptr_t)0x805adcu;
  *(volatile uint8_t *)(uintptr_t)0x805adcu=(uint8_t)(counter+1u);
  (void)opencfw_em9305_wsf_critical_exit();
  return opencfw_em9305_ll_segment_error_32322c(7u);
 }
 uintptr_t parent=*(volatile uint32_t *)(stream+4u);
 *(volatile uint8_t *)(packet+13u)=0u;
 *(volatile uint8_t *)(packet+12u)=*(volatile uint8_t *)(parent+28u);
 uint32_t total=*(volatile uint16_t *)(decoded+14u);
 parent=*(volatile uint32_t *)(stream+4u);
 uint32_t header=*(volatile uint8_t *)(decoded+3u);
 *(volatile uint16_t *)(packet+8u)=(uint16_t)total;
 uint32_t word=*(volatile uint32_t *)(decoded+8u);
 *(volatile uint8_t *)(packet+14u)=(uint8_t)header;
 uint32_t unit=*(volatile uint8_t *)(parent+4u);
 *(volatile uint8_t *)(packet+11u)=0u;
 *(volatile uint32_t *)packet=(uint32_t)message;
 *(volatile uint8_t *)(packet+10u)=(uint8_t)unit;
 header=*(volatile uint8_t *)(decoded+3u);
 *(volatile uint32_t *)(packet+16u)=word;
 uintptr_t payload=message+4u*header+8u;
 *(volatile uint32_t *)(packet+4u)=(uint32_t)payload;
 if(total==0u){
  uint32_t result=opencfw_em9305_ll_stream_segment_header_316f50(packet+22u,0u,0u);
  *(volatile uint8_t *)(packet+21u)=0u;
  *(volatile uint8_t *)(packet+20u)=(uint8_t)result;
  *(volatile uint8_t *)(packet+11u)=1u;
 }else{
  uint32_t progress=0u,index=0u;
  do{
   unit=*(volatile uint8_t *)(packet+10u);
   uint32_t remaining=(uint16_t)(total-progress);
   uint32_t mode=*(volatile uint8_t *)(parent+30u);
   uint32_t offset;
   __asm__ volatile("mpyuw %0,%1,13":"=r"(offset):"r"((uint32_t)(uint8_t)index));
   uint32_t chunk=remaining<unit?remaining:unit;
   progress+=chunk;
   uint32_t completed=(uint16_t)progress;
   uint32_t kind=mode!=0u?2u:completed!=total;
   uint32_t result=opencfw_em9305_ll_stream_segment_header_316f50(packet+offset+22u,chunk,kind);
   parent=*(volatile uint32_t *)(stream+4u);
   uint32_t current=*(volatile uint8_t *)(packet+11u);
   *(volatile uint32_t *)(stream+228u)=(uint32_t)(uintptr_t)timing;
   uint32_t groups=*(volatile uint8_t *)(parent+24u);
   uint32_t high_word=*(volatile uint32_t *)(parent+36u);
   uint32_t low_word=*(volatile uint32_t *)(parent+32u);
   __asm__ volatile("mpyuw %0,%1,13":"=r"(offset):"r"(current));
   uint32_t high=opencfw_em9305_native_mpywhl(high_word,groups);
   struct opencfw_em9305_native_product_pair product=opencfw_em9305_native_mpydu_329154(low_word,groups);
   uintptr_t callback=*(volatile uint32_t *)(uintptr_t)0x8051e0u;
   *(volatile uint8_t *)(packet+offset+20u)=(uint8_t)result;
   high+=product.high;
   uint32_t low=product.low+current;
   timing[0]=low;timing[1]=high+(low<product.low);
   if(callback!=0u){
    current=*(volatile uint8_t *)(packet+11u);
    __asm__ volatile("mpyuw %0,%1,13":"=r"(offset):"r"(current));
    uint32_t status=((uint32_t (*)(uintptr_t,uintptr_t,uintptr_t,uintptr_t))callback)(stream+196u,packet+offset+22u,payload,packet+offset+29u);
    if(status!=0u){
     current=*(volatile uint8_t *)(packet+11u);
     __asm__ volatile("mpyuw %0,%1,13":"=r"(offset):"r"(current));
     *(volatile uint8_t *)(packet+offset+21u)=4u;
    }else{
     current=*(volatile uint8_t *)(packet+11u);
     __asm__ volatile("mpyuw %0,%1,13":"=r"(offset):"r"(current));
     *(volatile uint8_t *)(packet+offset+21u)=0u;
    }
   }else{
    current=*(volatile uint8_t *)(packet+11u);
    __asm__ volatile("mpyuw %0,%1,13":"=r"(offset):"r"(current));
    *(volatile uint8_t *)(packet+offset+21u)=0u;
   }
   total=*(volatile uint16_t *)(packet+8u);
   index=current+1u;payload+=chunk;
   *(volatile uint8_t *)(packet+11u)=(uint8_t)index;
   if(completed>=total) break;
  }while(1);
  *(volatile uint32_t *)(stream+228u)=0u;
 }
 uint32_t handler=*(volatile uint8_t *)decoded;
 return opencfw_em9305_ll_event_enqueue(stream+8u,handler,packet);
}

/* Native331100..33118c: mask-gated event types47/48 and exact byte layout. */
uint32_t opencfw_em9305_dispatch_331100(uintptr_t input)
{
 uint32_t type=*(volatile uint8_t *)(input+2u);
 uintptr_t event;
 if(type==47u){
  if((*(volatile uint8_t *)(uintptr_t)0x8056fcu&1u)==0u) return 0u;
  if((*(volatile uint8_t *)(uintptr_t)0x8056efu&32u)==0u) return 0u;
  event=opencfw_em9305_ll_event_allocate(62u,9u);
  if(event==0u) return 0u;
  *(volatile uint8_t *)event=33u;
  *(volatile uint8_t *)(event+1u)=*(volatile uint8_t *)(input+4u);
  for(uint32_t i=2u;i<9u;++i)
   *(volatile uint8_t *)(event+i)=*(volatile uint8_t *)(input+i+4u);
 }else if(type==48u){
  if((*(volatile uint8_t *)(uintptr_t)0x8056fbu&128u)==0u) return 0u;
  if((*(volatile uint8_t *)(uintptr_t)0x8056efu&32u)==0u) return 0u;
  event=opencfw_em9305_ll_event_allocate(62u,5u);
  if(event==0u) return 0u;
  *(volatile uint8_t *)event=32u;
  for(uint32_t i=1u;i<5u;++i)
   *(volatile uint8_t *)(event+i)=*(volatile uint8_t *)(input+i+3u);
 }else return 0u;
 (void)opencfw_em9305_ll_event_send(event-2u);
 return 1u;
}

extern uint32_t opencfw_em9305_command_30db64(uint32_t,uintptr_t);
extern uint32_t opencfw_em9305_command_30dc20(uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uintptr_t);
extern uint32_t opencfw_em9305_command_30dccc(uint32_t,uint32_t,uint32_t,uintptr_t);
/* Native331204..331334: native byte capture order, scratch padding left
 * undefined, response command reread after provider allocation. 30dc20
 * carries a seventh native R6 pointer; C boundary ABI remains unqualified. */
uint32_t opencfw_em9305_dispatch_331204(uintptr_t request,uintptr_t input)
{
 uint32_t command=*(volatile uint16_t *)request,status,id=0u,kind=0u,length;
 if(command==0x2086u){
  _Alignas(4) uint8_t scratch[12],bytes[12];
  const uint8_t order[12]={2,1,4,6,10,3,5,0,7,8,9,11};
  for(uint32_t i=0u;i<12u;++i) bytes[order[i]]=*(volatile uint8_t *)(input+order[i]);
  *(volatile uint8_t *)(scratch+9u)=bytes[10];
  *(volatile uint16_t *)scratch=(uint16_t)(bytes[1]+((uint32_t)bytes[2]<<8));
  *(volatile uint8_t *)(scratch+6u)=bytes[7];
  *(volatile uint8_t *)(scratch+7u)=bytes[8];
  *(volatile uint8_t *)(scratch+8u)=bytes[9];
  *(volatile uint8_t *)(scratch+10u)=bytes[11];
  *(volatile uint16_t *)(scratch+2u)=(uint16_t)(bytes[3]+((uint32_t)bytes[4]<<8));
  *(volatile uint16_t *)(scratch+4u)=(uint16_t)(bytes[5]+((uint32_t)bytes[6]<<8));
  kind=bytes[0];status=opencfw_em9305_command_30db64(kind,(uintptr_t)scratch);length=2u;
 }else if(command==0x2083u){
  uint32_t b1=*(volatile uint8_t *)(input+1u),b3=*(volatile uint8_t *)(input+3u);
  uint32_t b0=*(volatile uint8_t *)input,b2=*(volatile uint8_t *)(input+2u);
  uint32_t b7=*(volatile uint8_t *)(input+7u),b6=*(volatile uint8_t *)(input+6u);
  uint32_t b5=*(volatile uint8_t *)(input+5u),b4=*(volatile uint8_t *)(input+4u);
  id=b0+(b1<<8);status=opencfw_em9305_command_30dc20(id,b2+(b3<<8),b4,b5,b6,b7,input+8u);length=3u;
 }else if(command==0x2084u){
  uint32_t b1=*(volatile uint8_t *)(input+1u),b3=*(volatile uint8_t *)(input+3u);
  uint32_t b0=*(volatile uint8_t *)input,b2=*(volatile uint8_t *)(input+2u);
  uint32_t count=*(volatile uint8_t *)(input+4u);
  id=b0+(b1<<8);status=opencfw_em9305_command_30dccc(id,b2+(b3<<8),count,input+5u);length=3u;
 }else return 0u;
 command=*(volatile uint16_t *)request;
 uintptr_t response=opencfw_em9305_ll_response_allocate_32e428(length,command);
 if(response==0u) return 1u;
 *(volatile uint8_t *)response=(uint8_t)status;
 command=*(volatile uint16_t *)request;
 if(command-0x2083u<2u){
  *(volatile uint8_t *)(response+1u)=(uint8_t)id;
  *(volatile uint8_t *)(response+2u)=(uint8_t)(id>>8);
 }else if(command==0x2086u) *(volatile uint8_t *)(response+1u)=(uint8_t)kind;
 (void)opencfw_em9305_ll_event_send(response-5u);
 return 1u;
}
extern uint32_t opencfw_em9305_command_apply_3093a0(uint32_t,uintptr_t);
extern uint32_t opencfw_em9305_command_apply_309514(uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uintptr_t);
extern uint32_t opencfw_em9305_command_apply_3098ac(uint32_t,uint32_t,uint32_t,uintptr_t);
/* Native30dc20..30dc48: native fullword bounds, inputR6 preserved. */
uint32_t opencfw_em9305_command_30dc20(uint32_t id,uint32_t interval,uint32_t first,uint32_t second,uint32_t third,uint32_t size,uintptr_t input)
{
 if(first>=15u||second>=15u||id>3839u||size>251u) return 18u;
 return opencfw_em9305_command_apply_309514(id,interval,first,second,third,size,input);
}
/* Native30dccc..30dd04: only flagbit6 accepted; ordered list validation. */
uint32_t opencfw_em9305_command_30dccc(uint32_t id,uint32_t flags,uint32_t count,uintptr_t input)
{
 if(id>3839u||(flags&0xffbfu)!=0u) return 18u;
 for(uint32_t i=0u;i<count;++i) if(*(volatile uint8_t *)(input+i)>=15u) return 18u;
 return opencfw_em9305_command_apply_3098ac(id,flags,count,input);
}
/* Native30db64..30dbd4: busy gate before kind/range/group constraints. */
uint32_t opencfw_em9305_command_30db64(uint32_t kind,uintptr_t input)
{
 if(opencfw_em9305_ll_stream_gate_30e510()==0u) return 12u;
 if(kind>239u) return 48u;
 uint32_t minimum=*(volatile uint16_t *)input;
 uint32_t maximum=*(volatile uint16_t *)(input+2u);
 if(maximum<minimum||minimum<6u) return 18u;
 uint32_t groups=*(volatile uint8_t *)(input+6u);
 if(groups>=16u) return 18u;
 if(groups!=0u){
  uint32_t unit=*(volatile uint8_t *)(input+7u),product;
  __asm__ volatile("mpyuw %0,%1,%2":"=r"(product):"r"(groups),"r"(unit));
  if(unit<6u||maximum<product) return 18u;
  uint32_t extra=*(volatile uint8_t *)(input+10u);
  if(extra!=0u){
   uint32_t offset=*(volatile uint8_t *)(input+8u);
   if(offset==0u||offset==255u||offset>=unit) return 18u;
   uint32_t factor=*(volatile uint8_t *)(input+9u);
   if(factor<2u) return 18u;
   __asm__ volatile("mpyuw %0,%1,%2":"=r"(product):"r"(factor),"r"(extra));
   if((int32_t)((unit-offset)*10u)<(int32_t)product) return 18u;
  }
 }
 return opencfw_em9305_command_apply_3093a0(kind,input);
}

/* Native3098ac..309910: flags store precedes count validation; failed
 * elements retain the mask accumulated so far. 3027c8 masks shift to 6 bits. */
uint32_t opencfw_em9305_command_apply_3098ac(uint32_t id,uint32_t flags,uint32_t count,uintptr_t input)
{
 uint32_t offset;
 __asm__ volatile("mpyuw %0,%1,%2":"=r"(offset):"r"(id),"r"(784u));
 uintptr_t record=*(volatile uint32_t *)(uintptr_t)(0x804084u+offset);
 *(volatile uint16_t *)(record+366u)=(uint16_t)flags;
 if(count-1u>=15u) return 18u;
 uintptr_t capacity=(uintptr_t)(0x803f78u+offset);
 if(*(volatile uint8_t *)capacity<count) return 18u;
 uint32_t high=0u,low=0u;
 *(volatile uint32_t *)(record+12u)=0u;
 *(volatile uint32_t *)(record+8u)=0u;
 for(uint32_t i=0u;i<count;++i){
  uint32_t index=*(volatile uint8_t *)input++;
  if(index>=*(volatile uint8_t *)capacity) return 18u;
  uint32_t shift=index&63u;
  if(shift<32u) low|=1u<<shift;
  else high|=1u<<(shift-32u);
  *(volatile uint32_t *)(record+12u)=high;
  *(volatile uint32_t *)(record+8u)=low;
 }
 return 0u;
}

extern uint32_t opencfw_em9305_radio_record_ready_31ac08(uint32_t);
extern uint32_t opencfw_em9305_radio_duration_312be4(uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t);
extern uint32_t opencfw_em9305_radio_callback_32d7f4(uintptr_t);
/* Native3093a0..309514: pool claim and reset are committed before later
 * busy/duration rejection. Callback32d7f4 remains a genuine provider address. */
uint32_t opencfw_em9305_command_apply_3093a0(uint32_t id,uintptr_t input)
{
 uintptr_t record=opencfw_em9305_radio_record_find_31aa64(id);
 if(record==0u) return 66u;
 if(opencfw_em9305_radio_record_ready_31ac08(id)==0u){
  uintptr_t configuration=*(volatile uint32_t *)(uintptr_t)0x805cacu;
  uint32_t count=*(volatile uint8_t *)(configuration+13u),index;
  for(index=0u;index<count;++index){
   uintptr_t row=0x80517cu+index*12u;
   if(*(volatile uint8_t *)(row+8u)!=0u) continue;
   uintptr_t control=*(volatile uint32_t *)(row+4u);
   *(volatile uint8_t *)(row+8u)=1u;
   *(volatile uint8_t *)(row+10u)=(uint8_t)index;
   *(volatile uint8_t *)(row+9u)=(uint8_t)id;
   *(volatile uint32_t *)(record+2812u)=(uint32_t)control;
   (void)opencfw_em9305_memset((void *)control,0u,144u);
   uintptr_t buffer=*(volatile uint32_t *)row;
   control=*(volatile uint32_t *)(record+2812u);
   uint32_t spare=*(volatile uint32_t *)(uintptr_t)0x805ce4u;
   *(volatile uint32_t *)(record+1160u)=(uint32_t)buffer;
   *(volatile uint32_t *)control=spare;
   break;
  }
  if(index==count) return 7u;
 }
 uintptr_t buffer=*(volatile uint32_t *)(record+1160u);
 *(volatile uint32_t *)(buffer+3844u)=32767u;
 *(volatile uint32_t *)(buffer+3848u)=0u;
 (void)opencfw_em9305_memset((void *)(buffer+3852u),255u,64u);
 if(*(volatile uint8_t *)(record+369u)!=0u) return 12u;
 uintptr_t configuration=*(volatile uint32_t *)(uintptr_t)0x805cacu;
 uint32_t maximum=*(volatile uint32_t *)(record+72u);
 uint32_t limit=*(volatile uint16_t *)(configuration+20u);
 uint32_t enabled=*(volatile uint8_t *)(record+804u);
 if(maximum>limit) limit=maximum;
 uint32_t timing=0u;
 if(enabled!=0u){
  uintptr_t callback=*(volatile uint32_t *)(uintptr_t)0x801a14u;
  if(callback!=0u) timing=((uint32_t (*)(void))callback)();
 }
 uint32_t value=*(volatile uint16_t *)(record+1144u);
 uint32_t channel=*(volatile uint8_t *)(record+63u);
 uint32_t duration=opencfw_em9305_radio_duration_312be4(channel,0u,timing,(uint16_t)limit,value,0u,2u,5u);
 uint32_t upper=*(volatile uint16_t *)(input+2u),scaled_upper;
 __asm__ volatile("mpyuw %0,%1,%2":"=r"(scaled_upper):"r"(upper),"r"(1250u));
 if(duration>scaled_upper) return 69u;
 if((*(volatile uint8_t *)(record+32u)&59u)!=0u) return 18u;
 uint32_t lower=*(volatile uint16_t *)input;
 uint32_t latency=*(volatile uint16_t *)(input+4u),scaled_lower;
 *(volatile uint32_t *)(record+712u)=scaled_upper;
 __asm__ volatile("mpyuw %0,%1,%2":"=r"(scaled_lower):"r"(lower),"r"(1250u));
 *(volatile uint8_t *)(record+718u)=1u;
 *(volatile uint16_t *)(record+716u)=(uint16_t)latency;
 *(volatile uint32_t *)(record+708u)=scaled_lower;
 uint32_t seed=opencfw_em9305_radio_access_raw_318878();
 uint32_t groups=*(volatile uint8_t *)(input+6u),unit=*(volatile uint8_t *)(input+7u);
 *(volatile uint32_t *)(record+784u)=seed;
 *(volatile uint32_t *)(record+2816u)=(uint32_t)(uintptr_t)opencfw_em9305_radio_callback_32d7f4;
 *(volatile uint8_t *)(record+2809u)=1u;
 *(volatile uint8_t *)(record+788u)=(uint8_t)groups;
 *(volatile uint8_t *)(record+789u)=(uint8_t)unit;
 uint32_t offset=*(volatile uint16_t *)(input+8u),scaled_unit;
 __asm__ volatile("mpyuw %0,%1,%2":"=r"(scaled_unit):"r"(unit),"r"(1250u));
 uintptr_t control=*(volatile uint32_t *)(record+2812u);
 *(volatile uint16_t *)(record+796u)=(uint16_t)offset;
 uint32_t extra=*(volatile uint8_t *)(input+10u);
 *(volatile uint32_t *)(record+792u)=scaled_unit;
 *(volatile uint8_t *)(record+798u)=(uint8_t)extra;
 *(volatile uint16_t *)(control+76u)=15u;
 return 0u;
}

/* Native31ac08..31ac3c: full input ID compared against byte IDs, first
 * occupied matching pool row returned, without narrowing the input ID. */
uint32_t opencfw_em9305_radio_record_ready_31ac08(uint32_t id)
{
 uintptr_t configuration=*(volatile uint32_t *)(uintptr_t)0x805cacu;
 uint32_t count=*(volatile uint8_t *)(configuration+13u);
 uintptr_t row=0x805184u;
 for(uint32_t i=0u;i<count;++i,row+=12u){
  if(*(volatile uint8_t *)(row+1u)!=id) continue;
  if(*(volatile uint8_t *)row!=0u) return (uint32_t)(row-8u);
 }
 return 0u;
}
/* Native312b88..312bb4: PHY-specific duration, original MPYWHL retained. */
uint32_t opencfw_em9305_radio_duration_piece_312b88(uint32_t phy,uint32_t mode,uint32_t size)
{
 if(phy==2u) return 36u+(size<<2);
 if(phy!=3u) return (size<<3)+64u;
 uint32_t product;
 uint32_t factor=mode==1u?2u:8u,base=27u+(size<<3);
 __asm__ volatile("mpywhl %0,%1,%2":"=r"(product):"r"(base),"r"(factor));
 return product+376u;
}
/* Native312be4..312c5c: fullword thresholds, DIVU and native word/DSP
 * multiplication retained. Only remainder/piece calls explicitly truncate. */
uint32_t opencfw_em9305_radio_duration_312be4(uint32_t phy,uint32_t requested,uint32_t timing,uint32_t spacing,uint32_t size,uint32_t extended,uint32_t mode,uint32_t overhead)
{
 uint32_t first=66u,last=66u;
 if(extended==0u){
  first=overhead;last=overhead;
  if(overhead==0u){first=10u;last=5u;}
 }
 uint32_t divisor=requested,threshold=requested;
 if(requested==0u){divisor=257u-first;threshold=257u-last;}
 uint32_t full_size=first+divisor,result;
 if(threshold>=size){
  result=opencfw_em9305_radio_duration_piece_312b88(phy,mode,(uint16_t)(last+size));
 }else{
  uint32_t quotient,product;
  __asm__ volatile("divu %0,%1,%2":"=r"(quotient):"r"(size),"r"(divisor));
  __asm__ volatile("mpyw %0,%1,%2":"=r"(product):"r"(quotient),"r"(divisor));
  uint32_t remainder=size-product;
  uint32_t has_remainder=(uint16_t)remainder;
  if(has_remainder==0u) quotient-=1u;
  uint32_t piece=opencfw_em9305_radio_duration_piece_312b88(phy,mode,full_size);
  piece+=spacing+300u;
  __asm__ volatile("mpywhul %0,%1,%2":"=r"(result):"r"(piece),"r"(quotient));
  if(has_remainder!=0u)
   result+=opencfw_em9305_radio_duration_piece_312b88(phy,mode,(uint16_t)(remainder+last));
 }
 return result+timing;
}

extern uint32_t opencfw_em9305_radio_encode_3239d4(uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_radio_encode_323c94(uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_radio_transfer_31dd88(uintptr_t,uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_radio_encode_324594(uintptr_t,uintptr_t,uintptr_t,uint32_t);
/* Authenticated stock334474..334479, five-byte event template. */
static const uint8_t opencfw_em9305_radio_event_334474[5]={5u,0u,0u,0u,34u};
/* Native32d7f4..32d910: complete control/payload branches, fresh pointer
 * reads after child calls, explicit bitshift modulo64 and ordered stores. */
uint32_t opencfw_em9305_radio_callback_32d7f4(uintptr_t record)
{
 uintptr_t control=*(volatile uint32_t *)(record+2812u);
 uintptr_t context=record+428u;
 if(*(volatile uint8_t *)(control+77u)!=0u){
  uint8_t event[5];
  (void)opencfw_em9305_memcpy(event,opencfw_em9305_radio_event_334474,5u);
  *(volatile uint16_t *)(control+76u)=15u;
  uint32_t first=opencfw_em9305_radio_encode_3239d4(record+1077u,(uintptr_t)event);
  control=*(volatile uint32_t *)(record+2812u);
  uint32_t second=opencfw_em9305_radio_encode_323c94(record+1079u,control+100u);
  control=*(volatile uint32_t *)(record+2812u);
  uintptr_t base=*(volatile uint32_t *)(uintptr_t)0x805c70u;
  uint32_t id=*(volatile uint16_t *)(control+94u),offset;
  *(volatile uint16_t *)(context+100u)=(uint16_t)(first+second);
  __asm__ volatile("mpyuw %0,%1,%2":"=r"(offset):"r"(id),"r"(912u));
  *(volatile uint8_t *)(context+260u)=1u;
  return opencfw_em9305_radio_transfer_31dd88(base+offset,control+100u,record);
 }
 uint32_t index=*(volatile uint8_t *)(record+799u)&127u;
 uintptr_t buffer=*(volatile uint32_t *)(context+732u);
 uintptr_t slot=buffer+3852u+index;
 uint32_t entry_index=*(volatile uint8_t *)slot;
 if(entry_index!=255u&&*(volatile uint8_t *)(buffer+(entry_index<<8))!=0u){
  *(volatile uint8_t *)slot=255u;
  buffer=*(volatile uint32_t *)(context+732u);
  uintptr_t entry=buffer+(entry_index<<8);
  *(volatile uint8_t *)entry=0u;
  uintptr_t destination=*(volatile uint32_t *)(context+720u);
  uint32_t bytes=*(volatile uint8_t *)(entry+1u);
  (void)opencfw_em9305_memcpy((void *)destination,(const void *)(entry+4u),bytes);
  buffer=*(volatile uint32_t *)(context+732u);
  entry=buffer+(entry_index<<8);
  uint32_t length=*(volatile uint8_t *)(entry+1u);
  uint32_t value=*(volatile uint16_t *)(entry+2u);
  *(volatile uint8_t *)(context+261u)=1u;
  *(volatile uint16_t *)(record+1144u)=(uint16_t)length;
  *(volatile uint16_t *)(context+278u)=(uint16_t)value;
  uint32_t shift=entry_index&63u,low=0u,high=0u;
  if(shift<32u) low=1u<<shift;else high=1u<<(shift-32u);
  uint32_t prior_low=*(volatile uint32_t *)(buffer+3844u);
  uint32_t prior_high=*(volatile uint32_t *)(buffer+3848u);
  *(volatile uint32_t *)(buffer+3844u)=low|prior_low;
  *(volatile uint32_t *)(buffer+3848u)=high|prior_high;
 }else *(volatile uint8_t *)(context+261u)=3u;
 uint32_t result=opencfw_em9305_radio_encode_324594(record,record+1077u,record+1144u,1u);
 *(volatile uint16_t *)(context+100u)=(uint16_t)result;
 return result;
}
