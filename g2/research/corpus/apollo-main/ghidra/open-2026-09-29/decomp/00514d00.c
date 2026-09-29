
undefined4 FUN_00514d00(int param_1)

{
  int iVar1;
  
  if (param_1 == 0) {
    FUN_004b127c(0x2000);
    return 0xffffffff;
  }
  if ((*(int *)(param_1 + 0x1c) < 0) || (iVar1 = FUN_00514026(), -1 < iVar1)) {
    *(undefined4 *)(param_1 + 0x1c) = 0xffffffff;
  }
  return 0;
}

