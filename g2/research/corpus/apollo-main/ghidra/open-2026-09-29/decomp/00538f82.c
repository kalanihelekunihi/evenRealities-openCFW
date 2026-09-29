
undefined4 FUN_00538f82(uint *param_1)

{
  undefined4 uVar1;
  
  if ((param_1 == (uint *)0x0) || ((*param_1 & 0x1ffffff) != DAT_0053924c)) {
    uVar1 = 2;
  }
  else if (param_1[4] == param_1[5]) {
    uVar1 = 7;
  }
  else {
    param_1[5] = param_1[4];
    param_1[8] = param_1[8] - 1;
    uVar1 = 0;
  }
  return uVar1;
}

