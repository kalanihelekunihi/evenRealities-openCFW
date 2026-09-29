
undefined4 osEventFlagsGet(int param_1)

{
  bool bVar1;
  undefined4 uVar2;
  uint uVar3;
  
  if (param_1 == 0) {
    return 0;
  }
  uVar3 = 0;
  bVar1 = (bool)isCurrentModePrivileged();
  if (bVar1) {
    uVar3 = getCurrentExceptionNumber();
    uVar3 = uVar3 & 0x1ff;
  }
  if (uVar3 != 0) {
    uVar2 = case_read_word_protected();
    return uVar2;
  }
  uVar2 = case_atomic_clear_word(param_1,0);
  return uVar2;
}

