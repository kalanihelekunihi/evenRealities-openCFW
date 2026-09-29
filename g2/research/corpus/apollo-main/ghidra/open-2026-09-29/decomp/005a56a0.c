
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 atMkdirHandler(undefined4 param_1)

{
  undefined4 uVar1;
  int iVar2;
  
  if (*DAT_005a56f4 == 1) {
    iVar2 = FUN_004cfc5c(_DAT_005a5714,param_1);
    if (iVar2 == 0) {
      at_core_output(_DAT_005a571c);
    }
    else {
      at_core_output(_DAT_005a5718,param_1);
    }
    uVar1 = 1;
  }
  else {
    uVar1 = 0;
  }
  return uVar1;
}

