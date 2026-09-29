
void g2_timer_callback_2(void)

{
  if ((*(char *)(DAT_0800bb6c + 2) == '\x04') || (*(char *)(DAT_0800bb6c + 2) == '\x03')) {
    *(byte *)(DAT_0800bb70 + 0xc) = *(byte *)(DAT_0800bb70 + 0xc) ^ 1;
    case_gpio_pa6_write();
  }
  return;
}

