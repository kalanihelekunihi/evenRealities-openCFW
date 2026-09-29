
undefined4 _nvdbUpdataMac(void)

{
  int iVar1;
  char local_10 [8];
  short local_8;
  
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    FUN_0043d574(2,DAT_005da070,DAT_005da06c,DAT_005da068,0x41,DAT_005da064);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0x8000000,DAT_005da074,DAT_005da074);
  }
  iVar1 = SVC_NvdbRead(DAT_005da078,local_10,10);
  if (iVar1 < 1) {
    nvdbMacUpdate(DAT_005da07c);
  }
  else if ((local_8 != *(short *)(DAT_005da060 + 8)) && (local_10[0] == '\0')) {
    nvdbMacUpdate(DAT_005da060 + 1);
  }
  return 0;
}

