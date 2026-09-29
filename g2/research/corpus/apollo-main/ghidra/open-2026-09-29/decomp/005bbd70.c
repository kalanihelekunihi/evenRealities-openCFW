
undefined4 am_devices_mspi_a6ng_init(int param_1,undefined4 param_2,undefined4 param_3)

{
  undefined4 uVar1;
  
  if (param_1 == 0) {
    uVar1 = 0xffffffff;
  }
  else {
    *DAT_005bc880 = param_1;
    *DAT_005bc884 = param_2;
    am_devices_mspi_init(DAT_005bc87c,param_3,DAT_005bc88c,DAT_005bc888);
    uVar1 = am_devices_mspi_hongshi_init(1);
  }
  return uVar1;
}

