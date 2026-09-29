
undefined8
conversate_ui_send_start_request
          (int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  short *psVar1;
  int iVar2;
  int iVar3;
  
  iVar2 = DAT_005b5cc8;
  psVar1 = (short *)FUN_005b43e8();
  if (((*(int *)(iVar2 + 0x84) == -1) || (psVar1 == (short *)0x0)) || (*psVar1 == 0)) {
    APP_PbConversateTxEncodePrepNoteSelect(1,0);
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      param_1 = 0x34;
      param_2 = DAT_005b5ccc;
      FUN_0043d574(3,DAT_005b5cd8,DAT_005b5cd4,DAT_005b5cd0,0x34,DAT_005b5ccc,param_3,param_4);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0xc000000,DAT_005b5cdc,DAT_005b5cdc);
    }
  }
  else {
    iVar3 = *(int *)(iVar2 + 0x84);
    APP_PbConversateTxEncodePrepNoteSelect(0,*(undefined4 *)(psVar1 + iVar3 * 0x44 + 2));
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      param_1 = 0x38;
      param_2 = DAT_005b5ce0;
      FUN_0043d574(3,DAT_005b5cd8,DAT_005b5cd4,DAT_005b5cd0,0x38,DAT_005b5ce0,
                   *(undefined4 *)(psVar1 + iVar3 * 0x44 + 2),iVar3);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0xc800000,PTR_s__conversate_ui_send_start_reques_005b5ce4,
                          PTR_s__conversate_ui_send_start_reques_005b5ce4,
                          *(undefined4 *)(psVar1 + iVar3 * 0x44 + 2));
      param_1 = iVar3;
    }
  }
  return CONCAT44(param_2,param_1);
}

