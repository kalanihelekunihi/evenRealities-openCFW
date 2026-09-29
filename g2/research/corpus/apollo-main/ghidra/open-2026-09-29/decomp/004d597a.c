
undefined4 _parseJsonWhitelistToStruct(undefined4 param_1)

{
  byte *pbVar1;
  byte bVar2;
  int iVar3;
  undefined4 uVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  byte bVar8;
  
  iVar3 = FUN_0043d0ce();
  if (iVar3 << 0x1e < 0) {
    FUN_0043d574(4,DAT_004d6328,DAT_004d6324,DAT_004d6320,0x70,DAT_004d631c);
  }
  iVar3 = FUN_0043d0ce();
  if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
    compress_log_output(0x10000000,DAT_004d632c,DAT_004d632c);
  }
  iVar3 = cJSON_Parse(param_1);
  pbVar1 = DAT_004d6338;
  if (iVar3 == 0) {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(1,DAT_004d6328,DAT_004d6324,DAT_004d6320,0x73,DAT_004d6330,param_1);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x4400000,DAT_004d6334,DAT_004d6334,param_1);
    }
    uVar4 = 0;
  }
  else {
    FUN_0043c0e4(DAT_004d6338,0x1f42,0);
    uVar4 = DAT_004d633c;
    iVar5 = cJSON_GetObjectItem(iVar3,DAT_004d633c);
    if (iVar5 == 0) {
      iVar5 = FUN_0043d0ce();
      if (iVar5 << 0x1e < 0) {
        FUN_0043d574(1,DAT_004d6328,DAT_004d6324,DAT_004d6320,0x7b,DAT_004d6340,uVar4);
      }
      iVar5 = FUN_0043d0ce();
      if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
        compress_log_output(0x4400000,DAT_004d6344,DAT_004d6344,uVar4);
      }
      cJSON_Delete(iVar3);
      uVar4 = 0;
    }
    else {
      *pbVar1 = *pbVar1 & 0xfe | *(int *)(iVar5 + 0xc) == 2;
      uVar4 = DAT_004d6348;
      iVar5 = cJSON_GetObjectItem(iVar3,DAT_004d6348);
      if (iVar5 == 0) {
        iVar5 = FUN_0043d0ce();
        if (iVar5 << 0x1e < 0) {
          FUN_0043d574(1,DAT_004d6328,DAT_004d6324,DAT_004d6320,0x7c,DAT_004d6340,uVar4);
        }
        iVar5 = FUN_0043d0ce();
        if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
          compress_log_output(0x4400000,DAT_004d6344,DAT_004d6344,uVar4);
        }
        cJSON_Delete(iVar3);
        uVar4 = 0;
      }
      else {
        *pbVar1 = *pbVar1 & 0xfd | (*(int *)(iVar5 + 0xc) == 2) << 1;
        uVar4 = DAT_004d634c;
        iVar5 = cJSON_GetObjectItem(iVar3,DAT_004d634c);
        if (iVar5 == 0) {
          iVar5 = FUN_0043d0ce();
          if (iVar5 << 0x1e < 0) {
            FUN_0043d574(1,DAT_004d6328,DAT_004d6324,DAT_004d6320,0x7d,DAT_004d6340,uVar4);
          }
          iVar5 = FUN_0043d0ce();
          if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
            compress_log_output(0x4400000,DAT_004d6344,DAT_004d6344,uVar4);
          }
          cJSON_Delete(iVar3);
          uVar4 = 0;
        }
        else {
          *pbVar1 = *pbVar1 & 0xf7 | (*(int *)(iVar5 + 0xc) == 2) << 3;
          uVar4 = DAT_004d6350;
          iVar5 = cJSON_GetObjectItem(iVar3,DAT_004d6350);
          if (iVar5 == 0) {
            iVar5 = FUN_0043d0ce();
            if (iVar5 << 0x1e < 0) {
              FUN_0043d574(1,DAT_004d6328,DAT_004d6324,DAT_004d6320,0x7e,DAT_004d6340,uVar4);
            }
            iVar5 = FUN_0043d0ce();
            if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
              compress_log_output(0x4400000,DAT_004d6344,DAT_004d6344,uVar4);
            }
            cJSON_Delete(iVar3);
            uVar4 = 0;
          }
          else {
            *pbVar1 = *pbVar1 & 0xfb | (*(int *)(iVar5 + 0xc) == 2) << 2;
            iVar5 = cJSON_GetObjectItem(iVar3,&DAT_004d5f30);
            uVar4 = DAT_004d635c;
            if (iVar5 == 0) {
              iVar5 = FUN_0043d0ce();
              if (iVar5 << 0x1e < 0) {
                FUN_0043d574(1,DAT_004d6328,DAT_004d6324,DAT_004d6320,0x83,DAT_004d6354);
              }
              iVar5 = FUN_0043d0ce();
              if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
                compress_log_output(0x4000000,DAT_004d6358,DAT_004d6358);
              }
              cJSON_Delete(iVar3);
              uVar4 = 0;
            }
            else {
              iVar6 = cJSON_GetObjectItem(iVar5,DAT_004d635c);
              if (iVar6 == 0) {
                iVar5 = FUN_0043d0ce();
                if (iVar5 << 0x1e < 0) {
                  FUN_0043d574(1,DAT_004d6328,DAT_004d6324,DAT_004d6320,0x89,DAT_004d6340,uVar4);
                }
                iVar5 = FUN_0043d0ce();
                if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
                  compress_log_output(0x4400000,DAT_004d6344,DAT_004d6344,uVar4);
                }
                cJSON_Delete(iVar3);
                uVar4 = 0;
              }
              else {
                *pbVar1 = *pbVar1 & 0xef | (*(int *)(iVar6 + 0xc) == 2) << 4;
                iVar5 = cJSON_GetObjectItem(iVar5,DAT_004d6770);
                if (iVar5 == 0) {
                  iVar5 = FUN_0043d0ce();
                  if (iVar5 << 0x1e < 0) {
                    FUN_0043d574(1,DAT_004d6328,DAT_004d6324,DAT_004d6320,0x8e,DAT_004d6774);
                  }
                  iVar5 = FUN_0043d0ce();
                  if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
                    compress_log_output(0x4000000,DAT_004d6778,DAT_004d6778);
                  }
                  cJSON_Delete(iVar3);
                  uVar4 = 0;
                }
                else {
                  iVar6 = cJSON_IsArray(iVar5);
                  if (iVar6 != 0) {
                    bVar2 = cJSON_GetArraySize(iVar5);
                    pbVar1[1] = bVar2;
                    iVar6 = FUN_0043d0ce();
                    if (iVar6 << 0x1e < 0) {
                      FUN_0043d574(3,DAT_004d6328,DAT_004d6324,DAT_004d6320,0x95,DAT_004d677c,
                                   pbVar1[1]);
                    }
                    iVar6 = FUN_0043d0ce();
                    if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
                      compress_log_output(0xc400000,DAT_004d6780,DAT_004d6780,pbVar1[1]);
                    }
                    if (100 < pbVar1[1]) {
                      iVar6 = FUN_0043d0ce();
                      if (iVar6 << 0x1e < 0) {
                        FUN_0043d574(2,DAT_004d6328,DAT_004d6324,DAT_004d6320,0x97,DAT_004d6784,
                                     pbVar1[1],100);
                      }
                      iVar6 = FUN_0043d0ce();
                      if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
                        compress_log_output(0x8800000,DAT_004d6788,DAT_004d6788,pbVar1[1],100);
                      }
                      pbVar1[1] = 100;
                    }
                    bVar2 = 0;
                    for (bVar8 = 0; bVar8 < pbVar1[1]; bVar8 = bVar8 + 1) {
                      iVar6 = cJSON_GetArrayItem(iVar5,bVar8);
                      if (iVar6 == 0) {
                        iVar6 = FUN_0043d0ce();
                        if (iVar6 << 0x1e < 0) {
                          FUN_0043d574(2,DAT_004d6328,DAT_004d6324,DAT_004d6320,0x9f,DAT_004d6798,
                                       bVar8);
                        }
                        iVar6 = FUN_0043d0ce();
                        if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
                          compress_log_output(0x8400000,DAT_004d6a50,DAT_004d6a50,bVar8);
                        }
                      }
                      else {
                        iVar7 = cJSON_GetObjectItem(iVar6,&DAT_004d5f34);
                        iVar6 = cJSON_GetObjectItem(iVar6,DAT_004d678c);
                        if ((iVar7 == 0) || (iVar6 == 0)) {
                          iVar6 = FUN_0043d0ce();
                          if (iVar6 << 0x1e < 0) {
                            FUN_0043d574(2,DAT_004d6328,DAT_004d6324,DAT_004d6320,0xa7,DAT_004d6790,
                                         bVar8);
                          }
                          iVar6 = FUN_0043d0ce();
                          if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
                            compress_log_output(0x8400000,DAT_004d6794,DAT_004d6794,bVar8);
                          }
                        }
                        else {
                          FUN_0043c0e4(pbVar1 + (uint)bVar2 * 0x50 + 2,0x40,0);
                          FUN_0043c0e4(pbVar1 + (uint)bVar2 * 0x50 + 0x42,0x10,0);
                          FUN_0044b5a0(pbVar1 + (uint)bVar2 * 0x50 + 2,*(undefined4 *)(iVar7 + 0x10)
                                       ,0x3f);
                          FUN_0044b5a0(pbVar1 + (uint)bVar2 * 0x50 + 0x42,
                                       *(undefined4 *)(iVar6 + 0x10),0xf);
                          bVar2 = bVar2 + 1;
                        }
                      }
                    }
                  }
                  cJSON_Delete(iVar3);
                  uVar4 = 1;
                }
              }
            }
          }
        }
      }
    }
  }
  return uVar4;
}

