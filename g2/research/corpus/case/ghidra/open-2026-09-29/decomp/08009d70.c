
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void g2_timer_callback_1(void)

{
  int iVar1;
  int iVar2;
  
  iVar2 = _DAT_08009db8;
  iVar1 = DAT_08009db4;
  if ((*(char *)(DAT_08009db4 + 2) == '\x04') || (*(char *)(DAT_08009db4 + 2) == '\x03')) {
    if (*(char *)(_DAT_08009db8 + 7) != '\0') {
      return;
    }
    g2_log_printf(s_dont_clear_led__since_led_status_08009dcc);
  }
  else {
    case_gpio_pa6_write(0);
    case_gpio_pa7_write(0);
    *(undefined1 *)(iVar1 + 2) = 0;
    if (*(char *)(iVar2 + 7) != '\0') {
      return;
    }
    g2_log_printf(s_clear_led_08009dbb + 1);
  }
  g2_log_printf(&DAT_08009dc8);
  return;
}

