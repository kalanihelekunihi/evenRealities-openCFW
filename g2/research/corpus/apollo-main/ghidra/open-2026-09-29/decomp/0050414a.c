
undefined4 hal_i2c_power_down(byte param_1)

{
  undefined4 uVar1;
  int iVar2;
  int iVar3;
  
  iVar2 = 0;
  iVar3 = 0;
  while ((iVar3 < 1000 &&
         (iVar2 = FUN_0055c7e8(*(undefined4 *)(DAT_00504760 + (uint)param_1 * 0x10 + 4),0,1),
         iVar2 != 0))) {
    FUN_004910f4(10);
    iVar3 = iVar3 + 1;
  }
  iVar3 = DAT_00504760;
  FUN_00480f0c(**(undefined4 **)((uint)param_1 * 0x10 + DAT_00504760 + 8),
               *(undefined4 *)(*(int *)((uint)param_1 * 0x10 + DAT_00504760 + 8) + 8));
  FUN_00480f0c(*(undefined4 *)(*(int *)(iVar3 + (uint)param_1 * 0x10 + 8) + 4),
               *(undefined4 *)(*(int *)((uint)param_1 * 0x10 + iVar3 + 8) + 0xc));
  if (iVar2 == 0) {
    uVar1 = 0;
  }
  else {
    uVar1 = 4;
  }
  return uVar1;
}

