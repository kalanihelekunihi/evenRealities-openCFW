#include "init_lower_native.h"

extern uint32_t opencfw_em9305_common_init_303d18(uint32_t incoming);
extern uint32_t opencfw_em9305_common_init_302ec8(void);

/* Native 0x3104cc..0x3104d6. Both 0x30fc20 and 0x30fc24 tail-branch here.
 * The full-word store is in the return delay slot, after the mode byte. */
static uint32_t register_radio_mode(uint32_t value, uint32_t mode)
{
    *(volatile uint8_t *)0x805ebcu = (uint8_t)mode;
    init_write32(0x805eb8u, value);
    return value;
}
uint32_t opencfw_em9305_callback_30fc20(uint32_t value, uint32_t mode)
{ return register_radio_mode(value, mode); }
uint32_t opencfw_em9305_callback_30fc24(uint32_t value, uint32_t mode)
{ return register_radio_mode(value, mode); }

/* These native entries are direct tail branches to source children. */
uint32_t opencfw_em9305_callback_31d438(void)
{ return opencfw_em9305_init_child_317498(); }
uint32_t opencfw_em9305_callback_320084(void)
{ return opencfw_em9305_init_child_307980(); }

/* Native 0x32056c..0x32057c. Existing selected source already owns the
 * first two children; their return values are ignored by the following call. */
uint32_t opencfw_em9305_callback_32056c(uint32_t incoming)
{
    (void)opencfw_em9305_common_init_303d18(incoming);
    (void)opencfw_em9305_common_init_302ec8();
    return opencfw_em9305_init_child_307a68();
}
