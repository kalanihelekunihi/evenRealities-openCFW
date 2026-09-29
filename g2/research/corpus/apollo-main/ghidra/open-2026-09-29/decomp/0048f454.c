
undefined4 FUN_0048f454(undefined4 *param_1,undefined4 param_2)

{
  undefined4 uVar1;
  int iVar2;
  
  if (param_1[2] == 0) {
    uVar1 = DAT_0048fc7c;
    if (param_1[3] != 0) {
      uVar1 = param_1[3];
    }
    param_1[3] = uVar1;
    uVar1 = 0;
  }
  else {
    iVar2 = (*(code *)*param_1)(param_1,param_2,1);
    if (iVar2 == 0) {
      uVar1 = DAT_0048fc80;
      if (param_1[3] != 0) {
        uVar1 = param_1[3];
      }
      param_1[3] = uVar1;
      uVar1 = 0;
    }
    else {
      param_1[2] = param_1[2] + -1;
      uVar1 = 1;
    }
  }
  return uVar1;
}

