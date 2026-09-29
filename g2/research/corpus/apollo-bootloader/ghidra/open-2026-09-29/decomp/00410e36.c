
undefined8 FUN_00410e36(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  uint uVar1;
  undefined4 uVar2;
  int iVar3;
  
  uVar1 = *(int *)(param_1 + 0x5c) + *(int *)(param_1 + 0x54);
  *(uint *)(param_1 + 0x54) =
       uVar1 - *(uint *)(param_1 + 0x6c) * (uVar1 / *(uint *)(param_1 + 0x6c));
  *(undefined4 *)(param_1 + 0x5c) = 0;
  uVar2 = lfs_min(*(int *)(*(int *)(param_1 + 0x68) + 0x2c) << 3,*(undefined4 *)(param_1 + 0x60));
  *(undefined4 *)(param_1 + 0x58) = uVar2;
  FUN_0041560c(*(undefined4 *)(param_1 + 100),*(undefined4 *)(*(int *)(param_1 + 0x68) + 0x2c),0);
  iVar3 = FUN_00414954(param_1,DAT_00411be0,param_1,1);
  if (iVar3 == 0) {
    iVar3 = 0;
  }
  else {
    lfs_alloc_drop(param_1);
  }
  return CONCAT44(param_4,iVar3);
}

