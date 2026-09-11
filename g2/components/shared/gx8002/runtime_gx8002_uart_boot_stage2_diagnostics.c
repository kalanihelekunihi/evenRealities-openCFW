/* SPDX-License-Identifier: MIT */
/* Diagnostic printf format strings from the volatile UART-boot stage-2 IRAM
 * image (package [0x00007204,0x00009204)). These are the literal argument
 * text of NationalChip/lvp_kws printf call sites at pinned commit
 * 8bf9ee5cb6eeb226011e61c15fa4981b83b93bd5:
 *   - arch/soc/grus/trap_c.c (crash-dump register printer, four strings)
 *   - boards/nationalchip/grus_bk32887_1v/misc_board.c (padmux board-init error, one string)
 * Only the literal bytes are claimed; the surrounding trap-handler and
 * board-init control flow are not reconstructed here. See
 * docs/research/gx8002-uart-boot-stage2-diagnostics-source.md.
 */
const char open_cfw_gx8002_uart_boot_stage2_str_cpu_exception[] __attribute__((aligned(1))) = "CPU Exception : %u";
const char open_cfw_gx8002_uart_boot_stage2_str_vreg_dump[] __attribute__((aligned(1))) = "vr%d: %08x\t";
const char open_cfw_gx8002_uart_boot_stage2_str_reg_dump[] __attribute__((aligned(1))) = "r%d: %08x\t";
const char open_cfw_gx8002_uart_boot_stage2_str_epsr[] __attribute__((aligned(1))) = "epsr: %8x\n";
const char open_cfw_gx8002_uart_boot_stage2_str_epc[] __attribute__((aligned(1))) = "epc : %8x\n";
const char open_cfw_gx8002_uart_boot_stage2_str_pin_set_error[] __attribute__((aligned(1))) = "pin %d set error!\n";
