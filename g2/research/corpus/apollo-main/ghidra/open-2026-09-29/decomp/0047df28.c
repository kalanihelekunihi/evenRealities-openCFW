
undefined4 FUN_0047df28(void)

{
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  undefined4 in_r3;
  undefined1 auStack_20 [4];
  undefined4 local_1c;
  undefined4 local_18;
  undefined4 local_14;
  undefined4 uStack_10;
  
  uStack_10 = in_r3;
  FUN_00439c04(auStack_20,DAT_0047e2a0,0x10);
  local_1c = *DAT_0047e2a4;
  local_18 = *DAT_0047e2a8;
  local_14 = FUN_0047ddfe(auStack_20);
  iVar1 = file_open(DAT_0047e2ac,&DAT_0047e174);
  if (iVar1 == 0) {
    uVar2 = 0xfffffffb;
  }
  else {
    iVar3 = file_write(auStack_20,1,0x10,iVar1);
    file_close(iVar1);
    if (iVar3 == 0x10) {
      uVar2 = 0;
    }
    else {
      uVar2 = 0xfffffffb;
    }
  }
  return uVar2;
}

