
undefined8
TPL_Init(byte param_1,undefined4 param_2,undefined *param_3,undefined4 param_4,undefined4 param_5)

{
  int *piVar1;
  int iVar2;
  
  iVar2 = DAT_004b90e8;
  *(byte *)(DAT_004b90e8 + (uint)param_1 * 0x14) = param_1;
  *(undefined4 *)((uint)param_1 * 0x14 + iVar2 + 4) = param_2;
  *(undefined **)((uint)param_1 * 0x14 + iVar2 + 8) = param_3;
  *(undefined4 *)((uint)param_1 * 0x14 + iVar2 + 0xc) = param_4;
  *(undefined4 *)((uint)param_1 * 0x14 + iVar2 + 0x10) = param_5;
  FUN_0043c0e4(DAT_004b90ec,0xe0,0);
  piVar1 = DAT_004b90f0;
  if (*DAT_004b90f0 == 0) {
    iVar2 = osMutexNew(0);
    *piVar1 = iVar2;
    if (*piVar1 == 0) {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        param_2 = 0x62;
        param_3 = DAT_004b90f4;
        FUN_0043d574(1,PTR_s_prot_tran_004b9100,DAT_004b90fc,DAT_004b90f8,0x62,DAT_004b90f4,param_4)
        ;
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x4000000,PTR_s__prot_tran_Failed_to_create__g_S_004b9104,
                            PTR_s__prot_tran_Failed_to_create__g_S_004b9104);
      }
    }
    else {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        param_2 = 100;
        param_3 = PTR_s_Static_send_buffer_mutex_initial_004b9108;
        FUN_0043d574(4,PTR_s_prot_tran_004b9100,DAT_004b90fc,DAT_004b90f8,100,
                     PTR_s_Static_send_buffer_mutex_initial_004b9108,param_4);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x10000000,DAT_004b9608,DAT_004b9608);
      }
    }
  }
  return CONCAT44(param_3,param_2);
}

