
int FUN_005d1daa(undefined4 param_1,uint *param_2)

{
  int iVar1;
  uint uVar2;
  
  iVar1 = 0;
  uVar2 = *param_2;
  do {
    uVar2 = uVar2 + 1;
    if (0xff < uVar2) {
      uVar2 = 0;
      break;
    }
    iVar1 = FUN_005d1d64(param_1,uVar2);
  } while (iVar1 == 0);
  *param_2 = uVar2;
  return iVar1;
}

