
int FUN_0047e090(void)

{
  int iVar1;
  int local_50;
  undefined4 local_4c;
  undefined1 auStack_44 [64];
  
  while( true ) {
    iVar1 = FUN_0047deb4(&local_50);
    if (iVar1 != 0) {
      return iVar1;
    }
    if (local_50 < 4) break;
    FUN_0047de0a(auStack_44,0x40,local_4c);
    iVar1 = file_remove(auStack_44);
    if (iVar1 != 0) {
      return -5;
    }
  }
  return 0;
}

