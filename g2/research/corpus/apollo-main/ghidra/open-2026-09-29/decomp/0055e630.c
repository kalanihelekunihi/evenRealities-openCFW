
undefined4 FUN_0055e630(byte param_1)

{
  int iVar1;
  undefined4 uVar2;
  
  iVar1 = DAT_0055e98c;
  if (param_1 < 4) {
    *(undefined1 *)((uint)param_1 * 0x1c + DAT_0055e98c + 0x18) = 0;
    FUN_00480f0c(*(undefined4 *)(*(int *)((uint)param_1 * 0x1c + iVar1 + 8) + 4),*DAT_0055e994);
    FUN_00480f0c(**(undefined4 **)((uint)param_1 * 0x1c + iVar1 + 8),*DAT_0055e998);
    uVar2 = FUN_0058dbb8(*(undefined4 *)(iVar1 + (uint)param_1 * 0x1c + 4),2,1);
  }
  else {
    uVar2 = 1;
  }
  return uVar2;
}

