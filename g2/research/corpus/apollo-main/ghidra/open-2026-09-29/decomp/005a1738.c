
int FUN_005a1738(byte param_1,byte param_2,uint *param_3)

{
  char cVar1;
  byte bVar2;
  bool bVar3;
  bool bVar4;
  bool bVar5;
  bool bVar6;
  bool bVar7;
  char *pcVar8;
  byte *pbVar9;
  uint *puVar10;
  uint *puVar11;
  int iVar12;
  uint local_5c;
  uint local_58;
  uint local_54;
  uint local_50;
  uint local_4c;
  byte local_48;
  char local_47;
  char local_46;
  uint local_44 [3];
  uint local_38;
  uint local_34;
  uint local_30;
  uint local_2c;
  uint local_28;
  
  iVar12 = 0;
  local_5c = 0;
  local_44[0] = 0;
  bVar7 = false;
  bVar6 = false;
  bVar3 = false;
  if ((*DAT_005a1e18 & 0x3f) >> 4 == 3) {
    if (*DAT_005a1e1c == DAT_005a1e20) {
      local_28 = FUN_00473940();
      local_30 = local_30 & 0xfffc003f | 0xfbf | (param_1 & 0xf) << 0xc | (uint)param_2 << 0x10;
      local_2c = DAT_005a1e24;
      if (param_3 != (uint *)0x0) {
        local_2c = *param_3;
      }
      bVar5 = true;
      bVar4 = true;
      if ((((param_1 == 0) && (param_3 != (uint *)0x0)) &&
          ((cVar1 = (char)*param_3, *DAT_005a1e28 == '\x04' ||
           ((*DAT_005a1e28 == '\x03' || (*DAT_005a1e28 == '\x02')))))) &&
         ((cVar1 == '\0' || (cVar1 == '\x01')))) {
        bVar3 = true;
        *DAT_005a1e28 = cVar1;
      }
      pcVar8 = DAT_005a1e28;
      if (!bVar3) {
        local_58 = *DAT_005a1e2c;
        local_54 = *DAT_005a1e30;
        local_50 = *DAT_005a1e34;
        local_4c = *DAT_005a1e38;
        local_48 = *DAT_005a1e3c;
        if ((int)(local_58 << 0xd) < 0) {
          if (*DAT_005a1e40 == '\0') {
            local_46 = '\x01';
          }
          else {
            local_46 = '\x02';
          }
        }
        else {
          local_46 = '\0';
        }
        local_47 = *DAT_005a1e28;
        if (param_1 == 0) {
          bVar4 = bVar5;
          bVar6 = bVar7;
          if (param_3 == (uint *)0x0) {
            iVar12 = 6;
          }
          else {
            local_47 = (char)*param_3;
            if (*DAT_005a1e28 != local_47) {
              if (local_47 == '\x02') {
                FUN_005a0c20(&local_58);
                if ((*DAT_005a1e60 == 8) || (*DAT_005a1e60 == 0xc)) {
                  *DAT_005a1e64 = 0;
                }
                else {
                  *DAT_005a1e64 = 1;
                }
              }
              if ((*pcVar8 == '\0') && (local_47 == '\x01')) {
                *pcVar8 = '\x01';
              }
              else if ((*pcVar8 == '\x01') && (local_47 == '\0')) {
                bVar6 = true;
              }
              else if ((*pcVar8 == '\0') && (local_47 == '\x02')) {
                if (((((int)((uint)*DAT_005a1e08 << 0x1f) < 0) && (local_46 != '\x01')) &&
                    (local_46 != '\x02')) &&
                   (((local_58 & 0x3fffffff) == 0 && ((local_54 & 0x4c4) == 0)))) {
                  *DAT_005a1e68 = 1;
                }
                *pcVar8 = '\x02';
              }
              else {
                FUN_005a0d44(local_47,*pcVar8);
                *pcVar8 = local_47;
                bVar4 = false;
              }
            }
          }
        }
        else if (param_1 == 2) {
          if (param_3 == (uint *)0x0) {
            iVar12 = 6;
          }
          else {
            local_48 = FUN_005a0a70(*param_3);
            pbVar9 = DAT_005a1e3c;
            *DAT_005a1e3c = local_48;
            if (*pbVar9 < 3) {
              *DAT_005a1e44 = 1;
            }
            else {
              *DAT_005a1e44 = 0;
            }
            bVar2 = *pbVar9;
            if (bVar2 == 0) {
              param_3[1] = DAT_005a1e48;
              param_3[2] = DAT_005a1e4c;
            }
            else if (bVar2 == 2) {
              param_3[1] = 0xc0000000;
              param_3[2] = DAT_005a1e54;
            }
            else if (bVar2 < 2) {
              param_3[1] = DAT_005a1e50;
              param_3[2] = 0;
            }
            else if (bVar2 == 4) {
              param_3[1] = 0;
              param_3[2] = 0;
              iVar12 = 6;
            }
            else if (bVar2 < 4) {
              param_3[1] = DAT_005a1e58;
              param_3[2] = DAT_005a1e5c;
            }
          }
        }
        else if (param_1 < 2) {
          if (param_3 == (uint *)0x0) {
            iVar12 = 6;
          }
          else {
            local_46 = (char)*param_3;
          }
        }
        else if (param_1 == 4) {
          if (param_2 != 0) {
            if (param_3 == (uint *)0x0) {
              iVar12 = 6;
            }
            else {
              local_54 = local_54 | *param_3;
            }
          }
        }
        else if (param_1 < 4) {
          if (param_2 != 0) {
            if (param_3 == (uint *)0x0) {
              iVar12 = 6;
            }
            else {
              local_58 = local_58 | *param_3;
            }
          }
        }
        else if (param_1 == 6) {
          if (param_2 != 0) {
            if (param_3 == (uint *)0x0) {
              iVar12 = 6;
            }
            else {
              local_4c = *param_3;
            }
          }
        }
        else if (param_1 < 6) {
          if (param_3 == (uint *)0x0) {
            iVar12 = 6;
          }
          else {
            local_50 = *param_3;
          }
        }
        else {
          iVar12 = 6;
        }
        if (((iVar12 == 0) && (bVar4)) &&
           (iVar12 = FUN_005a13e8(&local_58,&local_5c,local_44), puVar10 = DAT_005a1e60, iVar12 == 0
           )) {
          if ((local_5c != *DAT_005a1e60) || (local_44[0] != *DAT_005a1e6c)) {
            local_38 = local_38 & 0xfffc0000 | local_5c & 0x3f | (local_44[0] & 0x3f) << 6 |
                       (param_1 & 0xf) << 0xc | (uint)param_2 << 0x10;
            local_34 = DAT_005a1e24;
            if (param_3 != (uint *)0x0) {
              local_34 = *param_3;
            }
            FUN_005a0fc4(local_5c,*DAT_005a1e60,local_44[0],*DAT_005a1e6c);
            if (bVar6) {
              FUN_005a0d44(local_47,*pcVar8);
              *pcVar8 = local_47;
            }
          }
          puVar11 = DAT_005a1e70;
          if (((*puVar10 == 0xc) && (((local_5c == 0xd || (local_5c == 0xe)) || (local_5c == 0xf))))
             || ((*puVar10 == 8 && (((local_5c == 9 || (local_5c == 10)) || (local_5c == 0xb)))))) {
            *DAT_005a1e70 = *DAT_005a1e70 | 0x40;
            *puVar11 = *puVar11 | 8;
          }
          *puVar10 = local_5c;
          *DAT_005a1e6c = local_44[0];
        }
      }
      bVar3 = (bool)isCurrentModePrivileged();
      if (bVar3) {
        enableIRQinterrupts((local_28 & 1) == 1);
      }
    }
    else {
      iVar12 = 1;
    }
  }
  else {
    iVar12 = 0;
  }
  return iVar12;
}

