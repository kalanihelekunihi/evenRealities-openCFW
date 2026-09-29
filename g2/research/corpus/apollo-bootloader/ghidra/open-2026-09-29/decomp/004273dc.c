
undefined4 syspll_disable_4273dc(uint *param_1)

{
  undefined4 uVar1;
  
  if ((param_1 == (uint *)0x0) || ((*param_1 & 0x1ffffff) != DAT_004275ac)) {
    uVar1 = 2;
  }
  else {
    *DAT_004275b4 = *DAT_004275b4 & 0xdfffffff;
    *param_1 = *param_1 & 0xfdffffff;
    uVar1 = 0;
  }
  return uVar1;
}

