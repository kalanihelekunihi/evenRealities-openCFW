#include <stdint.h>

/* Native 0x302f4c..0x302f6e: activate the dispatch child, prepare the
 * radio record, store the two source words at 0x8015d4/0x8015d8 and bind
 * the radio source block at 0x8015cc. */
extern uint32_t opencfw_em9305_dispatch_child_30fab8(uint32_t value);
extern uint32_t opencfw_em9305_common_radio_prepare_30fb4c(uintptr_t record);
extern uint32_t opencfw_em9305_common_radio_bind_30fc10(uintptr_t source);

uint32_t opencfw_em9305_dispatch_child_302f4c(uint32_t first,uint32_t second,
                                              uintptr_t record)
{
    (void)opencfw_em9305_dispatch_child_30fab8(first);
    (void)opencfw_em9305_common_radio_prepare_30fb4c(record);
    *(volatile uint32_t *)0x8015d8u=second;
    *(volatile uint32_t *)0x8015d4u=first;
    return opencfw_em9305_common_radio_bind_30fc10(0x8015ccu);
}
