
undefined4 FUN_005b0c30(byte param_1)

{
  undefined4 uVar1;
  
  if (param_1 == 0) {
    uVar1 = 0;
  }
  else if (param_1 == 2) {
    uVar1 = 4;
  }
  else if (param_1 < 2) {
    uVar1 = 1;
  }
  else {
    uVar1 = 0;
  }
  return uVar1;
}

