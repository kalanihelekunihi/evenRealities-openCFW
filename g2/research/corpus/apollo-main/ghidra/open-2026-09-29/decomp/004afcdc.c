
undefined4 SVC_ReadPSNFromOTP(int param_1,int *param_2,undefined4 param_3,undefined4 param_4)

{
  bool bVar1;
  int iVar2;
  int iVar3;
  undefined4 uVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  undefined1 auStack_4c [8];
  undefined1 local_44;
  undefined1 local_43;
  undefined1 local_42;
  undefined1 local_41;
  undefined1 local_40;
  undefined1 local_3f;
  undefined1 local_3e;
  int local_3c;
  undefined1 auStack_38 [16];
  undefined4 uStack_28;
  
  local_3c = 0x340;
  uStack_28 = param_4;
  FUN_0043c0e4(auStack_38,0x10,0);
  FUN_0043c0e4(auStack_4c,0xf,0);
  iVar5 = -1;
  FUN_0047f5b8(0x1d);
  FUN_0047f5b8(0x17);
  osDelay(1);
  for (iVar6 = 0; iVar6 < 8; iVar6 = iVar6 + 1) {
    iVar7 = local_3c + iVar6 * 0x10;
    bVar1 = true;
    FUN_0043c0e4(auStack_38,0x10,0);
    for (iVar8 = 0; iVar8 < 4; iVar8 = iVar8 + 1) {
      iVar2 = FUN_0051381a(iVar7 + iVar8 * 4,auStack_38 + iVar8 * 4);
      if (iVar2 != 0) {
        iVar3 = FUN_0043d0ce();
        if (iVar3 << 0x1e < 0) {
          FUN_0043d574(3,PTR_s_nv_sysDt_004b0320,DAT_004b031c,DAT_004b037c,0x203,DAT_004b0384,iVar6,
                       iVar7 + iVar8 * 4,iVar2);
        }
        iVar3 = FUN_0043d0ce();
        if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
          compress_log_output(0xcc00000,DAT_004b0388,DAT_004b0388,iVar6,iVar7 + iVar8 * 4,iVar2);
        }
        bVar1 = false;
        break;
      }
    }
    if (!bVar1) break;
    FUN_00439be4(auStack_4c,auStack_38,0xe);
    local_3e = 0;
    iVar8 = FUN_0044b610(auStack_4c,&DAT_004aff54,2);
    if (((((iVar8 == 0) && (iVar8 = FUN_005137b8(local_3f), iVar8 != 0)) &&
         (iVar8 = FUN_005137b8(local_40), iVar8 != 0)) &&
        ((iVar8 = FUN_005137b8(local_41), iVar8 != 0 && (iVar8 = FUN_005137b8(local_42), iVar8 != 0)
         ))) && ((iVar8 = FUN_005137b8(local_43), iVar8 != 0 &&
                 (iVar8 = FUN_005137b8(local_44), iVar8 != 0)))) {
      FUN_00439be4(param_1,auStack_4c,0xe);
      *(undefined1 *)(param_1 + 0xe) = 0;
      iVar5 = FUN_0043d0ce();
      if (iVar5 << 0x1e < 0) {
        FUN_0043d574(3,PTR_s_nv_sysDt_004b0320,DAT_004b031c,DAT_004b037c,0x21c,DAT_004b0378,iVar6,
                     iVar7,param_1);
      }
      iVar8 = FUN_0043d0ce();
      iVar5 = iVar6;
      if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
        compress_log_output(0xcc00000,DAT_004b0380,DAT_004b0380,iVar6,iVar7,param_1);
      }
    }
  }
  FUN_0047f7ae(0x17);
  FUN_0047f7ae(0x1d);
  if (iVar5 < 0) {
    iVar5 = FUN_0043d0ce();
    if (iVar5 << 0x1e < 0) {
      FUN_0043d574(1,PTR_s_nv_sysDt_004b0320,DAT_004b031c,DAT_004b037c,0x237,DAT_004b0394);
    }
    iVar5 = FUN_0043d0ce();
    if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_004b0398,DAT_004b0398);
    }
    uVar4 = 0xffffffff;
  }
  else {
    if (param_2 != (int *)0x0) {
      *param_2 = iVar5;
    }
    iVar6 = FUN_0043d0ce();
    if (iVar6 << 0x1e < 0) {
      FUN_0043d574(3,PTR_s_nv_sysDt_004b0320,DAT_004b031c,DAT_004b037c,0x232,DAT_004b038c,iVar5,
                   param_1);
    }
    iVar6 = FUN_0043d0ce();
    if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
      compress_log_output(0xc800000,DAT_004b0390,DAT_004b0390,iVar5,param_1);
    }
    uVar4 = 0;
  }
  return uVar4;
}

