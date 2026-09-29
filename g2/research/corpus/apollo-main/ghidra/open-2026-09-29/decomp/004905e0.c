
undefined4 FUN_004905e0(int param_1,undefined4 param_2,int param_3)

{
  int iVar1;
  
  iVar1 = *(int *)(param_1 + 4);
  *(int *)(param_1 + 4) = iVar1 + param_3;
  FUN_00439be4(iVar1);
  return 1;
}

