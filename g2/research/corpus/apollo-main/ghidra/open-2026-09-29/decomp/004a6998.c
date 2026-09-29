
undefined4 hub_timer_stop(void)

{
  undefined4 unaff_r7;
  
  osTimerStop(*DAT_004a7158);
  return unaff_r7;
}

