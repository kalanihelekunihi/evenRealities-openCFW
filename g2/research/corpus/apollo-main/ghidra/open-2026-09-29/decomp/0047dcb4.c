
int FUN_0047dcb4(undefined1 *param_1)

{
  int iVar1;
  
  iVar1 = osKernelGetState();
  if (iVar1 == 2) {
    iVar1 = service_time_rtc_refresh();
    *param_1 = (uint)(DAT_0047e280 + iVar1) < DAT_0047e284;
  }
  else {
    *param_1 = 0;
    iVar1 = 0;
  }
  return iVar1;
}

