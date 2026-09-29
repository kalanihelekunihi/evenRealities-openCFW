
void FUN_00472988(int param_1,undefined2 param_2)

{
  char cVar1;
  undefined4 uVar2;
  int iVar3;
  undefined1 local_10;
  undefined1 local_f;
  undefined1 local_e;
  undefined1 local_d;
  undefined1 local_c;
  undefined1 local_b;
  
  cVar1 = *(char *)(param_1 + 2);
  if (cVar1 == 'a') {
    FUN_0047269e(param_1,param_2);
  }
  else if (cVar1 == -0x7b) {
    fw_event_loop_remove_delayed(DAT_00472c40);
    fw_event_loop_remove_delayed(DAT_00472c44);
    iVar3 = central_is_ring_owner_side_004a2914();
    if (iVar3 == 0) {
      PB_TxEncodeNotifyRingConnectInfo(0);
    }
    else {
      APP_MasterPublishRingLinkReady();
    }
    FUN_0047263c(param_1);
  }
  else if (cVar1 == -0x76) {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(3,DAT_00472bbc,DAT_00472bb8,DAT_00472c4c,0x272,DAT_00472c48);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0xc000000,DAT_00472c50,DAT_00472c50);
    }
  }
  else if (cVar1 == -0x75) {
    FUN_004727aa(param_1,param_2);
  }
  else if (cVar1 == -0x74) {
    FUN_004728b2(param_1);
  }
  else if (cVar1 == -0x6c) {
    if ((*(char *)(param_1 + 4) == ' ') || (*(char *)(param_1 + 4) == '@')) {
      if (*(char *)(param_1 + 4) == ' ') {
        iVar3 = FUN_0043d0ce();
        if (iVar3 << 0x1e < 0) {
          FUN_0043d574(1,DAT_00472bbc,DAT_00472bb8,DAT_00472c4c,0x282,DAT_00472c54);
        }
        iVar3 = FUN_0043d0ce();
        if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
          compress_log_output(0x4000000,DAT_00472c58,DAT_00472c58);
        }
      }
      else {
        iVar3 = FUN_0043d0ce();
        if (iVar3 << 0x1e < 0) {
          FUN_0043d574(1,DAT_00472bbc,DAT_00472bb8,DAT_00472c4c,0x286,DAT_00472c5c);
        }
        iVar3 = FUN_0043d0ce();
        if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
          compress_log_output(0x4000000,DAT_00472c60,DAT_00472c60);
        }
      }
      uVar2 = DAT_00472c64;
      fw_event_loop_remove_delayed(DAT_00472c64);
      fw_event_loop_push_delayed(uVar2,0,100);
      uVar2 = DAT_00472c68;
      fw_event_loop_remove_delayed(DAT_00472c68);
      fw_event_loop_push_delayed(uVar2,0,500);
    }
    else {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        FUN_0043d574(4,DAT_00472bbc,DAT_00472bb8,DAT_00472c4c,0x28f,DAT_00472c6c);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x10000000,DAT_00472c70,DAT_00472c70);
      }
    }
  }
  else if (cVar1 == -0x6a) {
    FUN_0043c0e4(&local_10,6,0);
    target_addr_name_copy_004a2190(&local_10,0);
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(2,DAT_00472bbc,DAT_00472bb8,DAT_00472c4c,0x2aa,DAT_00472c74,local_b,local_c,
                   local_d,local_e,local_f,local_10);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x9800000,DAT_00472c78,DAT_00472c78,local_b,local_c,local_d,local_e,
                          local_f,local_10);
    }
    APP_MasterCleanupRingUnpair(&local_10);
  }
  return;
}

