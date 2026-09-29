
void periodic_timer_restart(void)

{
  int iVar1;
  
  iVar1 = DAT_0800bb8c;
  osTimerStop(*(undefined4 *)(DAT_0800bb8c + 0x14));
  osTimerStart(*(undefined4 *)(iVar1 + 0x14),1000);
  return;
}

