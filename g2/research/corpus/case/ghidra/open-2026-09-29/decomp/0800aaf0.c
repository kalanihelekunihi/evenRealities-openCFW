
undefined4 osTimerStart(int param_1,undefined4 param_2)

{
  bool bVar1;
  int iVar2;
  uint uVar3;
  
  uVar3 = 0;
  bVar1 = (bool)isCurrentModePrivileged();
  if (bVar1) {
    uVar3 = getCurrentExceptionNumber();
    uVar3 = uVar3 & 0x1ff;
  }
  if (uVar3 != 0) {
    return 0xfffffffa;
  }
  if (param_1 == 0) {
    return 0xfffffffc;
  }
  iVar2 = FUN_0800cd80(param_1,4,param_2,0,0);
  if (iVar2 != 1) {
    return 0xfffffffd;
  }
  return 0;
}

