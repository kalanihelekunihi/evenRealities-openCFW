
undefined4 IRQ_Context(void)

{
  bool bVar1;
  uint uVar2;
  int iVar3;
  undefined4 uVar4;
  
  uVar4 = 0;
  uVar2 = 0;
  bVar1 = (bool)isCurrentModePrivileged();
  if (bVar1) {
    uVar2 = getCurrentExceptionNumber();
    uVar2 = uVar2 & 0x1ff;
  }
  if (uVar2 == 0) {
    iVar3 = xTaskGetSchedulerState();
    if (iVar3 != 1) {
      iVar3 = 0;
      bVar1 = (bool)isCurrentModePrivileged();
      if (bVar1) {
        iVar3 = isIRQinterruptsEnabled();
      }
      if (iVar3 == 0) {
        iVar3 = 0;
        bVar1 = (bool)isCurrentModePrivileged();
        if (bVar1) {
          iVar3 = getBasePriority();
        }
        if (iVar3 == 0) {
          return 0;
        }
      }
      uVar4 = 1;
    }
  }
  else {
    uVar4 = 1;
  }
  return uVar4;
}

