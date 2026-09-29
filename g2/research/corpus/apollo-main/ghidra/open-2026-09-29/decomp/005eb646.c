
int FUN_005eb646(byte param_1,char param_2)

{
  byte bVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  int iVar9;
  int iVar10;
  int iVar11;
  int iVar12;
  int iVar13;
  uint uVar14;
  uint uVar15;
  
  iVar12 = DAT_005ebc34;
  if ((*(int *)(DAT_005ebc34 + 0x214) == 0) || (*(int *)(DAT_005ebc34 + 0x21c) == 0)) {
    iVar2 = 0;
  }
  else {
    bVar1 = FUN_005eb30c();
    if (param_1 < bVar1) {
      iVar2 = FUN_0044dce2(*(undefined4 *)(iVar12 + 0x21c),param_1);
      if (iVar2 == 0) {
        iVar2 = 0;
      }
      else {
        iVar3 = FUN_0043fdda(*(undefined4 *)(iVar12 + 0x214));
        iVar4 = func_0x005eb2a8(*(undefined4 *)(iVar12 + 0x214),0);
        iVar5 = func_0x005eb2b2(*(undefined4 *)(iVar12 + 0x214),0);
        iVar13 = (iVar3 - iVar4) - iVar5;
        if (iVar13 < 1) {
          iVar13 = iVar3;
        }
        iVar6 = FUN_0043fce0(*(undefined4 *)(iVar12 + 0x21c));
        iVar7 = FUN_0043fce0(iVar2);
        iVar8 = FUN_0043fce0(iVar2);
        iVar2 = FUN_0043fdda(iVar2);
        uVar14 = iVar2 + iVar8 + iVar6;
        iVar8 = 8 - iVar5;
        if (iVar8 < 0) {
          iVar8 = 0;
        }
        iVar9 = iVar8 + 2;
        if ((param_2 == '\0') || (bVar1 - 1 <= (uint)param_1)) {
          uVar15 = iVar9 + uVar14;
        }
        else {
          iVar2 = FUN_0044dce2(*(undefined4 *)(iVar12 + 0x21c),param_1 + 1);
          uVar15 = uVar14;
          if (iVar2 != 0) {
            iVar10 = FUN_0043fce0(iVar2);
            iVar2 = FUN_0043fdda(iVar2);
            uVar15 = iVar2 + iVar10 + iVar6;
          }
        }
        iVar2 = uVar15 - iVar13;
        if (iVar2 < 0) {
          iVar2 = 0;
        }
        iVar10 = FUN_0044e498(*(undefined4 *)(iVar12 + 0x214));
        iVar11 = FUN_0044e4bc(*(undefined4 *)(iVar12 + 0x214));
        iVar11 = iVar11 + iVar10;
        if (iVar11 < 0) {
          iVar11 = 0;
        }
        iVar10 = (iVar9 + uVar14) - iVar13;
        iVar7 = iVar7 + iVar6 + -8;
        if (iVar2 < iVar10) {
          iVar2 = iVar10;
        }
        if (iVar7 < iVar2) {
          iVar2 = iVar7;
        }
        if (iVar2 < 0) {
          iVar2 = 0;
        }
        iVar7 = FUN_0043d0ce();
        if (iVar7 << 0x1e < 0) {
          FUN_0043d574(3,PTR_s_terminal_ui_005ebc44,PTR_s_D__01_workspace_s200_ap510b_iar__005ebc40,
                       PTR_s_terminal_ui_query_panel_get_sele_005ebc3c,0x151,
                       PTR_s_query_align_before_clamp__idx__u_005ebc38,param_1,param_2,iVar3,iVar13,
                       iVar4,iVar5,iVar8,iVar9,iVar6,uVar14,uVar15,iVar2,iVar11,
                       *(undefined1 *)(iVar12 + 0x27c));
        }
        iVar7 = FUN_0043d0ce();
        if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
          compress_log_output((uVar15 & 0xf) << 0x16 | 0xc000000,
                              PTR_s__terminal_ui_query_align_before_c_005ebc48,
                              PTR_s__terminal_ui_query_align_before_c_005ebc48,param_1,param_2,iVar3
                              ,iVar13,iVar4,iVar5,iVar8,iVar9,iVar6,uVar14,uVar15,iVar2,iVar11,
                              *(undefined1 *)(iVar12 + 0x27c));
        }
        if (iVar11 < iVar2) {
          iVar2 = iVar11;
        }
        iVar12 = FUN_0043d0ce();
        if (iVar12 << 0x1e < 0) {
          FUN_0043d574(3,PTR_s_terminal_ui_005ebc44,PTR_s_D__01_workspace_s200_ap510b_iar__005ebc40,
                       PTR_s_terminal_ui_query_panel_get_sele_005ebc3c,0x155,
                       PTR_s_query_align_target__idx__u_targe_005ebc4c,param_1,iVar2);
        }
        iVar12 = FUN_0043d0ce();
        if ((iVar12 << 0x1f < 0) || (iVar12 = FUN_0043d0ce(), iVar12 << 0x1d < 0)) {
          compress_log_output(0xc800000,PTR_s__terminal_ui_query_align_target__005ebc50,
                              PTR_s__terminal_ui_query_align_target__005ebc50,param_1,iVar2);
        }
      }
    }
    else {
      iVar2 = 0;
    }
  }
  return iVar2;
}

