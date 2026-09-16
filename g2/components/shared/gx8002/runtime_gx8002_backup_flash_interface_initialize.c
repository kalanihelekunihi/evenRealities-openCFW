/* SPDX-License-Identifier: MIT */
/* Recovered backup initializer at package 0x406b8.
 * Unlike primary, status polling is inline and no XIP setup is performed. */
#include <stdint.h>
#include <stddef.h>

extern int open_cfw_gx8002_platform_config(unsigned int, const volatile void *);
extern void open_cfw_gx8002_platform_gate(unsigned int, unsigned int);
extern int open_cfw_gx8002_flash_discover(void);
extern int open_cfw_gx8002_flash_quad_enable(void);
extern int open_cfw_gx8002_flash_quad_enable_pair(void);
extern int open_cfw_gx8002_flash_device_config(void);
extern int open_cfw_gx8002_flash_word_program(unsigned, const uint32_t *, unsigned);
extern int open_cfw_gx8002_flash_word_read(unsigned, uint32_t *, unsigned);
#include "runtime_gx8002_flash_interface_table.h"

struct flash_device_prefix { uint32_t unknown; int32_t jedec; };
#include "runtime_gx8002_flash_state.h"

extern void open_cfw_gx8002_flash_protection_initialize(void);
extern int open_cfw_gx8002_flash_interrupt(int,void *);
extern void open_cfw_gx8002_request_irq(int,int (*)(int,void *),void *);
extern int backup_flash_command_read(unsigned, uint8_t *, unsigned);
extern int backup_flash_status_write(const uint8_t *, unsigned, unsigned);
static inline __attribute__((always_inline)) void wait_ready(void)
{
    uint8_t status;
    do { backup_flash_command_read(5, &status, 1); } while (status & 1u);
}
void *open_cfw_gx8002_flash_interface_initialize(void)
{
    uint32_t configuration = 0;
    open_cfw_gx8002_platform_config(9, &configuration);
    open_cfw_gx8002_platform_gate(13, 1);
    while (*(volatile uint32_t *)0xa2000028u & 1u) {}
    *(volatile uint32_t *)0xa2000008u = 0;
    *(volatile uint32_t *)0xa0300090u = 1;
    *(volatile uint32_t *)0xa200002cu = 78;
    *(volatile uint32_t *)0xa20000f0u = 1;
    *(volatile uint32_t *)0xa2000014u = 4;
    *(volatile uint32_t *)0xa200001cu = 31;
    *(volatile uint32_t *)0xa2000008u = 1;
    open_cfw_gx8002_request_irq(15,open_cfw_gx8002_flash_interrupt,NULL);
    wait_ready();
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
        uint8_t status;
        backup_flash_command_read(5, &status, 1);
        if (!(status&64u)) {
            uint8_t command=(uint8_t)(status|64u);
            backup_flash_status_write(&command,1,1);
            wait_ready();
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
    return &open_cfw_gx8002_flash_interface;
}
