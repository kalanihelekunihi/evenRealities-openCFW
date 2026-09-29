
undefined8 FUN_004d0294(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  
  iVar1 = FUN_004cfda0(param_1);
  if (iVar1 != 0) {
    FUN_004d09b4(DAT_004d0960,DAT_004d06ac,0x2a0);
  }
  iVar1 = FUN_004cfd70(param_2);
  *(int *)(param_1 + 4) = *DAT_004d0964 + iVar1 + *(int *)(param_1 + 4);
  FUN_004cfe88(param_1);
  return CONCAT44(param_4,param_1);
}

