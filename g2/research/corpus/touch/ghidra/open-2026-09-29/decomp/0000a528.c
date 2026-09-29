
undefined4 Cy_SysPm_CpuEnterSleep(void)

{
  int iVar1;
  undefined4 uVar2;
  
  if ((*DAT_0000a584 == 0) || (iVar1 = Cy_SysPm_ExecuteCallback(0,1), iVar1 == 0)) {
    uVar2 = Cy_SysLib_EnterCriticalSection();
    if (*DAT_0000a584 != 0) {
      Cy_SysPm_ExecuteCallback(0,4);
    }
    sleep_wfi_entry();
    Cy_SysLib_ExitCriticalSection(uVar2);
    uVar2 = 0;
    if (*DAT_0000a584 != 0) {
      Cy_SysPm_ExecuteCallback(0,8);
    }
  }
  else {
    Cy_SysPm_ExecuteCallback(0,2);
    uVar2 = DAT_0000a588;
  }
  return uVar2;
}

