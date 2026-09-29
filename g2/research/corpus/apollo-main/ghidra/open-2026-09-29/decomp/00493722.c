
undefined4
FUN_00493722(undefined4 param_1,int param_2,uint param_3,int param_4,uint param_5,int param_6,
            uint param_7)

{
  int iVar1;
  int iVar2;
  uint uVar3;
  byte bVar4;
  uint uVar5;
  uint uVar6;
  uint local_130;
  undefined4 local_12c;
  uint local_128;
  uint local_124;
  undefined4 local_120;
  byte local_11c [4];
  int local_118 [3];
  undefined1 auStack_10c [240];
  int iStack_1c;
  
  bVar4 = 1;
  uVar5 = 0;
  iStack_1c = param_4;
  for (uVar3 = 0; (uVar5 < param_3 && (uVar3 < 0x10)); uVar3 = uVar3 + 1) {
    local_11c[uVar3 * 0x10] = 0;
    local_118[uVar3 * 4] = uVar5 * 0x554 + param_2;
    local_118[uVar3 * 4 + 1] = 0x554;
    *(undefined4 *)(auStack_10c + uVar3 * 0x10 + -4) =
         *(undefined4 *)(uVar5 * 0x554 + param_2 + 0x550);
    if (*(char *)(uVar5 * 0x554 + param_2 + 0x54c) == '\0') {
      bVar4 = 0;
    }
    uVar5 = uVar5 + 1;
  }
  uVar5 = 0;
  for (; (uVar5 < param_5 && (uVar3 < 0x10)); uVar3 = uVar3 + 1) {
    local_11c[uVar3 * 0x10] = 1;
    local_118[uVar3 * 4] = uVar5 * 0x428 + param_4;
    local_118[uVar3 * 4 + 1] = 0x428;
    *(undefined4 *)(auStack_10c + uVar3 * 0x10 + -4) =
         *(undefined4 *)(uVar5 * 0x428 + param_4 + 0x424);
    if (*(char *)(uVar5 * 0x428 + param_4 + 0x420) == '\0') {
      bVar4 = 0;
    }
    uVar5 = uVar5 + 1;
  }
  uVar5 = 0;
  for (; (uVar5 < param_7 && (uVar3 < 0x10)); uVar3 = uVar3 + 1) {
    local_11c[uVar3 * 0x10] = 2;
    local_118[uVar3 * 4] = uVar5 * 0x2c + param_6;
    local_118[uVar3 * 4 + 1] = 0x2c;
    *(undefined4 *)(auStack_10c + uVar3 * 0x10 + -4) =
         *(undefined4 *)(uVar5 * 0x2c + param_6 + 0x28);
    if (*(char *)(uVar5 * 0x2c + param_6 + 0x24) == '\0') {
      bVar4 = 0;
    }
    uVar5 = uVar5 + 1;
  }
  if ((bVar4 == 0) || (uVar3 < 2)) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      local_128 = (uint)bVar4;
      local_12c = DAT_004940d4;
      local_130 = 0xb0;
      local_124 = uVar3;
      FUN_0043d574(3,DAT_004940c0,DAT_004940bc,DAT_004940cc);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      local_130 = uVar3;
      compress_log_output(0xc800000,DAT_004940d8,DAT_004940d8,bVar4);
    }
  }
  else {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      local_12c = DAT_004940c8;
      local_130 = 0xa4;
      local_128 = uVar3;
      FUN_0043d574(3,DAT_004940c0,DAT_004940bc,DAT_004940cc);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0xc400000,DAT_004940d0,DAT_004940d0,uVar3);
    }
    for (uVar5 = 1; uVar5 < uVar3; uVar5 = uVar5 + 1) {
      FUN_00439c04(&local_130,local_11c + uVar5 * 0x10,0x10);
      uVar6 = uVar5;
      while ((uVar6 = uVar6 - 1, -1 < (int)uVar6 &&
             (local_124 < *(uint *)(auStack_10c + uVar6 * 0x10 + -4)))) {
        FUN_00439c04(auStack_10c + uVar6 * 0x10,local_11c + uVar6 * 0x10,0x10);
      }
      FUN_00439c04(auStack_10c + uVar6 * 0x10,&local_130,0x10);
    }
  }
  uVar5 = 0;
  while( true ) {
    if (uVar3 <= uVar5) {
      return 0;
    }
    iVar1 = FUN_00493606(local_11c[uVar5 * 0x10],local_118[uVar5 * 4],local_118[uVar5 * 4 + 1]);
    if (iVar1 == 0) break;
    iVar2 = FUN_00494030(param_1,iVar1);
    if (iVar2 != 0) {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        local_12c = DAT_00494288;
        local_130 = 0xbc;
        local_128 = uVar5;
        FUN_0043d574(1,DAT_004940c0,DAT_004940bc,DAT_004940cc);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x4400000,PTR_s__evenhub_ui_evenhub_build_contai_00494450,
                            PTR_s__evenhub_ui_evenhub_build_contai_00494450,uVar5);
      }
      file_heap_free(*(undefined4 *)(iVar1 + 0xc));
      file_heap_free(iVar1);
      return 0xffffffff;
    }
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      local_120 = *(undefined4 *)(auStack_10c + uVar5 * 0x10 + -4);
      local_124 = (uint)local_11c[uVar5 * 0x10];
      local_12c = DAT_004940dc;
      local_130 = 0xc2;
      local_128 = uVar5;
      FUN_0043d574(4,DAT_004940c0,DAT_004940bc,DAT_004940cc);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      local_12c = *(undefined4 *)(auStack_10c + uVar5 * 0x10 + -4);
      local_130 = (uint)local_11c[uVar5 * 0x10];
      compress_log_output(0x10c00000,DAT_004940e0,DAT_004940e0,uVar5);
    }
    uVar5 = uVar5 + 1;
  }
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    local_12c = DAT_004940e4;
    local_130 = 0xb8;
    local_128 = uVar5;
    FUN_0043d574(1,DAT_004940c0,DAT_004940bc,DAT_004940cc);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0x4400000,DAT_00494284,DAT_00494284,uVar5);
  }
  return 0xffffffff;
}

