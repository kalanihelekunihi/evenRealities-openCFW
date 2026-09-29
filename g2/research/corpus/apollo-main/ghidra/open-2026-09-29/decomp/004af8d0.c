
void SVC_NvdbparsePsn(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined1 uVar1;
  undefined1 uVar2;
  undefined1 uVar3;
  undefined1 uVar4;
  uint uVar5;
  int iVar6;
  undefined4 uVar7;
  undefined4 uVar8;
  undefined4 uVar9;
  undefined1 auStack_38 [2];
  undefined1 local_36;
  undefined1 auStack_34 [4];
  undefined1 local_30;
  undefined1 auStack_2c [4];
  undefined1 local_28;
  undefined4 uStack_24;
  
  uStack_24 = param_4;
  uVar5 = FUN_0044a43c(param_1);
  if (uVar5 < 0xe) {
    iVar6 = FUN_0043d0ce();
    if (iVar6 << 0x1e < 0) {
      FUN_0043d574(4,PTR_s_nv_sysDt_004b0320,DAT_004b031c,PTR_s_SVC_NvdbparsePsn_004b0318,0x151,
                   PTR_s_length_too_short_004b0314);
    }
    iVar6 = FUN_0043d0ce();
    if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
      compress_log_output(0x10000000,PTR_s__nv_sysDt_length_too_short_004b0324,
                          PTR_s__nv_sysDt_length_too_short_004b0324);
    }
  }
  else {
    FUN_0044b5a0(auStack_2c,param_1,4);
    local_28 = 0;
    uVar4 = *(undefined1 *)(param_1 + 4);
    uVar1 = *(undefined1 *)(param_1 + 5);
    uVar2 = *(undefined1 *)(param_1 + 6);
    uVar3 = *(undefined1 *)(param_1 + 7);
    FUN_0044b5a0(auStack_38,param_1 + 8,2);
    local_36 = 0;
    FUN_0044b5a0(auStack_34,param_1 + 10,4);
    local_30 = 0;
    uVar7 = nvdbSysDtManufacturerName(uVar4);
    uVar8 = nvdbSysDtYear(uVar2);
    uVar9 = nvdbSysDtMonth(uVar3);
    iVar6 = FUN_0043d0ce();
    if (iVar6 << 0x1e < 0) {
      FUN_0043d574(4,PTR_s_nv_sysDt_004b0320,DAT_004b031c,PTR_s_SVC_NvdbparsePsn_004b0318,0x16b,
                   PTR_s_projectCode___s_004b0328,auStack_2c);
    }
    iVar6 = FUN_0043d0ce();
    if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
      compress_log_output(0x10400000,PTR_s__nv_sysDt__projectCode___s_004b032c,
                          PTR_s__nv_sysDt__projectCode___s_004b032c,auStack_2c);
    }
    iVar6 = FUN_0043d0ce();
    if (iVar6 << 0x1e < 0) {
      FUN_0043d574(4,PTR_s_nv_sysDt_004b0320,DAT_004b031c,PTR_s_SVC_NvdbparsePsn_004b0318,0x16c,
                   PTR_s_manufacturer___c___s__004b0330,uVar4,uVar7);
    }
    iVar6 = FUN_0043d0ce();
    if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
      compress_log_output(0x10800000,PTR_s__nv_sysDt_manufacturer___c___s__004b0334,
                          PTR_s__nv_sysDt_manufacturer___c___s__004b0334,uVar4,uVar7);
    }
    iVar6 = FUN_0043d0ce();
    if (iVar6 << 0x1e < 0) {
      FUN_0043d574(4,PTR_s_nv_sysDt_004b0320,DAT_004b031c,PTR_s_SVC_NvdbparsePsn_004b0318,0x16d,
                   PTR_s_color___c_004b0338,uVar1);
    }
    iVar6 = FUN_0043d0ce();
    if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
      compress_log_output(0x10400000,PTR_s__nv_sysDt__color___c_004b033c,
                          PTR_s__nv_sysDt__color___c_004b033c,uVar1);
    }
    iVar6 = FUN_0043d0ce();
    if (iVar6 << 0x1e < 0) {
      FUN_0043d574(4,PTR_s_nv_sysDt_004b0320,DAT_004b031c,PTR_s_SVC_NvdbparsePsn_004b0318,0x16e,
                   PTR_s_year___c___d__004b0340,uVar2,uVar8);
    }
    iVar6 = FUN_0043d0ce();
    if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
      compress_log_output(0x10800000,PTR_s__nv_sysDt__year___c___d__004b0344,
                          PTR_s__nv_sysDt__year___c___d__004b0344,uVar2,uVar8);
    }
    iVar6 = FUN_0043d0ce();
    if (iVar6 << 0x1e < 0) {
      FUN_0043d574(4,PTR_s_nv_sysDt_004b0320,DAT_004b031c,PTR_s_SVC_NvdbparsePsn_004b0318,0x16f,
                   PTR_s_month___c___s__004b0348,uVar3,uVar9);
    }
    iVar6 = FUN_0043d0ce();
    if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
      compress_log_output(0x10800000,PTR_s__nv_sysDt__month___c___s__004b034c,
                          PTR_s__nv_sysDt__month___c___s__004b034c,uVar3,uVar9);
    }
    iVar6 = FUN_0043d0ce();
    if (iVar6 << 0x1e < 0) {
      FUN_0043d574(4,PTR_s_nv_sysDt_004b0320,DAT_004b031c,PTR_s_SVC_NvdbparsePsn_004b0318,0x170,
                   PTR_s_day___s_004b0350,auStack_38);
    }
    iVar6 = FUN_0043d0ce();
    if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
      compress_log_output(0x10400000,PTR_s__nv_sysDt__day___s_004b0354,
                          PTR_s__nv_sysDt__day___s_004b0354,auStack_38);
    }
    iVar6 = FUN_0043d0ce();
    if (iVar6 << 0x1e < 0) {
      FUN_0043d574(4,PTR_s_nv_sysDt_004b0320,DAT_004b031c,PTR_s_SVC_NvdbparsePsn_004b0318,0x171,
                   PTR_s_serialNumber___s_004b0358,auStack_34);
    }
    iVar6 = FUN_0043d0ce();
    if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
      compress_log_output(0x10400000,PTR_s__nv_sysDt_serialNumber___s_004b035c,
                          PTR_s__nv_sysDt_serialNumber___s_004b035c,auStack_34);
    }
  }
  return;
}

