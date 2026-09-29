
undefined8 als_function_28(undefined4 param_1,undefined4 param_2,undefined4 param_3)

{
  undefined4 *puVar1;
  int *piVar2;
  int iVar3;
  undefined4 uVar4;
  
  piVar2 = DAT_004ae984;
  if (*DAT_004ae984 == 1) {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      param_3 = 0x1b6;
      FUN_0043d574(2,DAT_004ae4dc,DAT_004ae4d8,DAT_004ae98c,0x1b6,DAT_004ae988);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x8000000,DAT_004ae990,DAT_004ae990);
    }
    uVar4 = 0xffffffff;
  }
  else {
    iVar3 = als_function_25();
    if (iVar3 == 0) {
      *piVar2 = 1;
      *DAT_004ae99c = 1;
      *DAT_004ae734 = 0;
      *DAT_004ae738 = 0;
      *DAT_004ae6c8 = 0;
      uVar4 = service_settings_auto_brightness();
      *DAT_004ae6cc = uVar4;
      *DAT_004ae8d4 = 0;
      puVar1 = DAT_004ae8dc;
      uVar4 = service_settings_auto_brightness();
      *puVar1 = uVar4;
      *DAT_004ae8e0 = *puVar1;
      *DAT_004ae950 = 0;
      als_function_22();
      als_function_13();
      als_function_06();
      hub_timer_start(0x6e);
      uVar4 = 0;
    }
    else {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        param_3 = 0x1bc;
        FUN_0043d574(1,DAT_004ae4dc,DAT_004ae4d8,DAT_004ae98c,0x1bc,DAT_004ae994);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x4000000,DAT_004ae998,DAT_004ae998);
      }
      uVar4 = 0xffffffff;
    }
  }
  return CONCAT44(param_3,uVar4);
}

