
void dfu_payload_program_42dae8(int *param_1,uint *param_2)

{
  undefined4 uVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  int *piVar4;
  undefined4 uVar5;
  undefined4 uVar6;
  int iVar7;
  uint uVar8;
  uint uVar9;
  uint uVar10;
  uint uVar11;
  uint uVar12;
  uint uVar13;
  
  uVar10 = (*param_2 & 0xffffff) - 0x20;
  uVar11 = param_2[5];
  chunked_indirect_visit_42d9f0(uVar11,uVar10);
  uVar5 = DAT_0042e140;
  uVar3 = DAT_0042e118;
  uVar2 = DAT_0042e114;
  uVar13 = uVar10;
  uVar8 = uVar11;
  elog_output(4,DAT_0042e118,DAT_0042e114,DAT_0042e140,0x120,DAT_0042e144,uVar10,uVar11);
  uVar6 = stream_mode_42d84c(1);
  uVar1 = DAT_0042e108;
  iVar7 = FUN_004153a4(DAT_0042e108,uVar6);
  *param_1 = iVar7;
  if (*param_1 == 0) {
    elog_output(1,uVar3,uVar2,uVar5,0x123,DAT_0042e10c,uVar1,uVar8);
  }
  else {
    FUN_004154d2(*param_1,0x20,0);
    elog_output(4,uVar3,uVar2,uVar5,0x128,DAT_0042e148,uVar13,uVar8);
    for (; uVar10 != 0; uVar10 = uVar10 - uVar12) {
      uVar8 = 100 - (uVar10 * 100) / (*param_2 & 0xffffff);
      uVar13 = uVar10;
      elog_output(4,uVar3,uVar2,uVar5,300,DAT_0042e14c,uVar10,uVar8);
      uVar1 = DAT_0042e150;
      piVar4 = DAT_0042e124;
      uVar12 = uVar10;
      if (*(uint *)(*DAT_0042e124 + 4) < uVar10) {
        uVar12 = *(uint *)(*DAT_0042e124 + 4);
      }
      uVar9 = FUN_00415484(DAT_0042e150,1,uVar12,*param_1);
      if (uVar9 != uVar12) {
        uVar8 = uVar12;
        elog_output(1,uVar3,uVar2,uVar5,0x131,DAT_0042e128,uVar9,uVar12);
        uVar13 = uVar9;
      }
      (**(code **)(*piVar4 + 0x1c))(uVar11,uVar1,*(undefined4 *)(*piVar4 + 4));
      iVar7 = chunked_source_compare_42da1e(uVar11,uVar1,uVar12,*piVar4);
      if (iVar7 != 0) {
        uVar13 = uVar11;
        uVar8 = uVar12;
        elog_output(1,uVar3,uVar2,uVar5,0x136,DAT_0042e13c,uVar11,uVar12);
      }
      uVar11 = uVar12 + uVar11;
    }
    if (*param_1 != 0) {
      FUN_00415446(*param_1);
      *param_1 = 0;
    }
    elog_output(4,uVar3,uVar2,uVar5,0x13c,DAT_0042e154,uVar13,uVar8);
  }
  return;
}

