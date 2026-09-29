
undefined8 ui_onboarding_main_sub_004AA270(uint param_1,undefined4 param_2)

{
  undefined4 *puVar1;
  undefined4 *puVar2;
  undefined4 *puVar3;
  undefined4 *puVar4;
  int *piVar5;
  undefined4 *puVar6;
  uint uVar7;
  undefined4 uVar8;
  undefined4 uVar9;
  int iVar10;
  uint uVar11;
  
  uVar11 = param_1;
  FUN_0043ded4(*DAT_004aab78,1);
  puVar1 = DAT_004aab84;
  FUN_0043dfa4(*DAT_004aab84,1);
  puVar4 = DAT_004aae2c;
  FUN_0043dfa4(*DAT_004aae2c,1);
  piVar5 = DAT_004aae30;
  FUN_0043dfa4(*DAT_004aae30,1);
  puVar6 = DAT_004aae34;
  FUN_0043dfa4(*DAT_004aae34,1);
  puVar2 = DAT_004aab88;
  FUN_0043dfa4(*DAT_004aab88,1);
  puVar3 = DAT_004aae24;
  FUN_0043dfa4(*DAT_004aae24,1);
  uVar7 = param_1 & 0xff;
  if (uVar7 == 0) {
    if (*DAT_004aa650 == 1) {
      ui_onboarding_main_sub_004A9E48();
    }
    if (*piVar5 != 0) {
      FUN_0044ea04(*piVar5,0,0);
      *DAT_004aa64c = 0;
      ui_onboarding_main_sub_004A859E(0,0);
    }
    FUN_00441488(*puVar1,0xff,0);
    FUN_0050fc86(param_1 & 0xff);
    FUN_004ab004(param_1 & 0xff);
    uVar9 = DAT_004ab064;
    uVar8 = FUN_00460084(DAT_004ab064);
    uVar9 = FUN_0045fffe(uVar9,uVar8);
    FUN_0049942e(*DAT_004ab068,uVar9);
    FUN_00441488(*puVar4,0,0);
    FUN_00441488(*piVar5,0,0);
    FUN_00441488(*puVar6,0,0);
    iVar10 = FUN_0043fd9e(*puVar2);
    FUN_0043f09a(*puVar2,-iVar10,0);
    FUN_00441488(*DAT_004ab06c,0,0);
    FUN_00441488(*puVar3,0,0);
  }
  else if (uVar7 == 2) {
    FUN_00441488(*puVar1,0xff,0);
    FUN_0050fc86(param_1 & 0xff);
    FUN_004ab004(param_1 & 0xff);
    uVar9 = DAT_004ab070;
    uVar8 = FUN_00460084(DAT_004ab070);
    uVar9 = FUN_0045fffe(uVar9,uVar8);
    FUN_0049942e(*DAT_004ab068,uVar9);
    FUN_00441488(*puVar4,0x7f,0);
    ui_onboarding_main_sub_004A859E(*DAT_004aa64c,1);
    FUN_00441488(*piVar5,0x7f,0);
    FUN_00441488(*puVar6,0,0);
    iVar10 = FUN_0043fd9e(*puVar2);
    FUN_0043f09a(*puVar2,-iVar10,0);
    FUN_00441488(*DAT_004ab06c,0,0);
    FUN_00441488(*puVar3,0,0);
  }
  else if (uVar7 < 2) {
    FUN_00441488(*puVar1,0,0);
    FUN_0050fe0e();
    FUN_00441488(*puVar4,0,0);
    ui_onboarding_main_sub_004A859E(*DAT_004aa64c,0);
    FUN_00441488(*piVar5,0,0);
    FUN_00441488(*puVar6,0,0);
    iVar10 = FUN_0043fd9e(*puVar2);
    FUN_0043f09a(*puVar2,-iVar10,0);
    FUN_00441488(*DAT_004ab06c,0,0);
    FUN_00441488(*puVar3,0,0);
    ui_onboarding_main_sub_004A95E8(*puVar4);
    ui_onboarding_main_sub_004A95E8(*piVar5);
  }
  else if (uVar7 == 4) {
    FUN_00441488(*puVar1,0xff,0);
    FUN_0050fc86(param_1 & 0xff);
    FUN_004ab004(param_1 & 0xff);
    uVar9 = DAT_004ab074;
    uVar8 = FUN_00460084(DAT_004ab074);
    uVar9 = FUN_0045fffe(uVar9,uVar8);
    FUN_0049942e(*DAT_004ab068,uVar9);
    FUN_00441488(*puVar4,0x7f,0);
    ui_onboarding_main_sub_004A859E(*DAT_004aa64c,1);
    FUN_00441488(*piVar5,0x7f,0);
    FUN_00441488(*puVar6,0,0);
    iVar10 = FUN_0043fd9e(*puVar2);
    FUN_0043f09a(*puVar2,-iVar10,0);
    FUN_00441488(*DAT_004ab06c,0,0);
    FUN_00441488(*puVar3,0,0);
  }
  else if (uVar7 < 4) {
    FUN_00441488(*puVar1,0,0);
    FUN_0050fe0e();
    FUN_00441488(*puVar4,0xff,0);
    ui_onboarding_main_sub_004A859E(*DAT_004aa64c,0);
    FUN_00441488(*piVar5,0xff,0);
    FUN_00441488(*puVar6,0,0);
    iVar10 = FUN_0043fd9e(*puVar2);
    FUN_0043f09a(*puVar2,-iVar10,0);
    FUN_00441488(*DAT_004ab06c,0,0);
    FUN_00441488(*puVar3,0,0);
  }
  else if (uVar7 == 6) {
    FUN_00441488(*puVar1,0xff,0);
    FUN_0050fc86(param_1 & 0xff);
    FUN_004ab004(param_1 & 0xff);
    uVar9 = DAT_004ab078;
    uVar8 = FUN_00460084(DAT_004ab078);
    uVar9 = FUN_0045fffe(uVar9,uVar8);
    FUN_0049942e(*DAT_004ab068,uVar9);
    FUN_00441488(*puVar4,0,0);
    FUN_00441488(*piVar5,0,0);
    FUN_00441488(*puVar6,0x7f,0);
    iVar10 = FUN_0043fd9e(*puVar2);
    FUN_0043f09a(*puVar2,-iVar10,0);
    FUN_00441488(*DAT_004ab06c,0,0);
    FUN_00441488(*puVar3,0,0);
  }
  else if (uVar7 < 6) {
    FUN_00441488(*puVar1,0,0);
    FUN_0050fe0e();
    FUN_00441488(*puVar4,0,0);
    ui_onboarding_main_sub_004A859E(*DAT_004aa64c,0);
    FUN_00441488(*piVar5,0,0);
    FUN_00441488(*puVar6,0xff,0);
    iVar10 = FUN_0043fd9e(*puVar2);
    FUN_0043f09a(*puVar2,-iVar10,0);
    FUN_00441488(*DAT_004ab06c,0,0);
    FUN_00441488(*puVar3,0,0);
  }
  else if (uVar7 == 8) {
    FUN_00441488(*puVar1,0xff,0);
    FUN_0050fc86(param_1 & 0xff);
    FUN_004ab004(param_1 & 0xff);
    uVar9 = DAT_004ab080;
    uVar8 = FUN_00460084(DAT_004ab080);
    uVar9 = FUN_0045fffe(uVar9,uVar8);
    FUN_0049942e(*DAT_004ab068,uVar9);
    FUN_00441488(*puVar4,0x7f,0);
    ui_onboarding_main_sub_004A859E(*DAT_004ab07c,1);
    FUN_00441488(*piVar5,0x7f,0);
    FUN_00441488(*puVar6,0,0);
    iVar10 = FUN_0043fd9e(*puVar2);
    FUN_0043f09a(*puVar2,-iVar10,0);
    FUN_00441488(*DAT_004ab06c,0xff,0);
    FUN_00441488(*puVar3,0,0);
  }
  else if (uVar7 < 8) {
    FUN_00441488(*puVar1,0,0);
    FUN_0050fe0e();
    FUN_00441488(*puVar4,0xff,0);
    ui_onboarding_main_sub_004A859E(*DAT_004ab07c,0);
    FUN_00441488(*piVar5,0xff,0);
    FUN_00441488(*puVar6,0xff,0);
    iVar10 = FUN_0043fd9e(*puVar2);
    FUN_0043f09a(*puVar2,-iVar10,0);
    FUN_00441488(*DAT_004ab06c,0,0);
    FUN_00441488(*puVar3,0,0);
  }
  else if (uVar7 == 10) {
    FUN_00441488(*puVar1,0,0);
    FUN_0050fe0e();
    FUN_00441488(*puVar4,0x7f,0);
    ui_onboarding_main_sub_004A859E(*DAT_004ab07c,1);
    FUN_00441488(*piVar5,0x7f,0);
    FUN_00441488(*puVar6,0,0);
    FUN_0043f09a(*puVar2,0,0);
    FUN_00441488(*DAT_004ab06c,0x7f,0);
    FUN_00441488(*puVar3,0xff,0);
  }
  else if (uVar7 < 10) {
    FUN_00441488(*puVar1,0,0);
    FUN_0050fe0e();
    FUN_00441488(*puVar4,0x7f,0);
    ui_onboarding_main_sub_004A859E(*DAT_004ab07c,1);
    FUN_00441488(*piVar5,0x7f,0);
    FUN_00441488(*puVar6,0,0);
    FUN_00441488(*DAT_004ab06c,0xff,0);
    FUN_00441488(*puVar3,0,0);
    ui_onboarding_main_sub_004A88AA();
  }
  else if (uVar7 == 0xc) {
    FUN_00441488(*puVar1,0,0);
    FUN_0050fe0e();
    FUN_00441488(*puVar4,0x7f,0);
    ui_onboarding_main_sub_004A859E(*DAT_004ab07c,1);
    FUN_00441488(*piVar5,0x7f,0);
    FUN_00441488(*puVar6,0,0);
    FUN_00441488(*puVar3,0,0);
    ui_onboarding_main_sub_004A8968();
  }
  else if (uVar7 < 0xc) {
    FUN_00441488(*puVar1,0xff,0);
    FUN_0050fc86(param_1 & 0xff);
    FUN_004ab004(param_1 & 0xff);
    uVar9 = DAT_004ab084;
    uVar8 = FUN_00460084(DAT_004ab084);
    uVar9 = FUN_0045fffe(uVar9,uVar8);
    FUN_0049942e(*DAT_004ab068,uVar9);
    FUN_00441488(*puVar4,0x7f,0);
    ui_onboarding_main_sub_004A859E(*DAT_004ab07c,1);
    FUN_00441488(*piVar5,0x7f,0);
    FUN_00441488(*puVar6,0,0);
    FUN_0043f09a(*puVar2,0,0);
    FUN_00441488(*DAT_004ab06c,0x7f,0);
    FUN_00441488(*puVar3,0,0);
  }
  else if (uVar7 == 0xe) {
    ui_onboarding_main_sub_004A9648(*puVar1,0,0);
    ui_onboarding_main_sub_004A9648(*puVar4,0,0);
    ui_onboarding_main_sub_004A9648(*piVar5,0,0);
  }
  else if (uVar7 < 0xe) {
    FUN_00441488(*puVar1,0xff,0);
    FUN_0050fc86(param_1 & 0xff);
    FUN_004ab004(param_1 & 0xff);
    uVar9 = DAT_004ab088;
    uVar8 = FUN_00460084(DAT_004ab088);
    uVar9 = FUN_0045fffe(uVar9,uVar8);
    FUN_0049942e(*DAT_004ab068,uVar9);
    FUN_00441488(*puVar4,0x7f,0);
    ui_onboarding_main_sub_004A859E(*DAT_004ab07c,1);
    FUN_00441488(*piVar5,0x7f,0);
    FUN_00441488(*puVar6,0,0);
    iVar10 = FUN_0043fd9e(*puVar2);
    FUN_0043f09a(*puVar2,-iVar10,0);
    FUN_00441488(*DAT_004ab06c,0,0);
    FUN_00441488(*puVar3,0,0);
  }
  else {
    iVar10 = FUN_0043d0ce();
    if (iVar10 << 0x1e < 0) {
      uVar11 = 0xa36;
      param_2 = DAT_004ab6c0;
      FUN_0043d574(2,DAT_004aab68,DAT_004aab64,DAT_004ab6c4,0xa36,DAT_004ab6c0,param_1 & 0xff);
    }
    iVar10 = FUN_0043d0ce();
    if ((iVar10 << 0x1f < 0) || (iVar10 = FUN_0043d0ce(), iVar10 << 0x1d < 0)) {
      compress_log_output(0x8400000,DAT_004ab6c8,DAT_004ab6c8,param_1 & 0xff);
    }
  }
  return CONCAT44(param_2,uVar11);
}

