
undefined4 jbd4010_power_off_sequence(void)

{
  undefined4 *puVar1;
  byte *pbVar2;
  
  pbVar2 = (byte *)FUN_0050938e(1);
  jbd4010_configure_gpio_pins();
  if (*pbVar2 < 4) {
    *DAT_00593928 = 1;
  }
  else {
    FUN_005124fc();
  }
  osDelay(3);
  if (*pbVar2 < 3) {
    *DAT_00593928 = 0x8000;
  }
  else {
    FUN_005122ec();
  }
  osDelay(3);
  *DAT_00593928 = 0x4000;
  osDelay(10);
  FUN_004c32b4(0,0);
  puVar1 = DAT_005932f8;
  FUN_004c26e0(*DAT_005932f8,0,1);
  FUN_004c0ea8(*puVar1);
  FUN_004c099c(*puVar1,DAT_00593304);
  FUN_004c0e1e(*puVar1);
  *DAT_0059392c = 0x10;
  return 0;
}

