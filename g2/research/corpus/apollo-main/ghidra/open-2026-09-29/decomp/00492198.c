
undefined4 FUN_00492198(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  
  if (*(int *)(param_1 + 0x6428) != 0) {
    if (0x400U - *(int *)(param_1 + 0x6424) < 2) {
      FUN_004d9522(param_1,param_1 + 0x6021,*(undefined4 *)(param_1 + 0x6424));
      *(undefined4 *)(param_1 + 0x6424) = 0;
    }
    iVar1 = FUN_0049207a(*(int *)(param_1 + 0x6424) + param_1 + 0x6021,param_1 + 0x642c);
    *(int *)(param_1 + 0x6424) = iVar1 + *(int *)(param_1 + 0x6424);
  }
  FUN_004d9522(param_1,param_1 + 0x6021,*(undefined4 *)(param_1 + 0x6424));
  FUN_00491722(param_1);
  return param_4;
}

