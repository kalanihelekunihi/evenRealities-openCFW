
undefined8
ui_onboarding_stock_sub_0050DCBC(uint param_1,undefined4 param_2,undefined4 param_3,uint param_4)

{
  uint *puVar1;
  ushort *puVar2;
  int *piVar3;
  undefined4 *puVar4;
  int iVar5;
  undefined4 uVar6;
  undefined4 uVar7;
  undefined4 uVar8;
  
  puVar1 = DAT_0050dddc;
  *DAT_0050dddc = param_1;
  piVar3 = DAT_0050e868;
  if (*puVar1 < 6) {
    if (*(int *)(DAT_0050e85c + *puVar1 * 8 + 4) == 0) {
      iVar5 = FUN_0043d0ce();
      if (iVar5 << 0x1e < 0) {
        param_2 = 0x679;
        FUN_0043d574(1,DAT_0050e724,DAT_0050e720,DAT_0050e7e8,0x679,DAT_0050e860,*puVar1);
      }
      iVar5 = FUN_0043d0ce();
      if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
        compress_log_output(0x4400000,DAT_0050e864,DAT_0050e864,*puVar1);
      }
      uVar6 = 0xffffffff;
    }
    else {
      iVar5 = FUN_0043de82(*(undefined4 *)(DAT_0050e85c + *puVar1 * 8 + 4));
      *piVar3 = iVar5;
      if (*piVar3 == 0) {
        iVar5 = FUN_0043d0ce();
        if (iVar5 << 0x1e < 0) {
          param_2 = 0x681;
          FUN_0043d574(1,DAT_0050e724,DAT_0050e720,DAT_0050e7e8,0x681,DAT_0050e86c);
        }
        iVar5 = FUN_0043d0ce();
        if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
          compress_log_output(0x4000000,DAT_0050e8dc,DAT_0050e8dc);
        }
        uVar6 = 0xffffffff;
      }
      else {
        FUN_0043f09a(*piVar3,0x14,0x10);
        FUN_0043f4c0(*piVar3,0x13b,0xfe);
        FUN_0044129e(*piVar3,0,0);
        FUN_0044131c(*piVar3,0,0);
        ui_onboarding_stock_sub_0050CA24(*piVar3,0,0);
        FUN_0044e368(*piVar3,0);
        iVar5 = *DAT_0050e464;
        if (iVar5 * 3 < (int)(uint)*DAT_0050e51c) {
          uVar6 = FUN_00498668(*piVar3);
          FUN_0043f506(uVar6,0x18);
          FUN_0043f568(uVar6,0x18);
          FUN_0043f0e0(uVar6,0);
          FUN_0043f142(uVar6,3);
          FUN_0043ded4(uVar6,0x10000);
          FUN_0043dfa4(uVar6,0x10);
          FUN_00498680(uVar6,DAT_0050e8e0);
          uVar7 = FUN_00499416(*piVar3);
          FUN_0043f506(uVar7,0x9c);
          FUN_0043f568(uVar7,0x1c);
          FUN_0043f0e0(uVar7,0x20);
          FUN_0043f142(uVar7,0);
          puVar4 = DAT_0050e8e4;
          FUN_0044143e(uVar7,*DAT_0050e8e4,0);
          uVar6 = FUN_0044104c(0xffffff);
          FUN_0044140e(uVar7,uVar6,0);
          uVar6 = DAT_0050e8e8;
          uVar8 = FUN_00460084(DAT_0050e8e8);
          uVar6 = FUN_0045fffe(uVar6,uVar8);
          FUN_0049942e(uVar7,uVar6);
          uVar6 = FUN_00499416(*piVar3);
          FUN_0043f506(uVar6,0x7e);
          FUN_0043f568(uVar6,0x1c);
          FUN_0043f0e0(uVar6,0xbd);
          FUN_0043f142(uVar6,0);
          FUN_0044145a(uVar6,3,0);
          FUN_0044143e(uVar6,*puVar4,0);
          uVar7 = FUN_0044104c(0xffffff);
          FUN_0044140e(uVar6,uVar7,0);
          FUN_0049942e(uVar6,DAT_0050e8ec);
          uVar7 = FUN_00499416(*piVar3);
          FUN_0043f506(uVar7,0xf0);
          FUN_0043f568(uVar7,0x1c);
          FUN_0043f0e0(uVar7,0);
          FUN_0043f142(uVar7,0x22);
          FUN_0044143e(uVar7,*puVar4,0);
          uVar6 = FUN_0044104c(0xffffff);
          FUN_0044140e(uVar7,uVar6,0);
          uVar6 = DAT_0050e8f0;
          uVar8 = FUN_00460084(DAT_0050e8f0);
          uVar6 = FUN_0045fffe(uVar6,uVar8);
          FUN_0049942e(uVar7,uVar6);
          uVar6 = FUN_00499416(*piVar3);
          FUN_0043f506(uVar6,0x50);
          FUN_0043f568(uVar6,0x1c);
          FUN_0043f0e0(uVar6,0xeb);
          FUN_0043f142(uVar6,0x22);
          FUN_0044145a(uVar6,3,0);
          FUN_0044143e(uVar6,*puVar4,0);
          uVar7 = FUN_0044104c(0xffffff);
          FUN_0044140e(uVar6,uVar7,0);
          FUN_0049942e(uVar6,DAT_0050e8f4);
        }
        puVar2 = DAT_0050e51c;
        if (iVar5 * 3 + 1 < (int)(uint)*DAT_0050e51c) {
          uVar6 = FUN_00498668(*piVar3);
          FUN_0043f506(uVar6,0x18);
          FUN_0043f568(uVar6,0x18);
          FUN_0043f0e0(uVar6,0);
          FUN_0043f142(uVar6,99);
          FUN_0043ded4(uVar6,0x10000);
          FUN_0043dfa4(uVar6,0x10);
          FUN_00498680(uVar6,DAT_0050e8e0);
          uVar7 = FUN_00499416(*piVar3);
          FUN_0043f506(uVar7,0x9c);
          FUN_0043f568(uVar7,0x1c);
          FUN_0043f0e0(uVar7,0x20);
          FUN_0043f142(uVar7,0x60);
          puVar4 = DAT_0050e8e4;
          FUN_0044143e(uVar7,*DAT_0050e8e4,0);
          uVar6 = FUN_0044104c(0xffffff);
          FUN_0044140e(uVar7,uVar6,0);
          uVar6 = DAT_0050e8f8;
          uVar8 = FUN_00460084(DAT_0050e8f8);
          uVar6 = FUN_0045fffe(uVar6,uVar8);
          FUN_0049942e(uVar7,uVar6);
          uVar6 = FUN_00499416(*piVar3);
          FUN_0043f506(uVar6,0x7e);
          FUN_0043f568(uVar6,0x1c);
          FUN_0043f0e0(uVar6,0xbd);
          FUN_0043f142(uVar6,0x60);
          FUN_0044145a(uVar6,3,0);
          FUN_0044143e(uVar6,*puVar4,0);
          uVar7 = FUN_0044104c(0xffffff);
          FUN_0044140e(uVar6,uVar7,0);
          FUN_0049942e(uVar6,DAT_0050e8fc);
          uVar7 = FUN_00499416(*piVar3);
          FUN_0043f506(uVar7,0xf0);
          FUN_0043f568(uVar7,0x1c);
          FUN_0043f0e0(uVar7,0);
          FUN_0043f142(uVar7,0x82);
          FUN_0044143e(uVar7,*puVar4,0);
          uVar6 = FUN_0044104c(0xffffff);
          FUN_0044140e(uVar7,uVar6,0);
          uVar6 = DAT_0050e900;
          uVar8 = FUN_00460084(DAT_0050e900);
          uVar6 = FUN_0045fffe(uVar6,uVar8);
          FUN_0049942e(uVar7,uVar6);
          uVar6 = FUN_00499416(*piVar3);
          FUN_0043f506(uVar6,0x50);
          FUN_0043f568(uVar6,0x1c);
          FUN_0043f0e0(uVar6,0xeb);
          FUN_0043f142(uVar6,0x82);
          FUN_0044145a(uVar6,3,0);
          FUN_0044143e(uVar6,*puVar4,0);
          uVar7 = FUN_0044104c(0xffffff);
          FUN_0044140e(uVar6,uVar7,0);
          FUN_0049942e(uVar6,DAT_0050e904);
        }
        if (iVar5 * 3 + 2 < (int)(uint)*puVar2) {
          uVar6 = FUN_00498668(*piVar3);
          FUN_0043f506(uVar6,0x18);
          FUN_0043f568(uVar6,0x18);
          FUN_0043f0e0(uVar6,0);
          FUN_0043f142(uVar6,0xc3);
          FUN_0043ded4(uVar6,0x10000);
          FUN_0043dfa4(uVar6,0x10);
          FUN_00498680(uVar6,DAT_0050e8e0);
          uVar7 = FUN_00499416(*piVar3);
          FUN_0043f506(uVar7,0x9c);
          FUN_0043f568(uVar7,0x1c);
          FUN_0043f0e0(uVar7,0x20);
          FUN_0043f142(uVar7,0xc0);
          puVar4 = DAT_0050e8e4;
          FUN_0044143e(uVar7,*DAT_0050e8e4,0);
          uVar6 = FUN_0044104c(0xffffff);
          FUN_0044140e(uVar7,uVar6,0);
          uVar6 = DAT_0050e908;
          uVar8 = FUN_00460084(DAT_0050e908);
          uVar6 = FUN_0045fffe(uVar6,uVar8);
          FUN_0049942e(uVar7,uVar6);
          uVar6 = FUN_00499416(*piVar3);
          FUN_0043f506(uVar6,0x7e);
          FUN_0043f568(uVar6,0x1c);
          FUN_0043f0e0(uVar6,0xbd);
          FUN_0043f142(uVar6,0xc0);
          FUN_0044145a(uVar6,3,0);
          FUN_0044143e(uVar6,*puVar4,0);
          uVar7 = FUN_0044104c(0xffffff);
          FUN_0044140e(uVar6,uVar7,0);
          FUN_0049942e(uVar6,DAT_0050e90c);
          uVar7 = FUN_00499416(*piVar3);
          FUN_0043f506(uVar7,0xf0);
          FUN_0043f568(uVar7,0x1c);
          FUN_0043f0e0(uVar7,0);
          FUN_0043f142(uVar7,0xe2);
          FUN_0044143e(uVar7,*puVar4,0);
          uVar6 = FUN_0044104c(0xffffff);
          FUN_0044140e(uVar7,uVar6,0);
          uVar6 = DAT_0050e910;
          uVar8 = FUN_00460084(DAT_0050e910);
          uVar6 = FUN_0045fffe(uVar6,uVar8);
          FUN_0049942e(uVar7,uVar6);
          uVar6 = FUN_00499416(*piVar3);
          FUN_0043f506(uVar6,0x50);
          FUN_0043f568(uVar6,0x1c);
          FUN_0043f0e0(uVar6,0xeb);
          FUN_0043f142(uVar6,0xe2);
          FUN_0044145a(uVar6,3,0);
          FUN_0044143e(uVar6,*puVar4,0);
          uVar7 = FUN_0044104c(0xffffff);
          FUN_0044140e(uVar6,uVar7,0);
          FUN_0049942e(uVar6,DAT_0050e914);
        }
        iVar5 = ui_onboarding_stock_sub_0050E468(iVar5);
        uVar7 = FUN_0043de82(*piVar3);
        FUN_0043f506(uVar7,0x138);
        FUN_0043f568(uVar7,1);
        FUN_0043f0e0(uVar7,0);
        FUN_0043f142(uVar7,0x4f);
        uVar6 = DAT_0050e918;
        uVar8 = FUN_0044104c(DAT_0050e918);
        FUN_0044127e(uVar7,uVar8,0);
        FUN_0044129e(uVar7,0xff,0);
        FUN_0044131c(uVar7,0,0);
        ui_onboarding_stock_sub_0050CA24(uVar7,0,0);
        uVar8 = FUN_0043de82(*piVar3);
        FUN_0043f506(uVar8,0x138);
        FUN_0043f568(uVar8,1);
        FUN_0043f0e0(uVar8,0);
        FUN_0043f142(uVar8,0xaf);
        uVar6 = FUN_0044104c(uVar6);
        FUN_0044127e(uVar8,uVar6,0);
        FUN_0044129e(uVar8,0xff,0);
        FUN_0044131c(uVar8,0,0);
        ui_onboarding_stock_sub_0050CA24(uVar8,0,0);
        if (iVar5 < 2) {
          FUN_0043ded4(uVar7,1);
        }
        if (iVar5 < 3) {
          FUN_0043ded4(uVar8,1);
        }
        uVar6 = 0;
      }
    }
  }
  else {
    iVar5 = FUN_0043d0ce();
    if (iVar5 << 0x1e < 0) {
      param_4 = *puVar1;
      param_2 = 0x673;
      param_3 = DAT_0050e7e4;
      FUN_0043d574(1,DAT_0050e724,DAT_0050e720,DAT_0050e7e8,0x673,DAT_0050e7e4,param_4);
    }
    iVar5 = FUN_0043d0ce();
    if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
      compress_log_output(0x4400000,DAT_0050e7ec,DAT_0050e7ec,*puVar1,param_2,param_3,param_4);
    }
    uVar6 = 0xffffffff;
  }
  return CONCAT44(param_2,uVar6);
}

