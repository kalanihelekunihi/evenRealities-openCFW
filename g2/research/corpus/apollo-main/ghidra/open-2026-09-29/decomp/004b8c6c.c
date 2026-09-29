
void _rxNextPacketTimeout(undefined1 *param_1)

{
  int iVar1;
  int iVar2;
  undefined2 *puVar3;
  
  iVar1 = FUN_004b8122();
  if ((iVar1 == 0) || (*(char *)(iVar1 + 0x56) == '\0')) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(1,PTR_s_prot_tran_004b9100,DAT_004b90fc,DAT_004b9620,0x103,DAT_004b961c);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_004b9624,DAT_004b9624);
    }
  }
  else {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(2,PTR_s_prot_tran_004b9100,DAT_004b90fc,DAT_004b9620,0x108,DAT_004b9628,*param_1,
                   param_1[1],param_1[2]);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x8c00000,DAT_004b962c,DAT_004b962c,*param_1,param_1[1],param_1[2]);
    }
    puVar3 = (undefined2 *)WsfMsgAlloc(0xf);
    if (puVar3 == (undefined2 *)0x0) {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        FUN_0043d574(1,PTR_s_prot_tran_004b9100,DAT_004b90fc,DAT_004b9620,0x115,DAT_004b9630);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x4000000,DAT_004b99b8,DAT_004b99b8);
      }
    }
    else {
      *(undefined1 *)(puVar3 + 1) = 0xb8;
      *puVar3 = 0;
      *(undefined2 **)(puVar3 + 2) = puVar3 + 6;
      FUN_00439be4(*(undefined4 *)(puVar3 + 2),param_1,3);
      puVar3[4] = 3;
      WsfMsgSend(*(undefined1 *)(iVar1 + 0x56),puVar3);
    }
  }
  return;
}

