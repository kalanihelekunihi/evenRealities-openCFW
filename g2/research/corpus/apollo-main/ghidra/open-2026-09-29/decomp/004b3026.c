
void DmDevReset(void)

{
  int iVar1;
  int iVar2;
  
  iVar1 = DAT_004b306c;
  if (*(char *)(DAT_004b306c + 0x10) != '\0') {
    *(undefined1 *)(DAT_004b306c + 0x10) = 0;
  }
  iVar2 = WsfMsgAlloc(4);
  if (iVar2 != 0) {
    *(undefined1 *)(iVar2 + 2) = 0x38;
    WsfMsgSend(*(undefined1 *)(iVar1 + 0xc),iVar2);
  }
  return;
}

