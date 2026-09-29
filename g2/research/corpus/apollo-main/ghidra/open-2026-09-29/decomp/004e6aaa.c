
int even_ai_dialog_get(byte param_1)

{
  int iVar1;
  byte bVar2;
  
  if (param_1 < *(byte *)(DAT_004e74fc + 0x18)) {
    iVar1 = *(int *)(DAT_004e74fc + 0x10);
    for (bVar2 = 0; (iVar1 != 0 && (bVar2 < param_1)); bVar2 = bVar2 + 1) {
      iVar1 = *(int *)(iVar1 + 0x20);
    }
  }
  else {
    iVar1 = 0;
  }
  return iVar1;
}

