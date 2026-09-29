
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

longlong system_close_ui_event_handler
                   (int param_1,undefined4 param_2,uint param_3,undefined4 param_4)

{
  int iVar1;
  uint uVar2;
  
  if (param_1 == 2) {
    uVar2 = param_3;
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      uVar2 = 0x2c9;
      FUN_0043d574(4,DAT_0046b058,DAT_0046b054,PTR_s_system_close_ui_event_handler_0046b0c4,0x2c9,
                   PTR_s_system_close_DISPLAY_STARTUP_0046b0c0);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10000000,PTR_s__system_close_system_close_DISPL_0046b0c8,
                          PTR_s__system_close_system_close_DISPL_0046b0c8);
    }
    *DAT_0046b004 = 0;
    system_close_set_style_00469d24();
    *_DAT_0046b0cc = 0;
    *DAT_0046b00c = 2;
    *_DAT_0046b0d0 = 0;
    *_DAT_0046b0d4 = 0;
    *DAT_0046b010 = 0;
    *_DAT_0046b0d8 = 0;
    system_close_selection_animation_0046a18c(param_4,param_2,param_3);
    *(int *)(_DAT_0046b0e0 + 4) = *_DAT_0046b0dc;
    param_3 = uVar2;
  }
  else if (param_1 == 3) {
    system_close_ReflashEventHandler(param_2,param_3);
  }
  else if ((param_1 != 4) && (param_1 == 5)) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      param_3 = 0x2d9;
      FUN_0043d574(4,DAT_0046b058,DAT_0046b054,PTR_s_system_close_ui_event_handler_0046b0c4,0x2d9,
                   _DAT_0046b0e4);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10000000,_DAT_0046b0e8,_DAT_0046b0e8);
    }
    *DAT_0046b004 = 0;
    if (*_DAT_0046b0dc != 0) {
      FUN_00450500(*_DAT_0046b0dc,0);
    }
    system_close_set_style_00469d24();
    *_DAT_0046b0cc = 0;
    *DAT_0046b00c = 2;
    *_DAT_0046b0d0 = 0;
    *_DAT_0046b0d4 = 0;
    *DAT_0046b010 = 0;
    *_DAT_0046b0d8 = 0;
  }
  return (ulonglong)param_3 << 0x20;
}

