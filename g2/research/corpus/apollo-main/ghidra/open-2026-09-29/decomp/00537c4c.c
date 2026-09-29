
undefined8 SmpDmGetStk(undefined1 param_1,undefined1 *param_2,undefined4 param_3,undefined4 param_4)

{
  undefined1 uVar1;
  int iVar2;
  
  iVar2 = smpCcbByConnId(param_1);
  if ((iVar2 == 0) || (*(char *)(iVar2 + 0x44) == '\0')) {
    iVar2 = 0;
  }
  else if ((*(char *)(DAT_00537ebc + 0xf8) == '\0') ||
          ((**(char **)(iVar2 + 0x48) == '\0' || (*(int *)(*(int *)(iVar2 + 0x48) + 0x18) == 0)))) {
    if (*(int *)(iVar2 + 0x30) == 0) {
      iVar2 = 0;
    }
    else {
      if ((int)((uint)*(byte *)(iVar2 + 0x40) << 0x1d) < 0) {
        uVar1 = 2;
      }
      else {
        uVar1 = 1;
      }
      *param_2 = uVar1;
      iVar2 = *(int *)(iVar2 + 0x30) + 0x20;
    }
  }
  else {
    uVar1 = smpGetScSecLevel(iVar2);
    *param_2 = uVar1;
    iVar2 = *(int *)(*(int *)(iVar2 + 0x48) + 0x18) + 0x10;
  }
  return CONCAT44(param_4,iVar2);
}

