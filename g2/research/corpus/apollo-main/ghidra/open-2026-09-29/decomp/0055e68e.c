
undefined8 FUN_0055e68e(byte param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  
  iVar1 = DAT_0055e98c;
  if (param_1 < 4) {
    FUN_00480f0c(**(undefined4 **)((uint)param_1 * 0x1c + DAT_0055e98c + 8),*DAT_0055e994);
    FUN_0058e352(*(undefined4 *)((uint)param_1 * 0x1c + iVar1 + 4));
    FUN_00491102(10);
    FUN_00480f0c(*(undefined4 *)(*(int *)((uint)param_1 * 0x1c + iVar1 + 8) + 4),
                 *(undefined4 *)(*(int *)((uint)param_1 * 0x1c + iVar1 + 8) + 0xc));
    FUN_0058e352(*(undefined4 *)((uint)param_1 * 0x1c + iVar1 + 4));
    FUN_00491102(10);
    FUN_0055e288((int)(short)((short)*(undefined4 *)(iVar1 + (uint)param_1 * 0x1c) + 0xf));
    FUN_0055e2a6((int)(short)((short)*(undefined4 *)(iVar1 + (uint)param_1 * 0x1c) + 0xf),3);
    FUN_0055e244((int)(short)((short)*(undefined4 *)(iVar1 + (uint)param_1 * 0x1c) + 0xf));
    iVar3 = FUN_0058e782(*(undefined4 *)((uint)param_1 * 0x1c + iVar1 + 4),0x471);
    *(undefined1 *)(iVar1 + (uint)param_1 * 0x1c + 0x18) = 1;
    if (iVar3 == 0) {
      uVar2 = 0;
    }
    else {
      uVar2 = 1;
    }
  }
  else {
    uVar2 = 1;
  }
  return CONCAT44(param_4,uVar2);
}

