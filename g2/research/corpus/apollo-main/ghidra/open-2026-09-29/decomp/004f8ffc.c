
undefined4 FUN_004f8ffc(char *param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  char cVar1;
  byte *pbVar2;
  int *piVar3;
  int *piVar4;
  int iVar5;
  int *piVar6;
  
  piVar4 = DAT_004f9d78;
  piVar3 = DAT_004f9d74;
  pbVar2 = DAT_004f9360;
  piVar6 = DAT_004f9354;
  if (*DAT_004f9354 == 0) {
    iVar5 = FUN_0043d0ce();
    if (iVar5 << 0x1e < 0) {
      FUN_0043d574(2,DAT_004f9bd8,DAT_004f9af8,DAT_004f9be8,0xd86,DAT_004f9be4);
    }
    iVar5 = FUN_0043d0ce();
    if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
      compress_log_output(0x8000000,DAT_004f9bec);
    }
  }
  else if (param_2 == 0) {
    iVar5 = FUN_0043d0ce();
    if (iVar5 << 0x1e < 0) {
      FUN_0043d574(2,DAT_004f9bd8,DAT_004f9af8,DAT_004f9be8,0xd8a,DAT_004f9bf0);
    }
    iVar5 = FUN_0043d0ce();
    if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
      compress_log_output(0x8000000,DAT_004f9bf4,DAT_004f9bf4);
    }
  }
  else {
    cVar1 = *param_1;
    if (cVar1 == '\0') {
      cVar1 = param_1[1];
      if (*DAT_004f9d74 == 0) {
        if (cVar1 == '\n') {
          if (*DAT_004f9360 == 0) {
            if (*DAT_004f9350 != 0) {
              if (*DAT_004f9d78 < 0) {
                FUN_004f7ae4(0);
              }
              else {
                FUN_004f7ae4(*DAT_004f9d78);
              }
            }
          }
          else {
            iVar5 = 0;
            piVar6 = (int *)(uint)*DAT_004f9360;
            if (((int *)(uint)*DAT_004f9360 == (int *)0x2) &&
               (iVar5 = *DAT_004f9d78, piVar6 = DAT_004f9d78, -1 < iVar5)) {
              FUN_004f7cb0(*DAT_004f9d78);
            }
            else {
              iVar5 = FUN_0043d0ce(piVar6,iVar5,param_1[5],param_4,param_1,param_2,param_3,param_4);
              if (iVar5 << 0x1e < 0) {
                FUN_0043d574(4,DAT_004f9bd8,DAT_004f9af8,DAT_004f9be8,0xe18,DAT_004f9d7c,*pbVar2,
                             *DAT_004f9d78);
              }
              iVar5 = FUN_0043d0ce();
              if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
                compress_log_output(0x10800000,DAT_004f9d80,DAT_004f9d80,*pbVar2,*DAT_004f9d78);
              }
            }
          }
        }
        else if (cVar1 == 'D') {
          if (*DAT_004f9360 == 0) {
            if (*DAT_004f9350 != 0) {
              if (*DAT_004f9d78 < 0) {
                FUN_004f7ae4(0);
              }
              else {
                FUN_004f7ae4(*DAT_004f9d78);
              }
            }
          }
          else if ((*DAT_004f9360 == 2) && (-1 < *DAT_004f9d78)) {
            iVar5 = FUN_004f61a0(2);
            if (iVar5 != 0) {
              FUN_004f6282(2);
            }
            FUN_004f7c10(*piVar4 + 1);
          }
        }
        else if (cVar1 == 'E') {
          if (*DAT_004f9360 == 0) {
            if (*DAT_004f9350 != 0) {
              if (*DAT_004f9d78 < 0) {
                FUN_004f7ae4(0);
              }
              else {
                FUN_004f7ae4(*DAT_004f9d78);
              }
            }
          }
          else if ((*DAT_004f9360 == 2) && (-1 < *DAT_004f9d78)) {
            iVar5 = FUN_004f61a0(1);
            if (iVar5 != 0) {
              FUN_004f6282(1);
            }
            FUN_004f7c10(*piVar4 + -1);
          }
        }
        else if (cVar1 != 'F') {
          if (cVar1 == 'H') {
            if (*DAT_004f9360 == 2) {
              FUN_004f7b84();
            }
            else if (*DAT_004f9360 == 0) {
              FUN_004faf20();
            }
          }
          else if (cVar1 == 'I') {
            FUN_004e8a90();
            *piVar6 = 0;
            *piVar3 = 0;
          }
          else {
            iVar5 = FUN_0043d0ce(cVar1,0,param_1[5],param_4,param_1,param_2,param_3,param_4);
            if (iVar5 << 0x1e < 0) {
              FUN_0043d574(2,DAT_004f9bd8,DAT_004f9af8,DAT_004f9be8,0xe2d,DAT_004f9f04,cVar1);
            }
            iVar5 = FUN_0043d0ce();
            if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
              compress_log_output(0x8400000,DAT_004fa040,DAT_004fa040,cVar1);
            }
          }
        }
      }
      else {
        ui_common_api_fn_00509ca2(*DAT_004f9358,param_1 + 1,5);
      }
    }
    else if (cVar1 == '\x01') {
      FUN_004e8970(param_1 + 1,param_2 + -1);
    }
    else if (cVar1 == '\x05') {
      FUN_004f8644(param_1 + 1,param_2 + -1);
    }
  }
  return 0;
}

