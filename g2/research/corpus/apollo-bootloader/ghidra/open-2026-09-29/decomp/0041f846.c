
undefined8 FUN_0041f846(byte param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  
  iVar1 = DAT_0041f9c8;
  if (param_1 < 4) {
    uVar2 = FUN_00422ba8(*(undefined4 *)((uint)param_1 * 0x1c + DAT_0041f9c8 + 4),0,1);
    FUN_0041d92c(*(undefined4 *)(*(int *)((uint)param_1 * 0x1c + iVar1 + 8) + 4),
                 *(undefined4 *)(*(int *)((uint)param_1 * 0x1c + iVar1 + 8) + 0xc));
    FUN_0041d92c(**(undefined4 **)((uint)param_1 * 0x1c + iVar1 + 8),
                 *(undefined4 *)(*(int *)((uint)param_1 * 0x1c + iVar1 + 8) + 8));
    *(undefined1 *)(iVar1 + (uint)param_1 * 0x1c + 0x18) = 1;
  }
  else {
    uVar2 = 1;
  }
  return CONCAT44(param_4,uVar2);
}

