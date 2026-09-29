
undefined8 als_function_29(void)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 unaff_r5;
  
  if (*DAT_004ae984 == 0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      unaff_r5 = 0x1d4;
      FUN_0043d574(2,DAT_004ae4dc,DAT_004ae4d8,PTR_s_DRV_ALSClose_004ae9a4,0x1d4,
                   PTR_s_ALS_already_closed_004ae9a0);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x8000000,PTR_s__sensor_als_ALS_already_closed_004ae9a8,
                          PTR_s__sensor_als_ALS_already_closed_004ae9a8);
    }
    uVar2 = 0xffffffff;
  }
  else {
    *DAT_004ae984 = 0;
    *DAT_004ae99c = 0;
    als_function_26();
    hub_timer_stop();
    uVar2 = 0;
  }
  return CONCAT44(unaff_r5,uVar2);
}

