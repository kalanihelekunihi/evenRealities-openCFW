
undefined4 FUN_00420002(undefined1 *param_1)

{
  undefined4 uVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  int iVar4;
  uint uVar5;
  undefined4 uVar6;
  uint uVar7;
  byte bVar8;
  uint uVar9;
  uint uVar10;
  undefined1 local_c0;
  undefined1 local_bf;
  undefined1 local_be;
  undefined1 local_bd;
  byte local_bc;
  undefined1 local_bb;
  int local_b8;
  uint local_b4 [36];
  
  local_b8 = 0;
  memset_wrapper_426c10(local_b4,0,0x90);
  memset_wrapper_426c10(&local_c0,0,6);
  for (uVar7 = 0; uVar7 < 0x24; uVar7 = uVar7 + 1) {
    local_c0 = *(undefined1 *)(DAT_00420ae8 + uVar7 * 6);
    local_bf = *(undefined1 *)(uVar7 * 6 + DAT_00420ae8 + 1);
    local_be = *(undefined1 *)(uVar7 * 6 + DAT_00420ae8 + 2);
    local_bd = *(undefined1 *)(uVar7 * 6 + DAT_00420ae8 + 3);
    local_bb = 8;
    for (bVar8 = 0; bVar8 < 0x20; bVar8 = bVar8 + 1) {
      local_bc = bVar8;
      am_hal_mspi_control(*DAT_00420874,0x10,&local_c0);
      iVar4 = FUN_0042059e(&local_b8);
      if ((iVar4 == 0) && (local_b8 == DAT_00420ae4)) {
        local_b4[uVar7] = local_b4[uVar7] | 1 << (uint)bVar8;
      }
    }
  }
  uVar9 = 0;
  uVar7 = 0;
  for (uVar10 = 0; uVar3 = DAT_00420aec, uVar2 = DAT_00420adc, uVar1 = DAT_00420978, uVar10 < 0x24;
      uVar10 = uVar10 + 1) {
    uVar5 = FUN_0041ff60(local_b4 + uVar10);
    if (uVar7 < uVar5) {
      uVar7 = uVar5;
      uVar9 = uVar10;
    }
  }
  elog_output(2,DAT_00420adc,DAT_00420978,DAT_00420aec,0x1c6,DAT_00420af0,uVar7,uVar9);
  iVar4 = DAT_00420ae8;
  elog_output(2,uVar2,uVar1,uVar3,0x1cd,DAT_00420af4,*(undefined1 *)(DAT_00420ae8 + uVar9 * 6),
              *(undefined1 *)(uVar9 * 6 + DAT_00420ae8 + 1),
              *(undefined1 *)(uVar9 * 6 + DAT_00420ae8 + 2),
              *(undefined1 *)(uVar9 * 6 + DAT_00420ae8 + 3),
              *(undefined1 *)(uVar9 * 6 + DAT_00420ae8 + 5),local_b4[uVar9]);
  uVar6 = FUN_0041ff74(local_b4 + uVar9);
  elog_output(2,uVar2,uVar1,uVar3,0x1d3,DAT_00420c18,uVar6);
  param_1[4] = (char)uVar6;
  *param_1 = *(undefined1 *)(iVar4 + uVar9 * 6);
  param_1[1] = *(undefined1 *)(uVar9 * 6 + iVar4 + 1);
  param_1[2] = *(undefined1 *)(uVar9 * 6 + iVar4 + 2);
  param_1[3] = *(undefined1 *)(uVar9 * 6 + iVar4 + 3);
  param_1[5] = *(undefined1 *)(iVar4 + uVar9 * 6 + 5);
  return 0;
}

