
undefined4 FUN_005a0786(byte param_1,undefined4 param_2,char *param_3)

{
  undefined4 uVar1;
  
  uVar1 = 0;
  if (param_1 == 0) {
    if ((param_3 != (char *)0x0) && (*param_3 == '\x02')) {
      FUN_005a0204();
    }
  }
  else if (param_1 == 2) {
    uVar1 = FUN_005a00fc(param_3);
  }
  else if (param_1 < 2) {
    if (*param_3 == '\0') {
      uVar1 = FUN_005a05e0();
    }
    else {
      uVar1 = FUN_005a0328(*param_3);
    }
  }
  return uVar1;
}

