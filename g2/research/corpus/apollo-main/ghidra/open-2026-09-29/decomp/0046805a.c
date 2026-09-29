
undefined8 onboarding_check_start_disp(void)

{
  undefined4 uVar1;
  char cVar2;
  int iVar3;
  undefined4 unaff_r5;
  undefined4 unaff_r6;
  
  cVar2 = kvdbOnboardingConfigGet();
  if ((cVar2 == '\x01') &&
     ((iVar3 = FUN_00443484(), iVar3 == 0 || (iVar3 = FUN_004434d0(0x10), iVar3 != 1)))) {
    iVar3 = FUN_0043d0ce();
    uVar1 = DAT_00468a30;
    if (iVar3 << 0x1e < 0) {
      unaff_r5 = 0x83;
      FUN_0043d574(3,DAT_00468a3c,DAT_00468a38,DAT_00468a34);
      unaff_r6 = uVar1;
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0xc000000,DAT_00468c2c,DAT_00468c2c);
    }
    FUN_00464b2e(0x10,0,0,0);
  }
  return CONCAT44(unaff_r6,unaff_r5);
}

