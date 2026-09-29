
int FUN_0042ba00(byte param_1,char param_2,uint *param_3)

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
  int *piVar10;
  uint *puVar11;
  int iVar12;
  int local_40;
  uint local_3c;
  uint local_38;
  uint local_34;
  uint local_30;
  byte local_2c;
  char local_2b;
  char local_2a;
  int local_28;
  uint local_24;
  
  iVar12 = 0;
  local_40 = 0;
  local_28 = 0;
  bVar7 = false;
  bVar6 = false;
  bVar3 = false;
  bVar5 = true;
  bVar4 = true;
  if ((*DAT_0042bfc8 & 0x3f) >> 4 == 3) {
    if (*DAT_0042bfcc == DAT_0042bfd0) {
      local_24 = critical_save();
      if ((((param_1 == 0) && (param_3 != (uint *)0x0)) &&
          ((cVar1 = (char)*param_3, *DAT_0042bfd4 == '\x04' ||
           ((*DAT_0042bfd4 == '\x03' || (*DAT_0042bfd4 == '\x02')))))) &&
         ((cVar1 == '\0' || (cVar1 == '\x01')))) {
        bVar3 = true;
        *DAT_0042bfd4 = cVar1;
      }
      pbVar9 = DAT_0042bfe8;
      pcVar8 = DAT_0042bfd4;
      if (!bVar3) {
        local_3c = *DAT_0042bfd8;
        local_38 = *DAT_0042bfdc;
        local_34 = *DAT_0042bfe0;
        local_30 = *DAT_0042bfe4;
        local_2c = *DAT_0042bfe8;
        if ((int)(local_3c << 0xd) < 0) {
          if (*DAT_0042bfec == '\0') {
            local_2a = '\x01';
          }
          else {
            local_2a = '\x02';
          }
        }
        else {
          local_2a = '\0';
        }
        local_2b = *DAT_0042bfd4;
        if (param_1 == 0) {
          bVar4 = bVar5;
          bVar6 = bVar7;
          if (param_3 == (uint *)0x0) {
            iVar12 = 6;
          }
          else {
            local_2b = (char)*param_3;
            if (*DAT_0042bfd4 != local_2b) {
              if (local_2b == '\x02') {
                spotmgr_buck_deepsleep_scan_42aef0(&local_3c);
                if ((*DAT_0042c00c == 8) || (*DAT_0042c00c == 0xc)) {
                  *DAT_0042c010 = 0;
                }
                else {
                  *DAT_0042c010 = 1;
                }
              }
              if ((*pcVar8 == '\0') && (local_2b == '\x01')) {
                *pcVar8 = '\x01';
              }
              else if ((*pcVar8 == '\x01') && (local_2b == '\0')) {
                bVar6 = true;
              }
              else if ((*pcVar8 == '\0') && (local_2b == '\x02')) {
                if (((((int)((uint)*DAT_0042bfb8 << 0x1f) < 0) && (local_2a != '\x01')) &&
                    (local_2a != '\x02')) &&
                   (((local_3c & 0x3fffffff) == 0 && ((local_38 & 0x4c4) == 0)))) {
                  *DAT_0042c014 = 1;
                }
                *pcVar8 = '\x02';
              }
              else {
                spotmgr_state_transition_effects_42b014(local_2b,*pcVar8);
                *pcVar8 = local_2b;
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
            local_2c = spotmgr_temperature_range_42ad40(*param_3);
            *pbVar9 = local_2c;
            if (*pbVar9 < 3) {
              *DAT_0042bff0 = 1;
            }
            else {
              *DAT_0042bff0 = 0;
            }
            bVar2 = *pbVar9;
            if (bVar2 == 0) {
              param_3[1] = DAT_0042bff4;
              param_3[2] = DAT_0042bff8;
            }
            else if (bVar2 == 2) {
              param_3[1] = 0xc0000000;
              param_3[2] = DAT_0042c000;
            }
            else if (bVar2 < 2) {
              param_3[1] = DAT_0042bffc;
              param_3[2] = 0;
            }
            else if (bVar2 == 4) {
              param_3[1] = 0;
              param_3[2] = 0;
              iVar12 = 6;
            }
            else if (bVar2 < 4) {
              param_3[1] = DAT_0042c004;
              param_3[2] = DAT_0042c008;
            }
          }
        }
        else if (param_1 < 2) {
          if (param_3 == (uint *)0x0) {
            iVar12 = 6;
          }
          else {
            local_2a = (char)*param_3;
          }
        }
        else if (param_1 == 4) {
          if (param_2 != '\0') {
            if (param_3 == (uint *)0x0) {
              iVar12 = 6;
            }
            else {
              local_38 = local_38 | *param_3;
            }
          }
        }
        else if (param_1 < 4) {
          if (param_2 != '\0') {
            if (param_3 == (uint *)0x0) {
              iVar12 = 6;
            }
            else {
              local_3c = local_3c | *param_3;
            }
          }
        }
        else if (param_1 == 6) {
          if (param_2 != '\0') {
            if (param_3 == (uint *)0x0) {
              iVar12 = 6;
            }
            else {
              local_30 = *param_3;
            }
          }
        }
        else if (param_1 < 6) {
          if (param_3 == (uint *)0x0) {
            iVar12 = 6;
          }
          else {
            local_34 = *param_3;
          }
        }
        else {
          iVar12 = 6;
        }
        if (((iVar12 == 0) && (bVar4)) &&
           (iVar12 = hw_state_decode_42b6b8(&local_3c,&local_40,&local_28), piVar10 = DAT_0042c00c,
           iVar12 == 0)) {
          if (((local_40 != *DAT_0042c00c) || (local_28 != *DAT_0042c018)) &&
             (spotmgr_state_transition_42b294(local_40,*DAT_0042c00c,local_28,*DAT_0042c018), bVar6)
             ) {
            spotmgr_state_transition_effects_42b014(local_2b,*pcVar8);
            *pcVar8 = local_2b;
          }
          puVar11 = DAT_0042c01c;
          if (((*piVar10 == 0xc) && (((local_40 == 0xd || (local_40 == 0xe)) || (local_40 == 0xf))))
             || ((*piVar10 == 8 && (((local_40 == 9 || (local_40 == 10)) || (local_40 == 0xb)))))) {
            *DAT_0042c01c = *DAT_0042c01c | 0x40;
            *puVar11 = *puVar11 | 8;
          }
          *piVar10 = local_40;
          *DAT_0042c018 = local_28;
        }
      }
      bVar3 = (bool)isCurrentModePrivileged();
      if (bVar3) {
        enableIRQinterrupts((local_24 & 1) == 1);
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

