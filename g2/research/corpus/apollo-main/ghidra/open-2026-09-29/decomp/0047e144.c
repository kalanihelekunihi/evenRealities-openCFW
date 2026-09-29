
undefined4 FUN_0047e144(void)

{
  int *piVar1;
  int iVar2;
  undefined4 uVar3;
  undefined1 auStack_48 [64];
  
  FUN_0047de0a(auStack_48,0x40,*DAT_0047e2b8);
  piVar1 = DAT_0047e2c0;
  iVar2 = file_open(auStack_48,&DAT_0047e274);
  *piVar1 = iVar2;
  if (*piVar1 == 0) {
    uVar3 = 0xfffffffb;
  }
  else {
    uVar3 = 0;
  }
  return uVar3;
}

