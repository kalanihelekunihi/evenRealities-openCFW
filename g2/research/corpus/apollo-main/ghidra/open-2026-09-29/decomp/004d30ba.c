
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8 FUN_004d30ba(char *param_1,undefined *param_2,undefined4 param_3,undefined4 param_4)

{
  char cVar1;
  undefined4 *puVar2;
  undefined *puVar3;
  int iVar4;
  undefined4 uVar5;
  undefined4 uVar6;
  char *pcVar7;
  undefined *puVar8;
  
  pcVar7 = param_1;
  puVar8 = param_2;
  iVar4 = FUN_0043d0ce();
  if (iVar4 << 0x1e < 0) {
    pcVar7 = (char *)0xd4;
    puVar8 = PTR_s_system_alert_ReflashEventHandler_004d3484;
    FUN_0043d574(4,PTR_s_system_alert_004d3428,PTR_s_D__01_workspace_s200_ap510b_iar__004d3424,
                 PTR_s_system_alert_ReflashEventHandler_004d3488,0xd4,
                 PTR_s_system_alert_ReflashEventHandler_004d3484,param_3,param_4);
  }
  iVar4 = FUN_0043d0ce();
  if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
    compress_log_output(0x10000000,PTR_s__system_alert_system_alert_Refla_004d348c);
  }
  puVar2 = _DAT_004d347c;
  if ((param_1 == (char *)0x0) || (param_2 == (undefined *)0x0)) {
    if ((*_DAT_004d3430 & 0xff) == 1) {
      FUN_0044d878(*_DAT_004d347c);
      uVar5 = FUN_00498668(*puVar2);
      FUN_00498680(uVar5,PTR_DAT_004d3498);
      FUN_0043f506(uVar5,0x18);
      FUN_0043f568(uVar5,0x18);
      FUN_0043f0e0(uVar5,0);
      FUN_0043f142(uVar5,8);
      FUN_0043ded4(uVar5,0x10000);
      FUN_0043dfa4(uVar5,0x10);
      uVar5 = FUN_00499416(*puVar2);
      puVar3 = PTR_s_ID_GENERAL_RING_DISCONNECT_004d349c;
      uVar6 = FUN_00460084(PTR_s_ID_GENERAL_RING_DISCONNECT_004d349c);
      uVar6 = FUN_0045fffe(puVar3,uVar6);
      FUN_0049942e(uVar5,uVar6);
      FUN_0043f506(uVar5,0x3fffffff);
      FUN_0043f568(uVar5,0x3fffffff);
      FUN_0043f0e0(uVar5,0x24);
      FUN_0043f142(uVar5,6);
      FUN_0043ded4(uVar5,0x10000);
      FUN_0043dfa4(uVar5,0x10);
      FUN_0044143e(uVar5,*_DAT_004d34a0,0);
      uVar6 = FUN_0044104c(0xffffff);
      FUN_0044140e(uVar5,uVar6,0);
      iVar4 = FUN_0045a568();
      if (iVar4 == 1) {
        FUN_0043f6b8(*puVar2,9,0,0);
      }
      puVar2 = _DAT_004d3478;
      FUN_0043f6b8(*_DAT_004d3478,2,0,0);
      FUN_0043f66c(*puVar2);
    }
    else if ((*_DAT_004d3430 & 0xff) == 2) {
      FUN_0044d878(*_DAT_004d347c);
      uVar5 = FUN_00498668(*puVar2);
      FUN_00498680(uVar5,PTR_DAT_004d34a4);
      FUN_0043f506(uVar5,0x18);
      FUN_0043f568(uVar5,0x18);
      FUN_0043f0e0(uVar5,0);
      FUN_0043f142(uVar5,8);
      FUN_0043ded4(uVar5,0x10000);
      FUN_0043dfa4(uVar5,0x10);
      uVar5 = FUN_00499416(*puVar2);
      puVar3 = PTR_s_ID_GENERAL_RING_CONNECT_004d34a8;
      uVar6 = FUN_00460084(PTR_s_ID_GENERAL_RING_CONNECT_004d34a8);
      uVar6 = FUN_0045fffe(puVar3,uVar6);
      FUN_0049942e(uVar5,uVar6);
      FUN_0043f506(uVar5,0x3fffffff);
      FUN_0043f568(uVar5,0x3fffffff);
      FUN_0043f0e0(uVar5,0x24);
      FUN_0043f142(uVar5,6);
      FUN_0043ded4(uVar5,0x10000);
      FUN_0043dfa4(uVar5,0x10);
      FUN_0044143e(uVar5,*_DAT_004d34a0,0);
      uVar6 = FUN_0044104c(0xffffff);
      FUN_0044140e(uVar5,uVar6,0);
      iVar4 = FUN_0045a568();
      if (iVar4 == 1) {
        FUN_0043f6b8(*puVar2,9,0,0);
      }
      puVar2 = _DAT_004d3478;
      FUN_0043f6b8(*_DAT_004d3478,2,0,0);
      FUN_0043f66c(*puVar2);
    }
  }
  else {
    cVar1 = *param_1;
    if (cVar1 == '\x05') {
      *_DAT_004d3440 = 0;
      *_DAT_004d3444 = 0xb4;
      FUN_00464c36(0x21,0,0,0);
    }
    else {
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        pcVar7 = (char *)0xdf;
        puVar8 = PTR_s_unknown_system_alert_event_type__004d3490;
        FUN_0043d574(2,PTR_s_system_alert_004d3428,PTR_s_D__01_workspace_s200_ap510b_iar__004d3424,
                     PTR_s_system_alert_ReflashEventHandler_004d3488,0xdf,
                     PTR_s_unknown_system_alert_event_type__004d3490,cVar1);
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        compress_log_output(0x8400000,PTR_s__system_alert_unknown_system_ale_004d3494,
                            PTR_s__system_alert_unknown_system_ale_004d3494,cVar1);
      }
    }
  }
  return CONCAT44(puVar8,pcVar7);
}

