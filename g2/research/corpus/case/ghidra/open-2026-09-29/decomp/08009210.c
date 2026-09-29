
int FUN_08009210(byte *param_1,uint *param_2,undefined4 param_3,code *param_4)

{
  byte bVar1;
  char cVar2;
  uint uVar3;
  int *piVar4;
  uint uVar5;
  int iVar6;
  char *pcVar7;
  int extraout_r2;
  uint uVar8;
  byte *pbVar9;
  int iVar10;
  uint uVar11;
  bool bVar12;
  longlong lVar13;
  uint local_68;
  int local_64;
  uint local_60;
  int *local_5c;
  int local_58;
  undefined4 local_54;
  byte local_50 [36];
  undefined4 *****local_2c [2];
  byte *pbStack_24;
  uint *puStack_20;
  undefined4 local_1c;
  code *local_18;
  
  local_18 = param_4;
  local_1c = param_3;
  puStack_20 = param_2;
  pbStack_24 = param_1;
  iVar10 = 0;
  do {
    while( true ) {
      bVar1 = *param_1;
      if (bVar1 == 0) {
        return iVar10;
      }
      if (bVar1 == 0x25) break;
      (*local_18)(bVar1,local_1c);
      param_1 = param_1 + 1;
      iVar10 = iVar10 + 1;
    }
    uVar8 = 0;
    local_68 = 0;
    local_60 = 0;
    while( true ) {
      pbVar9 = param_1 + 1;
      uVar3 = 1 << (*pbVar9 - 0x20 & 0xff);
      if ((uVar3 & DAT_0800960c) == 0) break;
      uVar8 = uVar8 | uVar3;
      param_1 = pbVar9;
    }
    if (*pbVar9 == 0x2a) {
      local_68 = *param_2;
      param_2 = param_2 + 1;
      if ((int)local_68 < 0) {
        uVar8 = uVar8 | 0x2000;
        local_68 = -local_68;
      }
      uVar8 = uVar8 | 2;
      pbVar9 = param_1 + 2;
    }
    else {
      for (; *pbVar9 - 0x30 < 10; pbVar9 = pbVar9 + 1) {
        local_68 = (uint)*pbVar9 + local_68 * 10 + -0x30;
        uVar8 = uVar8 | 2;
      }
    }
    if (*pbVar9 == 0x2e) {
      uVar8 = uVar8 | 4;
      if (pbVar9[1] == 0x2a) {
        local_60 = *param_2;
        param_2 = param_2 + 1;
        pbVar9 = pbVar9 + 2;
      }
      else {
        while( true ) {
          pbVar9 = pbVar9 + 1;
          if (9 < *pbVar9 - 0x30) break;
          local_60 = (uint)*pbVar9 + local_60 * 10 + -0x30;
        }
      }
    }
    bVar1 = *pbVar9;
    if (bVar1 == 0x6c) {
      uVar3 = 0x100000;
LAB_080092f4:
      uVar8 = uVar8 | uVar3;
      if (pbVar9[1] == bVar1) {
        uVar8 = uVar8 + 0x100000;
        pbVar9 = pbVar9 + 1;
      }
LAB_08009304:
      pbVar9 = pbVar9 + 1;
    }
    else {
      if (bVar1 < 0x6d) {
        if (bVar1 != 0x4c) {
          if (bVar1 == 0x68) {
            uVar3 = 0x300000;
            goto LAB_080092f4;
          }
          if (bVar1 != 0x6a) goto LAB_08009306;
          uVar8 = uVar8 | 0x200000;
        }
        goto LAB_08009304;
      }
      if ((bVar1 == 0x74) || (bVar1 == 0x7a)) goto LAB_08009304;
    }
LAB_08009306:
    bVar1 = *pbVar9;
    if (bVar1 == 0x6e) {
      uVar8 = (uVar8 & 0x7fffff) >> 0x14;
      if (uVar8 == 2) {
        piVar4 = (int *)*param_2;
        *piVar4 = iVar10;
        piVar4[1] = iVar10 >> 0x1f;
      }
      else if (uVar8 == 3) {
        *(short *)*param_2 = (short)iVar10;
      }
      else if (uVar8 == 4) {
        *(char *)*param_2 = (char)iVar10;
      }
      else {
        *(int *)*param_2 = iVar10;
      }
      param_2 = param_2 + 1;
    }
    else {
      if (bVar1 < 0x6f) {
        if (bVar1 != 99) {
          if (bVar1 < 100) {
            if (bVar1 == 0) {
              return iVar10;
            }
            if (bVar1 == 0x58) {
LAB_08009486:
              local_58 = 0x10;
              goto LAB_0800949e;
            }
          }
          else if ((bVar1 == 100) || (bVar1 == 0x69)) {
            local_58 = 10;
            local_54 = 0;
            uVar3 = (uVar8 & 0x7fffff) >> 0x14;
            if (uVar3 == 2) {
              param_2 = (uint *)((uint)((int)param_2 + 7) & 0xfffffff8);
              uVar5 = *param_2;
              uVar11 = param_2[1];
              param_2 = param_2 + 2;
            }
            else {
              uVar5 = *param_2;
              param_2 = param_2 + 1;
              if (uVar3 == 3) {
                uVar5 = (uint)(short)uVar5;
              }
              uVar11 = (int)uVar5 >> 0x1f;
              if (uVar3 == 4) {
                uVar5 = (uint)(char)uVar5;
                uVar11 = (int)uVar5 >> 0x1f;
              }
            }
            if ((int)uVar11 < 0) {
              bVar12 = uVar5 != 0;
              uVar5 = -uVar5;
              uVar11 = -(uint)bVar12 - uVar11;
              local_50[0] = 0x2d;
LAB_0800946e:
              local_64 = 1;
            }
            else {
              if ((int)(uVar8 << 0x14) < 0) {
                local_50[0] = 0x2b;
                goto LAB_0800946e;
              }
              local_64 = 0;
              if ((uVar8 & 1) != 0) {
                local_50[0] = 0x20;
                goto LAB_0800946e;
              }
            }
            goto LAB_0800952c;
          }
LAB_08009342:
          (*local_18)(bVar1,local_1c);
          iVar10 = iVar10 + 1;
          goto LAB_08009412;
        }
        local_58._0_2_ = (ushort)(byte)*param_2;
        local_5c = &local_58;
        iVar6 = 1;
LAB_08009392:
        param_2 = param_2 + 1;
        if ((int)(uVar8 << 0x1d) < 0) {
          for (local_64 = 0;
              (local_64 < (int)local_60 &&
              ((local_64 < iVar6 || (*(char *)((int)local_5c + local_64) != '\0'))));
              local_64 = local_64 + 1) {
          }
        }
        else {
          for (local_64 = 0; (local_64 < iVar6 || (*(char *)((int)local_5c + local_64) != '\0'));
              local_64 = local_64 + 1) {
          }
        }
        local_68 = local_68 - local_64;
        iVar6 = case_emit_right_padding(local_68,uVar8,local_1c,local_18);
        iVar10 = iVar6 + iVar10 + local_64;
        while (local_64 = local_64 + -1, local_64 != -1) {
          iVar6 = *local_5c;
          local_5c = (int *)((int)local_5c + 1);
          (*local_18)((char)iVar6,local_1c);
        }
      }
      else {
        if (bVar1 == 0x73) {
          local_5c = (int *)*param_2;
          iVar6 = -1;
          goto LAB_08009392;
        }
        if (bVar1 < 0x74) {
          if (bVar1 == 0x6f) {
            local_58 = 8;
            goto LAB_0800949e;
          }
          if (bVar1 != 0x70) goto LAB_08009342;
          local_58 = 0x10;
          uVar8 = uVar8 | 4;
          local_54 = 0;
          local_60 = 8;
        }
        else {
          if (bVar1 != 0x75) {
            if (bVar1 == 0x78) goto LAB_08009486;
            goto LAB_08009342;
          }
          local_58 = 10;
LAB_0800949e:
          local_54 = 0;
        }
        uVar3 = (uVar8 & 0x7fffff) >> 0x14;
        if (uVar3 == 2) {
          param_2 = (uint *)((uint)((int)param_2 + 7) & 0xfffffff8);
          uVar5 = *param_2;
          uVar11 = param_2[1];
          param_2 = param_2 + 2;
        }
        else {
          uVar5 = *param_2;
          param_2 = param_2 + 1;
          uVar11 = 0;
          if (uVar3 == 3) {
            uVar5 = uVar5 & 0xffff;
          }
          if (uVar3 == 4) {
            uVar5 = uVar5 & 0xff;
          }
        }
        local_64 = 0;
        if ((int)(uVar8 << 0x1c) < 0) {
          if (bVar1 == 0x70) {
            local_50[0] = 0x40;
            local_64 = 1;
          }
          else if ((local_58 == 0x10) && (uVar11 != 0 || uVar5 != 0)) {
            local_50[0] = 0x30;
            local_50[1] = bVar1;
            local_64 = 2;
          }
          if ((local_58 == 8) && ((uVar11 != 0 || uVar5 != 0 || ((int)(uVar8 << 0x1d) < 0)))) {
            local_50[0] = 0x30;
            local_64 = 1;
            local_60 = local_60 - 1;
          }
        }
LAB_0800952c:
        lVar13 = CONCAT44(uVar11,uVar5);
        local_54 = 0;
        if (bVar1 == 0x58) {
          pcVar7 = s_0123456789ABCDEF_08009624;
        }
        else {
          pcVar7 = s_0123456789abcdef_08009610;
        }
        local_2c[0] = local_2c;
        while( true ) {
          if (lVar13 == 0) break;
          lVar13 = FUN_08000210((int)lVar13,(int)((ulonglong)lVar13 >> 0x20),local_58,local_54);
          local_2c[0] = (undefined4 *****)((int)local_2c[0] + -1);
          *(char *)local_2c[0] = pcVar7[extraout_r2];
        }
        local_5c = (int *)((int)local_2c - (int)local_2c[0]);
        if ((int)(uVar8 << 0x1d) < 0) {
          uVar8 = uVar8 & 0xfffeffff;
        }
        else {
          local_60 = 1;
        }
        if ((int)local_5c < (int)local_60) {
          local_60 = local_60 - (int)local_5c;
        }
        else {
          local_60 = 0;
        }
        local_68 = local_68 - (local_60 + (int)local_5c + local_64);
        if (-1 < (int)(uVar8 << 0xf)) {
          iVar6 = case_emit_right_padding(local_68,uVar8,local_1c,local_18);
          iVar10 = iVar6 + iVar10;
        }
        for (local_58 = 0; local_58 < local_64; local_58 = local_58 + 1) {
          (*local_18)(local_50[local_58],local_1c);
          iVar10 = iVar10 + 1;
        }
        if ((int)(uVar8 << 0xf) < 0) {
          iVar6 = case_emit_right_padding(local_68,uVar8,local_1c,local_18);
          iVar10 = iVar6 + iVar10;
        }
        while (0 < (int)local_60) {
          (*local_18)(0x30,local_1c);
          iVar10 = iVar10 + 1;
          local_60 = local_60 + -1;
        }
        while (0 < (int)local_5c) {
          cVar2 = *(char *)local_2c[0];
          local_2c[0] = (undefined4 *****)((int)local_2c[0] + 1);
          (*local_18)(cVar2,local_1c);
          iVar10 = iVar10 + 1;
          local_5c = (int *)((int)local_5c + -1);
        }
      }
      iVar6 = case_emit_left_padding(local_68,uVar8,local_1c,local_18);
      iVar10 = iVar6 + iVar10;
    }
LAB_08009412:
    param_1 = pbVar9 + 1;
  } while( true );
}

