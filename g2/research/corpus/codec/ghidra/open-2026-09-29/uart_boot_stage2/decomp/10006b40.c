
int FUN_10006b40(byte *param_1,byte *param_2)

{
  undefined *puVar1;
  undefined *puVar2;
  undefined *puVar3;
  undefined *puVar4;
  byte *pbVar5;
  int iVar6;
  byte *pbVar7;
  undefined4 uVar8;
  uint uVar9;
  byte bVar10;
  byte *pbVar11;
  
  puVar4 = PTR_PTR_10006bb8;
  puVar3 = PTR_PTR_10006bb4;
  puVar2 = PTR_PTR_10006bac;
  puVar1 = PTR_PTR_10006ba8;
  bVar10 = *param_2;
  iVar6 = 0;
  pbVar11 = param_1;
  if (bVar10 != 0) {
    do {
      if (bVar10 == 0x25) {
        bVar10 = param_2[1];
        pbVar5 = param_2 + 1;
        if ((byte)(bVar10 - 0x20) < 0x11) {
                    /* WARNING: Could not recover jumptable at 0x10006ba2. Too many branches */
                    /* WARNING: Treating indirect jump as call */
          iVar6 = (*(code *)(*(uint *)(puVar1 + (uint)(byte)(bVar10 - 0x20) * 4) & 0xfffffffe))();
          return iVar6;
        }
        if ((byte)(bVar10 - 0x30) < 10) {
          do {
            pbVar5 = pbVar5 + 1;
            bVar10 = *pbVar5;
          } while ((byte)(bVar10 - 0x30) < 10);
        }
        else if (bVar10 == 0x2a) {
          pbVar5 = param_2 + 2;
          bVar10 = param_2[2];
        }
        pbVar7 = pbVar5;
        if (bVar10 == 0x2e) {
          bVar10 = pbVar5[1];
          pbVar7 = pbVar5 + 1;
          if ((byte)(bVar10 - 0x30) < 10) {
            do {
              pbVar7 = pbVar7 + 1;
              bVar10 = *pbVar7;
            } while ((byte)(bVar10 - 0x30) < 10);
          }
          else if (bVar10 == 0x2a) {
            bVar10 = pbVar5[2];
            pbVar7 = pbVar5 + 2;
          }
        }
        if (bVar10 == 0x68) {
LAB_10006c4a:
          uVar9 = pbVar7[1] - 0x25 & 0xff;
          param_2 = pbVar7 + 1;
          if (uVar9 < 0x54) {
                    /* WARNING: Could not recover jumptable at 0x10006c60. Too many branches */
                    /* WARNING: Treating indirect jump as call */
            iVar6 = (*(code *)(*(uint *)(puVar2 + uVar9 * 4) & 0xfffffffe))(pbVar7,bVar10);
            return iVar6;
          }
        }
        else {
          if (bVar10 == 0x6c) {
            if (pbVar7[1] != 0x6c) {
              uVar9 = (uint)(byte)(pbVar7[1] - 0x25);
              param_2 = pbVar7 + 1;
              if (uVar9 < 0x54) {
                    /* WARNING: Could not recover jumptable at 0x10006ce0. Too many branches */
                    /* WARNING: Treating indirect jump as call */
                iVar6 = (*(code *)(*(uint *)(puVar4 + uVar9 * 4) & 0xfffffffe))();
                return iVar6;
              }
              goto LAB_10006ca4;
            }
            bVar10 = pbVar7[2];
            uVar8 = 0x4c;
            pbVar7 = pbVar7 + 2;
          }
          else {
            if (((bVar10 == 0x4c) || ((bVar10 & 0xdf) == 0x5a)) || (bVar10 == 0x74))
            goto LAB_10006c4a;
            uVar8 = 0xffffffff;
          }
          param_2 = pbVar7;
          if ((byte)(bVar10 - 0x25) < 0x54) {
                    /* WARNING: Could not recover jumptable at 0x10006c48. Too many branches */
                    /* WARNING: Treating indirect jump as call */
            iVar6 = (*(code *)(*(uint *)(puVar3 + (uint)(byte)(bVar10 - 0x25) * 4) & 0xfffffffe))
                              (pbVar7,uVar8);
            return iVar6;
          }
        }
LAB_10006ca4:
        *pbVar11 = 0x25;
        if (*param_2 == 0) {
          pbVar11 = pbVar11 + 1;
          break;
        }
        pbVar11[1] = *param_2;
        bVar10 = param_2[1];
        pbVar11 = pbVar11 + 2;
      }
      else {
        *pbVar11 = bVar10;
        bVar10 = param_2[1];
        pbVar11 = pbVar11 + 1;
      }
      param_2 = param_2 + 1;
    } while (bVar10 != 0);
    iVar6 = (int)pbVar11 - (int)param_1;
  }
  *pbVar11 = 0;
  return iVar6;
}

