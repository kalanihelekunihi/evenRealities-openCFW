
int FUN_005a490c(uint param_1,byte param_2,uint *param_3,undefined4 param_4)

{
  char cVar1;
  byte bVar2;
  bool bVar3;
  bool bVar4;
  bool bVar5;
  char *pcVar6;
  byte *pbVar7;
  uint *puVar8;
  uint uVar9;
  int iVar10;
  uint local_60;
  uint local_5c;
  uint local_58;
  uint local_54;
  byte local_50;
  char local_4f;
  char local_4e;
  uint local_4c;
  uint local_48 [3];
  uint local_3c;
  uint local_38;
  uint local_34;
  uint local_30;
  uint local_2c;
  undefined4 uStack_28;
  
  iVar10 = 0;
  local_48[0] = 0;
  local_4c = 0;
  bVar5 = true;
  bVar3 = true;
  if ((*DAT_005a4e88 & 0x3f) >> 4 == 3) {
    if (*DAT_005a4d3c == DAT_005a4e8c) {
      uStack_28 = param_4;
      local_2c = FUN_00473940();
      local_34 = local_34 & 0xfffc003f | 0xfbf | (param_1 & 0xf) << 0xc | (uint)param_2 << 0x10;
      local_30 = DAT_005a4e90;
      if (param_3 != (uint *)0x0) {
        local_30 = *param_3;
      }
      bVar4 = false;
      if (((((param_1 & 0xff) == 0) && (param_3 != (uint *)0x0)) &&
          ((cVar1 = (char)*param_3, *DAT_005a4e94 == '\x04' ||
           ((*DAT_005a4e94 == '\x03' || (*DAT_005a4e94 == '\x02')))))) &&
         ((cVar1 == '\0' || (cVar1 == '\x01')))) {
        bVar4 = true;
        *DAT_005a4e94 = cVar1;
      }
      pbVar7 = DAT_005a4ea8;
      pcVar6 = DAT_005a4e94;
      if (!bVar4) {
        local_60 = *DAT_005a4e98;
        local_5c = *DAT_005a4e9c;
        local_58 = *DAT_005a4ea0;
        local_54 = *DAT_005a4ea4;
        local_50 = *DAT_005a4ea8;
        if ((int)(local_60 << 0xd) < 0) {
          if (*DAT_005a4eac == '\0') {
            local_4e = '\x01';
          }
          else {
            local_4e = '\x02';
          }
        }
        else {
          local_4e = '\0';
        }
        local_4f = *DAT_005a4e94;
        uVar9 = param_1 & 0xff;
        if (uVar9 == 0) {
          bVar3 = bVar5;
          if (param_3 == (uint *)0x0) {
            iVar10 = 6;
          }
          else {
            local_4f = (char)*param_3;
            if (*DAT_005a4e94 != local_4f) {
              if (local_4f == '\x02') {
                FUN_005a410c(&local_60);
                if ((*DAT_005a4ecc - 9 < 3) && (*DAT_005a4ed0 != '\a')) {
                  *DAT_005a4ed4 = 1;
                }
                else {
                  *DAT_005a4ed4 = 0;
                }
              }
              if ((*pcVar6 == '\0') && (local_4f == '\x01')) {
                *pcVar6 = '\x01';
              }
              else if ((*pcVar6 == '\x01') && (local_4f == '\0')) {
                *pcVar6 = '\0';
              }
              else if ((*pcVar6 == '\0') && (local_4f == '\x02')) {
                *pcVar6 = '\x02';
              }
              else {
                FUN_005a421c(local_4f,*pcVar6);
                *pcVar6 = local_4f;
                bVar3 = false;
              }
            }
          }
        }
        else if (uVar9 == 2) {
          if (param_3 == (uint *)0x0) {
            iVar10 = 6;
          }
          else {
            local_50 = FUN_005a1e8c(*param_3);
            *pbVar7 = local_50;
            if (*pbVar7 < 3) {
              *DAT_005a4eb0 = 1;
            }
            else {
              *DAT_005a4eb0 = 0;
            }
            bVar2 = *pbVar7;
            if (bVar2 == 0) {
              param_3[1] = DAT_005a4eb4;
              param_3[2] = DAT_005a4eb8;
            }
            else if (bVar2 == 2) {
              param_3[1] = 0xc0000000;
              param_3[2] = DAT_005a4ec0;
            }
            else if (bVar2 < 2) {
              param_3[1] = DAT_005a4ebc;
              param_3[2] = 0;
            }
            else if (bVar2 == 4) {
              param_3[1] = 0;
              param_3[2] = 0;
              iVar10 = 6;
            }
            else if (bVar2 < 4) {
              param_3[1] = DAT_005a4ec4;
              param_3[2] = DAT_005a4ec8;
            }
          }
        }
        else if (uVar9 < 2) {
          if (param_3 == (uint *)0x0) {
            iVar10 = 6;
          }
          else {
            local_4e = (char)*param_3;
          }
        }
        else if (uVar9 == 4) {
          if (param_2 != 0) {
            if (param_3 == (uint *)0x0) {
              iVar10 = 6;
            }
            else {
              local_5c = local_5c | *param_3;
            }
          }
        }
        else if (uVar9 < 4) {
          if (param_2 != 0) {
            if (param_3 == (uint *)0x0) {
              iVar10 = 6;
            }
            else {
              local_60 = local_60 | *param_3;
            }
          }
        }
        else if (uVar9 == 6) {
          if (param_2 != 0) {
            if (param_3 == (uint *)0x0) {
              iVar10 = 6;
            }
            else {
              local_54 = *param_3;
            }
          }
        }
        else if (uVar9 < 6) {
          if (param_3 == (uint *)0x0) {
            iVar10 = 6;
          }
          else {
            local_58 = *param_3;
          }
        }
        else {
          iVar10 = 6;
        }
        if (((iVar10 == 0) && (bVar3)) &&
           (iVar10 = FUN_005a45d0(&local_60,local_48,&local_4c), puVar8 = DAT_005a4ecc, iVar10 == 0)
           ) {
          if ((local_48[0] != *DAT_005a4ecc) || (local_4c != *DAT_005a4ed8)) {
            local_3c = local_3c & 0xfffc0000 | local_48[0] & 0x3f | (local_4c & 0x3f) << 6 |
                       (param_1 & 0xf) << 0xc | (uint)param_2 << 0x10;
            local_38 = DAT_005a4e90;
            if (param_3 != (uint *)0x0) {
              local_38 = *param_3;
            }
            FUN_005a453c(local_48[0],*DAT_005a4ecc,local_4c,*DAT_005a4ed8);
          }
          *puVar8 = local_48[0];
          *DAT_005a4ed8 = local_4c;
        }
      }
      bVar3 = (bool)isCurrentModePrivileged();
      if (bVar3) {
        enableIRQinterrupts((local_2c & 1) == 1);
      }
    }
    else {
      iVar10 = 1;
    }
  }
  else {
    iVar10 = 0;
  }
  return iVar10;
}

