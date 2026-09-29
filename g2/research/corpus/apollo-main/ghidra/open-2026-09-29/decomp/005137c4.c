
undefined4 FUN_005137c4(uint param_1)

{
  undefined4 uVar1;
  
  if ((param_1 & 3) == 0) {
    if (param_1 < 0x3fd) {
      uVar1 = 0;
    }
    else {
      uVar1 = 5;
    }
  }
  else {
    uVar1 = 6;
  }
  return uVar1;
}

