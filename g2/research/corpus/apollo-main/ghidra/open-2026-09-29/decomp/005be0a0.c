
void FUN_005be0a0(byte *param_1,int *param_2,undefined4 param_3,undefined4 param_4)

{
  byte bVar1;
  uint uVar2;
  int iVar3;
  undefined4 uVar4;
  uint uVar5;
  int iVar6;
  uint uVar7;
  byte *pbVar8;
  uint uVar9;
  uint uVar10;
  uint uVar11;
  uint uVar12;
  undefined4 local_4c;
  int *local_48;
  undefined4 local_44;
  undefined4 local_40;
  undefined4 local_3c;
  undefined4 local_38;
  undefined4 local_34;
  undefined4 local_30;
  uint local_2c;
  undefined4 uStack_28;
  
  pbVar8 = (byte *)*param_2;
  uVar7 = param_2[1];
  uVar10 = *(uint *)(param_1 + 0x20);
  uVar11 = *(uint *)(param_1 + 0x1c);
  uVar9 = *(uint *)(param_1 + 0x34);
  uStack_28 = param_4;
  if (uVar9 < *(uint *)(param_1 + 0x30)) {
    uVar2 = (*(int *)(param_1 + 0x30) - uVar9) - 1;
  }
  else {
    uVar2 = *(int *)(param_1 + 0x2c) - uVar9;
  }
  do {
    while( true ) {
      while( true ) {
        while (bVar1 = *param_1, bVar1 == 0) {
          for (; uVar11 < 3; uVar11 = uVar11 + 8) {
            if (uVar7 == 0) {
              *(uint *)(param_1 + 0x20) = uVar10;
              *(uint *)(param_1 + 0x1c) = uVar11;
              param_2[1] = 0;
              param_2[2] = (int)(pbVar8 + (param_2[2] - *param_2));
              *param_2 = (int)pbVar8;
              *(uint *)(param_1 + 0x34) = uVar9;
              FUN_005bd8f6(param_1,param_2,param_3);
              return;
            }
            param_3 = 0;
            uVar7 = uVar7 - 1;
            uVar10 = (uint)*pbVar8 << (uVar11 & 0xff) | uVar10;
            pbVar8 = pbVar8 + 1;
          }
          *(uint *)(param_1 + 0x18) = uVar10 & 1;
          uVar12 = (uVar10 & 7) >> 1;
          if (uVar12 == 0) {
            uVar12 = uVar11 - 3 & 7;
            uVar10 = (uVar10 >> 3) >> uVar12;
            uVar11 = (uVar11 - 3) - uVar12;
            *param_1 = 1;
          }
          else if (uVar12 == 2) {
            uVar10 = uVar10 >> 3;
            uVar11 = uVar11 - 3;
            *param_1 = 3;
          }
          else if (uVar12 < 2) {
            FUN_005bd8d2(&local_30,&local_34,&local_48,&local_4c,param_2);
            uVar4 = FUN_005bd9cc(local_30,local_34,local_48,local_4c,param_2);
            *(undefined4 *)(param_1 + 4) = uVar4;
            if (*(int *)(param_1 + 4) == 0) {
              *(uint *)(param_1 + 0x20) = uVar10;
              *(uint *)(param_1 + 0x1c) = uVar11;
              param_2[1] = uVar7;
              param_2[2] = (int)(pbVar8 + (param_2[2] - *param_2));
              *param_2 = (int)pbVar8;
              *(uint *)(param_1 + 0x34) = uVar9;
              FUN_005bd8f6(param_1,param_2,0xfffffffc);
              return;
            }
            uVar10 = uVar10 >> 3;
            uVar11 = uVar11 - 3;
            *param_1 = 6;
          }
          else if (uVar12 == 3) {
            *param_1 = 9;
            param_2[6] = DAT_005beef4;
            *(uint *)(param_1 + 0x20) = uVar10 >> 3;
            *(uint *)(param_1 + 0x1c) = uVar11 - 3;
            param_2[1] = uVar7;
            param_2[2] = (int)(pbVar8 + (param_2[2] - *param_2));
            *param_2 = (int)pbVar8;
            *(uint *)(param_1 + 0x34) = uVar9;
            FUN_005bd8f6(param_1,param_2,0xfffffffd);
            return;
          }
        }
        if (bVar1 != 2) break;
        if (uVar7 == 0) {
          *(uint *)(param_1 + 0x20) = uVar10;
          *(uint *)(param_1 + 0x1c) = uVar11;
          param_2[1] = 0;
          param_2[2] = (int)(pbVar8 + (param_2[2] - *param_2));
          *param_2 = (int)pbVar8;
          *(uint *)(param_1 + 0x34) = uVar9;
          FUN_005bd8f6(param_1,param_2,param_3);
          return;
        }
        if (uVar2 == 0) {
          if ((uVar9 == *(uint *)(param_1 + 0x2c)) &&
             (*(int *)(param_1 + 0x30) != *(int *)(param_1 + 0x28))) {
            uVar9 = *(uint *)(param_1 + 0x28);
            if (uVar9 < *(uint *)(param_1 + 0x30)) {
              uVar2 = (*(int *)(param_1 + 0x30) - uVar9) - 1;
            }
            else {
              uVar2 = *(int *)(param_1 + 0x2c) - uVar9;
            }
          }
          if (uVar2 == 0) {
            *(uint *)(param_1 + 0x34) = uVar9;
            uVar4 = FUN_005bd8f6(param_1,param_2,param_3);
            uVar9 = *(uint *)(param_1 + 0x34);
            if (uVar9 < *(uint *)(param_1 + 0x30)) {
              uVar2 = (*(int *)(param_1 + 0x30) - uVar9) - 1;
            }
            else {
              uVar2 = *(int *)(param_1 + 0x2c) - uVar9;
            }
            if ((uVar9 == *(uint *)(param_1 + 0x2c)) &&
               (*(int *)(param_1 + 0x30) != *(int *)(param_1 + 0x28))) {
              uVar9 = *(uint *)(param_1 + 0x28);
              if (uVar9 < *(uint *)(param_1 + 0x30)) {
                uVar2 = (*(int *)(param_1 + 0x30) - uVar9) - 1;
              }
              else {
                uVar2 = *(int *)(param_1 + 0x2c) - uVar9;
              }
            }
            if (uVar2 == 0) {
              *(uint *)(param_1 + 0x20) = uVar10;
              *(uint *)(param_1 + 0x1c) = uVar11;
              param_2[1] = uVar7;
              param_2[2] = (int)(pbVar8 + (param_2[2] - *param_2));
              *param_2 = (int)pbVar8;
              *(uint *)(param_1 + 0x34) = uVar9;
              FUN_005bd8f6(param_1,param_2,uVar4);
              return;
            }
          }
        }
        param_3 = 0;
        uVar12 = *(uint *)(param_1 + 4);
        if (uVar7 < *(uint *)(param_1 + 4)) {
          uVar12 = uVar7;
        }
        if (uVar2 < uVar12) {
          uVar12 = uVar2;
        }
        local_2c = uVar12;
        FUN_00439be4(uVar9,pbVar8,uVar12);
        pbVar8 = pbVar8 + uVar12;
        uVar7 = uVar7 - uVar12;
        uVar9 = uVar9 + uVar12;
        uVar2 = uVar2 - uVar12;
        *(uint *)(param_1 + 4) = *(int *)(param_1 + 4) - uVar12;
        if (*(int *)(param_1 + 4) == 0) {
          if (*(int *)(param_1 + 0x18) == 0) {
            bVar1 = 0;
          }
          else {
            bVar1 = 7;
          }
          *param_1 = bVar1;
        }
      }
      if (1 < bVar1) break;
      for (; uVar11 < 0x20; uVar11 = uVar11 + 8) {
        if (uVar7 == 0) {
          *(uint *)(param_1 + 0x20) = uVar10;
          *(uint *)(param_1 + 0x1c) = uVar11;
          param_2[1] = 0;
          param_2[2] = (int)(pbVar8 + (param_2[2] - *param_2));
          *param_2 = (int)pbVar8;
          *(uint *)(param_1 + 0x34) = uVar9;
          FUN_005bd8f6(param_1,param_2,param_3);
          return;
        }
        param_3 = 0;
        uVar7 = uVar7 - 1;
        uVar10 = (uint)*pbVar8 << (uVar11 & 0xff) | uVar10;
        pbVar8 = pbVar8 + 1;
      }
      if (~uVar10 >> 0x10 != (uVar10 & 0xffff)) {
        *param_1 = 9;
        param_2[6] = DAT_005beef8;
        *(uint *)(param_1 + 0x20) = uVar10;
        *(uint *)(param_1 + 0x1c) = uVar11;
        param_2[1] = uVar7;
        param_2[2] = (int)(pbVar8 + (param_2[2] - *param_2));
        *param_2 = (int)pbVar8;
        *(uint *)(param_1 + 0x34) = uVar9;
        FUN_005bd8f6(param_1,param_2,0xfffffffd);
        return;
      }
      *(uint *)(param_1 + 4) = uVar10 & 0xffff;
      uVar11 = 0;
      uVar10 = 0;
      if (*(int *)(param_1 + 4) == 0) {
        if (*(int *)(param_1 + 0x18) == 0) {
          bVar1 = 0;
        }
        else {
          bVar1 = 7;
        }
      }
      else {
        bVar1 = 2;
      }
      *param_1 = bVar1;
    }
    if (bVar1 != 4) {
      if (bVar1 < 4) {
        for (; uVar11 < 0xe; uVar11 = uVar11 + 8) {
          if (uVar7 == 0) {
            *(uint *)(param_1 + 0x20) = uVar10;
            *(uint *)(param_1 + 0x1c) = uVar11;
            param_2[1] = 0;
            param_2[2] = (int)(pbVar8 + (param_2[2] - *param_2));
            *param_2 = (int)pbVar8;
            *(uint *)(param_1 + 0x34) = uVar9;
            FUN_005bd8f6(param_1,param_2,param_3);
            return;
          }
          param_3 = 0;
          uVar7 = uVar7 - 1;
          uVar10 = (uint)*pbVar8 << (uVar11 & 0xff) | uVar10;
          pbVar8 = pbVar8 + 1;
        }
        *(uint *)(param_1 + 4) = uVar10 & 0x3fff;
        if ((0x1d < (uVar10 & 0x1f)) || (0x1d < (uVar10 & 0x3ff) >> 5)) {
          *param_1 = 9;
          param_2[6] = DAT_005beff4;
          *(uint *)(param_1 + 0x20) = uVar10;
          *(uint *)(param_1 + 0x1c) = uVar11;
          param_2[1] = uVar7;
          param_2[2] = (int)(pbVar8 + (param_2[2] - *param_2));
          *param_2 = (int)pbVar8;
          *(uint *)(param_1 + 0x34) = uVar9;
          FUN_005bd8f6(param_1,param_2,0xfffffffd);
          return;
        }
        uVar4 = (*(code *)param_2[8])
                          (param_2[10],((uVar10 & 0x3ff) >> 5) + (uVar10 & 0x1f) + 0x102,4);
        *(undefined4 *)(param_1 + 0xc) = uVar4;
        if (*(int *)(param_1 + 0xc) == 0) {
          *(uint *)(param_1 + 0x20) = uVar10;
          *(uint *)(param_1 + 0x1c) = uVar11;
          param_2[1] = uVar7;
          param_2[2] = (int)(pbVar8 + (param_2[2] - *param_2));
          *param_2 = (int)pbVar8;
          *(uint *)(param_1 + 0x34) = uVar9;
          FUN_005bd8f6(param_1,param_2,0xfffffffc);
          return;
        }
        uVar10 = uVar10 >> 0xe;
        uVar11 = uVar11 - 0xe;
        param_1[8] = 0;
        param_1[9] = 0;
        param_1[10] = 0;
        param_1[0xb] = 0;
        *param_1 = 4;
        goto LAB_005be5a0;
      }
      if (bVar1 == 6) goto LAB_005be70a;
      if (bVar1 < 6) goto LAB_005be68e;
      if (bVar1 == 8) goto LAB_005be9c4;
      if (7 < bVar1) {
        if (bVar1 != 9) {
          *(uint *)(param_1 + 0x20) = uVar10;
          *(uint *)(param_1 + 0x1c) = uVar11;
          param_2[1] = uVar7;
          param_2[2] = (int)(pbVar8 + (param_2[2] - *param_2));
          *param_2 = (int)pbVar8;
          *(uint *)(param_1 + 0x34) = uVar9;
          FUN_005bd8f6(param_1,param_2,0xfffffffe);
          return;
        }
        *(uint *)(param_1 + 0x20) = uVar10;
        *(uint *)(param_1 + 0x1c) = uVar11;
        param_2[1] = uVar7;
        param_2[2] = (int)(pbVar8 + (param_2[2] - *param_2));
        *param_2 = (int)pbVar8;
        *(uint *)(param_1 + 0x34) = uVar9;
        FUN_005bd8f6(param_1,param_2,0xfffffffd);
        return;
      }
LAB_005be966:
      *(uint *)(param_1 + 0x34) = uVar9;
      uVar4 = FUN_005bd8f6(param_1,param_2,param_3);
      uVar9 = *(uint *)(param_1 + 0x34);
      if (*(int *)(param_1 + 0x30) != *(int *)(param_1 + 0x34)) {
        *(uint *)(param_1 + 0x20) = uVar10;
        *(uint *)(param_1 + 0x1c) = uVar11;
        param_2[1] = uVar7;
        param_2[2] = (int)(pbVar8 + (param_2[2] - *param_2));
        *param_2 = (int)pbVar8;
        *(uint *)(param_1 + 0x34) = uVar9;
        FUN_005bd8f6(param_1,param_2,uVar4);
        return;
      }
      *param_1 = 8;
LAB_005be9c4:
      *(uint *)(param_1 + 0x20) = uVar10;
      *(uint *)(param_1 + 0x1c) = uVar11;
      param_2[1] = uVar7;
      param_2[2] = (int)(pbVar8 + (param_2[2] - *param_2));
      *param_2 = (int)pbVar8;
      *(uint *)(param_1 + 0x34) = uVar9;
      FUN_005bd8f6(param_1,param_2,1);
      return;
    }
LAB_005be5a0:
    while (*(uint *)(param_1 + 8) < (*(uint *)(param_1 + 4) >> 10) + 4) {
      for (; uVar11 < 3; uVar11 = uVar11 + 8) {
        if (uVar7 == 0) {
          *(uint *)(param_1 + 0x20) = uVar10;
          *(uint *)(param_1 + 0x1c) = uVar11;
          param_2[1] = 0;
          param_2[2] = (int)(pbVar8 + (param_2[2] - *param_2));
          *param_2 = (int)pbVar8;
          *(uint *)(param_1 + 0x34) = uVar9;
          FUN_005bd8f6(param_1,param_2,param_3);
          return;
        }
        param_3 = 0;
        uVar7 = uVar7 - 1;
        uVar10 = (uint)*pbVar8 << (uVar11 & 0xff) | uVar10;
        pbVar8 = pbVar8 + 1;
      }
      iVar3 = *(int *)(param_1 + 8);
      *(int *)(param_1 + 8) = iVar3 + 1;
      *(uint *)(*(int *)(param_1 + 0xc) + *(int *)(DAT_005beff8 + iVar3 * 4) * 4) = uVar10 & 7;
      uVar10 = uVar10 >> 3;
      uVar11 = uVar11 - 3;
    }
    while (*(uint *)(param_1 + 8) < 0x13) {
      iVar3 = *(int *)(param_1 + 8);
      *(int *)(param_1 + 8) = iVar3 + 1;
      *(undefined4 *)(*(int *)(param_1 + 0xc) + *(int *)(DAT_005beff8 + iVar3 * 4) * 4) = 0;
    }
    param_1[0x10] = 7;
    param_1[0x11] = 0;
    param_1[0x12] = 0;
    param_1[0x13] = 0;
    iVar3 = FUN_005bd738(*(undefined4 *)(param_1 + 0xc),param_1 + 0x10,param_1 + 0x14,
                         *(undefined4 *)(param_1 + 0x24),param_2);
    if (iVar3 != 0) {
      if (iVar3 == -3) {
        (*(code *)param_2[9])(param_2[10],*(undefined4 *)(param_1 + 0xc));
        *param_1 = 9;
      }
      *(uint *)(param_1 + 0x20) = uVar10;
      *(uint *)(param_1 + 0x1c) = uVar11;
      param_2[1] = uVar7;
      param_2[2] = (int)(pbVar8 + (param_2[2] - *param_2));
      *param_2 = (int)pbVar8;
      *(uint *)(param_1 + 0x34) = uVar9;
      FUN_005bd8f6(param_1,param_2,iVar3);
      return;
    }
    param_1[8] = 0;
    param_1[9] = 0;
    param_1[10] = 0;
    param_1[0xb] = 0;
    *param_1 = 5;
LAB_005be68e:
    while (*(uint *)(param_1 + 8) <
           ((*(uint *)(param_1 + 4) & 0x3ff) >> 5) + (*(uint *)(param_1 + 4) & 0x1f) + 0x102) {
      for (; uVar11 < *(uint *)(param_1 + 0x10); uVar11 = uVar11 + 8) {
        if (uVar7 == 0) {
          *(uint *)(param_1 + 0x20) = uVar10;
          *(uint *)(param_1 + 0x1c) = uVar11;
          param_2[1] = 0;
          param_2[2] = (int)(pbVar8 + (param_2[2] - *param_2));
          *param_2 = (int)pbVar8;
          *(uint *)(param_1 + 0x34) = uVar9;
          FUN_005bd8f6(param_1,param_2,param_3);
          return;
        }
        param_3 = 0;
        uVar7 = uVar7 - 1;
        uVar10 = (uint)*pbVar8 << (uVar11 & 0xff) | uVar10;
        pbVar8 = pbVar8 + 1;
      }
      iVar3 = *(int *)(param_1 + 0x14) +
              (*(uint *)(DAT_005beffc + *(uint *)(param_1 + 0x10) * 4) & uVar10) * 8;
      uVar12 = (uint)*(byte *)(iVar3 + 1);
      uVar2 = *(uint *)(iVar3 + 4);
      if (uVar2 < 0x10) {
        uVar10 = uVar10 >> uVar12;
        uVar11 = uVar11 - uVar12;
        iVar3 = *(int *)(param_1 + 8);
        *(int *)(param_1 + 8) = iVar3 + 1;
        *(uint *)(*(int *)(param_1 + 0xc) + iVar3 * 4) = uVar2;
      }
      else {
        if (uVar2 == 0x12) {
          uVar5 = 7;
          iVar3 = 0xb;
        }
        else {
          uVar5 = uVar2 - 0xe;
          iVar3 = 3;
        }
        for (; uVar11 < uVar5 + uVar12; uVar11 = uVar11 + 8) {
          if (uVar7 == 0) {
            *(uint *)(param_1 + 0x20) = uVar10;
            *(uint *)(param_1 + 0x1c) = uVar11;
            param_2[1] = 0;
            param_2[2] = (int)(pbVar8 + (param_2[2] - *param_2));
            *param_2 = (int)pbVar8;
            *(uint *)(param_1 + 0x34) = uVar9;
            FUN_005bd8f6(param_1,param_2,param_3);
            return;
          }
          param_3 = 0;
          uVar7 = uVar7 - 1;
          uVar10 = (uint)*pbVar8 << (uVar11 & 0xff) | uVar10;
          pbVar8 = pbVar8 + 1;
        }
        iVar3 = (*(uint *)(DAT_005beffc + uVar5 * 4) & uVar10 >> uVar12) + iVar3;
        uVar10 = (uVar10 >> uVar12) >> (uVar5 & 0xff);
        uVar11 = (uVar11 - uVar12) - uVar5;
        iVar6 = *(int *)(param_1 + 8);
        if ((((*(uint *)(param_1 + 4) & 0x3ff) >> 5) + (*(uint *)(param_1 + 4) & 0x1f) + 0x102 <
             (uint)(iVar3 + iVar6)) || ((uVar2 == 0x10 && (iVar6 == 0)))) {
          (*(code *)param_2[9])(param_2[10],*(undefined4 *)(param_1 + 0xc));
          *param_1 = 9;
          param_2[6] = DAT_005bf000;
          *(uint *)(param_1 + 0x20) = uVar10;
          *(uint *)(param_1 + 0x1c) = uVar11;
          param_2[1] = uVar7;
          param_2[2] = (int)(pbVar8 + (param_2[2] - *param_2));
          *param_2 = (int)pbVar8;
          *(uint *)(param_1 + 0x34) = uVar9;
          FUN_005bd8f6(param_1,param_2,0xfffffffd);
          return;
        }
        if (uVar2 == 0x10) {
          uVar4 = *(undefined4 *)(*(int *)(param_1 + 0xc) + iVar6 * 4 + -4);
        }
        else {
          uVar4 = 0;
        }
        do {
          *(undefined4 *)(*(int *)(param_1 + 0xc) + iVar6 * 4) = uVar4;
          iVar6 = iVar6 + 1;
          iVar3 = iVar3 + -1;
        } while (iVar3 != 0);
        *(int *)(param_1 + 8) = iVar6;
      }
    }
    param_1[0x14] = 0;
    param_1[0x15] = 0;
    param_1[0x16] = 0;
    param_1[0x17] = 0;
    local_40 = 9;
    local_44 = 6;
    local_4c = *(undefined4 *)(param_1 + 0x24);
    local_48 = param_2;
    iVar3 = FUN_005bd7b8((*(uint *)(param_1 + 4) & 0x1f) + 0x101,
                         ((*(uint *)(param_1 + 4) & 0x3ff) >> 5) + 1,*(undefined4 *)(param_1 + 0xc),
                         &local_40,&local_44,&local_38,&local_3c);
    if (iVar3 != 0) {
      if (iVar3 == -3) {
        (*(code *)param_2[9])(param_2[10],*(undefined4 *)(param_1 + 0xc));
        *param_1 = 9;
      }
      *(uint *)(param_1 + 0x20) = uVar10;
      *(uint *)(param_1 + 0x1c) = uVar11;
      param_2[1] = uVar7;
      param_2[2] = (int)(pbVar8 + (param_2[2] - *param_2));
      *param_2 = (int)pbVar8;
      *(uint *)(param_1 + 0x34) = uVar9;
      FUN_005bd8f6(param_1,param_2,iVar3);
      return;
    }
    iVar3 = FUN_005bd9cc(local_40,local_44,local_38,local_3c,param_2);
    if (iVar3 == 0) {
      *(uint *)(param_1 + 0x20) = uVar10;
      *(uint *)(param_1 + 0x1c) = uVar11;
      param_2[1] = uVar7;
      param_2[2] = (int)(pbVar8 + (param_2[2] - *param_2));
      *param_2 = (int)pbVar8;
      *(uint *)(param_1 + 0x34) = uVar9;
      FUN_005bd8f6(param_1,param_2,0xfffffffc);
      return;
    }
    *(int *)(param_1 + 4) = iVar3;
    (*(code *)param_2[9])(param_2[10],*(undefined4 *)(param_1 + 0xc));
    *param_1 = 6;
LAB_005be70a:
    *(uint *)(param_1 + 0x20) = uVar10;
    *(uint *)(param_1 + 0x1c) = uVar11;
    param_2[1] = uVar7;
    param_2[2] = (int)(pbVar8 + (param_2[2] - *param_2));
    *param_2 = (int)pbVar8;
    *(uint *)(param_1 + 0x34) = uVar9;
    iVar3 = FUN_005bd9f4(param_1,param_2,param_3);
    if (iVar3 != 1) {
      FUN_005bd8f6(param_1,param_2,iVar3);
      return;
    }
    param_3 = 0;
    FUN_005bdfbc(*(undefined4 *)(param_1 + 4),param_2);
    pbVar8 = (byte *)*param_2;
    uVar7 = param_2[1];
    uVar10 = *(uint *)(param_1 + 0x20);
    uVar11 = *(uint *)(param_1 + 0x1c);
    uVar9 = *(uint *)(param_1 + 0x34);
    if (uVar9 < *(uint *)(param_1 + 0x30)) {
      uVar2 = (*(int *)(param_1 + 0x30) - uVar9) - 1;
    }
    else {
      uVar2 = *(int *)(param_1 + 0x2c) - uVar9;
    }
    if (*(int *)(param_1 + 0x18) != 0) {
      *param_1 = 7;
      goto LAB_005be966;
    }
    *param_1 = 0;
  } while( true );
}

