#include <stdint.h>

extern uint32_t opencfw_em9305_ll_record_error_322f08(uint32_t,uint32_t);
extern uint32_t opencfw_em9305_dispatch_child_322e80(uintptr_t,uint32_t);
extern void opencfw_em9305_radio_record_release_31ac84(uintptr_t);
extern uint32_t opencfw_em9305_command_count_down_30e48c(void);
extern uint32_t opencfw_em9305_common_release_304588(uint32_t);
extern uint32_t opencfw_em9305_dispatch_child_323574(uint32_t,uint32_t);

/* Native 0x31cb20..0x31cb40: connection failed to establish: report error
 * 0 for the record's id (+2), post status 0x44, release the record and
 * count down the command credit. */
uint32_t opencfw_em9305_dispatch_callback_31cb20(uintptr_t record)
{
    (void)opencfw_em9305_ll_record_error_322f08(0u,*(volatile uint8_t *)(record+2u));
    (void)opencfw_em9305_dispatch_child_322e80(record,0x44u);
    opencfw_em9305_radio_record_release_31ac84(record);
    return opencfw_em9305_command_count_down_30e48c();
}

/* Native 0x31cb40..0x31cb82: connection closed: release the common
 * resource (mode 1), clear the linked object's active byte (+196 -> +410),
 * report the end for a role-3 record (+1) (with the stored reason +200
 * through 323574, else error 0), release the record and count down the
 * command credit. */
uint32_t opencfw_em9305_dispatch_callback_31cb40(uintptr_t record)
{
    (void)opencfw_em9305_common_release_304588(1u);
    uintptr_t linked=*(volatile uint32_t *)(record+196u);
    if(linked!=0u) *(volatile uint8_t *)(linked+410u)=0u;
    if(*(volatile uint8_t *)(record+1u)==3u) {
        uint32_t reason=*(volatile uint8_t *)(record+200u);
        uint32_t id=*(volatile uint8_t *)(record+2u);
        if(reason!=0u)
            (void)opencfw_em9305_dispatch_child_323574(id,reason);
        else
            (void)opencfw_em9305_ll_record_error_322f08(0u,id);
    }
    opencfw_em9305_radio_record_release_31ac84(record);
    return opencfw_em9305_command_count_down_30e48c();
}
