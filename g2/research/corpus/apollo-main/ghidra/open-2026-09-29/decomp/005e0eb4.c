
undefined4
FUN_005e0eb4(int param_1,uint param_2,undefined4 param_3,undefined4 param_4,uint param_5,
            undefined1 param_6)

{
  byte bVar1;
  byte bVar2;
  byte bVar3;
  byte bVar4;
  byte bVar5;
  short sVar6;
  int iVar7;
  undefined1 *puVar8;
  byte *pbVar9;
  undefined4 uVar10;
  uint uVar11;
  uint uVar12;
  uint uVar13;
  byte *pbVar14;
  uint uVar15;
  byte *local_30;
  uint local_2c;
  undefined4 uStack_28;
  
  local_30 = (byte *)(*(int *)(param_1 + 0x24) + *(int *)(param_1 + 0x1c));
  pbVar14 = *(byte **)(param_1 + 0x28);
  iVar7 = *(int *)(param_1 + 0x20);
  uVar12 = 0;
  uVar11 = 0;
  if (100 < param_5) {
    return 8;
  }
LAB_005e0ee6:
  if (iVar7 != 0) {
    uVar15 = (uint)CONCAT11(*local_30,local_30[1]);
    if ((param_2 < uVar15) || (CONCAT11(local_30[2],local_30[3]) < param_2)) goto LAB_005e0ede;
    uVar13 = (uint)local_30[7] |
             (uint)local_30[5] << 0x10 | (uint)local_30[4] << 0x18 | (uint)local_30[6] << 8;
    iVar7 = *(int *)(param_1 + 0x24) + *(int *)(param_1 + 0x1c);
    if ((uint)((int)pbVar14 - iVar7) < uVar13) {
      return 8;
    }
    puVar8 = (undefined1 *)(iVar7 + uVar13);
    if (puVar8 + 8 <= pbVar14) {
      sVar6 = CONCAT11(*puVar8,puVar8[1]);
      local_2c = (uint)CONCAT11(puVar8[2],puVar8[3]);
      bVar1 = puVar8[4];
      bVar2 = puVar8[5];
      bVar3 = puVar8[6];
      bVar4 = puVar8[7];
      uStack_28 = param_4;
      if (sVar6 == 1) {
        pbVar9 = puVar8 + (param_2 - uVar15) * 4 + 8;
        if (pbVar9 + 8 <= pbVar14) {
          uVar12 = (uint)pbVar9[3] |
                   (uint)pbVar9[1] << 0x10 | (uint)*pbVar9 << 0x18 | (uint)pbVar9[2] << 8;
          local_30 = pbVar9 + 8;
          uVar11 = (uint)pbVar9[7] |
                   (uint)pbVar9[5] << 0x10 | (uint)pbVar9[4] << 0x18 | (uint)pbVar9[6] << 8;
          if (uVar12 != uVar11) goto LAB_005e1074;
        }
      }
      else if (sVar6 == 2) {
        if (puVar8 + 0x14 <= pbVar14) {
          local_30 = puVar8 + 0xc;
          uVar11 = (uint)(byte)puVar8[9] << 0x10 | (uint)(byte)puVar8[8] << 0x18 |
                   (uint)(byte)puVar8[10] << 8 | (uint)(byte)puVar8[0xb];
          iVar7 = FUN_005e08d0(param_1,&local_30,pbVar14,1);
          if (iVar7 == 0) {
            uVar12 = (param_2 - uVar15) * uVar11;
            uVar11 = uVar11 + uVar12;
            goto LAB_005e1074;
          }
        }
      }
      else if (sVar6 == 3) {
        puVar8 = puVar8 + (param_2 - uVar15) * 2 + 8;
        if (puVar8 + 4 <= pbVar14) {
          uVar12 = (uint)CONCAT11(*puVar8,puVar8[1]);
          local_30 = puVar8 + 4;
          uVar11 = (uint)CONCAT11(puVar8[2],puVar8[3]);
          if (uVar12 != uVar11) goto LAB_005e1074;
        }
      }
      else if (sVar6 == 4) {
        if (puVar8 + 0xc <= pbVar14) {
          local_30 = puVar8 + 0xc;
          uVar15 = (uint)(byte)puVar8[0xb] |
                   (uint)(byte)puVar8[9] << 0x10 | (uint)(byte)puVar8[8] << 0x18 |
                   (uint)(byte)puVar8[10] << 8;
          if ((puVar8 + 0x10 <= pbVar14) && (uVar15 <= ((int)pbVar14 - (int)local_30 >> 2) - 1U)) {
            uVar13 = 0;
            goto LAB_005e1186;
          }
        }
      }
      else if (((sVar6 == 5) || (sVar6 == 0x13)) && (puVar8 + 0x18 <= pbVar14)) {
        local_30 = puVar8 + 0xc;
        uVar11 = (uint)(byte)puVar8[0xb] |
                 (uint)(byte)puVar8[9] << 0x10 | (uint)(byte)puVar8[8] << 0x18 |
                 (uint)(byte)puVar8[10] << 8;
        iVar7 = FUN_005e08d0(param_1,&local_30,pbVar14,1);
        if (iVar7 == 0) {
          uVar15 = (uint)local_30[3] |
                   (uint)local_30[1] << 0x10 | (uint)*local_30 << 0x18 | (uint)local_30[2] << 8;
          if (uVar15 <= (uint)((int)pbVar14 - (int)(local_30 + 4) >> 1)) {
            uVar12 = 0;
            local_30 = local_30 + 4;
            while ((uVar12 < uVar15 &&
                   (pbVar9 = local_30 + 2, bVar5 = *local_30, pbVar14 = local_30 + 1,
                   local_30 = pbVar9, CONCAT11(bVar5,*pbVar14) != param_2))) {
              uVar12 = uVar12 + 1;
            }
            if (uVar15 <= uVar12) goto LAB_005e0f66;
            uVar12 = uVar12 * uVar11;
            uVar11 = uVar11 + uVar12;
            goto LAB_005e1074;
          }
        }
      }
    }
  }
  goto LAB_005e0f66;
LAB_005e0ede:
  local_30 = local_30 + 8;
  iVar7 = iVar7 + -1;
  goto LAB_005e0ee6;
LAB_005e1186:
  if (uVar15 <= uVar13) {
LAB_005e11de:
    if (uVar13 < uVar15) {
LAB_005e1074:
      if (uVar12 <= uVar11) {
        uVar10 = FUN_005e0d30(param_1,local_2c,
                              uVar12 + ((uint)bVar4 |
                                       (uint)bVar2 << 0x10 | (uint)bVar1 << 0x18 | (uint)bVar3 << 8)
                              ,uVar11 - uVar12,param_3,param_4,param_5,param_6);
        return uVar10;
      }
    }
LAB_005e0f66:
    if (param_5 == 0) {
      return 0x9d;
    }
    return 0x15;
  }
  if (CONCAT11(*local_30,local_30[1]) == param_2) {
    uVar12 = (uint)CONCAT11(local_30[2],local_30[3]);
    uVar11 = (uint)CONCAT11(local_30[6],local_30[7]);
    local_30 = local_30 + 6;
    goto LAB_005e11de;
  }
  local_30 = local_30 + 4;
  uVar13 = uVar13 + 1;
  goto LAB_005e1186;
}

