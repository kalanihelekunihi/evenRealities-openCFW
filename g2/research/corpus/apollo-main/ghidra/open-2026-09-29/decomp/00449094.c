
undefined4 osKernelStart(void)

{
  int *piVar1;
  int iVar2;
  undefined4 uVar3;
  
  iVar2 = IRQ_Context();
  if (iVar2 == 0) {
    iVar2 = xTaskGetSchedulerState();
    piVar1 = DAT_00449698;
    if ((iVar2 == 1) && (*DAT_00449698 == 1)) {
      FUN_0044900c();
      *piVar1 = 2;
      FUN_00454cec();
      return 0;
    }
    uVar3 = 0xffffffff;
  }
  else {
    uVar3 = 0xfffffffa;
  }
  return uVar3;
}

