
undefined8 FUN_0058ee9e(undefined4 *param_1,uint *param_2,uint *param_3,int param_4)

{
  byte bVar1;
  undefined4 uVar2;
  uint uVar3;
  uint *puVar4;
  uint uVar5;
  int iVar6;
  int iVar7;
  uint uVar8;
  byte *pbVar9;
  byte *pbVar10;
  byte *pbVar11;
  byte *pbVar12;
  int local_28;
  
  local_28 = 0;
  puVar4 = param_2;
  if (param_1 == (undefined4 *)0x0) {
    local_28 = 0x21;
  }
  else if ((param_2 == (uint *)0x0) || (param_3 == (uint *)0x0)) {
    local_28 = 6;
  }
  else {
    uVar2 = *param_1;
    if (*(byte *)((int)param_2 + 0x12) - 1 < 7) {
      uVar5 = param_3[2];
      if ((int)uVar5 < 0) {
        uVar5 = -uVar5;
      }
      uVar3 = *param_3;
      *(undefined1 *)((int)param_3 + 0x12) = 2;
      *param_3 = *param_2;
      param_3[1] = param_2[1];
      iVar6 = 0;
      if (0 < param_4) {
        iVar7 = param_2[1] - param_4 * ((int)param_2[1] / param_4);
        iVar6 = 0;
        if (iVar7 != 0) {
          iVar6 = param_4 - iVar7;
        }
      }
      uVar8 = iVar6 + param_2[1];
      if ((0 < (int)uVar8) && (0xffffffff / uVar8 < *param_3)) {
        local_28 = 6;
        goto LAB_0058f152;
      }
      puVar4 = (uint *)param_3[3];
      uVar5 = ft_mem_qrealloc(uVar2,1,uVar5 * uVar3,uVar8 * *param_3,puVar4,&local_28);
      param_3[3] = uVar5;
      if (local_28 != 0) goto LAB_0058f152;
      if ((int)param_3[2] < 0) {
        uVar8 = -uVar8;
      }
      param_3[2] = uVar8;
    }
    else {
      local_28 = 6;
    }
    pbVar9 = (byte *)param_2[3];
    pbVar10 = (byte *)param_3[3];
    if ((int)param_2[2] < 0) {
      pbVar9 = pbVar9 + -((*param_2 - 1) * param_2[2]);
    }
    if ((int)param_3[2] < 0) {
      pbVar10 = pbVar10 + -((*param_3 - 1) * param_3[2]);
    }
    bVar1 = *(byte *)((int)param_2 + 0x12);
    if (bVar1 == 1) {
      *(undefined2 *)(param_3 + 4) = 2;
      for (uVar5 = *param_2; uVar5 != 0; uVar5 = uVar5 - 1) {
        pbVar11 = pbVar10;
        pbVar12 = pbVar9;
        for (uVar3 = param_2[1] >> 3; uVar3 != 0; uVar3 = uVar3 - 1) {
          bVar1 = *pbVar12;
          uVar8 = (uint)bVar1;
          *pbVar11 = bVar1 >> 7;
          pbVar11[1] = (byte)((uVar8 << 0x19) >> 0x1f);
          pbVar11[2] = (byte)((uVar8 << 0x1a) >> 0x1f);
          pbVar11[3] = (byte)((uVar8 << 0x1b) >> 0x1f);
          pbVar11[4] = (byte)((uVar8 << 0x1c) >> 0x1f);
          pbVar11[5] = (byte)((uVar8 << 0x1d) >> 0x1f);
          pbVar11[6] = (byte)((uVar8 << 0x1e) >> 0x1f);
          pbVar11[7] = bVar1 & 1;
          pbVar11 = pbVar11 + 8;
          pbVar12 = pbVar12 + 1;
        }
        uVar3 = (byte)param_2[1] & 7;
        if (((byte)param_2[1] & 7) != 0) {
          bVar1 = *pbVar12;
          for (; uVar3 != 0; uVar3 = uVar3 - 1) {
            *pbVar11 = bVar1 >> 7;
            bVar1 = bVar1 << 1;
            pbVar11 = pbVar11 + 1;
          }
        }
        pbVar9 = pbVar9 + param_2[2];
        pbVar10 = pbVar10 + param_3[2];
      }
    }
    else if (bVar1 != 0) {
      if (bVar1 == 3) {
        *(undefined2 *)(param_3 + 4) = 4;
        for (uVar5 = *param_2; uVar5 != 0; uVar5 = uVar5 - 1) {
          pbVar11 = pbVar10;
          pbVar12 = pbVar9;
          for (uVar3 = param_2[1] >> 2; uVar3 != 0; uVar3 = uVar3 - 1) {
            bVar1 = *pbVar12;
            *pbVar11 = bVar1 >> 6;
            pbVar11[1] = (byte)(((uint)bVar1 << 0x1a) >> 0x1e);
            pbVar11[2] = (byte)(((uint)bVar1 << 0x1c) >> 0x1e);
            pbVar11[3] = bVar1 & 3;
            pbVar12 = pbVar12 + 1;
            pbVar11 = pbVar11 + 4;
          }
          uVar3 = (byte)param_2[1] & 3;
          if (((byte)param_2[1] & 3) != 0) {
            bVar1 = *pbVar12;
            for (; uVar3 != 0; uVar3 = uVar3 - 1) {
              *pbVar11 = bVar1 >> 6;
              bVar1 = bVar1 << 2;
              pbVar11 = pbVar11 + 1;
            }
          }
          pbVar9 = pbVar9 + param_2[2];
          pbVar10 = pbVar10 + param_3[2];
        }
      }
      else {
        if ((2 < bVar1) && (bVar1 != 5)) {
          if (bVar1 < 5) {
            *(undefined2 *)(param_3 + 4) = 0x10;
            for (uVar5 = *param_2; uVar5 != 0; uVar5 = uVar5 - 1) {
              pbVar11 = pbVar9;
              pbVar12 = pbVar10;
              for (uVar3 = param_2[1] >> 1; uVar3 != 0; uVar3 = uVar3 - 1) {
                bVar1 = *pbVar11;
                *pbVar12 = bVar1 >> 4;
                pbVar12[1] = bVar1 & 0xf;
                pbVar11 = pbVar11 + 1;
                pbVar12 = pbVar12 + 2;
              }
              if ((int)((uint)(byte)param_2[1] << 0x1f) < 0) {
                *pbVar12 = *pbVar11 >> 4;
              }
              pbVar9 = pbVar9 + param_2[2];
              pbVar10 = pbVar10 + param_3[2];
            }
            goto LAB_0058f152;
          }
          if (bVar1 == 7) {
            *(undefined2 *)(param_3 + 4) = 0x100;
            for (uVar5 = *param_2; uVar5 != 0; uVar5 = uVar5 - 1) {
              pbVar11 = pbVar10;
              pbVar12 = pbVar9;
              for (uVar3 = param_2[1]; uVar3 != 0; uVar3 = uVar3 - 1) {
                bVar1 = FUN_0058ee58(pbVar12);
                *pbVar11 = bVar1;
                pbVar12 = pbVar12 + 4;
                pbVar11 = pbVar11 + 1;
              }
              pbVar9 = pbVar9 + param_2[2];
              pbVar10 = pbVar10 + param_3[2];
            }
            goto LAB_0058f152;
          }
          if (6 < bVar1) goto LAB_0058f152;
        }
        uVar3 = param_2[1];
        *(undefined2 *)(param_3 + 4) = 0x100;
        for (uVar5 = *param_2; uVar5 != 0; uVar5 = uVar5 - 1) {
          FUN_00439be4(pbVar10,pbVar9,uVar3);
          pbVar9 = pbVar9 + param_2[2];
          pbVar10 = pbVar10 + param_3[2];
        }
      }
    }
  }
LAB_0058f152:
  return CONCAT44(puVar4,local_28);
}

