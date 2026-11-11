/* SPDX-License-Identifier: MIT
 * UART stage-2 exception entry from the locked image at 0x10002950.
 * The frame layout and g_trap_sp address match the public GX8002 grus
 * vectors.S and the stock disassembly. This has to be a naked C function:
 * the stack and r13 are changed before a C prologue can execute.
 *
 * Stock trap_c prints the saved register frame before stopping. Use the
 * source-owned UART console sink to emit the same fields and formats.
 */
#include <stdint.h>

extern void gx8002_uart_stage2_console_putc_2a84(uint32_t character);

static void emit(char c)
{
    gx8002_uart_stage2_console_putc_2a84((uint8_t)c);
}

static void emit_text(const char *text)
{
    while (*text != '\0') emit(*text++);
}

static void emit_decimal(uint32_t value)
{
    char digits[10];
    uint32_t count = 0;
    do {
        digits[count++] = (char)('0' + value % 10u);
        value /= 10u;
    } while (value != 0u);
    while (count != 0u) emit(digits[--count]);
}

static void emit_hex(uint32_t value, int zero_pad)
{
    static const char alphabet[] = "0123456789abcdef";
    int started = zero_pad;
    for (int shift = 28; shift >= 0; shift -= 4) {
        uint32_t nibble = (value >> (uint32_t)shift) & 15u;
        if (nibble != 0u || shift == 0) started = 1;
        emit(started ? alphabet[nibble] : ' ');
    }
}

static void emit_registers(const uint32_t *frame, uint32_t first,
                           uint32_t count, uint32_t label_base,
                           const char *prefix)
{
    for (uint32_t i = 0; i < count; ++i) {
        emit_text(prefix);
        emit_decimal(label_base + i);
        emit_text(": ");
        emit_hex(frame[first + i], 1);
        emit('\t');
        if (((first + i) % 5u) == 4u) emit('\n');
    }
    emit('\n');
}

__attribute__((noreturn)) void gx8002_uart_stage2_trap_report(uint32_t *frame)
{
    uint32_t psr;
    __asm__ volatile("mfcr %0, cr<0, 0>" : "=r"(psr));
    emit_text("CPU Exception : ");
    emit_decimal((uint32_t)(int32_t)(int8_t)(psr >> 16));
    emit('\n');
    emit_registers(frame, 0u, 16u, 0u, "vr");
    emit_registers(frame, 16u, 16u, 0u, "r");
    emit_registers(frame, 32u, 16u, 16u, "r");
    emit_text("epsr: ");
    emit_hex(frame[48], 0);
    emit('\n');
    emit_text("epc : ");
    emit_hex(frame[49], 0);
    emit('\n');
    for (;;) { }
}

__attribute__((naked, noreturn,
               section(".text.gx8002_uart_stage2_trap_entry_2950")))
void gx8002_uart_stage2_trap_entry_2950(void)
{
    __asm__ volatile(
        "psrset ee\n"
        "subi r14, r14, 4\n"
        "st.w r13, (r14, 0)\n"
        "addi r14, r14, 4\n"
        "lrw r13, 0x2000983c\n"
        "st.w r14, (r13, 0)\n"
        "lrw r14, 0x2000983c\n"
        "subi r14, r14, 72\n"
        "stm r0-r12, (r14)\n"
        "lrw r0, 0x2000983c\n"
        "ld.w r0, (r0, 0)\n"
        "st.w r0, (r14, 0x38)\n"
        "subi r0, r0, 4\n"
        "ld.w r13, (r0, 0)\n"
        "st.w r13, (r14, 0x34)\n"
        "st.w r15, (r14, 0x3c)\n"
        "mfcr r0, cr<2, 0>\n"
        "st.w r0, (r14, 0x40)\n"
        "mfcr r0, cr<4, 0>\n"
        "st.w r0, (r14, 0x44)\n"
        "mov r0, r14\n"
        "bsr gx8002_uart_stage2_trap_report\n"
        ".global gx8002_uart_stage2_exception_bridge_2994\n"
        ".type gx8002_uart_stage2_exception_bridge_2994, @function\n"
        "gx8002_uart_stage2_exception_bridge_2994:\n"
        "br gx8002_uart_stage2_trap_entry_2950\n");
}
