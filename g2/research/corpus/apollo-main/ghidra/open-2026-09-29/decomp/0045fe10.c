
undefined4 FUN_0045fe10(int param_1,int param_2,undefined1 param_3)

{
  undefined4 uVar1;
  int iVar2;
  
  if ((param_1 == 0) || (param_2 == 0)) {
    uVar1 = 0;
  }
  else {
    iVar2 = FUN_0045f840();
    if (iVar2 == 0) {
      uVar1 = 0;
    }
    else {
      *(undefined1 *)(iVar2 + 10) = param_3;
      uVar1 = 1;
    }
  }
  return uVar1;
}

