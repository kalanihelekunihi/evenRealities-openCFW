
undefined4 FUN_0053916e(uint *param_1)

{
  undefined4 uVar1;
  uint uVar2;
  
  if ((param_1 == (uint *)0x0) || ((*param_1 & 0x1ffffff) != DAT_0053924c)) {
    uVar1 = 2;
  }
  else if ((int)(*param_1 << 6) < 0) {
    uVar1 = 7;
  }
  else {
    **(uint **)param_1[9] = **(uint **)param_1[9] & 0xfffffffe;
    uVar2 = param_1[1];
    param_1[3] = uVar2;
    param_1[5] = uVar2;
    param_1[4] = uVar2;
    param_1[7] = 0;
    param_1[8] = 0;
    **(undefined4 **)(param_1[9] + 8) = 0;
    **(undefined4 **)(param_1[9] + 0xc) = 0;
    **(uint **)(param_1[9] + 4) = param_1[1];
    *param_1 = *param_1 & 0xfdffffff;
    uVar1 = 0;
  }
  return uVar1;
}

