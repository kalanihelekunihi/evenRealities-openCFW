
undefined4 os_event_flags_create_wrapper(int param_1)

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
    iVar3 = -1;
    if (param_1 == 0) {
      iVar3 = 0;
    }
    else if ((*(int *)(param_1 + 8) == 0) || (*(uint *)(param_1 + 0xc) < 0x20)) {
      if ((*(int *)(param_1 + 8) == 0) && (*(int *)(param_1 + 0xc) == 0)) {
        iVar3 = 0;
      }
    }
    else {
      iVar3 = 1;
    }
    if (iVar3 == 1) {
      uVar4 = FUN_0800c4aa(*(undefined4 *)(param_1 + 8));
    }
    else if (iVar3 == 0) {
      uVar4 = FUN_0800c48c();
    }
  }
  return uVar4;
}

