
undefined4 FUN_005badf4(uint *param_1,uint *param_2,undefined4 param_3,undefined4 param_4)

{
  uint uVar1;
  
  uVar1 = service_time_current_epoch_get();
  if (param_1 != (uint *)0x0) {
    *param_1 = (uVar1 / 0xe10) % 0x18;
  }
  if (param_2 != (uint *)0x0) {
    *param_2 = (uVar1 / 0x3c) % 0x3c;
  }
  return param_4;
}

