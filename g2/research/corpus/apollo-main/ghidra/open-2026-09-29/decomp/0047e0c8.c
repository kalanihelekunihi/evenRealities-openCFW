
int FUN_0047e0c8(void)

{
  int *piVar1;
  int iVar2;
  undefined4 in_r3;
  int iVar3;
  undefined1 auStack_70 [32];
  undefined1 auStack_50 [64];
  undefined4 uStack_10;
  
  uStack_10 = in_r3;
  iVar2 = FUN_0047e090();
  if (iVar2 == 0) {
    iVar3 = *DAT_0047e2a8;
    *DAT_0047e2a8 = *DAT_0047e2a8 + 1;
    iVar2 = FUN_0047df28();
    if (iVar2 == 0) {
      FUN_0047de0a(auStack_50,0x40,iVar3);
      piVar1 = DAT_0047e2c0;
      iVar2 = file_open(auStack_50,&DAT_0047e174);
      *piVar1 = iVar2;
      if (*piVar1 == 0) {
        iVar2 = -5;
      }
      else {
        FUN_0048ed00(auStack_70,iVar3,*DAT_0047e2a4);
        iVar2 = file_write(auStack_70,1,0x20,*piVar1);
        if (iVar2 == 0x20) {
          *DAT_0047e2b8 = iVar3;
          *DAT_0047e2bc = 0x20;
          iVar2 = 0;
        }
        else {
          FUN_0047e06a();
          iVar2 = -5;
        }
      }
    }
  }
  return iVar2;
}

