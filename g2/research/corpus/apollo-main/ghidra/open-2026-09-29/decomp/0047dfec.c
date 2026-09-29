
int FUN_0047dfec(void)

{
  char *pcVar1;
  int iVar2;
  undefined4 in_r3;
  int local_58 [2];
  int local_50;
  undefined1 auStack_4c [64];
  undefined4 uStack_c;
  
  pcVar1 = DAT_0047e2b4;
  if (*DAT_0047e2b4 == '\0') {
    uStack_c = in_r3;
    file_mkdir(DAT_0047e29c,0);
    FUN_0047df8a();
    *DAT_0047e2a4 = *DAT_0047e2a4 + 1;
    iVar2 = FUN_0047deb4(local_58);
    if (iVar2 == 0) {
      if (0 < local_58[0]) {
        if (*DAT_0047e2a8 < local_50 + 1U) {
          *DAT_0047e2a8 = local_50 + 1;
        }
        FUN_0047de0a(auStack_4c,0x40,local_50);
        iVar2 = FUN_0047de7a(auStack_4c);
        if (iVar2 - 0x20U < 0x7fe0) {
          *DAT_0047e2b8 = local_50;
          *DAT_0047e2bc = iVar2;
        }
      }
      iVar2 = FUN_0047df28();
      if (iVar2 == 0) {
        *pcVar1 = '\x01';
        iVar2 = 0;
      }
    }
  }
  else {
    iVar2 = 0;
  }
  return iVar2;
}

