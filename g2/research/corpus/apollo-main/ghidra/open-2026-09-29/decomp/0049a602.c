
void FUN_0049a602(int param_1)

{
  bool bVar1;
  ushort uVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  uint uVar7;
  int iVar8;
  undefined4 uVar9;
  byte bVar10;
  int local_108;
  int local_104;
  uint local_100;
  int local_fc;
  int local_f8;
  undefined1 auStack_f4 [16];
  int local_e4;
  undefined1 *local_e0;
  undefined4 local_c0;
  undefined4 local_b8;
  int local_b4;
  int local_b0;
  undefined4 local_ac;
  int local_a8;
  undefined4 local_a4;
  undefined4 local_a0;
  byte local_88;
  int local_84;
  undefined1 *local_80;
  undefined4 local_60;
  undefined4 local_58;
  int local_54;
  int local_50;
  undefined4 local_40;
  
  if (*(int *)(param_1 + 0x2c) != 0) {
    *(undefined4 *)(param_1 + 0x38) = 0xffffffff;
    *(byte *)(param_1 + 0x5c) = *(byte *)(param_1 + 0x5c) | 0x80;
    FUN_0043feca(param_1,auStack_f4);
    iVar3 = FUN_00451598(auStack_f4);
    iVar4 = FUN_004993c0(param_1,0);
    iVar5 = FUN_004993d4(param_1,0);
    iVar6 = FUN_004993ca(param_1,0);
    uVar7 = FUN_0049abea(param_1);
    FUN_0049aacc(param_1);
    local_100 = uVar7 & 0xff;
    local_108 = iVar5;
    local_104 = iVar3;
    FUN_00489546(&local_fc,*(undefined4 *)(param_1 + 0x2c),iVar4,iVar6);
    FUN_0043ffa0(param_1);
    if ((*(byte *)(param_1 + 0x5c) & 0xf) == 2) {
      iVar3 = FUN_00499402(param_1,0);
      iVar5 = FUN_0049940c(param_1,0);
      if (iVar5 == 0) {
        iVar5 = FUN_004505a2(0x28,300,10000);
      }
      FUN_004503d6(&local_e4);
      local_a0 = 0xffffffff;
      local_ac = 300;
      local_a4 = 300;
      bVar1 = false;
      local_e4 = param_1;
      iVar6 = FUN_00451598(auStack_f4);
      if (iVar6 < local_fc) {
        local_108 = FUN_00451598(auStack_f4);
        local_108 = local_108 - local_fc;
        FUN_004506ce(&local_e4,0,local_108);
        local_e0 = &LAB_0049abbc_1;
        iVar8 = FUN_00450566(param_1,&LAB_0049abbc_1);
        iVar6 = 0;
        bVar10 = 0;
        if (iVar8 != 0) {
          iVar6 = *(int *)(iVar8 + 0x34);
          bVar10 = (byte)(((uint)*(byte *)(iVar8 + 0x5c) << 0x1e) >> 0x1f);
        }
        iVar8 = FUN_004506fc(iVar5,0,local_108);
        uVar9 = local_c0;
        if (iVar8 < iVar6) {
          iVar6 = iVar8;
        }
        if (bVar10 != 0) {
          local_88 = local_88 | 2;
          local_c0 = local_b8;
          local_b8 = uVar9;
        }
        local_b4 = iVar5;
        local_b0 = iVar6;
        local_a8 = iVar5;
        if (iVar3 != 0) {
          FUN_0049a5c0(&local_e4,iVar3,*(byte *)(param_1 + 0x5c) & 0xf);
        }
        FUN_00450408(&local_e4);
        if (iVar6 < 0) {
          *(undefined4 *)(param_1 + 0x54) = 0;
        }
        bVar1 = true;
      }
      else {
        FUN_00450500(param_1,&LAB_0049abbc_1);
        *(undefined4 *)(param_1 + 0x54) = 0;
      }
      iVar6 = FUN_004515a4(auStack_f4);
      if ((local_f8 <= iVar6) || (bVar1)) {
        FUN_00450500(param_1,&LAB_0049abc8_1);
        *(undefined4 *)(param_1 + 0x58) = 0;
      }
      else {
        iVar6 = FUN_004515a4(auStack_f4);
        FUN_004506ce(&local_e4,0,(iVar6 - local_f8) - *(int *)(iVar4 + 0xc));
        local_e0 = &LAB_0049abc8_1;
        iVar4 = FUN_00450566(param_1,&LAB_0049abc8_1);
        uVar9 = local_c0;
        local_b0 = 0;
        bVar10 = 0;
        if (iVar4 != 0) {
          local_b0 = *(int *)(iVar4 + 0x34);
          bVar10 = (byte)(((uint)*(byte *)(iVar4 + 0x5c) << 0x1e) >> 0x1f);
        }
        if (local_b4 < local_b0) {
          local_b0 = local_b4;
        }
        if (bVar10 != 0) {
          local_88 = local_88 | 2;
          local_c0 = local_b8;
          local_b8 = uVar9;
        }
        local_b4 = iVar5;
        local_a8 = iVar5;
        if (iVar3 != 0) {
          FUN_0049a5c0(&local_e4,iVar3,*(byte *)(param_1 + 0x5c) & 0xf);
        }
        FUN_00450408(&local_e4);
      }
    }
    else if ((*(byte *)(param_1 + 0x5c) & 0xf) == 3) {
      iVar3 = FUN_00499402(param_1,0);
      iVar5 = FUN_0049940c(param_1,0);
      if (iVar5 == 0) {
        iVar5 = FUN_004505a2(0x28,300,10000);
      }
      FUN_004503d6(&local_84);
      local_40 = 0xffffffff;
      bVar1 = false;
      local_84 = param_1;
      iVar6 = FUN_00451598(auStack_f4);
      if (iVar6 < local_fc) {
        uVar7 = FUN_004d57f4(iVar4,0x20,0x20);
        FUN_004506ce(&local_84,0,(uVar7 & 0xffff) * -3 - local_fc);
        local_80 = &LAB_0049abbc_1;
        local_54 = iVar5;
        iVar6 = FUN_00450566(param_1,&LAB_0049abbc_1);
        if (iVar6 == 0) {
          iVar6 = 0;
        }
        else {
          iVar6 = *(int *)(iVar6 + 0x34);
        }
        iVar8 = FUN_004506fc(iVar5,local_60,local_58);
        if (iVar6 < iVar8) {
          local_50 = iVar6;
        }
        if (iVar3 != 0) {
          FUN_0049a5c0(&local_84,iVar3,*(byte *)(param_1 + 0x5c) & 0xf);
        }
        FUN_00450408(&local_84);
        bVar1 = true;
      }
      else {
        FUN_00450500(param_1,&LAB_0049abbc_1);
        *(undefined4 *)(param_1 + 0x54) = 0;
      }
      iVar6 = FUN_004515a4(auStack_f4);
      if ((local_f8 <= iVar6) || (bVar1)) {
        FUN_00450500(param_1,&LAB_0049abc8_1);
        *(undefined4 *)(param_1 + 0x58) = 0;
      }
      else {
        FUN_004506ce(&local_84,0,-*(int *)(iVar4 + 0xc) - local_f8);
        local_80 = &LAB_0049abc8_1;
        local_54 = iVar5;
        iVar4 = FUN_00450566(param_1,&LAB_0049abc8_1);
        if (iVar4 == 0) {
          iVar4 = 0;
        }
        else {
          iVar4 = *(int *)(iVar4 + 0x34);
        }
        if (iVar3 == 0) {
          if (iVar4 < local_54) {
            local_50 = iVar4;
          }
        }
        else {
          FUN_0049a5c0(&local_84,iVar3,*(byte *)(param_1 + 0x5c) & 0xf);
        }
        FUN_00450408(&local_84);
      }
    }
    else if ((*(byte *)(param_1 + 0x5c) & 0xf) == 1) {
      iVar3 = FUN_004515a4(auStack_f4);
      if (((iVar3 < local_f8) && (*(int *)(iVar4 + 0xc) < local_f8)) &&
         (uVar7 = (**(code **)PTR_DAT_0049ab94)(*(undefined4 *)(param_1 + 0x2c)), 3 < uVar7)) {
        iVar3 = FUN_00451598(auStack_f4);
        uVar2 = FUN_004d57f4(iVar4,0x2e,0x2e);
        local_108 = (iVar6 + (uint)uVar2) * -3 + iVar3;
        iVar3 = FUN_004515a4(auStack_f4);
        iVar6 = iVar5 + *(int *)(iVar4 + 0xc);
        iVar6 = iVar3 - iVar6 * (iVar3 / iVar6);
        if (iVar6 < *(int *)(iVar4 + 0xc)) {
          local_104 = (iVar3 - iVar6) - iVar5;
        }
        else {
          local_104 = *(int *)(iVar4 + 0xc) + (iVar3 - iVar6);
        }
        uVar9 = FUN_00499a5c(param_1,&local_108,0);
        uVar7 = FUN_00454768(*(undefined4 *)(param_1 + 0x2c));
        local_100 = (*(code *)*DAT_0049aba0)(*(undefined4 *)(param_1 + 0x2c),uVar9);
        while (uVar7 < local_100 + 3) {
          (*(code *)*DAT_0049aba4)(*(undefined4 *)(param_1 + 0x2c),&local_100);
        }
        FUN_0049ab06(param_1,local_100);
      }
    }
    FUN_00440656(param_1);
  }
  return;
}

