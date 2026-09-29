
undefined8 FUN_0045faa8(int *param_1,byte param_2,int param_3,undefined4 param_4)

{
  undefined4 uVar1;
  int iVar2;
  
  if (param_1 == (int *)0x0) {
    uVar1 = 0;
  }
  else if (param_2 == 0) {
    if (*param_1 == 0) {
      uVar1 = 0;
    }
    else {
      FUN_0045f6da(param_1,0);
      uVar1 = 1;
    }
  }
  else if (param_2 == 2) {
    if (param_3 == 0) {
      uVar1 = 0;
    }
    else {
      iVar2 = FUN_0045f840(param_1,param_3);
      if ((iVar2 == 0) || (*(char *)(iVar2 + 0xb) != '\x01')) {
        uVar1 = 0;
      }
      else if ((*param_1 == 0) || (*(int *)*param_1 != param_3)) {
        FUN_0045f6ec(param_1,param_3);
        uVar1 = 1;
      }
      else {
        uVar1 = 1;
      }
    }
  }
  else if (param_2 < 2) {
    if (param_3 == 0) {
      uVar1 = 0;
    }
    else {
      iVar2 = FUN_0045f840(param_1,param_3);
      if ((iVar2 == 0) || (*(char *)(iVar2 + 0xb) != '\x01')) {
        uVar1 = 0;
      }
      else {
        FUN_0045f6c0(param_1,param_3);
        uVar1 = 1;
      }
    }
  }
  else {
    uVar1 = 0;
  }
  return CONCAT44(param_4,uVar1);
}

