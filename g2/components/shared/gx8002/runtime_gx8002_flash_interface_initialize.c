/* SPDX-License-Identifier: MIT */
/* Candidate reconstructed from image A at 0x1002443c.
 * Service calls and installed callbacks now have separate C reconstructions.
 * State/interface ownership and complete startup composition remain pending. */
#include <stdint.h>
#include <stddef.h>

extern int open_cfw_gx8002_platform_config(unsigned int, const volatile void *);
extern void open_cfw_gx8002_platform_gate(unsigned int, unsigned int);
extern int open_cfw_gx8002_spi_wait_idle(void);
extern int open_cfw_gx8002_flash_wait_ready(void);
extern int open_cfw_gx8002_flash_discover(void);
extern int open_cfw_gx8002_flash_quad_enable(void);
extern int open_cfw_gx8002_flash_quad_enable_pair(void);
extern int open_cfw_gx8002_flash_device_config(void);
extern int open_cfw_gx8002_flash_xip_config(unsigned int, unsigned int,
    unsigned int, unsigned int, unsigned int, unsigned int, unsigned int,
    unsigned int, unsigned int);
extern int open_cfw_gx8002_flash_word_program(unsigned, const uint32_t *, unsigned);
extern int open_cfw_gx8002_flash_word_read(unsigned, uint32_t *, unsigned);
#include "runtime_gx8002_flash_interface_table.h"

struct flash_device_prefix { uint32_t unknown; int32_t jedec; };
#include "runtime_gx8002_flash_state.h"

extern void open_cfw_gx8002_flash_protection_initialize(void);
extern unsigned open_cfw_gx8002_flash_read_status(void);
extern int open_cfw_gx8002_flash_write_enable(void);
extern int open_cfw_gx8002_flash_command_write(unsigned,const uint8_t *,unsigned);
extern int open_cfw_gx8002_flash_interrupt(int,void *);
extern void open_cfw_gx8002_request_irq(int,int (*)(int,void *),void *);
void *open_cfw_gx8002_flash_interface_initialize(void)
{
    uint32_t configuration = 0;
    open_cfw_gx8002_platform_config(9, &configuration);
    open_cfw_gx8002_platform_gate(13, 1);
    open_cfw_gx8002_spi_wait_idle();
    *(volatile uint32_t *)0xa2000008u = 0;
    *(volatile uint32_t *)0xa0300090u = 1;
    *(volatile uint32_t *)0xa200002cu = 78;
    *(volatile uint32_t *)0xa20000f0u = 1;
    *(volatile uint32_t *)0xa2000014u = 4;
    *(volatile uint32_t *)0xa200001cu = 31;
    *(volatile uint32_t *)0xa2000008u = 1;
    open_cfw_gx8002_request_irq(15,open_cfw_gx8002_flash_interrupt,NULL);
    open_cfw_gx8002_flash_wait_ready();
    if (open_cfw_gx8002_flash_discover() != 0)
        return NULL;

    open_cfw_gx8002_flash_protection_initialize();
    *(volatile uint32_t *)0xa2000008u = 0;
    *(volatile uint32_t *)0xa2000014u = 2;
    int32_t id=((volatile struct flash_device_prefix *)open_cfw_gx8002_flash_state.selected_device)->jedec;
    switch (id) {
    case 0x0b4014: case 0x0b4016: case 0x0b4017:
    case 0x854012: case 0x856013: case 0x856014:
    case 0xb36014: case 0xba6015: case 0xc84015: case 0xc84215:
    case 0xc86015: case 0xc86016: case 0xcd7015: case 0xef4015:
        open_cfw_gx8002_flash_quad_enable_pair(); break;
    case 0x1c3812: case 0x1c3813: case 0x1c7017: break;
    case 0x684015:
        open_cfw_gx8002_flash_quad_enable();
        open_cfw_gx8002_flash_quad_enable_pair(); break;
    case 0xc22017: {
        unsigned status=open_cfw_gx8002_flash_read_status();
        if (!(status&64u)) {
            uint8_t command=(uint8_t)(status|64u);
            open_cfw_gx8002_flash_wait_ready();
            open_cfw_gx8002_flash_write_enable();
            open_cfw_gx8002_flash_command_write(1,&command,1);
            open_cfw_gx8002_flash_wait_ready();
        }
        break;
    }
    default:open_cfw_gx8002_flash_quad_enable();break;
    }
    if (id==0x204016) open_cfw_gx8002_flash_device_config();
    open_cfw_gx8002_flash_state.program_words =
        open_cfw_gx8002_flash_word_program;
    open_cfw_gx8002_flash_state.read_words =
        open_cfw_gx8002_flash_word_read;
    open_cfw_gx8002_flash_xip_config(235,8,1,24,4,0,1,4,4);
    return &open_cfw_gx8002_flash_interface;
}
