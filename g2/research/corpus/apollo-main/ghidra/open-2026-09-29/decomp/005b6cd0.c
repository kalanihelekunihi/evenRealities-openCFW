
undefined4 FUN_005b6cd0(char param_1)

{
  ushort uVar1;
  undefined4 uVar2;
  int iVar3;
  int iVar4;
  undefined4 uVar5;
  ushort uVar6;
  uint uVar7;
  
  iVar4 = DAT_005b7604;
  if ((*(int *)(DAT_005b7604 + 0x24) == 0) || (*(int *)(DAT_005b7604 + 0x2c) == 0)) {
    uVar2 = 0xffffffff;
  }
  else {
    *(undefined2 *)(DAT_005b7604 + 0x60) = 0;
    *(undefined4 *)(iVar4 + 0x28) = 0;
    FUN_0043c0e4(iVar4 + 0x30,0x30,0);
    FUN_0044ea04(*(undefined4 *)(iVar4 + 0x24),0,0);
    FUN_0044d878(*(undefined4 *)(iVar4 + 0x24));
    FUN_0043ded4(*(undefined4 *)(iVar4 + 0x24),1);
    FUN_0043ded4(*(undefined4 *)(iVar4 + 0x2c),1);
    iVar3 = FUN_005b476a();
    if (iVar3 == 0) {
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        FUN_0043d574(2,PTR_s_conversate_prep_005b7614,DAT_005b7610,
                     PTR_s_conversate_ui_prep_note_sync_con_005b7620,0xda,
                     PTR_s_prep_note_content_not_ready__kee_005b761c);
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        compress_log_output(0x8000000,PTR_s__conversate_prep_prep_note_conte_005b7624,
                            PTR_s__conversate_prep_prep_note_conte_005b7624);
      }
      uVar2 = 0;
    }
    else {
      uVar1 = FUN_005b4770();
      if (uVar1 == 0) {
        iVar4 = FUN_0043d0ce();
        if (iVar4 << 0x1e < 0) {
          FUN_0043d574(2,PTR_s_conversate_prep_005b7614,DAT_005b7610,
                       PTR_s_conversate_ui_prep_note_sync_con_005b7620,0xe0,
                       PTR_s_prep_note_content_ready_but_line_005b7628);
        }
        iVar4 = FUN_0043d0ce();
        if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
          compress_log_output(0x8000000,PTR_s__conversate_prep_prep_note_conte_005b762c,
                              PTR_s__conversate_prep_prep_note_conte_005b762c);
        }
        uVar2 = 0;
      }
      else {
        uVar7 = (uint)uVar1 * 0x1c;
        if (uVar7 < 0xe0) {
          uVar7 = 0xe0;
        }
        uVar2 = FUN_0043de82(*(undefined4 *)(iVar4 + 0x24));
        FUN_0043f4c0(uVar2,0x220,uVar7);
        FUN_0043f09a(uVar2,0,0);
        FUN_0044129e(uVar2,0,0);
        FUN_0044131c(uVar2,0,0);
        FUN_0044146a(uVar2,0,0);
        FUN_005b69d4(uVar2,0,0);
        FUN_0043dfa4(uVar2,0x10);
        *(undefined4 *)(iVar4 + 0x28) = uVar2;
        for (uVar6 = 0; uVar6 < 0xc; uVar6 = uVar6 + 1) {
          uVar5 = FUN_00499416(uVar2);
          *(undefined4 *)(iVar4 + (uint)uVar6 * 4 + 0x30) = uVar5;
          FUN_0043f4c0(*(undefined4 *)(iVar4 + (uint)uVar6 * 4 + 0x30),0x220,0x1c);
          FUN_0044144c(*(undefined4 *)(iVar4 + (uint)uVar6 * 4 + 0x30),0,0);
          FUN_00499678(*(undefined4 *)(iVar4 + (uint)uVar6 * 4 + 0x30),4);
          uVar5 = FUN_0044104c(0xffffff);
          FUN_0044140e(*(undefined4 *)(iVar4 + (uint)uVar6 * 4 + 0x30),uVar5,0);
          FUN_0044143e(*(undefined4 *)(iVar4 + (uint)uVar6 * 4 + 0x30),*DAT_005b7630,0);
          FUN_0044145a(*(undefined4 *)(iVar4 + (uint)uVar6 * 4 + 0x30),1,0);
          FUN_005b69d4(*(undefined4 *)(iVar4 + (uint)uVar6 * 4 + 0x30),0,0);
        }
        FUN_005b6ac0(0);
        FUN_0043f66c(*(undefined4 *)(iVar4 + 0x24));
        FUN_005b6b58(0);
        FUN_0043dfa4(*(undefined4 *)(iVar4 + 0x24),1);
        if (param_1 != '\0') {
          FUN_0058c238(*(undefined4 *)(iVar4 + 0x24),200,0);
        }
        iVar3 = FUN_0043e0e0(*(undefined4 *)(iVar4 + 0x2c),1);
        if ((iVar3 == 0) && (param_1 != '\0')) {
          FUN_0058c238(*(undefined4 *)(iVar4 + 0x2c),200,0);
        }
        iVar4 = FUN_0043d0ce();
        if (iVar4 << 0x1e < 0) {
          FUN_0043d574(3,PTR_s_conversate_prep_005b7614,DAT_005b7610,
                       PTR_s_conversate_ui_prep_note_sync_con_005b7620,0x10d,
                       PTR_s_prep_note_virtual_view_lines__u_v_005b7634,uVar1,8,0xc);
        }
        iVar4 = FUN_0043d0ce();
        if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
          compress_log_output(0xcc00000,PTR_s__conversate_prep_prep_note_virtu_005b7638,
                              PTR_s__conversate_prep_prep_note_virtu_005b7638,uVar1,8,0xc);
        }
        uVar2 = 0;
      }
    }
  }
  return uVar2;
}

