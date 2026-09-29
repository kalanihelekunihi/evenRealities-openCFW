
int Cy_SysPm_CpuEnterDeepSleep(void)

{
  int iVar1;
  undefined4 uVar2;
  
  if (*(int *)(DAT_0000a5f0 + 4) == 0) {
    iVar1 = 0;
  }
  else {
    iVar1 = Cy_SysPm_ExecuteCallback(1,1);
    if (iVar1 != 0) goto LAB_0000a5dc;
  }
  uVar2 = Cy_SysLib_EnterCriticalSection();
  if (*(int *)(DAT_0000a5f0 + 4) != 0) {
    Cy_SysPm_ExecuteCallback(1,4);
  }
  sflash_trim_load();
  Cy_SysLib_ExitCriticalSection(uVar2);
  if (iVar1 == 0) {
    if (*(int *)(DAT_0000a5f0 + 4) == 0) {
      return 0;
    }
    Cy_SysPm_ExecuteCallback(1,8);
    return 0;
  }
LAB_0000a5dc:
  if (*(int *)(DAT_0000a5f0 + 4) != 0) {
    Cy_SysPm_ExecuteCallback(1,2);
  }
  return iVar1;
}

