
uint FUN_0054ef08(byte *param_1,byte *param_2,int param_3,int param_4,char param_5,char param_6,
                 byte *param_7,int param_8,uint param_9)

{
  byte bVar1;
  uint uVar2;
  int iVar3;
  uint uVar4;
  byte *pbVar5;
  byte *pbVar6;
  byte *pbVar7;
  byte *pbVar8;
  byte *local_50;
  byte *local_4c;
  int local_48;
  byte *local_44;
  uint local_40;
  byte *local_3c;
  byte *local_38;
  byte *local_34;
  byte *local_30;
  byte *local_28;
  
  if ((param_1 == (byte *)0x0) || (param_4 < 0)) {
    uVar2 = 0xffffffff;
  }
  else {
    local_4c = param_1 + param_3;
    pbVar5 = param_2 + param_4;
    if (param_8 == 0) {
      local_48 = 0;
    }
    else {
      local_48 = param_8 + param_9;
    }
    local_40 = (uint)(param_9 < 0x10000);
    local_30 = local_4c + -0x10;
    local_34 = pbVar5 + -0x20;
    if (param_4 == 0) {
      if (param_5 == '\0') {
        if ((param_3 == 1) && (*param_1 == 0)) {
          uVar2 = 0;
        }
        else {
          uVar2 = 0xffffffff;
        }
      }
      else {
        uVar2 = 0;
      }
    }
    else {
      local_50 = param_1;
      local_3c = param_2;
      local_28 = param_1;
      if (param_3 == 0) {
        uVar2 = 0xffffffff;
      }
      else {
LAB_0054efc8:
        bVar1 = *local_50;
        local_50 = local_50 + 1;
        uVar2 = (uint)(bVar1 >> 4);
        if (((uVar2 == 0xf) || (local_30 <= local_50)) || (local_34 < param_2)) {
          if ((uVar2 == 0xf) &&
             (((iVar3 = FUN_0054ee90(&local_50,local_4c + -0xf,1), iVar3 == *DAT_0054f358 ||
               (uVar2 = iVar3 + 0xf, param_2 + uVar2 < param_2)) || (local_50 + uVar2 < local_50))))
          goto LAB_0054f0b0;
          pbVar6 = param_2 + uVar2;
          if ((pbVar5 + -0xc < pbVar6) || (local_4c + -8 < local_50 + uVar2)) {
            if (param_5 == '\0') {
              if ((local_50 + uVar2 != local_4c) || (pbVar5 < pbVar6)) goto LAB_0054f0b0;
            }
            else {
              if (local_4c < local_50 + uVar2) {
                uVar2 = (int)local_4c - (int)local_50;
                pbVar6 = param_2 + uVar2;
              }
              if (pbVar5 < pbVar6) {
                uVar2 = (int)pbVar5 - (int)param_2;
                pbVar6 = pbVar5;
              }
            }
            local_44 = local_50;
            FUN_00439710(param_2,local_50,uVar2);
            local_50 = local_50 + uVar2;
            param_2 = param_2 + uVar2;
            if (((param_5 == '\0') || (pbVar6 == pbVar5)) ||
               (pbVar6 = param_2, local_4c + -2 <= local_50)) goto LAB_0054f0c2;
          }
          else {
            FUN_0054ee6e(param_2,local_50,pbVar6);
            local_50 = local_50 + uVar2;
          }
          uVar2 = FUN_0054ee4e(local_50);
          local_50 = local_50 + 2;
          pbVar8 = pbVar6 + -uVar2;
        }
        else {
          local_44 = local_50;
          FUN_00439be4(param_2,local_50,0x10);
          pbVar6 = param_2 + uVar2;
          local_50 = local_50 + uVar2;
          uVar4 = bVar1 & 0xf;
          uVar2 = FUN_0054ee4e(local_50);
          local_50 = local_50 + 2;
          pbVar8 = pbVar6 + -uVar2;
          if (((uVar4 != 0xf) && (7 < uVar2)) && ((param_6 == '\x01' || (param_7 <= pbVar8)))) {
            FUN_00439be4(pbVar6,pbVar8,8);
            FUN_00439be4(pbVar6 + 8,pbVar8 + 8,8);
            FUN_00439be4(pbVar6 + 0x10,pbVar8 + 0x10,2);
            param_2 = pbVar6 + uVar4 + 4;
            goto LAB_0054efc8;
          }
        }
        uVar4 = bVar1 & 0xf;
        if (((uVar4 == 0xf) &&
            ((iVar3 = FUN_0054ee90(&local_50,local_4c + -4,0), iVar3 == *DAT_0054f358 ||
             (uVar4 = iVar3 + 0xf, pbVar6 + uVar4 < pbVar6)))) ||
           ((uVar4 = uVar4 + 4, local_40 != 0 && (pbVar8 + param_9 < param_7)))) {
LAB_0054f0b0:
          return ~((int)local_50 - (int)local_28);
        }
        if ((param_6 == '\x02') && (pbVar8 < param_7)) {
          if (pbVar5 + -5 < pbVar6 + uVar4) {
            if (param_5 == '\0') goto LAB_0054f0b0;
            if ((uint)((int)pbVar5 - (int)pbVar6) <= uVar4) {
              uVar4 = (int)pbVar5 - (int)pbVar6;
            }
          }
          if ((uint)((int)param_7 - (int)pbVar8) < uVar4) {
            iVar3 = (int)param_7 - (int)pbVar8;
            uVar4 = uVar4 - iVar3;
            FUN_00439be4(pbVar6,local_48 - iVar3,iVar3);
            param_2 = pbVar6 + iVar3;
            if ((uint)((int)param_2 - (int)param_7) < uVar4) {
              pbVar8 = param_2 + uVar4;
              pbVar6 = param_7;
              for (; param_2 < pbVar8; param_2 = param_2 + 1) {
                *param_2 = *pbVar6;
                pbVar6 = pbVar6 + 1;
              }
            }
            else {
              FUN_00439be4(param_2,param_7,uVar4);
              param_2 = param_2 + uVar4;
            }
          }
          else {
            FUN_00439710(pbVar6,local_48 - ((int)param_7 - (int)pbVar8),uVar4);
            param_2 = pbVar6 + uVar4;
          }
          goto LAB_0054efc8;
        }
        param_2 = pbVar6 + uVar4;
        if ((param_5 == '\0') || (param_2 <= pbVar5 + -0xc)) {
          if (uVar2 < 8) {
            FUN_0054ee3e(pbVar6,0);
            *pbVar6 = *pbVar8;
            pbVar6[1] = pbVar8[1];
            pbVar6[2] = pbVar8[2];
            pbVar6[3] = pbVar8[3];
            local_44 = pbVar8 + *(int *)(DAT_0054f35c + uVar2 * 4);
            local_38 = local_44;
            FUN_00439be4(pbVar6 + 4,local_44,4);
            pbVar8 = local_44 + -*(int *)(DAT_0054f360 + uVar2 * 4);
          }
          else {
            FUN_00439be4(pbVar6,pbVar8,8);
            pbVar8 = pbVar8 + 8;
          }
          pbVar7 = pbVar6 + 8;
          if (pbVar5 + -0xc < param_2) {
            pbVar6 = pbVar5 + -7;
            if (pbVar5 + -5 < param_2) goto LAB_0054f0b0;
            if (pbVar7 < pbVar6) {
              FUN_0054ee6e(pbVar7,pbVar8,pbVar6);
              pbVar8 = pbVar8 + ((int)pbVar6 - (int)pbVar7);
              pbVar7 = pbVar6;
            }
            for (; pbVar7 < param_2; pbVar7 = pbVar7 + 1) {
              *pbVar7 = *pbVar8;
              pbVar8 = pbVar8 + 1;
            }
          }
          else {
            FUN_00439be4(pbVar7,pbVar8,8);
            if (0x10 < uVar4) {
              FUN_0054ee6e(pbVar6 + 0x10,pbVar8 + 8,param_2);
            }
          }
          goto LAB_0054efc8;
        }
        if ((uint)((int)pbVar5 - (int)pbVar6) <= uVar4) {
          uVar4 = (int)pbVar5 - (int)pbVar6;
        }
        param_2 = pbVar6 + uVar4;
        if (pbVar6 < pbVar8 + uVar4) {
          for (; pbVar6 < param_2; pbVar6 = pbVar6 + 1) {
            *pbVar6 = *pbVar8;
            pbVar8 = pbVar8 + 1;
          }
        }
        else {
          FUN_00439be4(pbVar6,pbVar8);
        }
        if (param_2 != pbVar5) goto LAB_0054efc8;
LAB_0054f0c2:
        uVar2 = (int)param_2 - (int)local_3c;
      }
    }
  }
  return uVar2;
}

