
void FUN_00551abc(int *param_1,byte param_2,byte param_3,undefined4 param_4)

{
  byte bVar1;
  byte bVar2;
  int iVar3;
  int iVar4;
  char *pcVar5;
  int *piVar6;
  undefined4 local_40 [8];
  undefined4 uStack_20;
  
  if ((param_1 != (int *)0x0) && (*param_1 != 0)) {
    uStack_20 = param_4;
    bVar2 = service_ancc_message_count_get();
    if (param_2 < bVar2) {
      iVar3 = service_ancc_record_find((bVar2 - param_2) + -1);
      if ((iVar3 == 0) || (*(char *)(iVar3 + 0x2fc) == '\0')) {
        FUN_0043ded4(*param_1,1);
      }
      else {
        FUN_0054ff64(*param_1,iVar3,param_2,param_3);
        if ((param_1[2] != 0) && (iVar3 != -8)) {
          navigation_apply_named_resource(param_1[2],iVar3 + 8);
        }
        if ((param_1 + 3 != (int *)0x0) && (param_1[3] != 0)) {
          if (param_1[4] != 0) {
            if (iVar3 == -0x48) {
              iVar4 = navigation_record_third_field_lookup(0xffffffc0);
            }
            else {
              iVar4 = iVar3 + 0x48;
            }
            FUN_0049942e(param_1[4],iVar4);
          }
          if ((param_1[8] != 0) && (iVar3 != -0x2e8)) {
            FUN_0054fb84(iVar3 + 0x2e8,local_40,0x20);
            FUN_0049942e(param_1[8],local_40);
          }
          if ((param_1[5] != 0) && (iVar3 != -0x68)) {
            FUN_0043f506(param_1[5],0x3fffffff);
            FUN_0049942e(param_1[5],iVar3 + 0x68);
          }
          if ((param_1[7] != 0) && (iVar3 != -0xa8)) {
            FUN_0043f506(param_1[7],0x3fffffff);
            FUN_0049942e(param_1[7],iVar3 + 0xa8);
          }
          if ((param_1[9] != 0) && (iVar3 != -0xe8)) {
            FUN_0043f568(param_1[9],0x3fffffff);
            FUN_00499678(param_1[9],0);
            FUN_0049942e(param_1[9],iVar3 + 0xe8);
            FUN_0043f66c(param_1[9]);
            iVar3 = FUN_0043fdda(param_1[9]);
            if (0x5a < iVar3) {
              FUN_0043f568(param_1[9],0x5a);
              FUN_00499678(param_1[9],1);
            }
          }
          bVar2 = 1;
          bVar1 = 1;
          pcVar5 = (char *)FUN_004997f8(param_1[5]);
          iVar3 = FUN_004997f8(param_1[4]);
          if (((pcVar5 == (char *)0x0) || (*pcVar5 == '\0')) ||
             ((iVar3 != 0 && (iVar3 = FUN_0046cacc(pcVar5,iVar3), iVar3 == 0)))) {
            bVar2 = 0;
            FUN_0043ded4(param_1[5],1);
            FUN_0043ded4(param_1[6],1);
          }
          else {
            FUN_0043dfa4(param_1[5],1);
          }
          pcVar5 = (char *)FUN_004997f8(param_1[7]);
          if ((pcVar5 == (char *)0x0) || (*pcVar5 == '\0')) {
            bVar1 = 0;
            FUN_0043ded4(param_1[7],1);
            FUN_0043ded4(param_1[6],1);
          }
          else {
            FUN_0043dfa4(param_1[7],1);
          }
          if ((bool)(bVar1 | bVar2)) {
            if ((bool)(bVar1 ^ 1 | bVar2)) {
              if ((bool)(bVar2 & (bVar1 ^ 1))) {
                FUN_0043f506(param_1[5],0x1d9);
                local_40[0] = 0xc;
                FUN_0043f6d6(param_1[5],param_1[4],0xd,0);
                local_40[0] = 4;
                FUN_0043f6d6(param_1[9],param_1[5],0xd,0);
              }
              else {
                FUN_0043dfa4(param_1[6],1);
                FUN_0043f506(param_1[5],0x3fffffff);
                FUN_0043f506(param_1[7],0x3fffffff);
                FUN_0043f66c(param_1[5]);
                FUN_0043f66c(param_1[7]);
                iVar3 = FUN_0043fd9e(param_1[5]);
                iVar4 = FUN_0043fd9e(param_1[7]);
                if ((iVar3 < 0xe1) || (iVar4 < 0xe1)) {
                  if ((iVar3 < 0xe1) && (0xe0 < iVar4)) {
                    FUN_0043f506(param_1[7],0x1c1 - iVar3);
                  }
                  else if ((0xe0 < iVar3) && (iVar4 < 0xe1)) {
                    FUN_0043f506(param_1[5],0x1c1 - iVar4);
                  }
                }
                else {
                  FUN_0043f506(param_1[5],0xe0);
                  FUN_0043f506(param_1[7],0xe0);
                }
                local_40[0] = 0xc;
                FUN_0043f6d6(param_1[5],param_1[4],0xd,0);
                local_40[0] = 0;
                FUN_0043f6d6(param_1[6],param_1[5],0x14,0);
                local_40[0] = 0;
                FUN_0043f6d6(param_1[7],param_1[6],0x14,0);
                local_40[0] = 4;
                FUN_0043f6d6(param_1[9],param_1[5],0xd,0);
              }
            }
            else {
              FUN_0043f506(param_1[7],0x1d9);
              local_40[0] = 0xc;
              FUN_0043f6d6(param_1[7],param_1[4],0xd,0);
              local_40[0] = 4;
              FUN_0043f6d6(param_1[9],param_1[7],0xd,0);
            }
          }
          else {
            local_40[0] = 0xc;
            FUN_0043f6d6(param_1[9],param_1[4],0xd,0);
          }
        }
        FUN_0043dfa4(*param_1,1);
        FUN_00441488(*param_1,0xff,0);
        if (param_3 == 0) {
          FUN_0043f6b8(*param_1,1,0,0);
        }
        else {
          piVar6 = (int *)(DAT_00551e9c + (uint)param_3 * 0x28 + 0x18);
          if (*piVar6 == 0) {
            FUN_0043f6b8(*param_1,1,0,0);
          }
          else {
            local_40[0] = 0;
            FUN_0043f6d6(*param_1,*piVar6,0xd,0);
          }
        }
      }
    }
    else {
      FUN_0043ded4(*param_1,1);
    }
  }
  return;
}

