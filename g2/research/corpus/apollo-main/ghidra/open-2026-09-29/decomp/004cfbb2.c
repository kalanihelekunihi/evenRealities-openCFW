
void FUN_004cfbb2(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  
  iVar1 = lfs_mlist_isopen(*(undefined4 *)(param_1 + 0x28),param_2,param_3,param_4,param_4);
  if (iVar1 == 0) {
    FUN_004d09b4(DAT_004cfcf0,DAT_004cfce8,0x1851);
  }
  FUN_004ce3bc(param_1,param_2,param_3,param_4);
  return;
}

