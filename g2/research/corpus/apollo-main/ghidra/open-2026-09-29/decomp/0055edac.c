
undefined8 FUN_0055edac(int param_1)

{
  int iVar1;
  undefined4 unaff_r7;
  
  if (*(char *)(param_1 + 0xcc) != '\0') {
    *(undefined1 *)(param_1 + 0xcc) = 0;
    iVar1 = FUN_0055eaae();
    if (iVar1 != DAT_0055ee50) goto LAB_0055edc8;
  }
  iVar1 = DAT_0055ee50;
LAB_0055edc8:
  return CONCAT44(unaff_r7,iVar1);
}

