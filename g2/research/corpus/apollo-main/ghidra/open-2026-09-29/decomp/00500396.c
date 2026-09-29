
undefined8 CB_RING_BAT_RegisterCallback(int param_1)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 unaff_r5;
  
  if (param_1 == 0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      unaff_r5 = 0x17;
      FUN_0043d574(1,PTR_s_cb_ring_bat_00500408,PTR_s_D__01_workspace_s200_ap510b_iar__00500404,
                   PTR_s_CB_RING_BAT_RegisterCallback_00500400,0x17,
                   PTR_s_Invalid_ring_callback_function_005003fc);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4000000,PTR_s__cb_ring_bat_Invalid_ring_callba_0050040c,
                          PTR_s__cb_ring_bat_Invalid_ring_callba_0050040c);
    }
    uVar2 = 0;
  }
  else {
    uVar2 = CALLBACK_MGR_Register(DAT_005003f8,param_1);
  }
  return CONCAT44(unaff_r5,uVar2);
}

