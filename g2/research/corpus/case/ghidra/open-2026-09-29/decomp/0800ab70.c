
void g2_timer_callback_6(void)

{
  char *pcVar1;
  
  pcVar1 = DAT_0800aba4;
  if ((((DAT_0800aba4[0x10] == '\0') && (DAT_0800aba4[0x11] == '\0')) && (DAT_0800aba4[2] == '\0'))
     && (*DAT_0800aba4 != '\x03')) {
    glasses_charge_side_select(0);
    pcVar1[2] = '\x01';
    osTimerStart(*(undefined4 *)(DAT_0800abac + 0x10),DAT_0800aba8);
  }
  return;
}

