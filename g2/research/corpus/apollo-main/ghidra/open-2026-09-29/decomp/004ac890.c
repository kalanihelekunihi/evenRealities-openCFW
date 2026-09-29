
void FUN_004ac890(byte *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  byte bVar1;
  byte bVar2;
  byte bVar3;
  bool bVar4;
  byte *pbVar5;
  uint uVar6;
  byte bVar7;
  byte bVar8;
  byte bVar9;
  int iVar10;
  undefined4 local_28;
  uint local_24;
  uint local_20;
  uint local_1c;
  uint local_18;
  undefined4 uStack_14;
  
  uStack_14 = param_4;
  if (param_1 == (byte *)0x0) {
    iVar10 = FUN_0043d0ce();
    if (iVar10 << 0x1e < 0) {
      FUN_0043d574(1,DAT_004acdc0,DAT_004acdbc,DAT_004acdb8,0x267,DAT_004acdb4);
    }
    iVar10 = FUN_0043d0ce();
    if ((iVar10 << 0x1f < 0) || (iVar10 = FUN_0043d0ce(), iVar10 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_004acdc4,DAT_004acdc4);
    }
  }
  else {
    iVar10 = FUN_0043d0ce();
    if (iVar10 << 0x1e < 0) {
      local_18 = (uint)param_1[7];
      local_1c = (uint)param_1[6];
      local_20 = (uint)param_1[5];
      local_24 = (uint)param_1[4];
      local_28 = (uint)*param_1;
      FUN_0043d574(4,DAT_004acdc0,DAT_004acdbc,DAT_004acdb8,0x26c,DAT_004acdc8);
    }
    iVar10 = FUN_0043d0ce();
    if ((iVar10 << 0x1f < 0) || (iVar10 = FUN_0043d0ce(), iVar10 << 0x1d < 0)) {
      local_24 = (uint)param_1[7];
      local_28 = (uint)param_1[6];
      compress_log_output(0x11400000,DAT_004acdcc,DAT_004acdcc,*param_1,param_1[4],param_1[5]);
    }
    FUN_0045a568();
    pbVar5 = DAT_004acdd0;
    *DAT_004acdd0 = param_1[4];
    pbVar5[1] = param_1[5];
    pbVar5[2] = param_1[6];
    pbVar5[3] = param_1[7];
    FUN_0043c0e4(&local_28,4,0);
    FUN_004ac776(&local_28);
    uVar6 = local_28;
    bVar7 = (byte)local_28;
    if ((uint)param_1[4] <= (local_28 & 0xff)) {
      bVar7 = param_1[4];
    }
    if ((local_28._1_1_ == '\0') || (param_1[5] == 0)) {
      bVar8 = 0;
    }
    else {
      bVar8 = 1;
    }
    local_28._2_1_ = SUB41(uVar6,2);
    if ((local_28._2_1_ == '\x01') && (param_1[6] == 1)) {
      bVar9 = 1;
    }
    else {
      bVar9 = 0;
    }
    local_28._3_1_ = SUB41(uVar6,3);
    local_28._0_3_ = CONCAT12(bVar9,CONCAT11(bVar8,bVar7));
    if ((local_28._3_1_ == '\x01') && (param_1[7] == 1)) {
      local_28._3_1_ = 1;
    }
    else {
      local_28._3_1_ = 0;
    }
    bVar1 = pbVar5[4];
    if (bVar1 != bVar7) {
      pbVar5[4] = bVar7;
    }
    bVar2 = pbVar5[5];
    if (bVar2 != bVar8) {
      pbVar5[5] = bVar8;
    }
    bVar3 = pbVar5[6];
    if (bVar3 != bVar9) {
      pbVar5[6] = bVar9;
    }
    bVar4 = bVar3 != bVar9 || (bVar2 != bVar8 || bVar1 != bVar7);
    if (pbVar5[7] != local_28._3_1_) {
      pbVar5[7] = local_28._3_1_;
      bVar4 = true;
      if (*DAT_004acb00 == '\0') {
        FUN_004abf86();
        if (local_28._3_1_ == 1) {
          input_msg_send_id3();
        }
        FUN_0047243a();
      }
      else {
        iVar10 = FUN_0043d0ce();
        if (iVar10 << 0x1e < 0) {
          FUN_0043d574(3,DAT_004acdc0,DAT_004acdbc,DAT_004acdb8,0x29e,DAT_004acdd4);
        }
        iVar10 = FUN_0043d0ce();
        if ((iVar10 << 0x1f < 0) || (iVar10 = FUN_0043d0ce(), iVar10 << 0x1d < 0)) {
          compress_log_output(0xc000000,PTR_s__box_detect_force_out_box_enable_004acdd8,
                              PTR_s__box_detect_force_out_box_enable_004acdd8);
        }
      }
    }
    if (bVar4) {
      FUN_004abec8();
    }
    if (*param_1 == 3) {
      FUN_004ac828(2);
    }
  }
  return;
}

