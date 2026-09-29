
undefined8 FUN_005111e6(undefined4 param_1,undefined *param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  int iVar2;
  int iVar3;
  
  uVar1 = func_0x0055ee74(DAT_00511984,1);
  iVar2 = func_0x0055ee7e(uVar1,5);
  if (iVar2 != DAT_00511964) {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      param_1 = 0x17c;
      param_2 = PTR_s_ERROR__npmx_gpio_mode_set__d_00511bc8;
      FUN_0043d574(1,DAT_00511958,DAT_00511954,PTR_s_npmx_int_pin_configure_00511bcc,0x17c,
                   PTR_s_ERROR__npmx_gpio_mode_set__d_00511bc8,iVar2,param_4);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x4400000,PTR_s__npmx_driver_ERROR__npmx_gpio_mo_00511bd0,
                          PTR_s__npmx_driver_ERROR__npmx_gpio_mo_00511bd0,iVar2);
    }
  }
  return CONCAT44(param_2,param_1);
}

