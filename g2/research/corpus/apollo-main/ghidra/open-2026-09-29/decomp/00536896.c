
undefined4 FUN_00536896(void)

{
  undefined4 unaff_r7;
  
  if (*(char *)(DAT_00536a14 + 0x18) == '\x02') {
    *(undefined1 *)(DAT_00536a14 + 0x18) = 3;
    HciLeSetScanEnableCmd(0,0);
  }
  return unaff_r7;
}

