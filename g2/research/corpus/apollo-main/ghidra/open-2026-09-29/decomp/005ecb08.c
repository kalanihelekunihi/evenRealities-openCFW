
undefined4 FUN_005ecb08(int param_1,char param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  undefined1 uVar2;
  
  if (param_1 != 0) {
    uVar1 = FUN_0044104c(0xffffff);
    FUN_004412ec(param_1,uVar1,0);
    if (param_2 == '\0') {
      uVar2 = 0;
    }
    else {
      uVar2 = 0xff;
    }
    FUN_0044130c(param_1,uVar2,0);
    if (param_2 == '\0') {
      FUN_00589892(param_1);
    }
    else {
      FUN_005897ee(param_1);
    }
  }
  return param_4;
}

