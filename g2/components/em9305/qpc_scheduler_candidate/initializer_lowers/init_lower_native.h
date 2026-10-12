#ifndef OPENCFW_EM9305_INIT_LOWER_NATIVE_H
#define OPENCFW_EM9305_INIT_LOWER_NATIVE_H
#include <stdint.h>
#include <stddef.h>

/* Fixed RAM addresses below are authenticated stock data-slot addresses.
 * Function identities are linker relocations, never numeric code pointers. */
static inline uint32_t init_read32(uintptr_t address)
{ return *(volatile uint32_t *)address; }
static inline uint8_t init_read8(uintptr_t address)
{ return *(volatile uint8_t *)address; }
static inline void init_write32(uintptr_t address, uint32_t value)
{ *(volatile uint32_t *)address = value; }
static inline void init_write16(uintptr_t address, uint16_t value)
{ *(volatile uint16_t *)address = value; }
static inline uint32_t init_code_address(void (*function)(void))
{ return (uint32_t)(uintptr_t)function; }

/* True, separately source-owned firmware children. */
extern uint32_t opencfw_em9305_init_child_317498(void);
extern void opencfw_em9305_init_child_3078a0(void);
extern uint32_t opencfw_em9305_init_child_307980(void);
extern uint32_t opencfw_em9305_init_child_307a68(void);

/* Relocatable native callback identities; the linker must resolve bodies. */
extern void opencfw_em9305_callback_32483c(void);
extern uint32_t opencfw_em9305_callback_31e7fc(void);
extern void opencfw_em9305_callback_318c1c(void);
extern void opencfw_em9305_callback_318f2c(void);
extern void opencfw_em9305_callback_3189f4(void);
extern void opencfw_em9305_callback_31df8c(void);
extern uint32_t opencfw_em9305_callback_31e604(uint32_t incoming);
extern uint32_t opencfw_em9305_mode_event_31bd78(uintptr_t,uint32_t);
extern void opencfw_em9305_callback_320f78(void);
extern void opencfw_em9305_callback_322754(void);
extern void opencfw_em9305_callback_325984(void);
extern void opencfw_em9305_callback_317f5c(void);
extern void opencfw_em9305_callback_317ca8(void);
extern void opencfw_em9305_callback_31ce50(void);
extern uint32_t opencfw_em9305_callback_31d438(void);
extern uint32_t opencfw_em9305_callback_31f9b0(uint32_t context,uint32_t event);
extern uint32_t opencfw_em9305_callback_30fc24(uint32_t value, uint32_t mode);
extern void opencfw_em9305_callback_319890(void);
extern void opencfw_em9305_callback_31fa44(void);
extern uint32_t opencfw_em9305_callback_30fc20(uint32_t value, uint32_t mode);
extern void opencfw_em9305_callback_31ff68(void);
extern uint32_t opencfw_em9305_callback_320084(void);
extern uint32_t opencfw_em9305_callback_307a18(uint32_t index);
extern void opencfw_em9305_callback_320434(void);
extern uint32_t opencfw_em9305_callback_32056c(uint32_t incoming);
extern void opencfw_em9305_callback_322a30(void);
extern uint32_t opencfw_em9305_callback_307b60(uint32_t index);

#endif
