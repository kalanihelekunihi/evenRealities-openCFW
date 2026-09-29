
undefined4 am_hal_mspi_deinitialize(uint *param_1)

{
  undefined4 uVar1;
  
  if ((param_1 == (uint *)0x0) || ((*param_1 & 0x1ffffff) != DAT_004251b0)) {
    uVar1 = 2;
  }
  else {
    if ((int)(*param_1 << 6) < 0) {
      am_hal_mspi_disable();
    }
    *param_1 = *param_1 & 0xfeffffff;
    param_1[1] = 0;
    uVar1 = 0;
  }
  return uVar1;
}

