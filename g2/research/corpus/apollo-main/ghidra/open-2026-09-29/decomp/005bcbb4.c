
undefined4 hongshi_power_off_sequence(void)

{
  undefined4 *puVar1;
  
  FUN_004c26e0(*DAT_005bd304,2,1);
  FUN_004c3500(0,0x10);
  FUN_0050938e(1);
  driver_a6ng_set_gpio_output();
  puVar1 = DAT_005bd308;
  *DAT_005bd308 = 0x4000;
  osDelay(1);
  *puVar1 = 1;
  osDelay(1);
  FUN_00512410();
  osDelay(10);
  return 0;
}

