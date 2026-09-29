
undefined4 cmdq_disable_4278c8(uint *param_1)

{
  undefined4 uVar1;
  
  if ((param_1 == (uint *)0x0) || ((*param_1 & 0x1ffffff) != DAT_00427c88)) {
    uVar1 = 2;
  }
  else if ((int)(*param_1 << 6) < 0) {
    **(uint **)param_1[9] = **(uint **)param_1[9] & 0xfffffffe;
    *param_1 = *param_1 & 0xfdffffff;
    uVar1 = 0;
  }
  else {
    uVar1 = 0;
  }
  return uVar1;
}

