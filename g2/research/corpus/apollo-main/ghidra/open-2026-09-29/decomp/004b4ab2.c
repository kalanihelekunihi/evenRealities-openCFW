
int HciDrvHandler(undefined4 param_1,int param_2,undefined4 param_3,int param_4)

{
  uint *puVar1;
  uint *puVar2;
  int *piVar3;
  undefined4 uVar4;
  int *piVar5;
  ushort uVar6;
  int iVar7;
  undefined4 *puVar8;
  int iVar9;
  uint uVar10;
  uint uVar11;
  uint uVar12;
  uint uVar13;
  uint uVar14;
  int local_28;
  
  puVar2 = DAT_004b4d88;
  puVar1 = DAT_004b4d84;
  uVar12 = 0;
  uVar11 = 0;
  local_28 = param_4;
  if ((param_2 == 0) || (*(char *)(param_2 + 2) != '\x02')) {
    uVar13 = 0;
    if (*DAT_004b4d88 < *DAT_004b4d84) {
      uVar6 = hciTrSerialRxIncoming
                        (*DAT_004b4dac + *DAT_004b4d88,*DAT_004b4d84 - *DAT_004b4d88 & 0xffff);
      *puVar2 = *puVar2 + (uint)uVar6;
      if (*puVar2 != *puVar1) {
        WsfSetEvent(*DAT_004b4da4,1);
        return param_4;
      }
      *puVar1 = 0;
      *puVar2 = 0;
    }
    do {
      while( true ) {
        while( true ) {
          piVar5 = DAT_004b4db0;
          uVar4 = DAT_004b4d9c;
          piVar3 = DAT_004b4d94;
          iVar7 = DAT_004b4d90;
          uVar14 = uVar13 + 1;
          if (999 < uVar13) goto LAB_004b4c66;
          uVar13 = uVar14;
          if (-1 < *DAT_004b4db0 << 10) break;
          local_28 = *DAT_004b4d94;
          WsfTimerStop(DAT_004b4d9c);
          WsfTimerStartMs(uVar4,10000);
          *puVar1 = 0;
          iVar7 = FUN_0052e1ea(*DAT_004b4d74,DAT_004b4db4,puVar1);
          if (0x100 < *puVar1) {
            error_check(DAT_004b4db8);
          }
          if (iVar7 == 0) {
            uVar10 = 0;
            while (((uVar10 < 2000 && (*piVar5 << 10 < 0)) && (*piVar3 == local_28))) {
              FUN_00491102(1);
              uVar10 = uVar10 + 1;
            }
            uVar10 = hciTrSerialRxIncoming(*DAT_004b4dac,*puVar1 & 0xffff);
            *puVar2 = uVar10;
            if (*puVar2 != *puVar1) {
              WsfSetEvent(*DAT_004b4da4,1);
              goto LAB_004b4c66;
            }
            *puVar1 = 0;
            *puVar2 = 0;
            uVar11 = uVar11 + 1;
          }
          else if (iVar7 != 0) {
            error_check(iVar7);
            HciDrvRadioShutdown();
            HciDrvRadioBoot(0);
            HciDrvEmptyWriteQueue();
            DmDevReset();
            return local_28;
          }
          if (3 < uVar11) {
            WsfSetEvent(*DAT_004b4da4,1);
            goto LAB_004b4c66;
          }
        }
        if (*(int *)(DAT_004b4d90 + 8) == 0) goto LAB_004b4c66;
        puVar8 = (undefined4 *)(*(int *)(DAT_004b4d90 + 0x14) + *(int *)(DAT_004b4d90 + 4));
        iVar9 = FUN_0052e0d2(*DAT_004b4d74,puVar8 + 1,*puVar8);
        uVar4 = DAT_004b4d9c;
        if (iVar9 != 0) break;
        WsfTimerStop(DAT_004b4d9c);
        WsfTimerStartMs(uVar4,10000);
        FUN_005300e2(iVar7,0,1);
        uVar12 = 0;
        uVar13 = 0;
      }
      uVar12 = uVar12 + 1;
    } while (uVar12 < 0x2711);
    WsfSetEvent(*DAT_004b4da4,1);
LAB_004b4c66:
    if (uVar14 == 1000) {
      error_check(DAT_004b4dbc);
      HciDrvRadioShutdown();
      HciDrvRadioBoot(0);
      HciDrvEmptyWriteQueue();
      DmDevReset();
    }
  }
  else {
    HciReadBufSizeCmd();
    WsfTimerStartMs(DAT_004b4d9c,10000);
  }
  return local_28;
}

