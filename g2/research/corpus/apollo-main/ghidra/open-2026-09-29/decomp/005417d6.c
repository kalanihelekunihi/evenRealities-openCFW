
undefined8
uart_thread_handler(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int *piVar1;
  int *piVar2;
  undefined4 uVar3;
  int iVar4;
  int iVar5;
  char *pcVar6;
  uint uVar7;
  uint uVar8;
  
  piVar1 = DAT_00541a94;
  iVar4 = osMutexNew(0);
  *piVar1 = iVar4;
  piVar2 = DAT_00541a8c;
  if (*piVar1 == 0) {
    iVar4 = FUN_0043d0ce();
    if (iVar4 << 0x1e < 0) {
      param_1 = 0x60;
      param_2 = DAT_00541a98;
      FUN_0043d574(1,DAT_00541aa4,DAT_00541aa0,DAT_00541a9c,0x60,DAT_00541a98,param_3);
    }
    iVar4 = FUN_0043d0ce();
    if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_00541aa8,DAT_00541aa8);
    }
  }
  else {
    iVar4 = osEventFlagsNew(0);
    *piVar2 = iVar4;
    piVar1 = DAT_00541a88;
    if (*piVar2 == 0) {
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        param_1 = 0x66;
        param_2 = DAT_00541aac;
        FUN_0043d574(1,DAT_00541aa4,DAT_00541aa0,DAT_00541a9c,0x66,DAT_00541aac,param_3);
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        compress_log_output(0x4000000,DAT_00541ab0,DAT_00541ab0);
      }
    }
    else {
      param_2 = 0;
      param_1 = DAT_00541ab4;
      iVar4 = FUN_0057df7c(0x6000,1,0,DAT_00541ab8,DAT_00541ab4,0,0,param_4);
      *piVar1 = iVar4;
      if (*piVar1 == 0) {
        iVar4 = FUN_0043d0ce();
        if (iVar4 << 0x1e < 0) {
          param_1 = 0x71;
          param_2 = DAT_00541abc;
          FUN_0043d574(1,DAT_00541aa4,DAT_00541aa0,DAT_00541a9c);
        }
        iVar4 = FUN_0043d0ce();
        if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
          compress_log_output(0x4000000,DAT_00541ac0,DAT_00541ac0);
        }
      }
      else {
        iVar4 = FUN_0045e8d0();
        if (iVar4 == 0) {
          (*(code *)*DAT_00541acc)();
          FUN_00444720();
          uart_sync_transport_reset();
          FUN_00584e94();
          FUN_004ac828(3);
          iVar4 = FUN_0045a570();
          if (iVar4 == 2) {
            FUN_00471528();
          }
          RPC_OnboardingFlagSendToPeer();
          RPC_SyncRingStatusWithPeer();
          SVC_RingBattery_RequestFromPeer();
          FUN_00501d5c();
          FUN_00501066(1);
LAB_0054199a:
          do {
            iVar4 = osEventFlagsWait(*piVar2,7,2,0xffffffff);
            if (iVar4 << 0x1f < 0) {
              osEventFlagsClear(*piVar2,1);
              uVar7 = 0;
              uVar8 = 0;
              iVar5 = productModeGet();
              pcVar6 = DAT_00541ad8;
              if ((iVar5 == 1) && (*DAT_00541ad8 == '\x01')) {
                *DAT_00541ad8 = '\0';
                pcVar6 = pcVar6 + 1;
                FUN_0057e136(*piVar1,pcVar6,10,0);
                iVar4 = FUN_0043d0ce();
                if (iVar4 << 0x1e < 0) {
                  FUN_0043d574(3,DAT_00541aa4,DAT_00541aa0,DAT_00541a9c,0x9f,DAT_00541ad0,pcVar6);
                }
                iVar4 = FUN_0043d0ce();
                if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
                  compress_log_output(0xc400000,DAT_00541ad4,DAT_00541ad4,pcVar6);
                }
                goto LAB_0054199a;
              }
              while( true ) {
                uVar3 = DAT_00541adc;
                FUN_0043c0e4(DAT_00541adc,0x400,0);
                iVar5 = FUN_0057e136(*piVar1,uVar3,0x400,0);
                if (iVar5 == 0) break;
                uVar7 = iVar5 + uVar7;
                FUN_0045d4dc(uVar3,iVar5);
                uVar8 = uVar8 + 1;
                if ((0x7fff < uVar7) || (0x1f < uVar8)) break;
              }
            }
            if (iVar4 << 0x1e < 0) {
              osEventFlagsClear(*piVar2,2);
              FUN_0045e664();
            }
            if (iVar4 << 0x1d < 0) {
              osEventFlagsClear(*piVar2,4);
              FUN_0045d4b8();
            }
          } while( true );
        }
        iVar4 = FUN_0043d0ce();
        if (iVar4 << 0x1e < 0) {
          param_1 = 0x76;
          param_2 = DAT_00541ac4;
          FUN_0043d574(1,DAT_00541aa4,DAT_00541aa0,DAT_00541a9c);
        }
        iVar4 = FUN_0043d0ce();
        if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
          compress_log_output(0x4000000,DAT_00541ac8,DAT_00541ac8);
        }
      }
    }
  }
  return CONCAT44(param_2,param_1);
}

