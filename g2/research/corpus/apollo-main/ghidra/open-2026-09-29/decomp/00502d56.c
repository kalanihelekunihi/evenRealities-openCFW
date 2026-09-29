
undefined8 FUN_00502d56(int param_1,char param_2)

{
  undefined *puVar1;
  int iVar2;
  undefined4 unaff_r5;
  undefined *unaff_r6;
  
  if ((param_1 << 0x1d < 0) && (param_2 == '\x01')) {
    DRV_BuzzerPlay(3);
    iVar2 = FUN_0043d0ce();
    puVar1 = PTR_s_EVENT_SLIDER_SINGLE_CLICK_00503230;
    if (iVar2 << 0x1e < 0) {
      unaff_r5 = 0x25;
      FUN_0043d574(4,PTR_s_touch_ges_0050323c,PTR_s_D__01_workspace_s200_ap510b_iar__00503238,
                   PTR_s_production_test_gesture_process_00503234);
      unaff_r6 = puVar1;
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x10000000,PTR_s__touch_ges_EVENT_SLIDER_SINGLE_C_00503240,
                          PTR_s__touch_ges_EVENT_SLIDER_SINGLE_C_00503240);
    }
  }
  return CONCAT44(unaff_r6,unaff_r5);
}

