/* Experimental direct bindings to native BL destinations in resident IROM
 * 0x100000..0x10ffff (EM9305 datasheet memory map). These do not supply ROM
 * source bodies or establish producing SDK ABI equality. Public facades
 * explicitly preserve observed argument registers through ordinary ARC C.
 * No ROM executable bytes are embedded. */
#include <stdint.h>
uint32_t opencfw_em9305_sleep_metadata_rom(uint32_t a,uintptr_t b,uintptr_t c)
{ return ((uint32_t (*)(uint32_t,uintptr_t,uintptr_t))(uintptr_t)0x103b0cu)(a,b,c); }
uint32_t opencfw_em9305_sleep_mode_query(uint32_t a,uint32_t b)
{ return ((uint32_t (*)(uint32_t,uint32_t))(uintptr_t)0x101e34u)(a,b); }
uint32_t opencfw_em9305_sleep_rom_action(uint32_t a)
{ return ((uint32_t (*)(uint32_t))(uintptr_t)0x101d50u)(a); }
uint32_t opencfw_em9305_sleep_rom_configure(uint32_t a)
{ return ((uint32_t (*)(uint32_t))(uintptr_t)0x103b54u)(a); }
uint32_t opencfw_em9305_sleep_rom_enter(uint32_t a)
{ return ((uint32_t (*)(uint32_t))(uintptr_t)0x103724u)(a); }
uint32_t opencfw_em9305_sleep_rom_prepare(uint32_t a)
{ return ((uint32_t (*)(uint32_t))(uintptr_t)0x103ab4u)(a); }
void opencfw_em9305_sleep_rom_restore(uint32_t a)
{ ((void (*)(uint32_t))(uintptr_t)0x103b7cu)(a); }
uint32_t opencfw_em9305_sleep_rom_start(uint32_t a)
{ return ((uint32_t (*)(uint32_t))(uintptr_t)0x103b20u)(a); }

/* Native controller-init BL destination, resident IROM. */
uint32_t opencfw_em9305_controller_rom_init(uint32_t a)
{ return ((uint32_t (*)(uint32_t))(uintptr_t)0x103c40u)(a); }
/* Native timer calibration ROM contracts. */
uint32_t opencfw_em9305_timer_rom_set_a(uint32_t a)
{ return ((uint32_t (*)(uint32_t))(uintptr_t)0x104cc4u)(a); }
uint32_t opencfw_em9305_timer_rom_set_b(uint32_t a)
{ return ((uint32_t (*)(uint32_t))(uintptr_t)0x104d04u)(a); }
uint32_t opencfw_em9305_timer_rom_probe_a(uint32_t a)
{ return ((uint32_t (*)(uint32_t))(uintptr_t)0x104ca4u)(a); }
uint32_t opencfw_em9305_timer_rom_probe_b(uint32_t a)
{ return ((uint32_t (*)(uint32_t))(uintptr_t)0x104cb4u)(a); }
uint32_t opencfw_em9305_controller_rom_mode_action(uint32_t a)
{ return ((uint32_t (*)(uint32_t))(uintptr_t)0x103cf0u)(a); }
uint32_t opencfw_em9305_controller_rom_level_prepare(uint32_t a)
{ return ((uint32_t (*)(uint32_t))(uintptr_t)0x103b9cu)(a); }
uint32_t opencfw_em9305_controller_rom_level_set(uint32_t a)
{ return ((uint32_t (*)(uint32_t))(uintptr_t)0x103bdcu)(a); }
uint32_t opencfw_em9305_controller_rom_level_finish(uint32_t a)
{ return ((uint32_t (*)(uint32_t))(uintptr_t)0x103bbcu)(a); }
uint32_t opencfw_em9305_controller_rom_second_value(uint32_t a)
{ return ((uint32_t (*)(uint32_t))(uintptr_t)0x104d24u)(a); }
uint32_t opencfw_em9305_controller_rom_boot_status(uint32_t a)
{ return ((uint32_t (*)(uint32_t))(uintptr_t)0x103678u)(a); }
uint32_t opencfw_em9305_controller_rom_boot_ready(uint32_t a)
{ return ((uint32_t (*)(uint32_t))(uintptr_t)0x10361cu)(a); }
uint32_t opencfw_em9305_controller_rom_construct(uint32_t a,uint32_t b,uint32_t c,uint32_t d,uint32_t e)
{ return ((uint32_t (*)(uint32_t,uint32_t,uint32_t,uint32_t,uint32_t))(uintptr_t)0x10aa8cu)(a,b,c,d,e); }
uint32_t opencfw_em9305_controller_rom_delay(uint32_t a)
{ return ((uint32_t (*)(uint32_t))(uintptr_t)0x100c10u)(a); }
uint32_t opencfw_em9305_controller_rom_register_irq(uint32_t a,uint32_t b,uint32_t c,uint32_t d)
{ return ((uint32_t (*)(uint32_t,uint32_t,uint32_t,uint32_t))(uintptr_t)0x1035dcu)(a,b,c,d); }
uint32_t opencfw_em9305_controller_rom_allocator(uint32_t a)
{ return ((uint32_t (*)(uint32_t))(uintptr_t)0x10305cu)(a); }
uint32_t opencfw_em9305_controller_rom_alloc_query(uint32_t a)
{ return ((uint32_t (*)(uint32_t))(uintptr_t)0x103084u)(a); }
uintptr_t opencfw_em9305_controller_rom_address(uintptr_t a)
{ return ((uintptr_t (*)(uintptr_t))(uintptr_t)0x1031a4u)(a); }
uint32_t opencfw_em9305_pal_rom_baseband_init(uintptr_t a,uintptr_t b)
{ return ((uint32_t (*)(uintptr_t,uintptr_t))(uintptr_t)0x10a84cu)(a,b); }
