
undefined4 FUN_005458a2(int param_1,short *param_2,undefined4 param_3,undefined4 param_4)

{
  uint uVar1;
  uint *puVar2;
  byte bVar3;
  undefined1 uVar4;
  char cVar5;
  ushort uVar6;
  int iVar7;
  undefined4 uVar8;
  uint uVar9;
  uint uVar10;
  int iVar11;
  uint uVar12;
  uint uVar13;
  int iVar14;
  short *psVar15;
  uint uVar16;
  uint local_40;
  undefined *local_3c;
  uint local_38;
  uint local_34;
  undefined *local_30;
  int local_2c;
  undefined4 uStack_28;
  
  local_2c = param_1;
  uStack_28 = param_4;
  if ((param_1 == 0) || (param_2 == (short *)0x0)) {
    iVar7 = FUN_0043d0ce();
    if (iVar7 << 0x1e < 0) {
      FUN_0043d574(1,DAT_00545cc8,DAT_00545cc4,DAT_00545d04,0x174,DAT_00545d00);
    }
    iVar7 = FUN_0043d0ce();
    if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_00545d08);
    }
    uVar8 = 0xffffffff;
  }
  else if (*param_2 == 0x4d42) {
    if (param_2[0xe] == 4) {
      uVar12 = *(uint *)(param_2 + 9);
      uVar9 = FUN_00509694(*(undefined4 *)(param_2 + 0xb));
      if ((uVar12 == 0x240) && (uVar9 == 0xbc)) {
        iVar7 = FUN_0043d0ce();
        if (iVar7 << 0x1e < 0) {
          local_40 = uVar12;
          local_3c = (undefined *)uVar9;
          FUN_0043d574(4,DAT_00545cc8,DAT_00545cc4,DAT_00545d04,400,DAT_005464b0);
        }
        iVar7 = FUN_0043d0ce();
        if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
          compress_log_output(0x10800000,DAT_005464b4,DAT_005464b4,0x240,0xbc);
        }
        uVar1 = DAT_00545cec;
        if (*(int *)(param_2 + 0x17) == 0) {
          uVar13 = 0x10;
        }
        else {
          uVar13 = *(uint *)(param_2 + 0x17);
        }
        psVar15 = param_2 + 0x1b;
        local_3c = (undefined *)(*(int *)(param_2 + 5) + (int)param_2);
        local_40 = 0x120;
        uVar16 = DAT_00545cec;
        for (iVar7 = 0; uVar10 = DAT_00545ce8, iVar7 < 0xbc; iVar7 = iVar7 + 1) {
          for (iVar14 = 0; iVar14 < 0x240; iVar14 = iVar14 + 1) {
            iVar11 = iVar7;
            if (0 < *(int *)(param_2 + 0xb)) {
              iVar11 = 0xbb - iVar7;
            }
            bVar3 = *(byte *)((int)local_3c + local_40 * iVar11 + iVar14 / 2);
            if (iVar14 << 0x1f < 0) {
              uVar10 = bVar3 & 0xf;
            }
            else {
              uVar10 = (uint)(bVar3 >> 4);
            }
            bVar3 = (byte)uVar10;
            if (uVar13 <= uVar10) {
              bVar3 = 0;
            }
            uVar10 = (uint)bVar3;
            FUN_00441068((char)psVar15[uVar10 * 2 + 1],
                         *(undefined1 *)((int)psVar15 + uVar10 * 4 + 1),(char)psVar15[uVar10 * 2]);
            uVar4 = FUN_005456d6();
            *(undefined1 *)(uVar16 + iVar7 * 0x240 + iVar14) = uVar4;
          }
        }
        uVar6 = FUN_00545868(uVar16,DAT_00545ce8);
        cVar5 = FUN_004d4b24();
        iVar7 = FUN_0043d0ce();
        if (iVar7 << 0x1e < 0) {
          if (cVar5 == '\0') {
            local_30 = &DAT_00545cb0;
          }
          else {
            local_30 = &DAT_00545cac;
          }
          local_34 = uVar10;
          local_38 = (uint)uVar6;
          local_40 = uVar12;
          local_3c = (undefined *)uVar9;
          FUN_0043d574(4,DAT_00545cc8,DAT_00545cc4,DAT_00545d04,0x1cc,DAT_0054660c);
        }
        iVar7 = FUN_0043d0ce();
        if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
          if (cVar5 == '\0') {
            local_3c = &DAT_00545cb0;
          }
          else {
            local_3c = &DAT_00545cac;
          }
          local_40 = uVar10;
          compress_log_output(0x11400000,DAT_00546610,DAT_00546610,0x240,0xbc,uVar6);
        }
        local_40 = uVar1;
        local_3c = (undefined *)uVar10;
        FUN_0047510e(&local_40);
        puVar2 = DAT_00545cf0;
        *DAT_00545cf0 = *DAT_00545cf0 & 0xffffff00 | 0x19;
        *puVar2 = *puVar2 & 0xffff00ff | 0x600;
        *puVar2 = *puVar2 & 0xffff;
        puVar2[2] = puVar2[2] & 0xffff0000 | 0x240;
        puVar2[1] = puVar2[1] & 0xffff0000 | 0x240;
        puVar2[1] = puVar2[1] & 0xffff | 0xbc0000;
        puVar2[3] = uVar10;
        puVar2[4] = uVar1;
        puVar2[5] = 0;
        puVar2[6] = 0;
        FUN_00498680(local_2c);
        FUN_00440656(local_2c);
        iVar7 = FUN_0043d0ce();
        if (iVar7 << 0x1e < 0) {
          FUN_0043d574(4,DAT_00545cc8,DAT_00545cc4,DAT_00545d04,0x1fc,DAT_00546614);
        }
        iVar7 = FUN_0043d0ce();
        if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
          compress_log_output(0x10000000,DAT_005467d8,DAT_005467d8);
        }
        uVar8 = 0;
      }
      else {
        iVar7 = FUN_0043d0ce();
        if (iVar7 << 0x1e < 0) {
          local_3c = (undefined *)0xbc;
          local_40 = 0x240;
          local_38 = uVar12;
          local_34 = uVar9;
          FUN_0043d574(1,DAT_00545cc8,DAT_00545cc4,DAT_00545d04,0x18c,DAT_005464a8);
        }
        iVar7 = FUN_0043d0ce();
        if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
          local_40 = uVar9;
          compress_log_output(0x5000000,DAT_005464ac,DAT_005464ac,0x240,0xbc,uVar12);
        }
        uVar8 = 0xffffffff;
      }
    }
    else {
      iVar7 = FUN_0043d0ce();
      if (iVar7 << 0x1e < 0) {
        local_40 = (uint)(ushort)param_2[0xe];
        FUN_0043d574(1,DAT_00545cc8,DAT_00545cc4,DAT_00545d04,0x183,DAT_00545d14);
      }
      iVar7 = FUN_0043d0ce();
      if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
        compress_log_output(0x4400000,DAT_005464a4,DAT_005464a4,param_2[0xe]);
      }
      uVar8 = 0xffffffff;
    }
  }
  else {
    iVar7 = FUN_0043d0ce();
    if (iVar7 << 0x1e < 0) {
      FUN_0043d574(1,DAT_00545cc8,DAT_00545cc4,DAT_00545d04,0x17b,DAT_00545d0c);
    }
    iVar7 = FUN_0043d0ce();
    if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_00545d10,DAT_00545d10);
    }
    uVar8 = 0xffffffff;
  }
  return uVar8;
}

