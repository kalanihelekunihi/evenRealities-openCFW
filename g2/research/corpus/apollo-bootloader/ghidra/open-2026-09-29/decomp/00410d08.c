
void FUN_00410d08(undefined4 *param_1)

{
  undefined4 uVar1;
  
  uVar1 = lfs_tole32(*param_1);
  *param_1 = uVar1;
  uVar1 = lfs_tole32(param_1[1]);
  param_1[1] = uVar1;
  return;
}

