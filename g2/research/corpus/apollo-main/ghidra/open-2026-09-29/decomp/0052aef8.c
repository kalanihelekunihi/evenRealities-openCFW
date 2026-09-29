
void hciCmdRecvCmpl(void)

{
  int iVar1;
  
  iVar1 = DAT_0052b6b4;
  WsfTimerStop(DAT_0052b6b4);
  *(undefined1 *)(iVar1 + 0x1a) = 1;
  hciCmdSend(0);
  return;
}

