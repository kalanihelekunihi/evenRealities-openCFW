
undefined4 FUN_00538e3c(uint *param_1)

{
  undefined4 uVar1;
  
  if ((param_1 == (uint *)0x0) || ((*param_1 & 0x1ffffff) != DAT_0053924c)) {
    uVar1 = 2;
  }
  else if ((int)(*param_1 << 6) < 0) {
    uVar1 = 0;
  }
  else {
    if (DAT_00539250 <= param_1[2]) {
      DataMemoryBarrier(0x1f);
    }
    **(uint **)param_1[9] = **(uint **)param_1[9] | 1;
    *param_1 = *param_1 | 0x2000000;
    uVar1 = 0;
  }
  return uVar1;
}

