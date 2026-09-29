
uint gx_analog_set_ldo_ana_voltage(uint param_1)

{
  if (param_1 != 0xffffffff) {
    *(uint *)(iRam10004424 + 0x54) = param_1 & 0xff | *(uint *)(iRam10004424 + 0x54) & 0xf0;
    param_1 = 0;
  }
  return param_1;
}

