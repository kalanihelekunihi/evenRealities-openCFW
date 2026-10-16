/* Glyph descriptor calls the already source-owned NOR flash guards at 0x46f65e/0x46f674. */
extern void g2_norflash_lock_46f65e(void);
extern void g2_norflash_unlock_46f674(void);

void audio_uart_font_resource_enter_46f65e(void) {
    g2_norflash_lock_46f65e();
}

void audio_uart_font_resource_leave_46f674(void) {
    g2_norflash_unlock_46f674();
}
