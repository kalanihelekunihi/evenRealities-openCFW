
undefined4 SVC_WritePSNToOTP(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  int local_40;
  undefined1 auStack_3c [16];
  undefined4 local_2c [4];
  undefined4 uStack_1c;
  
  uStack_1c = param_4;
  FUN_0043c0e4(local_2c,0x10,0);
  FUN_0043c0e4(auStack_3c,0xf,0);
  local_40 = -1;
  if (param_1 == 0) {
    iVar1 = FUN_0043d0ce(0);
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(1,PTR_s_nv_sysDt_004b0320,DAT_004b031c,DAT_004b03a0,0x24b,DAT_004b039c);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_004b03a4,DAT_004b03a4);
    }
    uVar2 = 0xffffffff;
  }
  else {
    iVar1 = FUN_0044b610(param_1,&DAT_004b030c,2);
    if (((((iVar1 == 0) && (iVar1 = FUN_005137b8(*(undefined1 *)(param_1 + 0xd)), iVar1 != 0)) &&
         (iVar1 = FUN_005137b8(*(undefined1 *)(param_1 + 0xc)), iVar1 != 0)) &&
        ((iVar1 = FUN_005137b8(*(undefined1 *)(param_1 + 0xb)), iVar1 != 0 &&
         (iVar1 = FUN_005137b8(*(undefined1 *)(param_1 + 10)), iVar1 != 0)))) &&
       ((iVar1 = FUN_005137b8(*(undefined1 *)(param_1 + 9)), iVar1 != 0 &&
        (iVar1 = FUN_005137b8(*(undefined1 *)(param_1 + 8)), iVar1 != 0)))) {
      iVar1 = SVC_ReadPSNFromOTP(auStack_3c,&local_40);
      if (iVar1 == 0) {
        iVar1 = FUN_0044b610(auStack_3c,param_1,0xe);
        if (iVar1 == 0) {
          iVar1 = FUN_0043d0ce();
          if (iVar1 << 0x1e < 0) {
            FUN_0043d574(3,PTR_s_nv_sysDt_004b0320,DAT_004b031c,DAT_004b03a0,0x266,DAT_004b03b0,
                         local_40,param_1);
          }
          iVar1 = FUN_0043d0ce();
          if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
            compress_log_output(0xc800000,DAT_004b03b4,DAT_004b03b4,local_40,param_1);
          }
          return 0;
        }
        iVar4 = local_40 + 1;
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          FUN_0043d574(3,PTR_s_nv_sysDt_004b0320,DAT_004b031c,DAT_004b03a0,0x26e,DAT_004b03b8,
                       local_40,auStack_3c,param_1,iVar4);
        }
        iVar1 = FUN_0043d0ce();
        if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
          compress_log_output(0xd000000,DAT_004b03bc,DAT_004b03bc,local_40,auStack_3c,param_1,iVar4)
          ;
        }
      }
      else {
        iVar4 = 0;
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          FUN_0043d574(3,PTR_s_nv_sysDt_004b0320,DAT_004b031c,DAT_004b03a0,0x275,DAT_004b03c0);
        }
        iVar1 = FUN_0043d0ce();
        if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
          compress_log_output(0xc000000,DAT_004b03c4,DAT_004b03c4);
        }
      }
      if (iVar4 < 8) {
        iVar1 = iVar4 * 0x10 + 0x340;
        FUN_0047f5b8(0x1d);
        FUN_0047f5b8(0x17);
        osDelay(1);
        FUN_0043c0e4(local_2c,0x10,0);
        FUN_00439be4(local_2c,param_1,0xe);
        for (iVar5 = 0; iVar5 < 4; iVar5 = iVar5 + 1) {
          iVar3 = FUN_00513850(iVar1 + iVar5 * 4,local_2c[iVar5]);
          if (iVar3 != 0) {
            iVar4 = FUN_0043d0ce();
            if (iVar4 << 0x1e < 0) {
              FUN_0043d574(1,PTR_s_nv_sysDt_004b0320,DAT_004b031c,DAT_004b03a0,0x294,DAT_004b03d0,
                           iVar1 + iVar5 * 4,iVar3);
            }
            iVar4 = FUN_0043d0ce();
            if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
              compress_log_output(0x4800000,DAT_004b03d4,DAT_004b03d4,iVar1 + iVar5 * 4,iVar3);
            }
            FUN_0047f7ae(0x17);
            FUN_0047f7ae(0x1d);
            return 0xffffffff;
          }
        }
        iVar5 = FUN_0043d0ce();
        if (iVar5 << 0x1e < 0) {
          FUN_0043d574(3,PTR_s_nv_sysDt_004b0320,DAT_004b031c,DAT_004b03a0,0x2a0,DAT_004b03d8,iVar4,
                       iVar1,param_1);
        }
        iVar5 = FUN_0043d0ce();
        if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
          compress_log_output(0xcc00000,DAT_004b03dc,DAT_004b03dc,iVar4,iVar1,param_1);
        }
        FUN_0047f7ae(0x17);
        FUN_0047f7ae(0x1d);
        uVar2 = 0;
      }
      else {
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          FUN_0043d574(1,PTR_s_nv_sysDt_004b0320,DAT_004b031c,DAT_004b03a0,0x27b,DAT_004b03c8);
        }
        iVar1 = FUN_0043d0ce();
        if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
          compress_log_output(0x4000000,DAT_004b03cc,DAT_004b03cc);
        }
        uVar2 = 0xffffffff;
      }
    }
    else {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        FUN_0043d574(1,PTR_s_nv_sysDt_004b0320,DAT_004b031c,DAT_004b03a0,600,DAT_004b03a8,param_1);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x4400000,DAT_004b03ac,DAT_004b03ac,param_1);
      }
      uVar2 = 0xffffffff;
    }
  }
  return uVar2;
}

