
undefined8
jbd4010_vtable_init(char param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  
  if (param_1 != '\0') {
    jbd4010_power_off_sequence();
  }
  am_devices_mspi_jbd4010_configure();
  uVar1 = am_devices_mspi_jbd4010_read_chipId(0);
  if (param_1 != '\0') {
    jbd4010_clear_display();
    FUN_004910f4(5);
    jbd4010_power_on_sequence();
  }
  osDelay(10);
  return CONCAT44(param_4,uVar1);
}

