
void als_function_33(void)

{
  undefined4 *puVar1;
  int *piVar2;
  undefined4 uVar3;
  undefined4 uVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  
  uVar3 = als_function_27();
  *DAT_004ae734 = uVar3;
  als_function_04(uVar3);
  als_function_05(uVar3);
  puVar1 = DAT_004ae738;
  uVar4 = als_function_10();
  *puVar1 = uVar4;
  als_function_11(*puVar1);
  iVar5 = service_settings_auto_brightness();
  *DAT_004ae8dc = iVar5;
  iVar6 = FUN_0043d0ce();
  if (iVar6 << 0x1e < 0) {
    FUN_0043d574(3,DAT_004ae9e0,DAT_004ae9dc,DAT_004ae9d8,0x23f,DAT_004ae9d4,uVar3,*puVar1,
                 *DAT_004ae8d4,iVar5,*DAT_004ae810);
  }
  iVar6 = FUN_0043d0ce();
  if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
    compress_log_output(0xd400000,DAT_004ae9e4,DAT_004ae9e4,uVar3,*puVar1,*DAT_004ae8d4,iVar5,
                        *DAT_004ae810);
  }
  iVar6 = settings_get_config();
  if (*(int *)(iVar6 + 4) != 0) {
    iVar6 = service_time_current_epoch_get(0);
    iVar7 = als_function_12();
    if ((iVar7 != 1) &&
       (iVar7 = settings_get_config(), (uint)(iVar6 - *(int *)(iVar7 + 4)) < 0xa8c1)) {
      iVar5 = FUN_0043d0ce();
      if (iVar5 << 0x1e < 0) {
        FUN_0043d574(3,DAT_004ae9e0,DAT_004ae9dc,DAT_004ae9d8,0x249,DAT_004ae9f0);
      }
      iVar5 = FUN_0043d0ce();
      if ((-1 < iVar5 << 0x1f) && (iVar5 = FUN_0043d0ce(), -1 < iVar5 << 0x1d)) {
        return;
      }
      compress_log_output(0xc000000,DAT_004ae9f4,DAT_004ae9f4);
      return;
    }
    iVar6 = settings_get_config();
    *(undefined4 *)(iVar6 + 4) = 0;
    iVar6 = FUN_0043d0ce();
    if (iVar6 << 0x1e < 0) {
      FUN_0043d574(3,DAT_004ae9e0,DAT_004ae9dc,DAT_004ae9d8,0x247,DAT_004ae9e8);
    }
    iVar6 = FUN_0043d0ce();
    if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
      compress_log_output(0xc000000,DAT_004ae9ec);
    }
  }
  piVar2 = DAT_004ae8d4;
  if (*DAT_004ae8d4 != iVar5) {
    *DAT_004ae99c = 2;
    hub_timer_start(200);
    iVar6 = FUN_0043d0ce();
    if (iVar6 << 0x1e < 0) {
      FUN_0043d574(3,DAT_004ae9e0,DAT_004ae9dc,DAT_004ae9d8,0x254,DAT_004ae9f8,iVar5,*piVar2);
    }
    iVar6 = FUN_0043d0ce();
    if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
      compress_log_output(0xc800000,DAT_004ae9fc,DAT_004ae9fc,iVar5,*piVar2);
    }
  }
  return;
}

