
undefined4 hciCmdTimeout(void)

{
  undefined4 unaff_r7;
  
  HciDrvRadioShutdown();
  HciDrvRadioBoot(0);
  DmDevReset();
  return unaff_r7;
}

