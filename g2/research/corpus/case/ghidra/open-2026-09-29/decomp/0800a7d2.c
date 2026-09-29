
undefined4 osEventFlagsClear(int param_1,uint param_2)

{
  bool bVar1;
  uint uVar2;
  int iVar3;
  undefined4 uVar4;
  
  if ((param_1 == 0) || (param_2 >> 0x18 != 0)) {
    uVar4 = 0xfffffffc;
  }
  else {
    uVar2 = 0;
    bVar1 = (bool)isCurrentModePrivileged();
    if (bVar1) {
      uVar2 = getCurrentExceptionNumber();
      uVar2 = uVar2 & 0x1ff;
    }
    if (uVar2 == 0) {
      uVar4 = case_atomic_clear_word(param_1,param_2);
    }
    else {
      uVar4 = case_read_word_protected(param_1);
      iVar3 = case_dispatch_resource(param_1,param_2);
      if (iVar3 == 0) {
        uVar4 = 0xfffffffd;
      }
    }
  }
  return uVar4;
}

