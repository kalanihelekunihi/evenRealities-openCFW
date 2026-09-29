
undefined4 UX_BatterySyncHandler(undefined4 param_1,byte *param_2,uint param_3)

{
  byte bVar1;
  undefined1 uVar2;
  undefined1 uVar3;
  int iVar4;
  uint uVar5;
  uint uVar6;
  bool bVar7;
  bool bVar8;
  bool bVar9;
  
  if ((param_2 == (byte *)0x0) || (param_3 < 0xc)) {
    iVar4 = FUN_0043d0ce();
    if (iVar4 << 0x1e < 0) {
      FUN_0043d574(1,DAT_005f98dc,DAT_005f98d8,DAT_005f98d4,0x1a,DAT_005f98d0,param_2,param_3);
    }
    iVar4 = FUN_0043d0ce();
    if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
      compress_log_output(0x4800000,DAT_005f98e0,DAT_005f98e0,param_2,param_3);
    }
    return 0xffffffff;
  }
  iVar4 = FUN_0043d0ce();
  if (iVar4 << 0x1e < 0) {
    FUN_0043d574(4,DAT_005f98dc,DAT_005f98d8,DAT_005f98d4,0x21,DAT_005f98e4,*param_2,param_2[1],
                 param_2[2],param_2[3]);
  }
  iVar4 = FUN_0043d0ce();
  if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
    compress_log_output(0x11000000,DAT_005f98e8,DAT_005f98e8,*param_2,param_2[1],param_2[2],
                        param_2[3]);
  }
  bVar1 = *param_2;
  if (bVar1 == 1) {
    iVar4 = FUN_0043d0ce();
    if (iVar4 << 0x1e < 0) {
      FUN_0043d574(4,DAT_005f98dc,DAT_005f98d8,DAT_005f98d4,0x2c,DAT_005f98ec);
    }
    iVar4 = FUN_0043d0ce();
    if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
      compress_log_output(0x10000000,DAT_005f98f0,DAT_005f98f0);
    }
    CHG_SendBatteryInfoToPeer(2);
  }
  else {
    if (bVar1 == 0) {
LAB_005f988c:
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        FUN_0043d574(2,DAT_005f98dc,DAT_005f98d8,DAT_005f98d4,0x60,DAT_005f991c,*param_2);
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        compress_log_output(0x8400000,DAT_005f9920,DAT_005f9920,*param_2);
      }
      return 0xffffffff;
    }
    if (bVar1 == 3) {
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        FUN_0043d574(4,DAT_005f98dc,DAT_005f98d8,DAT_005f98d4,0x38,DAT_005f98fc);
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        compress_log_output(0x10000000,DAT_005f9900,DAT_005f9900);
      }
      CHG_ReceiveBatteryInfoFromPeer(param_2);
    }
    else if (bVar1 < 3) {
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        FUN_0043d574(4,DAT_005f98dc,DAT_005f98d8,DAT_005f98d4,0x32,DAT_005f98f4);
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        compress_log_output(0x10000000,DAT_005f98f8,DAT_005f98f8);
      }
      CHG_ReceiveBatteryInfoFromPeer(param_2);
    }
    else if (bVar1 == 5) {
      uVar6 = *(uint *)(param_2 + 4);
      if ((int)uVar6 < 0) {
        uVar6 = 0;
      }
      else if (100 < (int)uVar6) {
        uVar6 = 100;
      }
      bVar7 = param_2[8] != 0;
      uVar5 = ring_battery_level_get();
      bVar8 = uVar5 != (uVar6 & 0xff);
      uVar5 = ring_battery_charging_get();
      bVar9 = uVar5 != bVar7;
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        FUN_0043d574(3,DAT_005f98dc,DAT_005f98d8,DAT_005f98d4,0x52,DAT_005f9914,uVar6 & 0xff,bVar7,
                     bVar8,bVar9);
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        compress_log_output(0xd000000,DAT_005f9918,DAT_005f9918,uVar6 & 0xff,bVar7,bVar8,bVar9);
      }
      ring_battery_state_set(uVar6 & 0xff,bVar7);
      if (bVar8) {
        CB_RING_BAT_Notify(0,uVar6 & 0xff);
      }
      if (bVar9) {
        CB_RING_BAT_Notify(1,bVar7);
      }
    }
    else if (bVar1 < 5) {
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        FUN_0043d574(4,DAT_005f98dc,DAT_005f98d8,DAT_005f98d4,0x3e,DAT_005f9904);
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        compress_log_output(0x10000000,DAT_005f9908,DAT_005f9908);
      }
      CHG_SendBatteryInfoToPeer(3);
    }
    else {
      if (bVar1 != 6) goto LAB_005f988c;
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        FUN_0043d574(4,DAT_005f98dc,DAT_005f98d8,DAT_005f98d4,0x44,DAT_005f990c);
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        compress_log_output(0x10000000,DAT_005f9910,DAT_005f9910);
      }
      uVar2 = ring_battery_charging_get();
      uVar3 = ring_battery_level_get();
      SVC_RingBattery_Update(uVar3,uVar2);
    }
  }
  return 0;
}

