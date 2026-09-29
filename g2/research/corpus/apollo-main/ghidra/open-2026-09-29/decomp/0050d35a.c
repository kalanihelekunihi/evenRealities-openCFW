
void ui_onboarding_stock_sub_0050D35A(int param_1,int param_2)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  uint uVar4;
  uint uVar5;
  undefined4 local_a98;
  undefined4 local_a94;
  undefined1 auStack_718 [896];
  undefined1 auStack_398 [896];
  
  if (param_1 == 0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      local_a94 = DAT_0050d86c;
      local_a98 = 0x21a;
      FUN_0043d574(1,DAT_0050d558,DAT_0050d554,DAT_0050d870);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_0050d874);
    }
  }
  else {
    uVar5 = param_2 * 3 + 1;
    uVar4 = param_2 * 3 + 2;
    iVar1 = ui_onboarding_stock_sub_0050CB28();
    if ((param_2 * 3 < iVar1) &&
       (iVar1 = ui_onboarding_stock_sub_0050CA56(auStack_398,param_2 * 3 & 0xffff), iVar1 != 0)) {
      FUN_00498680(*(undefined4 *)(param_1 + 4),DAT_0050d878);
      uVar3 = DAT_0050d87c;
      uVar2 = FUN_00460084(DAT_0050d87c);
      uVar3 = FUN_0045fffe(uVar3,uVar2);
      FUN_0049942e(*(undefined4 *)(param_1 + 8),uVar3);
      uVar3 = DAT_0050d880;
      uVar2 = FUN_00460084(DAT_0050d880);
      uVar3 = FUN_0045fffe(uVar3,uVar2);
      FUN_0049942e(*(undefined4 *)(param_1 + 0xc),uVar3);
      FUN_0049942e(*(undefined4 *)(param_1 + 0x14),DAT_0050d884);
      FUN_0049942e(*(undefined4 *)(param_1 + 0x18),DAT_0050d888);
      FUN_00498680(*(undefined4 *)(param_1 + 0x10),DAT_0050d88c);
    }
    iVar1 = ui_onboarding_stock_sub_0050CB28();
    if (((int)uVar5 < iVar1) &&
       (iVar1 = ui_onboarding_stock_sub_0050CA56(auStack_718,uVar5 & 0xffff), iVar1 != 0)) {
      FUN_00498680(*(undefined4 *)(param_1 + 0x1c),DAT_0050d878);
      uVar3 = DAT_0050d890;
      uVar2 = FUN_00460084(DAT_0050d890);
      uVar3 = FUN_0045fffe(uVar3,uVar2);
      FUN_0049942e(*(undefined4 *)(param_1 + 0x20),uVar3);
      uVar3 = DAT_0050daa8;
      uVar2 = FUN_00460084(DAT_0050daa8);
      uVar3 = FUN_0045fffe(uVar3,uVar2);
      FUN_0049942e(*(undefined4 *)(param_1 + 0x24),uVar3);
      FUN_0049942e(*(undefined4 *)(param_1 + 0x2c),DAT_0050daac);
      FUN_0049942e(*(undefined4 *)(param_1 + 0x30),DAT_0050dab0);
      FUN_00498680(*(undefined4 *)(param_1 + 0x28),DAT_0050dab4);
    }
    iVar1 = ui_onboarding_stock_sub_0050CB28();
    if (((int)uVar4 < iVar1) &&
       (iVar1 = ui_onboarding_stock_sub_0050CA56(&local_a98,uVar4 & 0xffff), iVar1 != 0)) {
      FUN_00498680(*(undefined4 *)(param_1 + 0x34),DAT_0050d878);
      uVar3 = DAT_0050db1c;
      uVar2 = FUN_00460084(DAT_0050db1c);
      uVar3 = FUN_0045fffe(uVar3,uVar2);
      FUN_0049942e(*(undefined4 *)(param_1 + 0x38),uVar3);
      uVar3 = DAT_0050db20;
      uVar2 = FUN_00460084(DAT_0050db20);
      uVar3 = FUN_0045fffe(uVar3,uVar2);
      FUN_0049942e(*(undefined4 *)(param_1 + 0x3c),uVar3);
      FUN_0049942e(*(undefined4 *)(param_1 + 0x44),DAT_0050db24);
      FUN_0049942e(*(undefined4 *)(param_1 + 0x48),DAT_0050db28);
      FUN_00498680(*(undefined4 *)(param_1 + 0x40),DAT_0050dc4c);
    }
    ui_onboarding_stock_sub_0050E48A(param_1,param_2);
    *(undefined1 *)(param_1 + 0x5c) = 1;
  }
  return;
}

