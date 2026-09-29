
longlong jbd4010_power_on_sequence(void)

{
  undefined4 *puVar1;
  byte *pbVar2;
  uint in_r3;
  
  FUN_004c26e0(*DAT_005932f8,2,1);
  FUN_004c3500(0,0x10);
  pbVar2 = (byte *)FUN_0050938e(1);
  jbd4010_configure_gpio_pins();
  puVar1 = DAT_00593930;
  *DAT_00593930 = 0x4000;
  osDelay(3);
  if (*pbVar2 < 3) {
    *puVar1 = 0x8000;
  }
  else {
    FUN_00512410();
  }
  osDelay(3);
  if (*pbVar2 < 4) {
    *puVar1 = 1;
  }
  else {
    FUN_005125a8();
  }
  osDelay(10);
  *DAT_00593934 = 0x10;
  return (ulonglong)in_r3 << 0x20;
}

