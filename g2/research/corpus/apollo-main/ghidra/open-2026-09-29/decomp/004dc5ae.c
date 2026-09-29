
undefined4 FUN_004dc5ae(int param_1,short *param_2,uint param_3,undefined4 param_4)

{
  byte bVar1;
  undefined1 uVar2;
  ushort uVar3;
  int iVar4;
  undefined4 uVar5;
  uint uVar6;
  int iVar7;
  int iVar8;
  uint uVar9;
  int iVar10;
  uint uVar11;
  uint uVar12;
  int iVar13;
  int iVar14;
  short *psVar15;
  uint local_30;
  uint local_2c;
  undefined4 uStack_28;
  
  uStack_28 = param_4;
  if ((param_1 == 0) || (param_2 == (short *)0x0)) {
    iVar4 = FUN_0043d0ce();
    if (iVar4 << 0x1e < 0) {
      FUN_0043d574(1,PTR_s_common_image_container_004dca24,DAT_004dca20,DAT_004dcc04,0xdb,
                   DAT_004dcc00,param_1,param_2);
    }
    iVar4 = FUN_0043d0ce();
    if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
      compress_log_output(0x4800000,DAT_004dcc08,DAT_004dcc08,param_1,param_2);
    }
    uVar5 = 0xffffffff;
  }
  else if (param_3 < 0x36) {
    iVar4 = FUN_0043d0ce();
    if (iVar4 << 0x1e < 0) {
      FUN_0043d574(1,PTR_s_common_image_container_004dca24,DAT_004dca20,DAT_004dcc04,0xe0,
                   DAT_004dcc0c,param_3);
    }
    iVar4 = FUN_0043d0ce();
    if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
      compress_log_output(0x4400000,DAT_004dcc10,DAT_004dcc10,param_3);
    }
    uVar5 = 0xffffffff;
  }
  else if (*param_2 == 0x4d42) {
    if (param_2[0xe] == 4) {
      uVar11 = *(uint *)(param_2 + 9);
      uVar6 = FUN_00509694(*(undefined4 *)(param_2 + 0xb));
      if ((uVar11 == *(ushort *)(param_1 + 0x40)) && (uVar6 == *(ushort *)(param_1 + 0x42))) {
        iVar4 = FUN_0043d0ce();
        if (iVar4 << 0x1e < 0) {
          FUN_0043d574(4,PTR_s_common_image_container_004dca24,DAT_004dca20,DAT_004dcc04,0x100,
                       DAT_004dcc2c,uVar11,uVar6);
        }
        iVar4 = FUN_0043d0ce();
        if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
          compress_log_output(0x10800000,DAT_004dcc30,DAT_004dcc30,uVar11,uVar6);
        }
        if (*(int *)(param_2 + 0x17) == 0) {
          uVar12 = 0x10;
        }
        else {
          uVar12 = *(uint *)(param_2 + 0x17);
        }
        psVar15 = param_2 + 0x1b;
        iVar4 = *(int *)(param_2 + 5) + (int)param_2;
        iVar7 = ((int)(uVar11 + 1) / 2 + 3) / 4 << 2;
        iVar8 = *(int *)(param_1 + 8);
        for (iVar13 = 0; iVar13 < (int)uVar6; iVar13 = iVar13 + 1) {
          for (iVar14 = 0; iVar14 < (int)uVar11; iVar14 = iVar14 + 1) {
            iVar10 = iVar13;
            if (0 < *(int *)(param_2 + 0xb)) {
              iVar10 = (uVar6 - 1) - iVar13;
            }
            bVar1 = *(byte *)(iVar4 + iVar7 * iVar10 + iVar14 / 2);
            if (iVar14 << 0x1f < 0) {
              uVar9 = bVar1 & 0xf;
            }
            else {
              uVar9 = (uint)(bVar1 >> 4);
            }
            bVar1 = (byte)uVar9;
            if (uVar12 <= uVar9) {
              bVar1 = 0;
            }
            uVar9 = (uint)bVar1;
            FUN_00441068((char)psVar15[uVar9 * 2 + 1],*(undefined1 *)((int)psVar15 + uVar9 * 4 + 1),
                         (char)psVar15[uVar9 * 2]);
            uVar2 = FUN_005456d6();
            *(undefined1 *)(iVar8 + uVar11 * iVar13 + iVar14) = uVar2;
          }
        }
        uVar3 = FUN_004dcc98(iVar8,*(undefined4 *)(param_1 + 0x44));
        iVar4 = FUN_0043d0ce();
        if (iVar4 << 0x1e < 0) {
          local_2c = *(uint *)(param_1 + 0x44);
          local_30 = (uint)uVar3;
          FUN_0043d574(4,PTR_s_common_image_container_004dca24,DAT_004dca20,DAT_004dcc04,0x138,
                       DAT_004dcc34,uVar11,uVar6);
        }
        iVar4 = FUN_0043d0ce();
        if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
          compress_log_output(0x11000000,DAT_004dcc38,DAT_004dcc38,uVar11,uVar6,uVar3,
                              *(undefined4 *)(param_1 + 0x44));
        }
        local_30 = *(uint *)(param_1 + 8);
        local_2c = *(undefined4 *)(param_1 + 0x44);
        FUN_0047510e(&local_30);
        iVar4 = FUN_0043d0ce();
        if (iVar4 << 0x1e < 0) {
          FUN_0043d574(4,PTR_s_common_image_container_004dca24,DAT_004dca20,DAT_004dcc04,0x140,
                       DAT_004dcc3c,local_30,local_2c);
        }
        iVar4 = FUN_0043d0ce();
        if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
          compress_log_output(0x10800000,DAT_004dcc40,DAT_004dcc40,local_30,local_2c);
        }
        *(uint *)(param_1 + 0x24) = *(uint *)(param_1 + 0x24) & 0xffffff00 | 0x19;
        *(uint *)(param_1 + 0x24) = *(uint *)(param_1 + 0x24) & 0xffff00ff | 0x600;
        *(uint *)(param_1 + 0x24) = *(uint *)(param_1 + 0x24) & 0xffff;
        *(uint *)(param_1 + 0x2c) =
             *(uint *)(param_1 + 0x2c) & 0xffff0000 | (uint)*(ushort *)(param_1 + 0x40);
        *(uint *)(param_1 + 0x28) =
             *(uint *)(param_1 + 0x28) & 0xffff0000 | (uint)*(ushort *)(param_1 + 0x40);
        *(uint *)(param_1 + 0x28) =
             *(uint *)(param_1 + 0x28) & 0xffff | (uint)*(ushort *)(param_1 + 0x42) << 0x10;
        *(undefined4 *)(param_1 + 0x30) = *(undefined4 *)(param_1 + 0x44);
        *(undefined4 *)(param_1 + 0x34) = *(undefined4 *)(param_1 + 8);
        *(undefined4 *)(param_1 + 0x38) = 0;
        *(undefined4 *)(param_1 + 0x3c) = 0;
        FUN_00498680(*(undefined4 *)(param_1 + 4),param_1 + 0x24);
        FUN_00440656(*(undefined4 *)(param_1 + 4));
        iVar4 = FUN_0043d0ce();
        if (iVar4 << 0x1e < 0) {
          FUN_0043d574(4,PTR_s_common_image_container_004dca24,DAT_004dca20,DAT_004dcc04,0x154,
                       DAT_004dcc44);
        }
        iVar4 = FUN_0043d0ce();
        if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
          compress_log_output(0x10000000,DAT_004dcc48,DAT_004dcc48);
        }
        uVar5 = 0;
      }
      else {
        iVar4 = FUN_0043d0ce();
        if (iVar4 << 0x1e < 0) {
          local_30 = uVar11;
          local_2c = uVar6;
          FUN_0043d574(1,PTR_s_common_image_container_004dca24,DAT_004dca20,DAT_004dcc04,0xfc,
                       DAT_004dcc24,*(undefined2 *)(param_1 + 0x40),*(undefined2 *)(param_1 + 0x42))
          ;
        }
        iVar4 = FUN_0043d0ce();
        if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
          compress_log_output(0x5000000,DAT_004dcc28,DAT_004dcc28,*(undefined2 *)(param_1 + 0x40),
                              *(undefined2 *)(param_1 + 0x42),uVar11,uVar6);
        }
        uVar5 = 0xffffffff;
      }
    }
    else {
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        FUN_0043d574(1,PTR_s_common_image_container_004dca24,DAT_004dca20,DAT_004dcc04,0xf3,
                     DAT_004dcc1c,4,param_2[0xe]);
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        compress_log_output(0x4800000,DAT_004dcc20,DAT_004dcc20,4,param_2[0xe]);
      }
      uVar5 = 0xffffffff;
    }
  }
  else {
    iVar4 = FUN_0043d0ce();
    if (iVar4 << 0x1e < 0) {
      FUN_0043d574(1,PTR_s_common_image_container_004dca24,DAT_004dca20,DAT_004dcc04,0xe8,
                   DAT_004dcc14,*param_2,0x4d42);
    }
    iVar4 = FUN_0043d0ce();
    if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
      compress_log_output(0x4800000,DAT_004dcc18,DAT_004dcc18,*param_2,0x4d42);
    }
    uVar5 = 0xffffffff;
  }
  return uVar5;
}

