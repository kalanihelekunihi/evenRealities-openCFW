
undefined4 ring_master_reconnect(void)

{
  undefined4 unaff_r7;
  
  DmConnSetConnSpec(DAT_004a02e4);
  DmConnSetScanInterval(*DAT_004a05e4,DAT_004a05e4[1]);
  return unaff_r7;
}

