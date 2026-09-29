
void INP_SetTerminalMode(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  short sVar3;
  short asStack_18 [2];
  undefined4 uStack_14;
  
  uStack_14 = param_4;
  FUN_0043c0e4(asStack_18,2,0);
  if (param_1 != 0) {
    if (*(int *)(param_1 + 8) == 0) {
      sVar3 = 1000;
    }
    else {
      sVar3 = 500;
    }
    iVar1 = UX_GetSelfRingStatus();
    if (iVar1 != 0) {
      FUN_00472362(sVar3);
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        FUN_0043d574(3,PTR_s_thread_input_005134c8,DAT_005134c4,PTR_s_INP_SetTerminalMode_00513530,
                     0x127,PTR_s_set_ring_touch_algo_report_time__0051352c,sVar3);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0xc400000,PTR_s__thread_input_set_ring_touch_alg_00513534,
                            PTR_s__thread_input_set_ring_touch_alg_00513534,sVar3);
      }
    }
    iVar1 = FUN_0055b92a(asStack_18);
    if (iVar1 == 0) {
      if (asStack_18[0] == sVar3) {
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          FUN_0043d574(3,PTR_s_thread_input_005134c8,DAT_005134c4,PTR_s_INP_SetTerminalMode_00513530
                       ,0x12e,PTR_s_touch_long_press_threshold_uncha_00513548,
                       *(undefined4 *)(param_1 + 8),asStack_18[0]);
        }
        iVar1 = FUN_0043d0ce();
        if ((-1 < iVar1 << 0x1f) && (iVar1 = FUN_0043d0ce(), -1 < iVar1 << 0x1d)) {
          return;
        }
        compress_log_output(0xc800000,PTR_s__thread_input_touch_long_press_t_0051354c,
                            PTR_s__thread_input_touch_long_press_t_0051354c,
                            *(undefined4 *)(param_1 + 8),asStack_18[0]);
        return;
      }
    }
    else {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(2,PTR_s_thread_input_005134c8,DAT_005134c4,PTR_s_INP_SetTerminalMode_00513530,
                     300,PTR_s_read_touch_gesture_cfg_failed____00513538,iVar1);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x8400000,PTR_s__thread_input_read_touch_gesture_0051353c,
                            PTR_s__thread_input_read_touch_gesture_0051353c,iVar1);
      }
    }
    asStack_18[0] = sVar3;
    iVar1 = FUN_0055b840(asStack_18);
    if (iVar1 == 0) {
      osDelay(100);
      iVar1 = FUN_0055b92a(asStack_18);
      if (iVar1 == 0) {
        if (asStack_18[0] == sVar3) {
          iVar1 = FUN_0043d0ce();
          if (iVar1 << 0x1e < 0) {
            FUN_0043d574(3,PTR_s_thread_input_005134c8,DAT_005134c4,
                         PTR_s_INP_SetTerminalMode_00513530,0x146,
                         PTR_s_touch_long_press_threshold_set_b_00513560,
                         *(undefined4 *)(param_1 + 8),asStack_18[0]);
          }
          iVar1 = FUN_0043d0ce();
          if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
            compress_log_output(0xc800000,PTR_s__thread_input_touch_long_press_t_00513564,
                                PTR_s__thread_input_touch_long_press_t_00513564,
                                *(undefined4 *)(param_1 + 8),asStack_18[0]);
          }
        }
        else {
          iVar1 = FUN_0043d0ce();
          if (iVar1 << 0x1e < 0) {
            FUN_0043d574(1,PTR_s_thread_input_005134c8,DAT_005134c4,
                         PTR_s_INP_SetTerminalMode_00513530,0x142,
                         PTR_s_touch_gesture_cfg_verify_failed__00513558,sVar3,asStack_18[0]);
          }
          iVar1 = FUN_0043d0ce();
          if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
            compress_log_output(0x4800000,PTR_s__thread_input_touch_gesture_cfg_v_0051355c,
                                PTR_s__thread_input_touch_gesture_cfg_v_0051355c,sVar3,asStack_18[0]
                               );
          }
        }
      }
      else {
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          FUN_0043d574(2,PTR_s_thread_input_005134c8,DAT_005134c4,PTR_s_INP_SetTerminalMode_00513530
                       ,0x13e,PTR_s_readback_touch_gesture_cfg_faile_00513550,iVar1);
        }
        iVar2 = FUN_0043d0ce();
        if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
          compress_log_output(0x8400000,PTR_s__thread_input_readback_touch_ges_00513554,
                              PTR_s__thread_input_readback_touch_ges_00513554,iVar1);
        }
      }
    }
    else {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(1,PTR_s_thread_input_005134c8,DAT_005134c4,PTR_s_INP_SetTerminalMode_00513530,
                     0x136,PTR_s_write_touch_gesture_cfg_failed____00513540,iVar1,sVar3);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x4800000,PTR_s__thread_input_write_touch_gestur_00513544,
                            PTR_s__thread_input_write_touch_gestur_00513544,iVar1,sVar3);
      }
    }
  }
  return;
}

