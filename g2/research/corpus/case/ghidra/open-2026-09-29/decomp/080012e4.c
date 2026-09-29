
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void aging_led_status_clear(void)

{
  int iVar1;
  
  iVar1 = DAT_08001314;
  osTimerStop(*(undefined4 *)(DAT_08001314 + 0x18));
  case_gpio_pa6_write(0);
  case_gpio_pa7_write(0);
  *(undefined1 *)(_DAT_08001318 + 2) = 0;
  if (*(char *)(iVar1 + 7) == '\0') {
    g2_log_printf(s_clear_led_status__0800131b + 1);
    g2_log_printf(&DAT_08001330);
  }
  return;
}

