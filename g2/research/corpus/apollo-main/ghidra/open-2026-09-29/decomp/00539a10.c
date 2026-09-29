
undefined4 FUN_00539a10(uint *param_1)

{
  undefined4 uVar1;
  
  if ((param_1 == (uint *)0x0) || ((*param_1 & 0x1ffffff) != DAT_00539dac)) {
    uVar1 = 2;
  }
  else {
    *DAT_00539db4 = *DAT_00539db4 & 0xdfffffff;
    *param_1 = *param_1 & 0xfdffffff;
    uVar1 = 0;
  }
  return uVar1;
}

