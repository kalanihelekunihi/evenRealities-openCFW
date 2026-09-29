
undefined8 FUN_00442d64(void)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 unaff_r7;
  
  iVar1 = FUN_00467f08();
  if (((iVar1 == 1) || (iVar1 = onboarding_should_run(), iVar1 == 1)) ||
     (iVar1 = get_silent_mode_ui_showing(), iVar1 == 1)) {
    uVar2 = 1;
  }
  else {
    uVar2 = 0;
  }
  return CONCAT44(unaff_r7,uVar2);
}

