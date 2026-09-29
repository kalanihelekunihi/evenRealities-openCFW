
undefined4 loggerSetting_set_ble_transmit(char param_1)

{
  undefined4 unaff_r7;
  
  if (param_1 == '\0') {
    FUN_00448cb8(0,DAT_0045926c);
    *DAT_00459264 = 0;
    *DAT_00459268 = 0;
  }
  else {
    *DAT_00459264 = 1;
    *DAT_00459268 = 1000;
    FUN_00448cb8(1,DAT_0045926c);
  }
  return unaff_r7;
}

