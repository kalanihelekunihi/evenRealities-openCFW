
int FUN_004fb360(void)

{
  int *piVar1;
  int *piVar2;
  int *piVar3;
  int *piVar4;
  int iVar5;
  int iVar6;
  char local_24 [3];
  undefined1 local_21;
  undefined1 local_20;
  
  piVar1 = DAT_004fb738;
  *DAT_004fb738 = 0;
  piVar2 = DAT_004fb73c;
  iVar5 = 0;
  if (((*DAT_004fb73c != 0) &&
      (iVar5 = ui_common_api_fn_00509dfa(*DAT_004fb73c), piVar3 = DAT_004fb740, iVar5 == 0)) &&
     (iVar5 = *DAT_004fb740, iVar5 == 1)) {
    FUN_0043c0e4(local_24,10,0);
    FUN_0043c0e4(local_24,10,0);
    ui_common_api_fn_00509e14(*piVar2,local_24,5);
    piVar4 = DAT_004fb744;
    if (local_24[0] == '\n') {
      iVar5 = FUN_0044ddea(*DAT_004fb744,local_20,local_21);
      while (iVar5 = iVar5 + -1, -1 < iVar5) {
        iVar6 = FUN_0044dce2(*piVar4,iVar5);
        if (iVar6 != 0) {
          FUN_0044d7b8();
        }
      }
      if (*piVar2 != 0) {
        ui_common_api_fn_00509c96(*piVar2);
        *piVar2 = 0;
      }
      *piVar3 = 0;
      *piVar1 = 0;
      FUN_004e92f4();
      iVar5 = FUN_005000cc(*DAT_004fb748,5);
    }
    else if (local_24[0] == 'D') {
      if (*DAT_004fb734 + 1 < 2) {
        iVar5 = FUN_004fb290();
      }
      else {
        iVar5 = 1;
      }
    }
    else if (local_24[0] == 'E') {
      if (*DAT_004fb734 + -1 < 0) {
        iVar5 = 0;
      }
      else {
        iVar5 = FUN_004fb290();
      }
    }
    else if (local_24[0] == 'F') {
      iVar5 = 0x46;
    }
    else if (local_24[0] == 'G') {
      iVar5 = *piVar3;
      if (((iVar5 == 1) && (iVar5 = 0, *piVar2 != 0)) &&
         ((iVar5 = *piVar1, iVar5 == 0 && (iVar5 = 0, *DAT_004fb744 != 0)))) {
        FUN_0044d878(*DAT_004fb744);
        iVar5 = FUN_004fc644(*piVar4);
      }
    }
    else if (local_24[0] == 'H') {
      iVar5 = FUN_0044ddea(*DAT_004fb744,local_20,local_21);
      while (iVar5 = iVar5 + -1, -1 < iVar5) {
        iVar6 = FUN_0044dce2(*piVar4,iVar5);
        if (iVar6 != 0) {
          FUN_0044d7b8();
        }
      }
      if (*piVar2 != 0) {
        ui_common_api_fn_00509c96(*piVar2);
        *piVar2 = 0;
      }
      *piVar3 = 0;
      *piVar1 = 0;
      FUN_004e92f4();
      iVar5 = FUN_005000cc(*DAT_004fb748,5);
    }
    else if (local_24[0] == 'I') {
      FUN_004e8a90();
      *piVar3 = 0;
      iVar5 = 0;
      *piVar1 = 0;
    }
    else {
      iVar5 = FUN_0043d0ce();
      if (iVar5 << 0x1e < 0) {
        FUN_0043d574(2,DAT_004fb70c,DAT_004fb708,DAT_004fb750,0x146,DAT_004fb74c,local_24[0]);
      }
      iVar5 = FUN_0043d0ce();
      if (-1 < iVar5 << 0x1f) {
        iVar5 = FUN_0043d0ce();
        if (-1 < iVar5 << 0x1d) {
          return iVar5 << 0x1d;
        }
      }
      iVar5 = compress_log_output(0x8400000,DAT_004fb754,DAT_004fb754,local_24[0]);
    }
  }
  return iVar5;
}

