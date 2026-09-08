/* SPDX-License-Identifier: MIT */
/* Reconstructed from image A at 0x100245f0, not copied SDK implementation.
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

void *open_cfw_gx8002_flash_initialize(void)
{
    /* Operation9 only reads this value; constant storage avoids a stack word. */
    static const uint32_t configuration = 0;
    open_cfw_gx8002_platform_config(9, &configuration);
    open_cfw_gx8002_platform_gate(13, 1);
    open_cfw_gx8002_spi_wait_idle();
    *(volatile uint32_t *)0xa0300090u = 1;
    *(volatile uint32_t *)0xa2000008u = 0;
    *(volatile uint32_t *)0xa200002cu = 78;
    *(volatile uint32_t *)0xa20000f0u = 1;
    *(volatile uint32_t *)0xa2000014u = 2;
    *(volatile uint32_t *)0xa200001cu = 31;
    *(volatile uint32_t *)0xa2000008u = 1;
    open_cfw_gx8002_flash_wait_ready();
    if (open_cfw_gx8002_flash_discover() != 0)
        return NULL;

    int32_t id = ((volatile struct flash_device_prefix *)open_cfw_gx8002_flash_state.selected_device)->jedec;
    if (id == 0x854012 || id == 0x856013)
        open_cfw_gx8002_flash_quad_enable_pair();
    else if (id != 0x1c3812 && id != 0x1c3813)
        open_cfw_gx8002_flash_quad_enable();
    /* The first configuration call can alter state: reload both pointers/ID. */
    if (((volatile struct flash_device_prefix *)open_cfw_gx8002_flash_state.selected_device)->jedec == 0x204016)
        open_cfw_gx8002_flash_device_config();
    open_cfw_gx8002_flash_state.program_words =
        open_cfw_gx8002_flash_word_program;
    open_cfw_gx8002_flash_state.read_words =
        open_cfw_gx8002_flash_word_read;
    open_cfw_gx8002_flash_xip_config(235,8,1,24,4,0,1,4,4);
    return &open_cfw_gx8002_flash_interface;
}
