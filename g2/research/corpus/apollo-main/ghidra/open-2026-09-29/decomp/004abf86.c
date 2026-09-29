
undefined4 FUN_004abf86(void)

{
  int iVar1;
  undefined4 unaff_r7;
  
  iVar1 = FUN_00443484();
  if (iVar1 != 0) {
    iVar1 = FUN_004acad0();
    if (iVar1 == 1) {
      FUN_0047432c();
    }
    else {
      iVar1 = SVC_Settings_InputEventCheck();
      if (iVar1 == 1) {
        FUN_00474100();
      }
    }
  }
  return unaff_r7;
}

