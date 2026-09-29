
void TPL_RxPacketTimeoutHandler
               (char *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  iVar3 = 0;
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    FUN_0043d574(2,PTR_s_prot_tran_004b9100,DAT_004b90fc,DAT_004b9638,0x11f,DAT_004b9634,*param_1,
                 param_1[1],param_1[2],param_4);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0x8c00000,DAT_004b963c,DAT_004b963c,*param_1,param_1[1],param_1[2]);
  }
  iVar1 = 0;
  do {
    if (3 < iVar1) {
LAB_004b8e96:
      if (iVar3 == 0) {
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          FUN_0043d574(2,PTR_s_prot_tran_004b9100,DAT_004b90fc,DAT_004b9638,0x134,DAT_004b99d0);
        }
        iVar1 = FUN_0043d0ce();
        if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
          compress_log_output(0x8000000,DAT_004b99d4,DAT_004b99d4);
        }
      }
      else if (*(char *)(iVar3 + 0x30) == '\0') {
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          FUN_0043d574(2,PTR_s_prot_tran_004b9100,DAT_004b90fc,DAT_004b9638,0x131,DAT_004b99c8);
        }
        iVar1 = FUN_0043d0ce();
        if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
          compress_log_output(0x8000000,DAT_004b99cc,DAT_004b99cc);
        }
      }
      else {
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          FUN_0043d574(2,PTR_s_prot_tran_004b9100,DAT_004b90fc,DAT_004b9638,0x12e,DAT_004b99c0);
        }
        iVar1 = FUN_0043d0ce();
        if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
          compress_log_output(0x8000000,DAT_004b99c4,DAT_004b99c4);
        }
        tpl_context_free_004b8ba2(iVar3);
      }
      _tplReponse(param_1[2],param_1[1],*param_1,3);
      return;
    }
    if ((((*(char *)(iVar1 * 0x38 + DAT_004b90ec + 0x30) != '\0') &&
         (*(char *)(DAT_004b90ec + iVar1 * 0x38) == *param_1)) &&
        (*(char *)(iVar1 * 0x38 + DAT_004b90ec + 1) == param_1[1])) &&
       (*(char *)(iVar1 * 0x38 + DAT_004b90ec + 0x33) == param_1[2])) {
      iVar3 = DAT_004b90ec + iVar1 * 0x38;
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(2,PTR_s_prot_tran_004b9100,DAT_004b90fc,DAT_004b9638,0x127,DAT_004b9980,iVar1);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x8400000,DAT_004b99bc,DAT_004b99bc,iVar1);
      }
      goto LAB_004b8e96;
    }
    iVar1 = iVar1 + 1;
  } while( true );
}

