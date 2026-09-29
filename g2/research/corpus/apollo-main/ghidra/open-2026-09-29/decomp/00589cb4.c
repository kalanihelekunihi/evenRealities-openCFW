
undefined4 FUN_00589cb4(void)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 unaff_r7;
  
  iVar1 = FUN_0045a568();
  if (iVar1 == 1) {
    uVar2 = osKernelGetTickCount();
    *DAT_0058a364 = uVar2;
  }
  return unaff_r7;
}

