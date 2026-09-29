
longlong settings_set_terminal_mode(undefined1 param_1)

{
  int iVar1;
  uint unaff_r7;
  
  iVar1 = DAT_0046c6a8;
  *(undefined1 *)(DAT_0046c6a8 + 0x1d) = param_1;
  SVC_KvdbWriteTerminalMode(iVar1 + 0x1c);
  return (ulonglong)unaff_r7 << 0x20;
}

