
undefined4 osDelay(int param_1)

{
  bool bVar1;
  uint uVar2;
  undefined4 uVar3;
  
  uVar2 = 0;
  bVar1 = (bool)isCurrentModePrivileged();
  if (bVar1) {
    uVar2 = getCurrentExceptionNumber();
    uVar2 = uVar2 & 0x1ff;
  }
  if (uVar2 == 0) {
    uVar3 = 0;
    if (param_1 != 0) {
      FUN_0800c128(param_1);
    }
  }
  else {
    uVar3 = 0xfffffffa;
  }
  return uVar3;
}

