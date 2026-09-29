
void FUN_004541b6(int param_1,int param_2)

{
  byte bVar1;
  bool bVar2;
  byte bVar3;
  byte bVar4;
  char cVar5;
  char cVar6;
  int iVar7;
  undefined4 uVar8;
  uint uVar9;
  int iVar10;
  int iVar11;
  int iVar12;
  undefined1 uVar13;
  undefined4 uVar14;
  uint local_c8;
  uint local_c4;
  undefined4 local_c0;
  int local_bc;
  undefined4 local_b8;
  int local_b4;
  undefined4 local_b0;
  int local_ac;
  undefined4 local_a8;
  int local_a4;
  undefined1 auStack_a0 [28];
  int local_84;
  int local_70;
  undefined4 local_6c;
  undefined4 local_68;
  undefined4 local_64;
  undefined4 local_60;
  int local_5c;
  int local_58;
  undefined2 local_50;
  undefined1 auStack_48 [16];
  int local_38;
  undefined1 auStack_34 [16];
  
  iVar7 = FUN_0043e0e0(param_2,1);
  if ((iVar7 == 0) && (bVar3 = FUN_0045318c(param_2,0), 1 < bVar3)) {
    bVar1 = *(byte *)(param_1 + 0x38);
    uVar14 = *(undefined4 *)(param_1 + 0x39);
    bVar4 = FUN_00453180(param_2,0);
    if (bVar4 < 0xfd) {
      *(char *)(param_1 + 0x38) = (char)((uint)bVar4 * (uint)bVar1 >> 8);
    }
    uVar8 = FUN_0044c54a(param_2,0,*(undefined4 *)(param_1 + 0x39));
    *(undefined4 *)(param_1 + 0x39) = uVar8;
    cVar5 = FUN_00452dd8(param_2);
    if (cVar5 == '\0') {
      FUN_004531ae(param_1,param_2);
    }
    else {
      cVar6 = FUN_00454074(param_1,param_2,cVar5,&local_b0,auStack_34);
      if (cVar6 != '\x01') {
        return;
      }
      iVar7 = FUN_004515a4(&local_b0);
      uVar9 = FUN_004515a4(&local_b0);
      if (cVar5 == '\x01') {
        iVar10 = FUN_00451598(&local_b0);
        bVar4 = FUN_00441004(*(undefined1 *)(*(int *)(DAT_00454634 + 0x10) + 0x3c));
        iVar7 = (0x40000 / iVar10) / (int)(uint)bVar4;
        uVar9 = (uint)(0x40000 / iVar10) >> 2;
      }
      local_c0 = local_b0;
      local_b8 = local_a8;
      local_bc = local_ac;
      local_b4 = local_ac;
      while (local_b4 < local_a4) {
        local_b4 = iVar7 + local_bc + -1;
        if (local_a4 < local_b4) {
          local_b4 = local_a4;
        }
        iVar10 = FUN_004531a4(param_2,0);
        if ((iVar10 == 0) && (iVar11 = FUN_0045417c(param_2,&local_c0), iVar11 == 0)) {
          bVar2 = false;
        }
        else {
          bVar2 = true;
        }
        if ((bVar2) && (local_b4 = uVar9 + local_bc + -1, local_a4 < local_b4)) {
          local_b4 = local_a4;
        }
        if (bVar2) {
          uVar13 = 0x10;
        }
        else {
          uVar13 = 6;
        }
        iVar11 = FUN_0048475e(param_1,uVar13,&local_c0);
        FUN_004531ae(iVar11,param_2);
        local_c8 = FUN_00453138(param_2,0);
        local_c4 = FUN_00453142(param_2,0);
        if (((local_c8 & 0x60000000) == 0x20000000) && ((int)(local_c8 & 0x9fffffff) < 0x1fffffff))
        {
          if ((int)(local_c8 & 0x9fffffff) < 0x10000000) {
            local_c8 = local_c8 & 0x9fffffff;
          }
          else {
            local_c8 = 0xfffffff - (local_c8 & 0x9fffffff);
          }
          iVar12 = FUN_00451598(param_2 + 0x14);
          local_c8 = (int)(iVar12 * local_c8) / 100;
        }
        if (((local_c4 & 0x60000000) == 0x20000000) && ((int)(local_c4 & 0x9fffffff) < 0x1fffffff))
        {
          if ((int)(local_c4 & 0x9fffffff) < 0x10000000) {
            local_c4 = local_c4 & 0x9fffffff;
          }
          else {
            local_c4 = 0xfffffff - (local_c4 & 0x9fffffff);
          }
          iVar12 = FUN_004515a4(param_2 + 0x14);
          local_c4 = (int)(iVar12 * local_c4) / 100;
        }
        FUN_00488918(auStack_a0);
        local_5c = (local_c8 + *(int *)(param_2 + 0x14)) - *(int *)(iVar11 + 4);
        local_58 = (local_c4 + *(int *)(param_2 + 0x18)) - *(int *)(iVar11 + 8);
        local_50._0_1_ = bVar3;
        for (local_70 = FUN_0045312e(param_2,0); 0xe10 < local_70; local_70 = local_70 + -0xe10) {
        }
        for (; local_70 < 0; local_70 = local_70 + 0xe10) {
        }
        local_6c = FUN_0045311a(param_2,0);
        local_68 = FUN_00453124(param_2,0);
        local_64 = FUN_0045314c(param_2,0);
        local_60 = FUN_00453156(param_2,0);
        bVar4 = FUN_00453198(param_2,0);
        local_50 = CONCAT11(local_50._1_1_ & 0xf8 | bVar4 & 7,(byte)local_50);
        local_50 = local_50 & 0xf7ff |
                   (ushort)((*(uint *)(*(int *)(DAT_00454634 + 0x10) + 0x38) >> 0x10 & 1) << 0xb);
        local_38 = iVar10;
        FUN_00439c04(auStack_48,auStack_34,0x10);
        local_84 = iVar11;
        FUN_0048895e(param_1,auStack_a0,&local_c0);
        local_bc = local_b4 + 1;
      }
    }
    *(byte *)(param_1 + 0x38) = bVar1;
    *(undefined4 *)(param_1 + 0x39) = uVar14;
  }
  return;
}

