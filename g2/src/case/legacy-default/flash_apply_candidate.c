/* SPDX-License-Identifier: MIT
 * Full stock 0x0800373c control-flow source from retained P2 pseudocode.
 * Flash mode/init/read/wait/program/finalize and actual data persistence are
 * typed lower contracts; this C body contains every observed return path.
 */
#include <stdint.h>

extern uint32_t case_binary_5e_flash_mode(void); /* 0x08002f46 */
extern uint32_t case_binary_5e_flash_init(void); /* 0x08004bf4 */
extern uint32_t case_binary_5e_flash_read(void *config,uint32_t *error); /* 0x0800497c */
extern uint32_t case_binary_5e_wait(uint32_t ticks); /* 0x08004958 */
extern uint32_t case_binary_5e_flash_program(uint32_t selector,uint32_t address,
                                             uint32_t low,uint32_t high); /* 0x08004b94 */
extern uint32_t case_binary_5e_flash_finish(void); /* 0x08004b20 */
extern uint32_t case_binary_5e_failure_log(const char *format,...);

static uint32_t pack_be32(const uint8_t *bytes)
{
    return ((uint32_t)bytes[0]<<24)|((uint32_t)bytes[1]<<16)|
           ((uint32_t)bytes[2]<<8)|bytes[3];
}

/* Stock 0x0800373C (case_binary_5e_apply) */
uint32_t case_binary_5e_apply(const uint8_t *sixteen)
{
    volatile uint32_t *config=(volatile uint32_t *)(uintptr_t)0x200001a4u;
    config[0]=2u;
    uint32_t mode=case_binary_5e_flash_mode();
    config[1]=mode==1u ? 4u : 0x8000u;
    config[2]=0x7eu;
    config[3]=1u;
    case_binary_5e_flash_init();

    uint32_t error; /* read lower must populate on every failure status */
    uint32_t retries=0;
    do {
        if(case_binary_5e_flash_read((void *)(uintptr_t)0x200001a4u,&error)==0u)
            break;
        case_binary_5e_wait(10u);
        ++retries;
    } while(retries<3u);
    if(retries==3u) {
        if(*(volatile uint8_t *)(uintptr_t)0x200000bfu==0u) {
            case_binary_5e_failure_log("fail to erase. err:0x%x",error);
            case_binary_5e_failure_log("\r\n");
        }
        case_binary_5e_flash_finish();
        return 0u;
    }

    for(uint32_t block=0;block<2u;++block) {
        const uint8_t *bytes=sixteen+8u*block;
        uint32_t high=pack_be32(bytes);
        uint32_t low=pack_be32(bytes+4u);
        if(case_binary_5e_flash_program(1u,0x0803f000u+8u*block,low,high)!=0u) {
            if(*(volatile uint8_t *)(uintptr_t)0x200000bfu==0u) {
                case_binary_5e_failure_log("fail to program.");
                case_binary_5e_failure_log("\r\n");
            }
            case_binary_5e_flash_finish();
            return 0u;
        }
    }
    case_binary_5e_flash_finish();
    return 1u;
}
