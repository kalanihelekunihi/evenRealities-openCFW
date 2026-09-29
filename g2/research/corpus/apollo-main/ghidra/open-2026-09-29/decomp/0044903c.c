
undefined8 osKernelInitialize(void)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 unaff_r7;
  
  iVar1 = IRQ_Context();
  if (iVar1 == 0) {
    iVar1 = xTaskGetSchedulerState();
    if ((iVar1 == 1) && (*DAT_00449698 == 0)) {
      *DAT_00449698 = 1;
      uVar2 = 0;
    }
    else {
      uVar2 = 0xffffffff;
    }
  }
  else {
    uVar2 = 0xfffffffa;
  }
  return CONCAT44(unaff_r7,uVar2);
}

