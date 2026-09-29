
undefined4 hciCoreSendAclData(int param_1)

{
  int iVar1;
  undefined4 uVar2;
  
  iVar1 = hciTrSendAclData(param_1);
  if (iVar1 == 0) {
    uVar2 = 0;
  }
  else {
    *(char *)(param_1 + 0x19) = *(char *)(param_1 + 0x19) + '\x01';
    if (*(char *)(DAT_0052ae14 + 0x82) != '\0') {
      *(char *)(DAT_0052ae14 + 0x82) = *(char *)(DAT_0052ae14 + 0x82) + -1;
    }
    uVar2 = 1;
  }
  return uVar2;
}

