
void FUN_0049c2b0(undefined4 param_1,byte *param_2,undefined4 param_3,undefined4 param_4)

{
  byte bVar1;
  char cVar2;
  int iVar3;
  undefined4 uVar4;
  uint uStack_14;
  undefined4 uStack_10;
  
  uStack_10 = param_4;
  if (param_2 == (byte *)0x0) {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(1,PTR_s_dashboard_0049cb30,DAT_0049cb2c,
                   PTR_s_dashboard_msg_count_callback_0049cd28,0xb5,
                   PTR_s_dashboard_msg_count_callback__da_0049cd24);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x4000000,PTR_s__dashboard_dashboard_msg_count_c_0049cd2c);
    }
  }
  else {
    bVar1 = *param_2;
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      uStack_14 = (uint)bVar1;
      FUN_0043d574(4,PTR_s_dashboard_0049cb30,DAT_0049cb2c,
                   PTR_s_dashboard_msg_count_callback_0049cd28,0xba,
                   PTR_s_dashboard_msg_count_callback__ev_0049cd30,param_1);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x10800000,PTR_s__dashboard_dashboard_msg_count_c_0049cd34,
                          PTR_s__dashboard_dashboard_msg_count_c_0049cd34,param_1,bVar1);
    }
    cVar2 = FUN_0045a570();
    if (((cVar2 == '\x01') && (iVar3 = FUN_00443484(), iVar3 == 1)) &&
       (iVar3 = FUN_004434d0(1), iVar3 == 1)) {
      FUN_0049c146(bVar1);
      uStack_14 = CONCAT31(uStack_14._1_3_,*PTR_DAT_0049cd38);
      uVar4 = FUN_00464bb2(1,&uStack_14,1,0);
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        FUN_0043d574(4,PTR_s_dashboard_0049cb30,DAT_0049cb2c,
                     PTR_s_dashboard_msg_count_callback_0049cd28,0xc4,DAT_0049cd3c,uVar4);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x10400000,DAT_0049cd40,DAT_0049cd40,uVar4);
      }
    }
  }
  return;
}

