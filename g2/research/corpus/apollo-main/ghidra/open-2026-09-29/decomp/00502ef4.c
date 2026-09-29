
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_00502ef4(void)

{
  undefined2 uVar1;
  int iVar2;
  undefined4 uVar3;
  uint uVar4;
  uint uStack_60;
  undefined *puStack_5c;
  uint uStack_58;
  uint uStack_54;
  uint uStack_50;
  uint uStack_4c;
  uint uStack_48;
  uint uStack_44;
  uint uStack_40;
  uint uStack_3c;
  undefined4 uStack_38;
  ushort uStack_34;
  ushort uStack_32;
  ushort uStack_30;
  ushort uStack_2e;
  byte bStack_2c;
  byte bStack_2b;
  byte bStack_2a;
  byte bStack_29;
  undefined1 auStack_28 [2];
  undefined1 auStack_26 [2];
  undefined1 auStack_24 [2];
  undefined1 auStack_22 [6];
  
  FUN_0043c0e4(&bStack_2c,0x10,0);
  FUN_0055b676(&bStack_2c);
  if (*_DAT_00503270 != '\0') {
    Thread_MsgStreamingNotifyByBle(&bStack_2c,0x10);
  }
  uVar4 = (uint)bStack_2b;
  FUN_00439be4(&uStack_2e,auStack_28,2);
  FUN_00439be4(&uStack_30,auStack_26,2);
  FUN_00439be4(&uStack_32,auStack_24,2);
  FUN_00439be4(&uStack_34,auStack_22,2);
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    uStack_38 = FUN_00502dc2(bStack_2b);
    uStack_3c = (uint)bStack_2b;
    uStack_40 = (uint)bStack_29;
    uStack_44 = (uint)bStack_2a;
    uStack_48 = (uint)uStack_32;
    uStack_4c = (uint)uStack_30;
    uStack_50 = (uint)uStack_34;
    uStack_54 = (uint)uStack_2e;
    uStack_58 = (uint)bStack_2c;
    puStack_5c = PTR_s_prox__d__bsln__5d__kv_bsln__5d__r_00503274;
    uStack_60 = 0x70;
    FUN_0043d574(3,PTR_s_touch_ges_0050323c,PTR_s_D__01_workspace_s200_ap510b_iar__00503238,
                 PTR_s_process_gesture_data_00503278);
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    uStack_44 = FUN_00502dc2(bStack_2b);
    uStack_48 = (uint)bStack_2b;
    uStack_4c = (uint)bStack_29;
    uStack_50 = (uint)bStack_2a;
    uStack_54 = (uint)uStack_32;
    uStack_58 = (uint)uStack_30;
    puStack_5c = (undefined *)(uint)uStack_34;
    uStack_60 = (uint)uStack_2e;
    compress_log_output(0xe400000,PTR_s__touch_ges_prox__d__bsln__5d__kv_0050327c,
                        PTR_s__touch_ges_prox__d__bsln__5d__kv_0050327c,bStack_2c);
  }
  if (bStack_2c != 0) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      uStack_58 = FUN_00502db6(bStack_2c);
      uStack_54 = (uint)bStack_2c;
      puStack_5c = PTR_s_prox__s__u__00503280;
      uStack_60 = 0x74;
      FUN_0043d574(3,PTR_s_touch_ges_0050323c,PTR_s_D__01_workspace_s200_ap510b_iar__00503238,
                   PTR_s_process_gesture_data_00503278);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      uVar3 = FUN_00502db6(bStack_2c);
      uStack_60 = (uint)bStack_2c;
      compress_log_output(0xc800000,PTR_s__touch_ges_prox__s__u__00503284,
                          PTR_s__touch_ges_prox__s__u__00503284,uVar3);
    }
    *DAT_00503244 = bStack_2c;
    FUN_0049eae2(3,bStack_2c);
  }
  if (bStack_2b == 0) {
    return;
  }
  iVar2 = productModeGet();
  if (iVar2 == 1) {
    FUN_00502d56(bStack_2b,bStack_2a);
    return;
  }
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    uStack_54 = FUN_00502dc2(bStack_2b);
    uStack_4c = (uint)bStack_29;
    uStack_50 = (uint)bStack_2a;
    uStack_58 = (uint)bStack_2b;
    puStack_5c = PTR_s_slider_mask___0x_02x__s___diffX___00503288;
    uStack_60 = 0x82;
    FUN_0043d574(4,PTR_s_touch_ges_0050323c,PTR_s_D__01_workspace_s200_ap510b_iar__00503238,
                 PTR_s_process_gesture_data_00503278);
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    uStack_60 = FUN_00502dc2(bStack_2b);
    uStack_58 = (uint)bStack_29;
    puStack_5c = (undefined *)(uint)bStack_2a;
    compress_log_output(0x11000000,PTR_s__touch_ges_slider_mask___0x_02x__0050328c,
                        PTR_s__touch_ges_slider_mask___0x_02x__0050328c,bStack_2b);
  }
  if ((int)(uVar4 << 0x18) < 0) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      puStack_5c = PTR_s_SLIDER_EVENT_ERROR__reset_touch_00503290;
      uStack_60 = 0x85;
      FUN_0043d574(1,PTR_s_touch_ges_0050323c,PTR_s_D__01_workspace_s200_ap510b_iar__00503238,
                   PTR_s_process_gesture_data_00503278);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4000000,PTR_s__touch_ges_SLIDER_EVENT_ERROR__r_00503294,
                          PTR_s__touch_ges_SLIDER_EVENT_ERROR__r_00503294);
    }
    FUN_0055b64a();
    uStack_60 = 0;
    FUN_0055b6dc(&uStack_60);
    return;
  }
  if ((int)(uVar4 << 0x1f) < 0) {
    uVar1 = func_0x004c5874();
    FUN_004c5916(uVar1,0xd,0,0);
  }
  if ((int)(uVar4 << 0x1d) < 0) {
    if (bStack_2a < 2) {
      uVar1 = func_0x004c5874();
      FUN_004c5916(uVar1,0,0,0);
    }
    else if (9 < bStack_2a) {
      uVar1 = func_0x004c5874();
      FUN_004c5916(uVar1,0x1010,0,0);
    }
  }
  if ((int)(uVar4 << 0x1c) < 0) {
    uVar1 = func_0x004c5874();
    FUN_004c5916(uVar1,1,0,0);
  }
  if ((int)(uVar4 << 0x1b) < 0) {
    uVar1 = func_0x004c5874();
    FUN_004c5916(uVar1,3,0,0);
  }
  if ((int)(uVar4 << 0x1a) < 0) {
    uVar1 = func_0x004c5874();
    FUN_004c5916(uVar1,5,bStack_2a,bStack_29);
  }
  if ((int)(uVar4 << 0x19) < 0) {
    uVar1 = func_0x004c5874();
    FUN_004c5916(uVar1,4,bStack_2a,bStack_29);
  }
  if (-1 < (int)(uVar4 << 0x1e)) {
    return;
  }
  uVar1 = func_0x004c5874();
  FUN_004c5916(uVar1,0xe,0,0);
  return;
}

