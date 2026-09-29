
undefined4 _nvdbUpdataSysDt(void)

{
  undefined4 uVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  undefined4 in_r3;
  int iVar5;
  byte abStack_c8 [38];
  short sStack_a2;
  undefined4 uStack_a0;
  undefined1 uStack_9c;
  undefined1 uStack_9b;
  undefined1 uStack_9a;
  undefined4 uStack_1c;
  
  uStack_1c = in_r3;
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    FUN_0043d574(2,DAT_004af890,DAT_004af88c,DAT_004af888,0x42,DAT_004af884);
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0x8000000,DAT_004af894,DAT_004af894);
  }
  iVar2 = DAT_004af880;
  *(undefined1 *)(DAT_004af880 + 0xf) = 0;
  iVar5 = iVar2 + 1;
  SVC_NvdbparsePsn(iVar5);
  iVar3 = SVC_NvdbRead(DAT_004af898,abStack_c8,0xac);
  nvdbSysDtMarkLegacyPsn();
  uVar1 = DAT_004af89c;
  iVar4 = SVC_ReadPSNFromOTP(DAT_004af89c,0);
  if (iVar4 == 0) {
    iVar4 = FUN_0043d0ce();
    if (iVar4 << 0x1e < 0) {
      FUN_0043d574(3,DAT_004af890,DAT_004af88c,DAT_004af888,0x49,DAT_004af8a0,uVar1,iVar5);
    }
    iVar4 = FUN_0043d0ce();
    if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
      compress_log_output(0xc800000,DAT_004af8a4,DAT_004af8a4,uVar1,iVar5);
    }
    FUN_00439be4(iVar5,uVar1,0xe);
    *(undefined1 *)(iVar2 + 0xf) = 0;
  }
  else {
    iVar4 = FUN_0043d0ce();
    if (iVar4 << 0x1e < 0) {
      FUN_0043d574(1,DAT_004af890,DAT_004af88c,DAT_004af888,0x4f,DAT_004af8a8);
    }
    iVar4 = FUN_0043d0ce();
    if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
      compress_log_output(0x4000000,PTR_s__nv_sysDt_read_SN_from_OTP_faile_00759c83_1_004af8ac,
                          PTR_s__nv_sysDt_read_SN_from_OTP_faile_00759c83_1_004af8ac);
    }
  }
  if (0 < iVar3) {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(3,DAT_004af890,DAT_004af88c,DAT_004af888,0x52,PTR_s_version__d__d__004af8b0,
                   abStack_c8[0],2);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0xc800000,PTR_s__nv_sysDt_version__d__d__004af8b4,
                          PTR_s__nv_sysDt_version__d__d__004af8b4,abStack_c8[0],2);
    }
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(3,DAT_004af890,DAT_004af88c,DAT_004af888,0x53,PTR_s_crc_0x_x_0x_x__004af8b8,
                   sStack_a2,*(undefined2 *)(iVar2 + 0x26));
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0xc800000,PTR_s__nv_sysDt_crc_0x_x_0x_x__004af8bc,
                          PTR_s__nv_sysDt_crc_0x_x_0x_x__004af8bc,sStack_a2,
                          *(undefined2 *)(iVar2 + 0x26));
    }
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(3,DAT_004af890,DAT_004af88c,DAT_004af888,0x54,PTR_s_lux_base__d_004af8c0,
                   uStack_a0);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0xc400000,PTR_s__nv_sysDt_lux_base__d_004af8c4,
                          PTR_s__nv_sysDt_lux_base__d_004af8c4,uStack_a0);
    }
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(3,DAT_004af890,DAT_004af88c,DAT_004af888,0x55,
                   PTR_s_canvas_x__d__canvas_y__d_004af8c8,uStack_9c,uStack_9b);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0xc800000,PTR_s__nv_sysDt_canvas_x__d__canvas_y___004af8cc,
                          PTR_s__nv_sysDt_canvas_x__d__canvas_y___004af8cc,uStack_9c,uStack_9b);
    }
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(3,DAT_004af890,DAT_004af88c,DAT_004af888,0x56,DAT_004afbb8,uStack_9a);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0xc400000,DAT_004afca4,DAT_004afca4,uStack_9a);
    }
    if ((sStack_a2 != *(short *)(iVar2 + 0x26)) && (abStack_c8[0] < 2)) {
      SVC_NvdbWriteSysData(0,iVar5);
    }
    return 0;
  }
  SVC_NvdbWriteSysData(0,iVar5);
  return 0;
}

