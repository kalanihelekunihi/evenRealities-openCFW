
undefined4 HciReadBdAddrCmd(void)

{
  int iVar1;
  undefined4 unaff_r7;
  
  iVar1 = hciCmdAlloc(0x1009,0);
  if (iVar1 != 0) {
    hciCmdSend(iVar1);
  }
  return unaff_r7;
}

