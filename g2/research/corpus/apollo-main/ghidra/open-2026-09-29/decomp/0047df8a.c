
void FUN_0047df8a(void)

{
  int iVar1;
  int iVar2;
  undefined4 in_r3;
  int local_20;
  undefined4 local_1c;
  uint local_18;
  int local_14;
  undefined4 uStack_10;
  
  uStack_10 = in_r3;
  iVar1 = file_open(DAT_0047e2ac,&DAT_0047e140);
  if (iVar1 != 0) {
    iVar2 = file_read(&local_20,1,0x10,iVar1);
    file_close(iVar1);
    if (((iVar2 == 0x10) && (local_20 == DAT_0047e2b0)) &&
       (iVar1 = FUN_0047ddfe(&local_20), local_14 == iVar1)) {
      *DAT_0047e2a4 = local_1c;
      if (local_18 < 2) {
        *DAT_0047e2a8 = 1;
      }
      else {
        *DAT_0047e2a8 = local_18;
      }
    }
  }
  return;
}

