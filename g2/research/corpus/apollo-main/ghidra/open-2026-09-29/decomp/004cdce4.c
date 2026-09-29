
undefined4 FUN_004cdce4(undefined4 param_1,int param_2)

{
  undefined4 uVar1;
  
  uVar1 = FUN_004cdf74(param_1,param_2);
  lfs_mlist_remove(param_1,param_2);
  if (**(int **)(param_2 + 0x50) == 0) {
    FUN_004ca812(*(undefined4 *)(param_2 + 0x4c));
  }
  return uVar1;
}

