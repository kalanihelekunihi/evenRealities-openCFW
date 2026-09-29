
undefined4 FUN_1000ab10(int param_1)

{
  int iVar1;
  int iVar2;
  
  iVar2 = DAT_1000ab70;
  if ((param_1 == 0) || (iVar2 = DAT_1000ab78, param_1 == 1)) {
    iVar1 = FUN_1000a00c(iVar2 + 0x15c);
    if (iVar1 == 0) {
      *(undefined4 *)(iVar2 + 0x18) = 1;
      FUN_10009fbc(iVar2 + 0x15c,iVar2 + 0x3c);
      *(undefined4 *)(iVar2 + 0x174) = 0;
      FUN_1000a898(*(undefined4 *)(iVar2 + 0x178));
      FUN_10004650(*(undefined4 *)(iVar2 + 8),PTR_LAB_1000ab74,0);
      return 0;
    }
    *(undefined4 *)(iVar2 + 0x18) = 0;
    FUN_10004684(param_1);
  }
  return 0xffffffff;
}

