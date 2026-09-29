
undefined4 osTimerStop(int param_1)

{
  bool bVar1;
  uint uVar2;
  int iVar3;
  
  uVar2 = 0;
  bVar1 = (bool)isCurrentModePrivileged();
  if (bVar1) {
    uVar2 = getCurrentExceptionNumber();
    uVar2 = uVar2 & 0x1ff;
  }
  if (uVar2 != 0) {
    return 0xfffffffa;
  }
  if (param_1 == 0) {
    return 0xfffffffc;
  }
  iVar3 = case_critical_read_flag40(param_1);
  if (iVar3 != 0) {
    iVar3 = FUN_0800cd80(param_1,3,0,0,0);
    if (iVar3 != 1) {
      return 0xffffffff;
    }
    return 0;
  }
  return 0xfffffffd;
}

