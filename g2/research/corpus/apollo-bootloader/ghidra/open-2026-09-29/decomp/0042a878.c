
int spotmgr_power_state_update_42a878(byte param_1,char param_2,uint *param_3)

{
  char cVar1;
  byte bVar2;
  bool bVar3;
  bool bVar4;
  bool bVar5;
  char *pcVar6;
  byte *pbVar7;
  int *piVar8;
  int iVar9;
  uint local_40;
  uint local_3c;
  uint local_38;
  uint local_34;
  byte local_30;
  char local_2f;
  char local_2e;
  int local_2c;
  int local_28;
  uint local_24;
  
  iVar9 = 0;
  local_28 = 0;
  local_2c = 0;
  bVar3 = false;
  bVar5 = true;
  bVar4 = true;
  if ((*DAT_0042ace0 & 0x3f) >> 4 == 3) {
    if (*DAT_0042ac50 == DAT_0042ace4) {
      local_24 = critical_save();
      if ((((param_1 == 0) && (param_3 != (uint *)0x0)) &&
          ((cVar1 = (char)*param_3, *DAT_0042ace8 == '\x04' ||
           ((*DAT_0042ace8 == '\x03' || (*DAT_0042ace8 == '\x02')))))) &&
         ((cVar1 == '\0' || (cVar1 == '\x01')))) {
        bVar3 = true;
        *DAT_0042ace8 = cVar1;
      }
      pbVar7 = DAT_0042acfc;
      pcVar6 = DAT_0042ace8;
      if (!bVar3) {
        local_40 = *DAT_0042acec;
        local_3c = *DAT_0042acf0;
        local_38 = *DAT_0042acf4;
        local_34 = *DAT_0042acf8;
        local_30 = *DAT_0042acfc;
        if ((int)(local_40 << 0xd) < 0) {
          if (*DAT_0042ad00 == '\0') {
            local_2e = '\x01';
          }
          else {
            local_2e = '\x02';
          }
        }
        else {
          local_2e = '\0';
        }
        local_2f = *DAT_0042ace8;
        if (param_1 == 0) {
          bVar4 = bVar5;
          if (param_3 == (uint *)0x0) {
            iVar9 = 6;
          }
          else {
            local_2f = (char)*param_3;
            if (*DAT_0042ace8 != local_2f) {
              if (local_2f == '\x02') {
                spotmgr_buck_deepsleep_state_42a08c(&local_40);
                if ((*DAT_0042ad20 - 9U < 3) && (*DAT_0042abb4 != '\a')) {
                  *DAT_0042ad24 = 1;
                }
                else {
                  *DAT_0042ad24 = 0;
                }
              }
              if ((*pcVar6 == '\0') && (local_2f == '\x01')) {
                *pcVar6 = '\x01';
              }
              else if ((*pcVar6 == '\x01') && (local_2f == '\0')) {
                *pcVar6 = '\0';
              }
              else if ((*pcVar6 == '\0') && (local_2f == '\x02')) {
                *pcVar6 = '\x02';
              }
              else {
                spotmgr_internal_power_domain_42a19c(local_2f,*pcVar6);
                *pcVar6 = local_2f;
                bVar4 = false;
              }
            }
          }
        }
        else if (param_1 == 2) {
          if (param_3 == (uint *)0x0) {
            iVar9 = 6;
          }
          else {
            local_30 = float_range_classify_427e0c(*param_3);
            *pbVar7 = local_30;
            if (*pbVar7 < 3) {
              *DAT_0042ad04 = 1;
            }
            else {
              *DAT_0042ad04 = 0;
            }
            bVar2 = *pbVar7;
            if (bVar2 == 0) {
              param_3[1] = DAT_0042ad08;
              param_3[2] = DAT_0042ad0c;
            }
            else if (bVar2 == 2) {
              param_3[1] = 0xc0000000;
              param_3[2] = DAT_0042ad14;
            }
            else if (bVar2 < 2) {
              param_3[1] = DAT_0042ad10;
              param_3[2] = 0;
            }
            else if (bVar2 == 4) {
              param_3[1] = 0;
              param_3[2] = 0;
              iVar9 = 6;
            }
            else if (bVar2 < 4) {
              param_3[1] = DAT_0042ad18;
              param_3[2] = DAT_0042ad1c;
            }
          }
        }
        else if (param_1 < 2) {
          if (param_3 == (uint *)0x0) {
            iVar9 = 6;
          }
          else {
            local_2e = (char)*param_3;
          }
        }
        else if (param_1 == 4) {
          if (param_2 != '\0') {
            if (param_3 == (uint *)0x0) {
              iVar9 = 6;
            }
            else {
              local_3c = local_3c | *param_3;
            }
          }
        }
        else if (param_1 < 4) {
          if (param_2 != '\0') {
            if (param_3 == (uint *)0x0) {
              iVar9 = 6;
            }
            else {
              local_40 = local_40 | *param_3;
            }
          }
        }
        else if (param_1 == 6) {
          if (param_2 != '\0') {
            if (param_3 == (uint *)0x0) {
              iVar9 = 6;
            }
            else {
              local_34 = *param_3;
            }
          }
        }
        else if (param_1 < 6) {
          if (param_3 == (uint *)0x0) {
            iVar9 = 6;
          }
          else {
            local_38 = *param_3;
          }
        }
        else {
          iVar9 = 6;
        }
        if (((iVar9 == 0) && (bVar4)) &&
           (iVar9 = spotmgr_power_state_determine_42a550(&local_40,&local_28,&local_2c),
           piVar8 = DAT_0042ad20, iVar9 == 0)) {
          if ((local_28 != *DAT_0042ad20) || (local_2c != *DAT_0042ad28)) {
            spotmgr_power_trims_update_42a4bc(local_28,*DAT_0042ad20,local_2c,*DAT_0042ad28);
          }
          *piVar8 = local_28;
          *DAT_0042ad28 = local_2c;
        }
      }
      bVar3 = (bool)isCurrentModePrivileged();
      if (bVar3) {
        enableIRQinterrupts((local_24 & 1) == 1);
      }
    }
    else {
      iVar9 = 1;
    }
  }
  else {
    iVar9 = 0;
  }
  return iVar9;
}

