
undefined1 FUN_005b3680(undefined1 *param_1,undefined1 param_2,undefined1 param_3)

{
  undefined1 uVar1;
  int iVar2;
  
  if (param_1 == (undefined1 *)0x0) {
    uVar1 = 0;
  }
  else {
    iVar2 = FUN_005b3648(*param_1,param_2,param_3);
    if ((iVar2 == 0) || (iVar2 = FUN_005b3648(param_1[1],param_3,param_2), iVar2 == 0)) {
      uVar1 = 0;
    }
    else {
      uVar1 = 1;
    }
  }
  return uVar1;
}

