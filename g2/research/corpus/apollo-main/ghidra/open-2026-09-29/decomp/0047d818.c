
undefined8 RPC_SyncRingStatusWithPeer(void)

{
  undefined *puVar1;
  int iVar2;
  undefined4 unaff_r5;
  undefined *unaff_r6;
  
  iVar2 = APP_MasterRingMacIsSet();
  if (iVar2 == 0) {
    iVar2 = FUN_0043d0ce();
    puVar1 = PTR_s_RPC_SyncRingStatusWithPeer_skip__0047d9b4;
    if (iVar2 << 0x1e < 0) {
      unaff_r5 = 0xfd;
      FUN_0043d574(4,PTR_s_ux_setting_0047d918,PTR_s_D__01_workspace_s200_ap510b_iar__0047d914,
                   PTR_s_RPC_SyncRingStatusWithPeer_0047d9b8);
      unaff_r6 = puVar1;
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x10000000,PTR_s__ux_setting_RPC_SyncRingStatusWi_0047d9bc,
                          PTR_s__ux_setting_RPC_SyncRingStatusWi_0047d9bc);
    }
  }
  else {
    iVar2 = central_is_ring_owner_side_004a2914();
    if (iVar2 == 0) {
      UX_SendRingQueryToPeer();
    }
    else {
      UX_SendRingStatusToPeer();
    }
  }
  return CONCAT44(unaff_r6,unaff_r5);
}

