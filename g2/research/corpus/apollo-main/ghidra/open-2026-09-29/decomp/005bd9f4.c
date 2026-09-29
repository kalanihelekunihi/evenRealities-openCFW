
void FUN_005bd9f4(int param_1,int *param_2,undefined4 param_3,undefined4 param_4)

{
  byte bVar1;
  int iVar2;
  undefined4 uVar3;
  uint uVar4;
  undefined1 *puVar5;
  int iVar6;
  byte *pbVar7;
  byte *pbVar8;
  uint uVar9;
  uint uVar10;
  undefined1 *puVar11;
  byte *pbVar12;
  
  pbVar7 = *(byte **)(param_1 + 4);
  pbVar8 = (byte *)*param_2;
  iVar6 = param_2[1];
  uVar9 = *(uint *)(param_1 + 0x20);
  uVar10 = *(uint *)(param_1 + 0x1c);
  puVar5 = *(undefined1 **)(param_1 + 0x34);
  if (puVar5 < *(undefined1 **)(param_1 + 0x30)) {
    iVar2 = (*(int *)(param_1 + 0x30) - (int)puVar5) + -1;
  }
  else {
    iVar2 = *(int *)(param_1 + 0x2c) - (int)puVar5;
  }
LAB_005bda2c:
  do {
    while (bVar1 = *pbVar7, bVar1 == 0) {
      *(uint *)(pbVar7 + 0xc) = (uint)pbVar7[0x10];
      *(undefined4 *)(pbVar7 + 8) = *(undefined4 *)(pbVar7 + 0x14);
      *pbVar7 = 1;
LAB_005bda6c:
      for (; uVar10 < *(uint *)(pbVar7 + 0xc); uVar10 = uVar10 + 8) {
        if (iVar6 == 0) {
          *(uint *)(param_1 + 0x20) = uVar9;
          *(uint *)(param_1 + 0x1c) = uVar10;
          param_2[1] = 0;
          param_2[2] = (int)(pbVar8 + (param_2[2] - *param_2));
          *param_2 = (int)pbVar8;
          *(undefined1 **)(param_1 + 0x34) = puVar5;
          FUN_005bd8f6(param_1,param_2,param_3,puVar5,param_4);
          return;
        }
        param_3 = 0;
        iVar6 = iVar6 + -1;
        uVar9 = (uint)*pbVar8 << (uVar10 & 0xff) | uVar9;
        pbVar8 = pbVar8 + 1;
      }
      pbVar12 = (byte *)(*(int *)(pbVar7 + 8) +
                        (*(uint *)(DAT_005bdfb0 + *(uint *)(pbVar7 + 0xc) * 4) & uVar9) * 8);
      uVar9 = uVar9 >> pbVar12[1];
      uVar10 = uVar10 - pbVar12[1];
      uVar4 = (uint)*pbVar12;
      if (uVar4 == 0) {
        *(undefined4 *)(pbVar7 + 8) = *(undefined4 *)(pbVar12 + 4);
        *pbVar7 = 6;
      }
      else if ((int)(uVar4 << 0x1b) < 0) {
        *(uint *)(pbVar7 + 8) = uVar4 & 0xf;
        *(undefined4 *)(pbVar7 + 4) = *(undefined4 *)(pbVar12 + 4);
        *pbVar7 = 2;
      }
      else if ((int)(uVar4 << 0x19) < 0) {
        if (-1 < (int)(uVar4 << 0x1a)) {
          *pbVar7 = 9;
          param_2[6] = DAT_005bdfb4;
          *(uint *)(param_1 + 0x20) = uVar9;
          *(uint *)(param_1 + 0x1c) = uVar10;
          param_2[1] = iVar6;
          param_2[2] = (int)(pbVar8 + (param_2[2] - *param_2));
          *param_2 = (int)pbVar8;
          *(undefined1 **)(param_1 + 0x34) = puVar5;
          FUN_005bd8f6(param_1,param_2,0xfffffffd,puVar5,param_4);
          return;
        }
        *pbVar7 = 7;
      }
      else {
        *(uint *)(pbVar7 + 0xc) = uVar4;
        *(byte **)(pbVar7 + 8) = pbVar12 + *(int *)(pbVar12 + 4) * 8;
      }
    }
    if (bVar1 != 2) {
      if (bVar1 < 2) goto LAB_005bda6c;
      if (bVar1 == 4) {
        uVar4 = *(uint *)(pbVar7 + 8);
        for (; uVar10 < uVar4; uVar10 = uVar10 + 8) {
          if (iVar6 == 0) {
            *(uint *)(param_1 + 0x20) = uVar9;
            *(uint *)(param_1 + 0x1c) = uVar10;
            param_2[1] = 0;
            param_2[2] = (int)(pbVar8 + (param_2[2] - *param_2));
            *param_2 = (int)pbVar8;
            *(undefined1 **)(param_1 + 0x34) = puVar5;
            FUN_005bd8f6(param_1,param_2,param_3,puVar5,param_4);
            return;
          }
          param_3 = 0;
          iVar6 = iVar6 + -1;
          uVar9 = (uint)*pbVar8 << (uVar10 & 0xff) | uVar9;
          pbVar8 = pbVar8 + 1;
        }
        *(uint *)(pbVar7 + 0xc) =
             (*(uint *)(DAT_005bdfb0 + uVar4 * 4) & uVar9) + *(int *)(pbVar7 + 0xc);
        uVar9 = uVar9 >> (uVar4 & 0xff);
        uVar10 = uVar10 - uVar4;
        *pbVar7 = 5;
      }
      else {
        if (bVar1 < 4) goto LAB_005bdbc4;
        if (bVar1 == 6) {
          if (iVar2 == 0) {
            if ((puVar5 == *(undefined1 **)(param_1 + 0x2c)) &&
               (*(int *)(param_1 + 0x30) != *(int *)(param_1 + 0x28))) {
              puVar5 = *(undefined1 **)(param_1 + 0x28);
              if (puVar5 < *(undefined1 **)(param_1 + 0x30)) {
                iVar2 = (*(int *)(param_1 + 0x30) - (int)puVar5) + -1;
              }
              else {
                iVar2 = *(int *)(param_1 + 0x2c) - (int)puVar5;
              }
            }
            if (iVar2 == 0) {
              *(undefined1 **)(param_1 + 0x34) = puVar5;
              uVar3 = FUN_005bd8f6(param_1,param_2,param_3,puVar5,param_4);
              puVar5 = *(undefined1 **)(param_1 + 0x34);
              if (puVar5 < *(undefined1 **)(param_1 + 0x30)) {
                iVar2 = (*(int *)(param_1 + 0x30) - (int)puVar5) + -1;
              }
              else {
                iVar2 = *(int *)(param_1 + 0x2c) - (int)puVar5;
              }
              if ((puVar5 == *(undefined1 **)(param_1 + 0x2c)) &&
                 (*(int *)(param_1 + 0x30) != *(int *)(param_1 + 0x28))) {
                puVar5 = *(undefined1 **)(param_1 + 0x28);
                if (puVar5 < *(undefined1 **)(param_1 + 0x30)) {
                  iVar2 = (*(int *)(param_1 + 0x30) - (int)puVar5) + -1;
                }
                else {
                  iVar2 = *(int *)(param_1 + 0x2c) - (int)puVar5;
                }
              }
              if (iVar2 == 0) {
                *(uint *)(param_1 + 0x20) = uVar9;
                *(uint *)(param_1 + 0x1c) = uVar10;
                param_2[1] = iVar6;
                param_2[2] = (int)(pbVar8 + (param_2[2] - *param_2));
                *param_2 = (int)pbVar8;
                *(undefined1 **)(param_1 + 0x34) = puVar5;
                FUN_005bd8f6(param_1,param_2,uVar3,puVar5,param_4);
                return;
              }
            }
          }
          param_3 = 0;
          *puVar5 = (char)*(undefined4 *)(pbVar7 + 8);
          puVar5 = puVar5 + 1;
          iVar2 = iVar2 + -1;
          *pbVar7 = 0;
          goto LAB_005bda2c;
        }
        if (5 < bVar1) {
          if (bVar1 != 8) {
            if (7 < bVar1) {
              if (bVar1 != 9) {
                *(uint *)(param_1 + 0x20) = uVar9;
                *(uint *)(param_1 + 0x1c) = uVar10;
                param_2[1] = iVar6;
                param_2[2] = (int)(pbVar8 + (param_2[2] - *param_2));
                *param_2 = (int)pbVar8;
                *(undefined1 **)(param_1 + 0x34) = puVar5;
                FUN_005bd8f6(param_1,param_2,0xfffffffe,puVar5,param_4);
                return;
              }
              *(uint *)(param_1 + 0x20) = uVar9;
              *(uint *)(param_1 + 0x1c) = uVar10;
              param_2[1] = iVar6;
              param_2[2] = (int)(pbVar8 + (param_2[2] - *param_2));
              *param_2 = (int)pbVar8;
              *(undefined1 **)(param_1 + 0x34) = puVar5;
              FUN_005bd8f6(param_1,param_2,0xfffffffd,puVar5,param_4);
              return;
            }
            if (7 < uVar10) {
              uVar10 = uVar10 - 8;
              iVar6 = iVar6 + 1;
              pbVar8 = pbVar8 + -1;
            }
            *(undefined1 **)(param_1 + 0x34) = puVar5;
            uVar3 = FUN_005bd8f6(param_1,param_2,param_3,puVar5,param_4);
            puVar5 = *(undefined1 **)(param_1 + 0x34);
            if (*(int *)(param_1 + 0x30) != *(int *)(param_1 + 0x34)) {
              *(uint *)(param_1 + 0x20) = uVar9;
              *(uint *)(param_1 + 0x1c) = uVar10;
              param_2[1] = iVar6;
              param_2[2] = (int)(pbVar8 + (param_2[2] - *param_2));
              *param_2 = (int)pbVar8;
              *(undefined1 **)(param_1 + 0x34) = puVar5;
              FUN_005bd8f6(param_1,param_2,uVar3,puVar5,param_4);
              return;
            }
            *pbVar7 = 8;
          }
          *(uint *)(param_1 + 0x20) = uVar9;
          *(uint *)(param_1 + 0x1c) = uVar10;
          param_2[1] = iVar6;
          param_2[2] = (int)(pbVar8 + (param_2[2] - *param_2));
          *param_2 = (int)pbVar8;
          *(undefined1 **)(param_1 + 0x34) = puVar5;
          FUN_005bd8f6(param_1,param_2,1,puVar5,param_4);
          return;
        }
      }
      for (puVar11 = puVar5 + -*(int *)(pbVar7 + 0xc); puVar11 < *(undefined1 **)(param_1 + 0x28);
          puVar11 = puVar11 + (*(int *)(param_1 + 0x2c) - *(int *)(param_1 + 0x28))) {
      }
      while (*(int *)(pbVar7 + 4) != 0) {
        if (iVar2 == 0) {
          if ((puVar5 == *(undefined1 **)(param_1 + 0x2c)) &&
             (*(int *)(param_1 + 0x30) != *(int *)(param_1 + 0x28))) {
            puVar5 = *(undefined1 **)(param_1 + 0x28);
            if (puVar5 < *(undefined1 **)(param_1 + 0x30)) {
              iVar2 = (*(int *)(param_1 + 0x30) - (int)puVar5) + -1;
            }
            else {
              iVar2 = *(int *)(param_1 + 0x2c) - (int)puVar5;
            }
          }
          if (iVar2 == 0) {
            *(undefined1 **)(param_1 + 0x34) = puVar5;
            uVar3 = FUN_005bd8f6(param_1,param_2,param_3,puVar5,param_4);
            puVar5 = *(undefined1 **)(param_1 + 0x34);
            if (puVar5 < *(undefined1 **)(param_1 + 0x30)) {
              iVar2 = (*(int *)(param_1 + 0x30) - (int)puVar5) + -1;
            }
            else {
              iVar2 = *(int *)(param_1 + 0x2c) - (int)puVar5;
            }
            if ((puVar5 == *(undefined1 **)(param_1 + 0x2c)) &&
               (*(int *)(param_1 + 0x30) != *(int *)(param_1 + 0x28))) {
              puVar5 = *(undefined1 **)(param_1 + 0x28);
              if (puVar5 < *(undefined1 **)(param_1 + 0x30)) {
                iVar2 = (*(int *)(param_1 + 0x30) - (int)puVar5) + -1;
              }
              else {
                iVar2 = *(int *)(param_1 + 0x2c) - (int)puVar5;
              }
            }
            if (iVar2 == 0) {
              *(uint *)(param_1 + 0x20) = uVar9;
              *(uint *)(param_1 + 0x1c) = uVar10;
              param_2[1] = iVar6;
              param_2[2] = (int)(pbVar8 + (param_2[2] - *param_2));
              *param_2 = (int)pbVar8;
              *(undefined1 **)(param_1 + 0x34) = puVar5;
              FUN_005bd8f6(param_1,param_2,uVar3,puVar5,param_4);
              return;
            }
          }
        }
        param_3 = 0;
        *puVar5 = *puVar11;
        puVar11 = puVar11 + 1;
        puVar5 = puVar5 + 1;
        iVar2 = iVar2 + -1;
        if (puVar11 == *(undefined1 **)(param_1 + 0x2c)) {
          puVar11 = *(undefined1 **)(param_1 + 0x28);
        }
        *(int *)(pbVar7 + 4) = *(int *)(pbVar7 + 4) + -1;
      }
      *pbVar7 = 0;
      goto LAB_005bda2c;
    }
    uVar4 = *(uint *)(pbVar7 + 8);
    for (; uVar10 < uVar4; uVar10 = uVar10 + 8) {
      if (iVar6 == 0) {
        *(uint *)(param_1 + 0x20) = uVar9;
        *(uint *)(param_1 + 0x1c) = uVar10;
        param_2[1] = 0;
        param_2[2] = (int)(pbVar8 + (param_2[2] - *param_2));
        *param_2 = (int)pbVar8;
        *(undefined1 **)(param_1 + 0x34) = puVar5;
        FUN_005bd8f6(param_1,param_2,param_3,puVar5,param_4);
        return;
      }
      param_3 = 0;
      iVar6 = iVar6 + -1;
      uVar9 = (uint)*pbVar8 << (uVar10 & 0xff) | uVar9;
      pbVar8 = pbVar8 + 1;
    }
    *(uint *)(pbVar7 + 4) = (*(uint *)(DAT_005bdfb0 + uVar4 * 4) & uVar9) + *(int *)(pbVar7 + 4);
    uVar9 = uVar9 >> (uVar4 & 0xff);
    uVar10 = uVar10 - uVar4;
    *(uint *)(pbVar7 + 0xc) = (uint)pbVar7[0x11];
    *(undefined4 *)(pbVar7 + 8) = *(undefined4 *)(pbVar7 + 0x18);
    *pbVar7 = 3;
LAB_005bdbc4:
    for (; uVar10 < *(uint *)(pbVar7 + 0xc); uVar10 = uVar10 + 8) {
      if (iVar6 == 0) {
        *(uint *)(param_1 + 0x20) = uVar9;
        *(uint *)(param_1 + 0x1c) = uVar10;
        param_2[1] = 0;
        param_2[2] = (int)(pbVar8 + (param_2[2] - *param_2));
        *param_2 = (int)pbVar8;
        *(undefined1 **)(param_1 + 0x34) = puVar5;
        FUN_005bd8f6(param_1,param_2,param_3,puVar5,param_4);
        return;
      }
      param_3 = 0;
      iVar6 = iVar6 + -1;
      uVar9 = (uint)*pbVar8 << (uVar10 & 0xff) | uVar9;
      pbVar8 = pbVar8 + 1;
    }
    pbVar12 = (byte *)(*(int *)(pbVar7 + 8) +
                      (*(uint *)(DAT_005bdfb0 + *(uint *)(pbVar7 + 0xc) * 4) & uVar9) * 8);
    uVar9 = uVar9 >> pbVar12[1];
    uVar10 = uVar10 - pbVar12[1];
    uVar4 = (uint)*pbVar12;
    if ((int)(uVar4 << 0x1b) < 0) {
      *(uint *)(pbVar7 + 8) = uVar4 & 0xf;
      *(undefined4 *)(pbVar7 + 0xc) = *(undefined4 *)(pbVar12 + 4);
      *pbVar7 = 4;
    }
    else {
      if ((int)(uVar4 << 0x19) < 0) {
        *pbVar7 = 9;
        param_2[6] = DAT_005bdfb8;
        *(uint *)(param_1 + 0x20) = uVar9;
        *(uint *)(param_1 + 0x1c) = uVar10;
        param_2[1] = iVar6;
        param_2[2] = (int)(pbVar8 + (param_2[2] - *param_2));
        *param_2 = (int)pbVar8;
        *(undefined1 **)(param_1 + 0x34) = puVar5;
        FUN_005bd8f6(param_1,param_2,0xfffffffd,puVar5,param_4);
        return;
      }
      *(uint *)(pbVar7 + 0xc) = uVar4;
      *(byte **)(pbVar7 + 8) = pbVar12 + *(int *)(pbVar12 + 4) * 8;
    }
  } while( true );
}

