
void FUN_0048a0be(int param_1,int param_2,int *param_3,code *param_4)

{
  char *pcVar1;
  bool bVar2;
  char cVar3;
  char cVar4;
  int iVar5;
  int iVar6;
  uint uVar7;
  int iVar8;
  int iVar9;
  int iVar10;
  uint uVar11;
  uint uVar12;
  uint local_118;
  char local_114;
  undefined1 local_113 [3];
  int local_110;
  int local_10c;
  uint local_108;
  uint local_104;
  uint local_100;
  uint local_fc;
  undefined4 local_f8;
  undefined4 local_f4;
  int local_f0;
  uint local_ec;
  code *local_e8;
  uint local_e4;
  int local_e0;
  undefined4 local_dc;
  int local_d8;
  int local_d4;
  int local_d0;
  int local_cc;
  int local_c8;
  int local_c4;
  int local_c0;
  int local_bc;
  int local_b8;
  int local_b4;
  int local_b0;
  int local_ac;
  int local_a8;
  int local_a4;
  int local_a0;
  undefined1 auStack_9c [12];
  int *local_90;
  undefined1 auStack_88 [3];
  undefined1 local_85;
  undefined1 auStack_84 [3];
  undefined1 local_81;
  undefined4 local_80;
  undefined4 local_7c;
  int local_70;
  undefined1 auStack_6c [32];
  undefined1 local_4c;
  undefined1 auStack_4b [15];
  undefined1 auStack_3c [16];
  int local_2c;
  int *local_28;
  
  iVar10 = *(int *)(param_2 + 0x20);
  local_2c = param_1;
  local_28 = param_3;
  cVar3 = FUN_00450bcc(auStack_3c,param_3,param_1 + 0x38);
  if (cVar3 != '\0') {
    local_114 = *(char *)(param_2 + 0x51);
    local_113[0] = *(undefined1 *)(param_2 + 0x52);
    FUN_00489ed4(&local_114,local_113,*(undefined4 *)(param_2 + 0x1c));
    if ((*(byte *)(param_2 + 0x53) & 0xf) >> 3 == 0) {
      local_ec = FUN_00451598(local_28);
    }
    else {
      local_118 = (uint)(*(byte *)(param_2 + 0x53) >> 3);
      FUN_00489546(&local_104,*(undefined4 *)(param_2 + 0x1c),*(undefined4 *)(param_2 + 0x20),
                   *(undefined4 *)(param_2 + 0x2c),*(undefined4 *)(param_2 + 0x28),0x1fffffff);
      local_ec = local_104;
    }
    iVar5 = *(int *)(iVar10 + 0xc);
    local_f0 = *(int *)(param_2 + 0x28) + iVar5;
    local_110 = *local_28;
    local_d0 = *(int *)(param_2 + 0x30);
    local_10c = *(int *)(param_2 + 0x34) + local_28[1];
    iVar9 = -1;
    if (((*(int *)(param_2 + 0x58) != 0) && (*(int *)(param_2 + 0x34) == 0)) && (local_28[1] < 0)) {
      if (*(int *)(*(int *)(param_2 + 0x58) + 8) - local_28[1] < 1) {
        iVar9 = local_28[1] - *(int *)(*(int *)(param_2 + 0x58) + 8);
      }
      else {
        iVar9 = *(int *)(*(int *)(param_2 + 0x58) + 8) - local_28[1];
      }
      if (local_f0 * -2 + 0x400 < iVar9) {
        **(undefined4 **)(param_2 + 0x58) = 0xffffffff;
      }
      iVar9 = **(int **)(param_2 + 0x58);
    }
    iVar8 = 0;
    if ((*(int *)(param_2 + 0x58) != 0) && (-1 < iVar9)) {
      local_10c = *(int *)(*(int *)(param_2 + 0x58) + 4) + local_10c;
      iVar8 = iVar9;
    }
    local_104 = *(uint *)(param_2 + 0x4c);
    local_118 = (uint)(*(byte *)(param_2 + 0x53) >> 3);
    iVar9 = FUN_004897fc(*(int *)(param_2 + 0x1c) + iVar8,local_104,iVar10,
                         *(undefined4 *)(param_2 + 0x2c),local_ec,0);
    iVar9 = iVar9 + iVar8;
    do {
      if (*(int *)(local_2c + 0x3c) <= iVar5 + local_10c) {
        if (local_114 == '\x02') {
          iVar5 = FUN_004899a4(*(int *)(param_2 + 0x1c) + iVar8,iVar9 - iVar8,iVar10,
                               *(undefined4 *)(param_2 + 0x2c),*(byte *)(param_2 + 0x53) >> 3);
          iVar6 = FUN_00451598(local_28);
          local_110 = (iVar6 - iVar5) / 2 + local_110;
        }
        else if (local_114 == '\x03') {
          iVar5 = FUN_004899a4(*(int *)(param_2 + 0x1c) + iVar8,iVar9 - iVar8,iVar10,
                               *(undefined4 *)(param_2 + 0x2c),*(byte *)(param_2 + 0x53) >> 3);
          iVar6 = FUN_00451598(local_28);
          local_110 = (iVar6 + local_110) - iVar5;
        }
        local_fc = *(uint *)(param_2 + 0x3c);
        uVar7 = *(uint *)(param_2 + 0x40);
        local_100 = uVar7;
        if (uVar7 < local_fc) {
          local_100 = local_fc;
          local_fc = uVar7;
        }
        FUN_00489fd6(auStack_9c);
        local_85 = *(undefined1 *)(param_2 + 0x50);
        local_90 = &local_ac;
        FUN_00439be4(auStack_88,param_2 + 0x24,3);
        local_7c = *(undefined4 *)(param_2 + 0x38);
        local_80 = *(undefined4 *)(param_2 + 0x60);
        local_81 = *(undefined1 *)(param_2 + 0x5c);
        FUN_00439be4(auStack_84,param_2 + 0x5d,3);
        FUN_00451c3a(auStack_6c);
        local_4c = *(undefined1 *)(param_2 + 0x50);
        if (*(char *)(iVar10 + 0x16) == '\0') {
          local_e0 = 1;
        }
        else {
          local_e0 = (int)*(char *)(iVar10 + 0x16);
        }
        local_e4 = 0;
        local_f8 = FUN_004410a6(0);
        bVar2 = false;
        local_e8 = param_4;
        goto LAB_0048a364;
      }
      local_118 = (uint)(*(byte *)(param_2 + 0x53) >> 3);
      iVar6 = FUN_004897fc(*(int *)(param_2 + 0x1c) + iVar9,local_104,iVar10,
                           *(undefined4 *)(param_2 + 0x2c),local_ec,0);
      local_10c = local_f0 + local_10c;
      if (((*(int *)(param_2 + 0x58) != 0) && (-0x401 < local_10c)) &&
         (**(int **)(param_2 + 0x58) < 0)) {
        **(int **)(param_2 + 0x58) = iVar9;
        *(int *)(*(int *)(param_2 + 0x58) + 4) = local_10c - local_28[1];
        *(int *)(*(int *)(param_2 + 0x58) + 8) = local_28[1];
      }
      pcVar1 = (char *)(*(int *)(param_2 + 0x1c) + iVar9);
      iVar8 = iVar9;
      iVar9 = iVar6 + iVar9;
    } while (*pcVar1 != '\0');
  }
  return;
LAB_0048a364:
  if ((local_104 != 0) && (*(char *)(*(int *)(param_2 + 0x1c) + iVar8) != '\0')) {
    local_110 = local_d0 + local_110;
    cVar3 = '\0';
    local_108 = 0;
    local_d8 = *(int *)(param_2 + 0x1c) + iVar8;
    local_d4 = local_110;
LAB_0048a39a:
    while( true ) {
      if ((local_104 <= local_108) || ((uint)(iVar9 - iVar8) <= local_108)) goto LAB_0048a67e;
      uVar7 = 0;
      if ((local_fc != 0xffff) && (local_100 != 0xffff)) {
        uVar7 = (*(code *)*DAT_0048a964)(*(undefined4 *)(param_2 + 0x1c),local_108 + iVar8);
      }
      FUN_00489b3c(local_d8,&local_118,&local_dc,&local_108);
      if ((int)((uint)(*(byte *)(param_2 + 0x53) >> 3) << 0x1c) < 0) break;
LAB_0048a500:
      if (((int)((uint)(*(byte *)(param_2 + 0x53) >> 3) << 0x1c) < 0) && (cVar3 == '\x02')) {
        uVar7 = uVar7 - 7;
      }
      local_f4 = FUN_004d57f4(iVar10,local_118,local_dc);
      local_ac = local_110;
      local_a8 = local_10c;
      local_a4 = local_f4 + local_110 + -1;
      local_a0 = local_f0 + local_10c + -1;
      if ((uint)(iVar9 - iVar8) <= local_108) {
        if ((int)((uint)*(byte *)(param_2 + 0x53) << 0x1f) < 0) {
          local_bc = local_d4;
          local_b4 = local_f4 + local_110 + -1;
          local_b8 = ((*(int *)(iVar10 + 0xc) + local_10c) - *(int *)(iVar10 + 0x10)) -
                     (int)*(char *)(iVar10 + 0x15);
          local_b0 = local_e0 + local_b8 + -1;
          FUN_00439be4(auStack_4b,param_2 + 0x24,3);
          (*local_e8)(local_2c,0,auStack_6c,&local_bc);
        }
        if ((int)((uint)*(byte *)(param_2 + 0x53) << 0x1e) < 0) {
          local_cc = local_d4;
          local_c4 = local_f4 + local_110 + -1;
          local_c8 = (int)*(char *)(iVar10 + 0x16) / 2 +
                     ((*(int *)(iVar10 + 0xc) - *(int *)(iVar10 + 0x10)) * 2) / 3 + local_10c;
          local_c0 = local_e0 + local_c8 + -1;
          FUN_00439be4(auStack_4b,param_2 + 0x24,3);
          (*local_e8)(local_2c,0,auStack_6c,&local_cc);
        }
      }
      if (((local_fc == 0xffff) || (local_100 == 0xffff)) ||
         ((uVar7 < local_fc || (local_100 <= uVar7)))) {
        if (cVar3 == '\x02') {
          FUN_00439be4(auStack_88,&local_f8,3);
        }
        else {
          FUN_00439be4(auStack_88,param_2 + 0x24,3);
        }
      }
      else {
        FUN_00439be4(auStack_88,param_2 + 0x44,3);
        FUN_00439be4(auStack_4b,param_2 + 0x47,3);
        (*local_e8)(local_2c,0,auStack_6c,&local_ac);
      }
      FUN_0048a77e(local_2c,auStack_9c,&local_110,iVar10,local_118,local_e8);
      if (0 < (int)local_f4) {
        local_110 = *(int *)(param_2 + 0x2c) + local_f4 + local_110;
      }
    }
    if (local_118 == DAT_0048a74c) {
      if (cVar3 == '\0') {
        local_e4 = local_108;
        cVar3 = '\x01';
        goto LAB_0048a39a;
      }
      if (cVar3 == '\x01') {
        cVar3 = '\0';
        goto LAB_0048a40a;
      }
      if (cVar3 == '\x02') {
        cVar3 = '\0';
        goto LAB_0048a39a;
      }
    }
LAB_0048a40a:
    if (((cVar3 != '\x01') || (local_118 != 0x20)) || (bVar2)) {
      bVar2 = false;
    }
    else {
      bVar2 = true;
    }
    if (cVar3 == '\x01') {
      if (local_118 != 0x20) goto LAB_0048a39a;
      if (local_108 - local_e4 == 7) {
        FUN_00454738(&local_f8,local_e4 + local_d8,6);
        local_f4._0_3_ = (uint3)(ushort)local_f4;
        cVar3 = FUN_0048a750(local_f8 & 0xff);
        cVar3 = cVar3 << 4;
        cVar4 = FUN_0048a750(local_f8._1_1_);
        uVar12 = (uint)(byte)(cVar3 + cVar4);
        cVar3 = FUN_0048a750(local_f8._2_1_);
        cVar3 = cVar3 << 4;
        cVar4 = FUN_0048a750(local_f8._3_1_);
        uVar11 = (uint)(byte)(cVar3 + cVar4);
        cVar3 = FUN_0048a750(local_f4 & 0xff);
        cVar4 = FUN_0048a750(local_f4._1_1_);
        local_f8 = FUN_00441068(uVar12 & 0xff,uVar11 & 0xff,cVar3 * '\x10' + cVar4);
      }
      else {
        local_f8 = CONCAT22(CONCAT11(local_f8._3_1_,*(undefined1 *)(param_2 + 0x26)),
                            *(undefined2 *)(param_2 + 0x24));
      }
      cVar3 = '\x02';
    }
    if (!bVar2) goto LAB_0048a500;
    goto LAB_0048a39a;
  }
  goto LAB_0048a738;
LAB_0048a67e:
  local_104 = iVar8 + (local_104 - iVar9);
  iVar5 = iVar9;
  if (local_104 != 0) {
    local_118 = (uint)(*(byte *)(param_2 + 0x53) >> 3);
    iVar5 = FUN_004897fc(*(int *)(param_2 + 0x1c) + iVar9,local_104,iVar10,
                         *(undefined4 *)(param_2 + 0x2c),local_ec,0);
    iVar5 = iVar5 + iVar9;
  }
  local_110 = *local_28;
  if (local_114 == '\x02') {
    iVar8 = FUN_004899a4(*(int *)(param_2 + 0x1c) + iVar9,iVar5 - iVar9,iVar10,
                         *(undefined4 *)(param_2 + 0x2c),*(byte *)(param_2 + 0x53) >> 3);
    iVar6 = FUN_00451598(local_28);
    local_110 = (iVar6 - iVar8) / 2 + local_110;
  }
  else if (local_114 == '\x03') {
    iVar8 = FUN_004899a4(*(int *)(param_2 + 0x1c) + iVar9,iVar5 - iVar9,iVar10,
                         *(undefined4 *)(param_2 + 0x2c),*(byte *)(param_2 + 0x53) >> 3);
    iVar6 = FUN_00451598(local_28);
    local_110 = (iVar6 + local_110) - iVar8;
  }
  local_10c = local_f0 + local_10c;
  iVar8 = iVar9;
  iVar9 = iVar5;
  if (*(int *)(local_2c + 0x44) < local_10c) {
LAB_0048a738:
    if (local_70 == 0) {
      return;
    }
    FUN_0048b216(local_70);
    return;
  }
  goto LAB_0048a364;
}

