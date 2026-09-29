
longlong hongshi_power_on_sequence(void)

{
  uint unaff_r7;
  
  FUN_0050938e(1);
  driver_a6ng_set_gpio_output();
  FUN_005122ec();
  osDelay(7);
  FUN_004c32b4(0,0);
  osDelay(1);
  *DAT_005bd300 = 1;
  osDelay(0x6e);
  FUN_004c26e0(*DAT_005bd304,0,1);
  return (ulonglong)unaff_r7 << 0x20;
}

