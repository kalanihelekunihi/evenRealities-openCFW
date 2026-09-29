
undefined4 FUN_0045d4b8(void)

{
  int iVar1;
  undefined4 unaff_r7;
  
  while (iVar1 = osSemaphoreAcquire(*DAT_0045dd38,0), iVar1 == 0) {
    FUN_00492288(*DAT_0045dd64);
  }
  return unaff_r7;
}

