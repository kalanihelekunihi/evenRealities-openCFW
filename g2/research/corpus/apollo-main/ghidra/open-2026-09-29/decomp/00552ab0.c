
undefined4 FUN_00552ab0(void)

{
  int iVar1;
  undefined4 unaff_r7;
  
  iVar1 = FUN_0045a568();
  if (iVar1 == 1) {
    iVar1 = service_ancc_state_get();
    if (*(char *)(iVar1 + 2) == '\0') {
      FUN_00552948(10000);
    }
    else {
      FUN_00552948((uint)*(byte *)(iVar1 + 2) * 1000);
    }
  }
  return unaff_r7;
}

