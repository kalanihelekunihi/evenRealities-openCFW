
longlong FUN_00448c74(void)

{
  char *pcVar1;
  uint in_r3;
  
  pcVar1 = DAT_00448fc4;
  if (*DAT_00448fc4 == '\0') {
    FUN_0044895e();
    FUN_004489e8();
    FUN_0043c0e4(DAT_00448fbc,0x30,0);
    *DAT_00448fc8 = 1;
    *pcVar1 = '\x01';
  }
  return (ulonglong)in_r3 << 0x20;
}

