
void FUN_004cfa94(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  
  iVar1 = lfs_mlist_isopen(*(undefined4 *)(param_1 + 0x28),param_2,param_3,param_4,param_4);
  if (iVar1 != 0) {
    FUN_004d09b4(DAT_004cfcec,DAT_004cfce8,0x17e7);
  }
  FUN_004cdcc8(param_1,param_2,param_3,param_4);
  return;
}

