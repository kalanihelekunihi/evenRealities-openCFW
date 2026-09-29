
undefined4 FUN_0041f8ba(byte param_1)

{
  int iVar1;
  undefined4 uVar2;
  
  iVar1 = DAT_0041f9c8;
  if (param_1 < 4) {
    *(undefined1 *)((uint)param_1 * 0x1c + DAT_0041f9c8 + 0x18) = 0;
    FUN_0041d92c(*(undefined4 *)(*(int *)((uint)param_1 * 0x1c + iVar1 + 8) + 4),*DAT_0041f9d0);
    FUN_0041d92c(**(undefined4 **)((uint)param_1 * 0x1c + iVar1 + 8),*DAT_0041f9d4);
    uVar2 = FUN_00422ba8(*(undefined4 *)(iVar1 + (uint)param_1 * 0x1c + 4),2,1);
  }
  else {
    uVar2 = 1;
  }
  return uVar2;
}

