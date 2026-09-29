
undefined8 onboarding_should_run(void)

{
  char cVar1;
  int iVar2;
  undefined4 uVar3;
  undefined4 unaff_r7;
  
  cVar1 = kvdbOnboardingConfigGet();
  if ((cVar1 == '\x01') ||
     ((iVar2 = FUN_00443484(), iVar2 == 1 && (iVar2 = FUN_004434d0(0x10), iVar2 == 1)))) {
    uVar3 = 1;
  }
  else {
    uVar3 = 0;
  }
  return CONCAT44(unaff_r7,uVar3);
}

