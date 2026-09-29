
undefined4 FUN_0055e898(byte param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  int iVar2;
  undefined4 local_28 [4];
  undefined4 uStack_18;
  
  iVar2 = DAT_0055e98c;
  if ((param_1 < 4) && (*(char *)((uint)param_1 * 0x1c + DAT_0055e98c + 0x18) != '\0')) {
    uStack_18 = param_4;
    FUN_00439c04(local_28,*(undefined4 *)((uint)param_1 * 0x1c + DAT_0055e98c + 0xc),0x10);
    local_28[0] = param_2;
    iVar2 = FUN_0058e09e(*(undefined4 *)(iVar2 + (uint)param_1 * 0x1c + 4),local_28);
    if (iVar2 == 0) {
      uVar1 = 0;
    }
    else {
      uVar1 = 1;
    }
  }
  else {
    uVar1 = 1;
  }
  return uVar1;
}

