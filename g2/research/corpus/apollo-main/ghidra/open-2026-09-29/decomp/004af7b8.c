
void SVC_NvdbReadSysData(undefined1 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4
                        )

{
  undefined4 uVar1;
  int iVar2;
  int iVar3;
  
  iVar3 = DAT_004af880;
  SVC_NvdbRead(DAT_004af898,DAT_004af880,0xac);
  nvdbSysDtMarkLegacyPsn();
  uVar1 = DAT_004af89c;
  iVar2 = SVC_ReadPSNFromOTP(DAT_004af89c,0);
  if (iVar2 == 0) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(3,DAT_004af890,DAT_004af88c,PTR_s_SVC_NvdbReadSysData_004b0310,0x137,DAT_004af8a0
                   ,uVar1,iVar3 + 1,param_4);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0xc800000,DAT_004af8a4,DAT_004af8a4,uVar1,iVar3 + 1);
    }
    FUN_00439be4(iVar3 + 1,uVar1,0xe);
    *(undefined1 *)(iVar3 + 0xf) = 0;
  }
  else {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(1,DAT_004af890,DAT_004af88c,PTR_s_SVC_NvdbReadSysData_004b0310,0x13d,DAT_004af8a8
                  );
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x4000000,PTR_s__nv_sysDt_read_SN_from_OTP_faile_00759c83_1_004af8ac,
                          PTR_s__nv_sysDt_read_SN_from_OTP_faile_00759c83_1_004af8ac);
    }
  }
  SVC_NvdbGetSysData(param_1);
  return;
}

