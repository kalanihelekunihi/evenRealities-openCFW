
undefined4 FUN_00558314(char *param_1,char *param_2)

{
  undefined4 uVar1;
  int iVar2;
  byte bVar3;
  
  if ((param_1 == (char *)0x0) || (param_2 == (char *)0x0)) {
    uVar1 = 0;
  }
  else if (*param_1 == *param_2) {
    if (param_1[1] == param_2[1]) {
      for (bVar3 = 0; bVar3 < (byte)param_1[1]; bVar3 = bVar3 + 1) {
        if (param_1[bVar3 + 2] != param_2[bVar3 + 2]) {
          return 0;
        }
      }
      iVar2 = FUN_0055819e(param_1 + 8,param_2 + 8);
      if (iVar2 == 0) {
        uVar1 = 0;
      }
      else {
        uVar1 = 1;
      }
    }
    else {
      uVar1 = 0;
    }
  }
  else {
    uVar1 = 0;
  }
  return uVar1;
}

