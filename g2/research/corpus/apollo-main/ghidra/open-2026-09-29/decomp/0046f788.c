
undefined4
FUN_0046f788(undefined1 *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  uint uVar2;
  undefined4 uVar3;
  uint uVar4;
  byte bVar5;
  uint uVar6;
  uint uVar7;
  undefined1 local_b8;
  undefined1 local_b7;
  undefined1 local_b6;
  undefined1 local_b5;
  byte local_b4;
  undefined1 local_b3;
  int local_b0;
  uint local_ac [36];
  undefined4 uStack_1c;
  
  local_b0 = 0;
  uStack_1c = param_4;
  FUN_0043bb00(local_ac,0,0x90);
  FUN_0043bb00(&local_b8,0,6);
  for (uVar4 = 0; uVar4 < 0x24; uVar4 = uVar4 + 1) {
    local_b8 = *(undefined1 *)(DAT_00470488 + uVar4 * 6);
    local_b7 = *(undefined1 *)(uVar4 * 6 + DAT_00470488 + 1);
    local_b6 = *(undefined1 *)(uVar4 * 6 + DAT_00470488 + 2);
    local_b5 = *(undefined1 *)(uVar4 * 6 + DAT_00470488 + 3);
    local_b3 = 8;
    for (bVar5 = 0; bVar5 < 0x20; bVar5 = bVar5 + 1) {
      local_b4 = bVar5;
      FUN_004c0f78(*DAT_00470014,0x10,&local_b8);
      iVar1 = FUN_00470028(&local_b0);
      if ((iVar1 == 0) && (local_b0 == DAT_00470354)) {
        local_ac[uVar4] = local_ac[uVar4] | 1 << (uint)bVar5;
      }
    }
  }
  uVar4 = 0;
  uVar6 = 0;
  uVar2 = 0;
  for (uVar7 = 0; uVar7 < 0x24; uVar7 = uVar7 + 1) {
    uVar2 = FUN_0046f6e6(local_ac + uVar7);
    if (uVar6 < uVar2) {
      uVar4 = uVar7;
      uVar6 = uVar2;
    }
  }
  iVar1 = FUN_0043d0ce(uVar2);
  if (iVar1 << 0x1e < 0) {
    FUN_0043d574(2,DAT_004700a8,DAT_004700a4,DAT_0047035c,0x1c6,DAT_00470358,uVar6,uVar4);
  }
  iVar1 = FUN_0043d0ce();
  if (-1 < iVar1 << 0x1f) {
    iVar1 = FUN_0043d0ce();
    if (-1 < iVar1 << 0x1d) goto LAB_0046f8a4;
  }
  compress_log_output(0x8800000,DAT_00470360,DAT_00470360,uVar6,uVar4);
LAB_0046f8a4:
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    FUN_0043d574(2,DAT_004700a8,DAT_004700a4,DAT_0047035c,0x1cd,DAT_00470364,
                 *(undefined1 *)(DAT_00470488 + uVar4 * 6),
                 *(undefined1 *)(uVar4 * 6 + DAT_00470488 + 1),
                 *(undefined1 *)(uVar4 * 6 + DAT_00470488 + 2),
                 *(undefined1 *)(uVar4 * 6 + DAT_00470488 + 3),
                 *(undefined1 *)(uVar4 * 6 + DAT_00470488 + 5),local_ac[uVar4]);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0x9800000,DAT_0047048c,DAT_0047048c,
                        *(undefined1 *)(DAT_00470488 + uVar4 * 6),
                        *(undefined1 *)(uVar4 * 6 + DAT_00470488 + 1),
                        *(undefined1 *)(uVar4 * 6 + DAT_00470488 + 2),
                        *(undefined1 *)(uVar4 * 6 + DAT_00470488 + 3),
                        *(undefined1 *)(uVar4 * 6 + DAT_00470488 + 5),local_ac[uVar4]);
  }
  uVar3 = FUN_0046f6fa(local_ac + uVar4);
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    FUN_0043d574(2,DAT_004700a8,DAT_004700a4,DAT_0047035c,0x1d3,DAT_00470490,uVar3);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0x8400000,DAT_00470494,DAT_00470494,uVar3);
  }
  param_1[4] = (char)uVar3;
  iVar1 = DAT_00470488;
  *param_1 = *(undefined1 *)(DAT_00470488 + uVar4 * 6);
  param_1[1] = *(undefined1 *)(uVar4 * 6 + iVar1 + 1);
  param_1[2] = *(undefined1 *)(uVar4 * 6 + iVar1 + 2);
  param_1[3] = *(undefined1 *)(uVar4 * 6 + iVar1 + 3);
  param_1[5] = *(undefined1 *)(uVar4 * 6 + iVar1 + 5);
  return 0;
}

