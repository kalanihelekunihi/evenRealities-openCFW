
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 FUN_00502174(void)

{
  ushort uVar1;
  int iVar2;
  uint uVar3;
  int iVar4;
  undefined4 uVar5;
  uint uVar6;
  undefined4 in_r3;
  ushort *puVar7;
  undefined4 *puVar8;
  byte bVar9;
  byte bVar10;
  undefined1 uStack_94;
  undefined1 uStack_93;
  undefined1 auStack_92 [6];
  undefined1 uStack_8c;
  undefined1 uStack_88;
  undefined1 uStack_87;
  byte bStack_86;
  undefined1 uStack_85;
  undefined4 auStack_84 [3];
  byte bStack_78;
  undefined1 auStack_77 [31];
  undefined1 auStack_58 [68];
  undefined4 uStack_14;
  
  uStack_14 = in_r3;
  if (*_DAT_00502678 == '\0') {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(3,DAT_0050262c,DAT_00502628,PTR_s_dashboard_ext_apply_layout_pb_to_00502684,0x36d
                   ,PTR_s_apply_pb_to_layout__pb_not_loade_00502680);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0xc000000,PTR_s__dashboard_ext_apply_pb_to_layou_00502688,
                          PTR_s__dashboard_ext_apply_pb_to_layou_00502688);
    }
    FUN_00558376(0);
    return 0xffffffff;
  }
  FUN_0048949c(&uStack_94,0x80);
  iVar2 = DAT_00502660;
  bVar9 = *(byte *)(DAT_00502660 + 0x30);
  if (bVar9 == 0) {
    uStack_94 = 0;
  }
  else if (bVar9 == 2) {
    uStack_94 = 2;
  }
  else {
    if (1 < bVar9) {
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        FUN_0043d574(2,DAT_0050262c,DAT_00502628,PTR_s_dashboard_ext_apply_layout_pb_to_00502684,
                     0x382,PTR_s_apply_pb_to_layout__invalid_pos__0050268c,
                     *(undefined1 *)(iVar2 + 0x30));
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        compress_log_output(0x8400000,PTR_s__dashboard_ext_apply_pb_to_layou_00502690,
                            PTR_s__dashboard_ext_apply_pb_to_layou_00502690,
                            *(undefined1 *)(iVar2 + 0x30));
      }
      FUN_00558376(0);
      return 0xffffffff;
    }
    uStack_94 = 1;
  }
  uVar3 = *(uint *)(DAT_00502660 + 0x34);
  if ((uint)(byte)*(undefined2 *)(DAT_00502660 + 0x38) < (uVar3 & 0xff)) {
    uVar3 = (uint)*(ushort *)(DAT_00502660 + 0x38);
  }
  if (5 < (uVar3 & 0xff)) {
    uVar3 = 5;
  }
  uStack_93 = (undefined1)uVar3;
  for (bVar9 = 0; (uint)bVar9 < (uVar3 & 0xff); bVar9 = bVar9 + 1) {
    bVar10 = *(byte *)((uint)bVar9 + DAT_00502660 + 0x3a);
    if (bVar10 == 0) {
      auStack_92[bVar9] = 0;
    }
    else if (bVar10 == 2) {
      auStack_92[bVar9] = 2;
    }
    else if (bVar10 < 2) {
      auStack_92[bVar9] = 1;
    }
    else if (bVar10 == 4) {
      auStack_92[bVar9] = 4;
    }
    else {
      if (3 < bVar10) {
        iVar4 = FUN_0043d0ce();
        if (iVar4 << 0x1e < 0) {
          FUN_0043d574(2,DAT_0050262c,DAT_00502628,PTR_s_dashboard_ext_apply_layout_pb_to_00502684,
                       0x3a7,PTR_s_apply_pb_to_layout__unsupported_w_00502694,bVar9,
                       *(undefined1 *)((uint)bVar9 + iVar2 + 0x3a));
        }
        iVar4 = FUN_0043d0ce();
        if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
          compress_log_output(0x8800000,PTR_s__dashboard_ext_apply_pb_to_layou_00502698,
                              PTR_s__dashboard_ext_apply_pb_to_layou_00502698,bVar9,
                              *(undefined1 *)((uint)bVar9 + iVar2 + 0x3a));
        }
        FUN_00558376(0);
        return 0xffffffff;
      }
      auStack_92[bVar9] = 3;
    }
  }
  if (*(char *)(DAT_00502660 + 0x3f) == '\0') {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(2,DAT_0050262c,DAT_00502628,PTR_s_dashboard_ext_apply_layout_pb_to_00502684,0x3b2
                   ,PTR_s_apply_pb_to_layout__has_watchfac_0050269c);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x8000000,PTR_s__dashboard_ext_apply_pb_to_layou_005026a0,
                          PTR_s__dashboard_ext_apply_pb_to_layou_005026a0);
    }
    FUN_00558376(0);
    return 0xffffffff;
  }
  puVar7 = (ushort *)(DAT_00502660 + 0x40);
  uVar1 = *puVar7;
  if (uVar1 == 1) {
    uStack_8c = 1;
    uStack_88 = (undefined1)*(undefined4 *)(DAT_00502660 + 0x44);
    uStack_87 = *(undefined1 *)(DAT_00502660 + 0x48);
    bStack_86 = *(byte *)(DAT_00502660 + 0x49);
  }
  else {
    if (uVar1 == 0) {
LAB_00502534:
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(2,DAT_0050262c,DAT_00502628,PTR_s_dashboard_ext_apply_layout_pb_to_00502684,
                     0x3fd,PTR_s_apply_pb_to_layout__unsupported_w_005026ac,*puVar7);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x8400000,PTR_s__dashboard_ext_apply_pb_to_layou_005026b0,
                            PTR_s__dashboard_ext_apply_pb_to_layou_005026b0,*puVar7);
      }
      FUN_00558376(0);
      return 0xffffffff;
    }
    if (uVar1 == 3) {
      uStack_8c = 3;
      uStack_88 = (undefined1)*(undefined4 *)(DAT_00502660 + 0x44);
      uStack_87 = (undefined1)*(undefined4 *)(DAT_00502660 + 0x48);
      bStack_86 = (byte)*(undefined4 *)(DAT_00502660 + 0x4c);
    }
    else if (uVar1 < 3) {
      uStack_8c = 2;
      uStack_88 = (undefined1)*(undefined4 *)(DAT_00502660 + 0x44);
      uStack_87 = (undefined1)*(undefined4 *)(DAT_00502660 + 0x48);
      bStack_86 = (byte)*(undefined4 *)(DAT_00502660 + 0x4c);
      uVar3 = (uint)*(ushort *)(DAT_00502660 + 0x50);
      if (3 < (byte)*(ushort *)(DAT_00502660 + 0x50)) {
        uVar3 = 3;
      }
      uStack_85 = (undefined1)uVar3;
      for (uVar6 = 0; (uVar6 & 0xff) < (uVar3 & 0xff); uVar6 = uVar6 + 1) {
        *(undefined1 *)((int)auStack_84 + (uVar6 & 0xff)) =
             *(undefined1 *)(DAT_00502660 + 0x44 + (uVar6 & 0xff) + 0xe);
      }
    }
    else {
      if (uVar1 != 4) goto LAB_00502534;
      puVar8 = (undefined4 *)(DAT_00502660 + 0x44);
      uStack_8c = 4;
      uStack_88 = (undefined1)*puVar8;
      uStack_87 = (undefined1)*(undefined4 *)(DAT_00502660 + 0x48);
      bStack_86 = (byte)*(undefined2 *)(DAT_00502660 + 0xae);
      if (3 < bStack_86) {
        bStack_86 = 3;
      }
      for (bVar9 = 0; bVar9 < bStack_86; bVar9 = bVar9 + 1) {
        auStack_84[bVar9] = puVar8[bVar9 + 0x1b];
      }
      bVar9 = (byte)*(undefined2 *)(DAT_00502660 + 0x4c);
      if (3 < bVar9) {
        bVar9 = 3;
      }
      bStack_78 = bVar9;
      for (bVar10 = 0; bVar10 < bVar9; bVar10 = bVar10 + 1) {
        FUN_0044b5a0(auStack_77 + (uint)bVar10 * 0x20,(int)puVar8 + (uint)bVar10 * 0x20 + 10,0x1f);
        auStack_58[(uint)bVar10 * 0x20] = 0;
      }
    }
  }
  iVar2 = FUN_00558376(&uStack_94);
  if (iVar2 == 0) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(3,DAT_0050262c,DAT_00502628,PTR_s_dashboard_ext_apply_layout_pb_to_00502684,0x40e
                   ,PTR_s_apply_pb_to_layout_OK__base_pos__005026b4,uStack_94,uStack_93,uStack_8c);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0xcc00000,PTR_s__dashboard_ext_apply_pb_to_layou_005026b8,
                          PTR_s__dashboard_ext_apply_pb_to_layou_005026b8,uStack_94,uStack_93,
                          uStack_8c);
    }
    uVar5 = 0;
  }
  else {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(2,DAT_0050262c,DAT_00502628,PTR_s_dashboard_ext_apply_layout_pb_to_00502684,0x409
                   ,PTR_s_apply_pb_to_layout__dashboard_la_005026a4);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x8000000,PTR_s__dashboard_ext_apply_pb_to_layou_005026a8,
                          PTR_s__dashboard_ext_apply_pb_to_layou_005026a8);
    }
    uVar5 = 0xffffffff;
  }
  return uVar5;
}

