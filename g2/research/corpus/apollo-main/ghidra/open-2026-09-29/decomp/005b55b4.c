
undefined4 FUN_005b55b4(void)

{
  char cVar1;
  int iVar2;
  undefined4 uVar3;
  
  cVar1 = FUN_005b16d0();
  if ((cVar1 == '\0') || (cVar1 == '\x06')) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      uVar3 = FUN_005b16dc(cVar1);
      FUN_0043d574(2,PTR_s_conversate_005b56d4,PTR_s_D__01_workspace_s200_ap510b_iar__005b56d0,
                   PTR_s_conversate_action_heartbeat_005b5718,0x198,
                   PTR_s_recv_heartbeat__conversate_ui_st_005b5714,cVar1,uVar3);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      uVar3 = FUN_005b16dc(cVar1);
      compress_log_output(0x8800000,PTR_s__conversate_recv_heartbeat__conv_005b571c,
                          PTR_s__conversate_recv_heartbeat__conv_005b571c,cVar1,uVar3);
    }
    uVar3 = 0xffffffff;
  }
  else {
    uVar3 = 0;
  }
  return uVar3;
}

