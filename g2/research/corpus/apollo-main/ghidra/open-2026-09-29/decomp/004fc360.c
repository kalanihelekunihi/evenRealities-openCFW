
longlong FUN_004fc360(char *param_1,uint param_2,undefined4 param_3,undefined4 param_4)

{
  char cVar1;
  int *piVar2;
  int *piVar3;
  int *piVar4;
  undefined4 *puVar5;
  int iVar6;
  int iVar7;
  
  puVar5 = DAT_004fc634;
  piVar3 = DAT_004fc614;
  piVar2 = DAT_004fc5fc;
  if (*DAT_004fc614 == 0) {
    iVar6 = FUN_0043d0ce();
    if (iVar6 << 0x1e < 0) {
      param_2 = 0x3cf;
      FUN_0043d574(2,DAT_004fc60c,DAT_004fc608,DAT_004fc61c,0x3cf,DAT_004fc618);
    }
    iVar6 = FUN_0043d0ce();
    if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
      compress_log_output(0x8000000,DAT_004fc620);
    }
  }
  else if (param_2 == 0) {
    iVar6 = FUN_0043d0ce();
    if (iVar6 << 0x1e < 0) {
      param_2 = 0x3d3;
      FUN_0043d574(2,DAT_004fc60c,DAT_004fc608,DAT_004fc61c,0x3d3,DAT_004fc624);
    }
    iVar6 = FUN_0043d0ce();
    if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
      compress_log_output(0x8000000,DAT_004fc628,DAT_004fc628);
    }
  }
  else {
    cVar1 = *param_1;
    if (cVar1 == '\0') {
      cVar1 = param_1[1];
      if (*DAT_004fc5fc == 0) {
        if (cVar1 == '\n') {
          iVar6 = FUN_0044ddea(*DAT_004fc634,0,param_1[5],param_4,param_2,param_3,param_4);
          while (piVar4 = DAT_004fc62c, iVar6 = iVar6 + -1, -1 < iVar6) {
            iVar7 = FUN_0044dce2(*puVar5,iVar6);
            if (iVar7 != 0) {
              FUN_0044d7b8();
            }
          }
          if (*DAT_004fc62c != 0) {
            ui_common_api_fn_00509c96(*DAT_004fc62c);
            *piVar4 = 0;
          }
          *piVar3 = 0;
          *piVar2 = 0;
          FUN_004e92f4();
          FUN_005000cc(*DAT_004fc638,5);
        }
        else if (cVar1 == 'D') {
          if (*DAT_004fc630 + 1 < 2) {
            FUN_004fb290();
          }
        }
        else if (cVar1 == 'E') {
          if (-1 < *DAT_004fc630 + -1) {
            FUN_004fb290();
          }
        }
        else if (cVar1 != 'F') {
          if (cVar1 == 'H') {
            iVar6 = FUN_0044ddea(*DAT_004fc634,0,param_1[5],param_4,param_2,param_3,param_4);
            while (piVar4 = DAT_004fc62c, iVar6 = iVar6 + -1, -1 < iVar6) {
              iVar7 = FUN_0044dce2(*puVar5,iVar6);
              if (iVar7 != 0) {
                FUN_0044d7b8();
              }
            }
            if (*DAT_004fc62c != 0) {
              ui_common_api_fn_00509c96(*DAT_004fc62c);
              *piVar4 = 0;
            }
            *piVar3 = 0;
            *piVar2 = 0;
            FUN_004e92f4();
            FUN_005000cc(*DAT_004fc638,5);
          }
          else if (cVar1 == 'I') {
            FUN_004e8a90();
            *piVar3 = 0;
            *piVar2 = 0;
          }
          else {
            iVar6 = FUN_0043d0ce();
            if (iVar6 << 0x1e < 0) {
              param_2 = 0x42e;
              FUN_0043d574(2,DAT_004fc60c,DAT_004fc608,DAT_004fc61c,0x42e,DAT_004fc63c,cVar1);
            }
            iVar6 = FUN_0043d0ce();
            if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
              compress_log_output(0x8400000,DAT_004fc640,DAT_004fc640,cVar1);
            }
          }
        }
      }
      else {
        ui_common_api_fn_00509ca2(*DAT_004fc62c,param_1 + 1,5);
      }
    }
    else if (cVar1 == '\x01') {
      FUN_004e8970(param_1 + 1,param_2 - 1);
    }
    else if (cVar1 == '\x06') {
      FUN_004fb5e8(param_1 + 1,param_2 - 1);
    }
  }
  return (ulonglong)param_2 << 0x20;
}

