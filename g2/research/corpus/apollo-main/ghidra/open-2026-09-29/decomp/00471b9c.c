
undefined4 FUN_00471b9c(uint param_1)

{
  undefined4 uVar1;
  
  if (param_1 < 6) {
    uVar1 = 4;
  }
  else if (param_1 - 6 < 4) {
    uVar1 = 0;
  }
  else if (param_1 - 0x13 < 6) {
    uVar1 = 5;
  }
  else if (param_1 - 0x19 < 3) {
    uVar1 = 2;
  }
  else {
    uVar1 = 7;
  }
  return uVar1;
}

