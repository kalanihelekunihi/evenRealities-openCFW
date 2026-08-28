#include <stdint.h>

uint32_t open_cfw_hwsh_host_registers[4][0x40 / 4];
uint32_t open_cfw_hwsh_host_delay_count, open_cfw_hwsh_host_delay_ticks;
uint32_t open_cfw_hwsh_host_clear_count, open_cfw_hwsh_host_shutdown_count, open_cfw_hwsh_host_release_count;
uint32_t open_cfw_hwsh_host_order, open_cfw_hwsh_host_clear_order, open_cfw_hwsh_host_shutdown_order, open_cfw_hwsh_host_release_order;
uint32_t open_cfw_hwsh_host_clear_register, open_cfw_hwsh_host_shutdown_register, open_cfw_hwsh_host_release_register;

struct open_cfw_hwsh_instance;
void open_cfw_hwsh_host_delay(uint32_t ticks) { open_cfw_hwsh_host_delay_count++; open_cfw_hwsh_host_delay_ticks = ticks; }
void open_cfw_hwsh_host_register_clear(struct open_cfw_hwsh_instance *instance) { (void)instance; open_cfw_hwsh_host_clear_count++; open_cfw_hwsh_host_clear_order = ++open_cfw_hwsh_host_order; open_cfw_hwsh_host_clear_register = open_cfw_hwsh_host_registers[0][0x30 / 4]; }
void open_cfw_hwsh_host_shutdown(struct open_cfw_hwsh_instance *instance) { (void)instance; open_cfw_hwsh_host_shutdown_count++; open_cfw_hwsh_host_shutdown_order = ++open_cfw_hwsh_host_order; open_cfw_hwsh_host_shutdown_register = open_cfw_hwsh_host_registers[0][0x30 / 4]; }
void open_cfw_hwsh_host_release(struct open_cfw_hwsh_instance *instance) { (void)instance; open_cfw_hwsh_host_release_count++; open_cfw_hwsh_host_release_order = ++open_cfw_hwsh_host_order; open_cfw_hwsh_host_release_register = open_cfw_hwsh_host_registers[0][0x30 / 4]; }

#include "../../components/bootloader/core_overlay/runtime_hw_shutdown_422fde.c"
