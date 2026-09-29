
undefined4 semantic_preload_timer_stop(void)

{
  undefined4 unaff_r7;
  
  if (*DAT_0058bc18 != 0) {
    osTimerStop(*DAT_0058bc18);
  }
  return unaff_r7;
}

