
void FUN_005d23da(int param_1,undefined4 param_2)

{
  int iVar1;
  
  if ((*(int *)(param_1 + 0x14) != *(int *)(param_1 + 0xc)) ||
     (iVar1 = FUN_005d232c(param_1,*(int *)(param_1 + 0x10) + *(int *)(param_1 + 0xc)), iVar1 != 0))
  {
    FUN_00439be4(*(int *)(param_1 + 0x1c) + *(int *)(param_1 + 8) * *(int *)(param_1 + 0x14),param_2
                 ,*(undefined4 *)(param_1 + 8));
    *(int *)(param_1 + 0x14) = *(int *)(param_1 + 0x14) + 1;
  }
  return;
}

