/* Native CASE 0x08002c30, three-attempt PMIC stop/start request. */
#include <stdint.h>
extern uint32_t case_legacy_pmic_set(uint32_t selector,uint32_t value); /* 0x39e4 */
extern uint32_t case_legacy_ee_first(uint32_t selector,uint32_t *response,uint32_t count); /* 0x35d4 */

uint32_t case_legacy_ee_power_stop(uint32_t mode) {
    uint32_t expected=mode!=0u ? 9u : 8u;
    uint32_t request=mode!=0u ? 8u : 9u;
    uint32_t response=request;
    for(uint32_t attempt=0;attempt<3u;attempt++) {
        (void)case_legacy_pmic_set(21u,expected);
        (void)case_legacy_ee_first(21u,&response,1u);
        if((uint8_t)response==expected)break;
    }
    return (uint8_t)response;
}
