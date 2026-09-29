
void FUN_00410c8a(undefined4 *param_1)

{
  undefined4 uVar1;
  
  uVar1 = lfs_fromle32(*param_1);
  *param_1 = uVar1;
  uVar1 = lfs_fromle32(param_1[1]);
  param_1[1] = uVar1;
  uVar1 = lfs_fromle32(param_1[2]);
  param_1[2] = uVar1;
  return;
}

