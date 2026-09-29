
undefined4 HciDrvRadioShutdown(void)

{
  undefined4 unaff_r7;
  
  WsfTimerStop(DAT_004b4d9c);
  FUN_0052dd6a();
  FUN_0052eece(0);
  FUN_0052dd7c();
  *DAT_004b4d84 = 0;
  *DAT_004b4d88 = 0;
  FUN_0052df12(*DAT_004b4d74);
  return unaff_r7;
}

