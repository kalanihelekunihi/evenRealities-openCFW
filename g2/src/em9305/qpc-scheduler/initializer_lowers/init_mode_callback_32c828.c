#include <stdint.h>

/* Full native callback 0x32c828..0x32c868. EXTH retains low 16 bits
 * of the unsigned subtraction before unsigned BRHS 0x7fff. */
extern uint32_t opencfw_em9305_receive_terminate_325c08(uintptr_t,
                                                           uint32_t);
uint32_t opencfw_em9305_mode_callback_32c828(uintptr_t context,
                                               uintptr_t callback_identity)
{
    (void)callback_identity;
    uint16_t anchor=*(volatile uint16_t *)(context+262u);
    uint32_t third=*(volatile uint32_t *)(uintptr_t)0x802824u;
    uint32_t first=*(volatile uint32_t *)(uintptr_t)0x80281cu;
    uint32_t second=*(volatile uint32_t *)(uintptr_t)0x802820u;
    uint16_t delta=(uint16_t)(third-(uint32_t)anchor);
    *(volatile uint32_t *)(context+708u)=first;
    *(volatile uint32_t *)(context+712u)=second;
    *(volatile uint32_t *)(context+716u)=third;
    if (delta>=0x7fffu)
        return opencfw_em9305_receive_terminate_325c08(context,73u);
    uint32_t second_check=*(volatile uint32_t *)(context+712u);
    uint32_t first_check=*(volatile uint32_t *)(context+708u);
    if ((first_check|second_check)==0u)
        return opencfw_em9305_receive_terminate_325c08(context,73u);
    return (uint32_t)context;
}
