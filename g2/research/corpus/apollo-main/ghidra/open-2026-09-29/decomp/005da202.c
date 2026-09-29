
void FUN_005da202(int param_1,uint param_2,uint param_3,int *param_4)

{
  uint uVar1;
  int iVar2;
  int iVar3;
  uint uVar4;
  uint uVar5;
  int iVar6;
  byte *pbVar7;
  int iVar8;
  uint uVar9;
  uint uVar10;
  uint uVar11;
  uint uVar12;
  uint uVar13;
  
  iVar8 = (int)param_2 / 0x10;
  iVar6 = iVar8 * 0x10 + param_1;
  uVar4 = param_3;
  uVar5 = param_3;
  uVar10 = param_3;
  for (iVar2 = -iVar8; iVar2 != 0; iVar2 = iVar2 + 1) {
    uVar13 = DAT_005dae2c * *(int *)(iVar6 + iVar2 * 0x10);
    uVar5 = uVar5 ^ DAT_005dae30 * (uVar13 >> 0x11 | uVar13 * 0x8000);
    uVar5 = (uVar10 + (uVar5 >> 0xd | uVar5 << 0x13)) * 5 + DAT_005dae3c;
    uVar13 = DAT_005dae30 * *(int *)(iVar6 + iVar2 * 0x10 + 4);
    uVar10 = uVar10 ^ DAT_005dae34 * (uVar13 >> 0x10 | uVar13 * 0x10000);
    uVar10 = (param_3 + (uVar10 >> 0xf | uVar10 << 0x11)) * 5 + DAT_005dae40;
    uVar13 = DAT_005dae34 * *(int *)(iVar6 + iVar2 * 0x10 + 8);
    param_3 = param_3 ^ DAT_005dae38 * (uVar13 >> 0xf | uVar13 * 0x20000);
    param_3 = (uVar4 + (param_3 >> 0x11 | param_3 << 0xf)) * 5 + DAT_005dae44;
    uVar13 = DAT_005dae38 * *(int *)(iVar6 + iVar2 * 0x10 + 0xc);
    uVar4 = DAT_005dae2c * (uVar13 >> 0xe | uVar13 * 0x40000) ^ uVar4;
    uVar4 = (uVar5 + (uVar4 >> 0x13 | uVar4 << 0xd)) * 5 + DAT_005dae48;
  }
  pbVar7 = (byte *)(param_1 + iVar8 * 0x10);
  uVar9 = 0;
  uVar11 = 0;
  uVar12 = 0;
  uVar13 = 0;
  uVar1 = param_2 & 0xf;
  if (uVar1 != 1) {
    if (uVar1 == 0) goto LAB_005da3de;
    if (uVar1 == 3) {
LAB_005da3c0:
      uVar9 = uVar9 ^ (uint)pbVar7[2] << 0x10;
    }
    else if (2 < uVar1) {
      if (uVar1 == 5) {
LAB_005da3a4:
        uVar13 = DAT_005dae30 * (pbVar7[4] ^ uVar11);
        uVar10 = DAT_005dae34 * (uVar13 >> 0x10 | uVar13 * 0x10000) ^ uVar10;
      }
      else if (4 < uVar1) {
        if (uVar1 == 7) {
LAB_005da398:
          uVar11 = uVar11 ^ (uint)pbVar7[6] << 0x10;
        }
        else if (6 < uVar1) {
          if (uVar1 == 9) {
LAB_005da37c:
            uVar13 = DAT_005dae34 * (pbVar7[8] ^ uVar12);
            param_3 = DAT_005dae38 * (uVar13 >> 0xf | uVar13 * 0x20000) ^ param_3;
          }
          else if (8 < uVar1) {
            if (uVar1 == 0xb) {
LAB_005da370:
              uVar12 = uVar12 ^ (uint)pbVar7[10] << 0x10;
            }
            else if (10 < uVar1) {
              if (uVar1 == 0xd) {
LAB_005da352:
                uVar13 = DAT_005dae38 * (pbVar7[0xc] ^ uVar13);
                uVar4 = DAT_005dae2c * (uVar13 >> 0xe | uVar13 * 0x40000) ^ uVar4;
              }
              else if (0xc < uVar1) {
                if (uVar1 == 0xf) {
                  uVar13 = (uint)pbVar7[0xe] << 0x10;
                }
                else if (0xe < uVar1) goto LAB_005da3de;
                uVar13 = uVar13 ^ (uint)pbVar7[0xd] << 8;
                goto LAB_005da352;
              }
              uVar12 = (uint)pbVar7[0xb] << 0x18;
              goto LAB_005da370;
            }
            uVar12 = uVar12 ^ (uint)pbVar7[9] << 8;
            goto LAB_005da37c;
          }
          uVar11 = (uint)pbVar7[7] << 0x18;
          goto LAB_005da398;
        }
        uVar11 = uVar11 ^ (uint)pbVar7[5] << 8;
        goto LAB_005da3a4;
      }
      uVar9 = (uint)pbVar7[3] << 0x18;
      goto LAB_005da3c0;
    }
    uVar9 = uVar9 ^ (uint)pbVar7[1] << 8;
  }
  uVar13 = DAT_005dae2c * (uVar9 ^ *pbVar7);
  uVar5 = uVar5 ^ DAT_005dae30 * (uVar13 >> 0x11 | uVar13 * 0x8000);
LAB_005da3de:
  iVar2 = (uVar4 ^ param_2) + (param_3 ^ param_2) + (uVar10 ^ param_2) + (uVar5 ^ param_2);
  iVar6 = FUN_005da1e8(iVar2);
  iVar8 = FUN_005da1e8(iVar2 + (uVar10 ^ param_2));
  iVar3 = FUN_005da1e8(iVar2 + (param_3 ^ param_2));
  iVar2 = FUN_005da1e8(iVar2 + (uVar4 ^ param_2));
  iVar6 = iVar2 + iVar3 + iVar8 + iVar6;
  *param_4 = iVar6;
  param_4[1] = iVar6 + iVar8;
  param_4[2] = iVar6 + iVar3;
  param_4[3] = iVar6 + iVar2;
  return;
}

