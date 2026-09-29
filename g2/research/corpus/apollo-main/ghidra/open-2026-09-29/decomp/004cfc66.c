
void FUN_004cfc66(int param_1,undefined4 param_2,undefined4 param_3)

{
  int iVar1;
  
  iVar1 = lfs_mlist_isopen(*(undefined4 *)(param_1 + 0x28),param_2);
  if (iVar1 != 0) {
    FUN_004d09b4(DAT_004cfcf4,DAT_004cfce8,0x18ae);
  }
  FUN_004cd558(param_1,param_2,param_3);
  return;
}

