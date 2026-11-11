#include <stdint.h>

/* Native 0x322580..0x3225ae: reset the 148-byte block at +384 of the
 * record's context (+780), link it back to the record, point +428 at the
 * entry at +432 and seed that entry's kind (15) and the active byte at
 * +410. Returns the entry address. */
extern void *opencfw_em9305_memset(void *destination, uint32_t value, uint32_t bytes);

uintptr_t opencfw_em9305_callback_322580(uintptr_t record)
{
    uintptr_t context=*(volatile uint32_t *)(record+780u);
    (void)opencfw_em9305_memset((void *)(context+384u),0u,148u);
    uintptr_t entry=context+432u;
    *(volatile uint32_t *)(context+420u)=(uint32_t)record;
    *(volatile uint32_t *)(context+428u)=(uint32_t)entry;
    *(volatile uint8_t *)entry=15u;
    *(volatile uint8_t *)(context+410u)=1u;
    return entry;
}
