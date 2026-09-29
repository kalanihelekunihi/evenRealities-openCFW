
undefined8
als_function_32(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  uint *puVar1;
  int iVar2;
  uint uVar3;
  undefined4 uVar4;
  undefined4 local_18;
  undefined4 local_14;
  
  iVar2 = settings_get_config();
  local_18 = param_3;
  local_14 = param_4;
  if (*(int *)(iVar2 + 4) == 0) {
    uVar3 = service_settings_auto_brightness();
    uVar4 = 5;
    *DAT_004ae8dc = uVar3;
    puVar1 = DAT_004ae8d4;
    if (*DAT_004ae8d4 == uVar3) {
      *DAT_004ae99c = 3;
      hub_timer_start(1000);
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        local_14 = DAT_004ae9cc;
        local_18 = 0x21b;
        FUN_0043d574(3,DAT_004ae4dc,DAT_004ae4d8,DAT_004ae9c4);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0xc000000,DAT_004ae9d0);
      }
      als_function_23(uVar3,1);
    }
    else {
      if (uVar3 < *DAT_004ae8d4) {
        iVar2 = als_function_24();
        if (iVar2 != 0) {
          uVar4 = 2;
        }
        uVar4 = als_function_30(*puVar1,uVar3,uVar4);
      }
      else {
        uVar4 = als_function_30(*DAT_004ae8d4,uVar3,2);
      }
      als_function_23(uVar4,0);
    }
  }
  else {
    *DAT_004ae99c = 3;
    hub_timer_start(1000);
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      local_14 = DAT_004ae9c0;
      local_18 = 0x210;
      FUN_0043d574(3,DAT_004ae4dc,DAT_004ae4d8,DAT_004ae9c4);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0xc000000,DAT_004ae9c8,DAT_004ae9c8);
    }
  }
  return CONCAT44(local_14,local_18);
}

