
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8 FUN_005e6620(undefined1 param_1,undefined4 param_2)

{
  int iVar1;
  byte bVar2;
  
  bVar2 = *(byte *)(_DAT_005e68d8 + 0x277);
  FUN_005ec9c0();
  FUN_005e65f8();
  if (bVar2 == 0) {
    FUN_005e5442(param_1,0);
  }
  else if ((((bVar2 != 2) && (bVar2 != 7)) && (bVar2 != 0xb)) && (bVar2 != 0xc)) {
    FUN_005e57c6(param_1,0);
    bVar2 = 2;
  }
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    param_2 = 0x5ff;
    FUN_0043d574(3,PTR_s_terminal_ui_005e6b90,PTR_s_D__01_workspace_s200_ap510b_iar__005e6b8c,
                 PTR_s_terminal_ui_restore_notification_005e7064,0x5ff,
                 PTR_s_query_notification_dismissed__re_005e7060,bVar2);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0xc400000,PTR_s__terminal_ui_query_notification_d_005e7248,
                        PTR_s__terminal_ui_query_notification_d_005e7248,bVar2);
  }
  return CONCAT44(param_2,bVar2 + 1);
}

