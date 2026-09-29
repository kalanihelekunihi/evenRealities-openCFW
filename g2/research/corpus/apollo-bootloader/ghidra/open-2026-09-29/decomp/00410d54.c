
void FUN_00410d54(undefined4 *param_1)

{
  undefined4 uVar1;
  
  uVar1 = lfs_tole32(*param_1);
  *param_1 = uVar1;
  uVar1 = lfs_tole32(param_1[1]);
  param_1[1] = uVar1;
  uVar1 = lfs_tole32(param_1[2]);
  param_1[2] = uVar1;
  uVar1 = lfs_tole32(param_1[3]);
  param_1[3] = uVar1;
  uVar1 = lfs_tole32(param_1[4]);
  param_1[4] = uVar1;
  uVar1 = lfs_tole32(param_1[5]);
  param_1[5] = uVar1;
  return;
}

