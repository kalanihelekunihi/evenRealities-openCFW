
undefined4 FUN_005b90ae(char param_1,code *param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  
  if (param_2 != (code *)0x0) {
    for (iVar1 = 0; iVar1 < 3; iVar1 = iVar1 + 1) {
      if (*(char *)(iVar1 * 0xc + DAT_005b9a64 + 8) == param_1) {
        (*param_2)(iVar1 * 0xc + DAT_005b9a64,param_3);
      }
    }
  }
  return param_4;
}

