
uint FUN_0044ab42(undefined4 param_1)

{
  bool bVar1;
  bool bVar2;
  bool bVar3;
  bool bVar4;
  bool bVar5;
  bool bVar6;
  bool bVar7;
  uint *puVar8;
  char *pcVar9;
  char *pcVar10;
  uint uVar11;
  uint uVar12;
  undefined1 local_40;
  undefined1 local_3f [3];
  byte local_3c;
  byte local_3b;
  byte local_3a;
  undefined4 local_38;
  uint local_34;
  uint local_30;
  uint local_2c;
  undefined4 local_28;
  
  bVar7 = false;
  bVar3 = false;
  bVar2 = false;
  bVar6 = false;
  bVar4 = false;
  uVar12 = 0;
  local_30 = 0x62;
  bVar5 = false;
  bVar1 = false;
  local_28 = param_1;
  local_34 = FUN_00473940();
  FUN_00480008(&local_3c);
  local_2c = (uint)local_3a | (uint)local_3c << 8 | (uint)local_3b << 4;
  uVar11 = *DAT_0044b500;
  if (((char)local_28 == '\x01') && (-1 < (int)(*DAT_0044b504 << 4))) {
    local_38 = CONCAT31((int3)((uint)*DAT_0044b508 >> 8),local_3c);
    if (local_3b == 3) {
      local_38._2_2_ = (undefined2)((uint)*DAT_0044b508 >> 0x10);
      local_38._0_2_ = CONCAT11(3,local_3c);
    }
    FUN_0047ffc4(local_38);
    local_40 = 2;
    FUN_00480312(0,0,&local_40);
    local_40 = (*DAT_0044b50c & 3) == 2;
    bVar6 = true;
    bVar2 = bVar3;
    if ((((uVar11 & 0x3f) >> 4 == 3) &&
        (((((*DAT_0044b510 & 0xff) == 0x22 && (1 < *DAT_0044b514)) ||
          (((*DAT_0044b510 & 0xff) == 0x23 && (*DAT_0044b514 != 0)))) ||
         ((((*DAT_0044b518 & 0x4c4) == 0 && ((*DAT_0044b504 & 0x3fffffff) == 0)) &&
          (-1 < *DAT_0044b51c << 2)))))) &&
       ((bVar2 = true, *DAT_0044b4fc == '\0' && (*DAT_0044b520 == '\0')))) {
      bVar7 = true;
      FUN_0047fe6c(0);
      FUN_00480408();
    }
    *DAT_0044b524 = *DAT_0044b524 | 4;
    puVar8 = DAT_0044b50c;
    if ((*DAT_0044b50c & 3) == 2) {
      while ((*puVar8 & 0x1f) >> 3 != 2) {
        FUN_004807a0(1);
      }
    }
    if (*DAT_0044b528 != '\0') {
      *DAT_0044b52c = *DAT_0044b52c & 0xffffffe0 | (uint)DAT_0044b530[0x1a] >> 0x14 & 0x1f;
      puVar8 = DAT_0044b538;
      pcVar10 = DAT_0044b534;
      if (*DAT_0044b534 != '\0') {
        *DAT_0044b538 = *DAT_0044b538 & 0xfffffff7;
        *puVar8 = *puVar8 & 0xffffffbf;
      }
      if (((*DAT_0044b53c == '\0') || (*pcVar10 == '\0')) &&
         ((*DAT_0044b540 == '\0' || ((*pcVar10 == '\0' || (*DAT_0044b544 != '\0')))))) {
        bVar5 = false;
      }
      else {
        bVar5 = true;
      }
    }
    if (*DAT_0044b548 != '\0') {
      *DAT_0044b52c = *DAT_0044b52c & 0xffffffe0 | 0xb;
    }
    if (((*DAT_0044b530 == DAT_0044b54c) && (*DAT_0044b540 != '\0')) &&
       ((DAT_0044b530[0x15] & 0x3ffU) >> 5 < (*DAT_0044b550 & 0x3fffffff) >> 0x19)) {
      uVar12 = (*DAT_0044b550 & 0x3fffffff) >> 0x19;
      *DAT_0044b550 = *DAT_0044b550 & 0xc1ffffff | ((uint)DAT_0044b530[0x15] >> 5 & 0x1f) << 0x19;
      bVar4 = true;
    }
  }
  else {
    local_38 = CONCAT13(local_38._3_1_,CONCAT12(1,CONCAT11(1,local_3c)));
    if ((local_3b == 3) || (local_3b == 2)) {
      local_38._0_2_ = CONCAT11(local_3b,local_3c);
    }
    FUN_0047ffc4(local_38);
    *DAT_0044b524 = *DAT_0044b524 & 0xfffffffb;
  }
  WaitForInterrupt();
  InstructionSynchronizationBarrier(0xf);
  if (bVar4) {
    *DAT_0044b550 = *DAT_0044b550 & 0xc1ffffff | uVar12 << 0x19;
  }
  puVar8 = DAT_0044b538;
  if (*DAT_0044b528 != '\0') {
    if (bVar5) {
      *DAT_0044b538 = *DAT_0044b538 | 8;
      *puVar8 = *puVar8 | 0x40;
    }
    *DAT_0044b52c = *DAT_0044b52c & 0xffffffe0;
  }
  pcVar10 = DAT_0044b548;
  if (*DAT_0044b548 != '\0') {
    *DAT_0044b52c = *DAT_0044b52c & 0xffffffe0;
  }
  if (((*DAT_0044b540 != '\0') || (*DAT_0044b53c != '\0')) &&
     (((*DAT_0044b55c & 0x1fffff) >> 0xc == local_30 &&
      (FUN_0048039a(), (*DAT_0044b55c & 0x1fffff) >> 0xc == 0)))) {
    if (((char)local_28 == '\x01') && ((*DAT_0044b50c & 3) == 2)) {
      while ((*DAT_0044b50c & 0x1f) >> 3 != 2) {
        if ((*DAT_0044b55c & 0x1fffff) >> 0xc != 0) {
          bVar1 = true;
          break;
        }
        FUN_004807a0(1);
      }
    }
    if (!bVar1) {
      if (bVar6) {
        FUN_00480312(0,0,&local_40);
        local_3f[0] = 2;
        FUN_00480312(0,0,local_3f);
      }
      if (((bVar2) && (*DAT_0044b4fc == '\0')) && (*DAT_0044b520 == '\0')) {
        bVar7 = true;
        FUN_0047fe6c(0);
        FUN_00480408();
      }
      pcVar9 = DAT_0044b528;
      if ((*DAT_0044b528 != '\0') &&
         (*DAT_0044b52c = *DAT_0044b52c & 0xffffffe0 | (uint)DAT_0044b530[0x1a] >> 0x14 & 0x1f,
         puVar8 = DAT_0044b538, *DAT_0044b534 != '\0')) {
        *DAT_0044b538 = *DAT_0044b538 & 0xfffffff7;
        *puVar8 = *puVar8 & 0xffffffbf;
      }
      if (*pcVar10 != '\0') {
        *DAT_0044b52c = *DAT_0044b52c & 0xffffffe0 | 0xb;
      }
      if (bVar4) {
        *DAT_0044b550 = *DAT_0044b550 & 0xc1ffffff | ((uint)DAT_0044b530[0x15] >> 5 & 0x1f) << 0x19;
      }
      WaitForInterrupt();
      InstructionSynchronizationBarrier(0xf);
      if (bVar4) {
        *DAT_0044b550 = *DAT_0044b550 & 0xc1ffffff | uVar12 << 0x19;
      }
      puVar8 = DAT_0044b538;
      if (*pcVar9 != '\0') {
        if (bVar5) {
          *DAT_0044b538 = *DAT_0044b538 | 8;
          *puVar8 = *puVar8 | 0x40;
        }
        *DAT_0044b52c = *DAT_0044b52c & 0xffffffe0;
      }
      if (*pcVar10 != '\0') {
        *DAT_0044b52c = *DAT_0044b52c & 0xffffffe0;
      }
    }
  }
  if (*DAT_0044b528 != '\0') {
    *DAT_0044b528 = '\0';
    *DAT_0044b534 = '\0';
  }
  if (*pcVar10 != '\0') {
    *pcVar10 = '\0';
  }
  if (bVar6) {
    FUN_00480312(0,0,&local_40);
  }
  puVar8 = DAT_0044b560;
  if (bVar7) {
    *DAT_0044b560 = *DAT_0044b560 | 0x10000;
    *puVar8 = *puVar8 | 1;
    *puVar8 = *puVar8 | 0x20;
  }
  FUN_0048041e();
  *DAT_0044b564 = local_2c;
  bVar1 = (bool)isCurrentModePrivileged();
  if (bVar1) {
    enableIRQinterrupts((local_34 & 1) == 1);
  }
  return local_34;
}

