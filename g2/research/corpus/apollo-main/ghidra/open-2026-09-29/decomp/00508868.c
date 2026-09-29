
uint FUN_00508868(void)

{
  uint uVar1;
  uint uVar2;
  byte local_20 [4];
  undefined1 auStack_1c [13];
  char local_f;
  
  FUN_0043c0e4(auStack_1c,0xf,0);
  uVar2 = 0;
  while ((local_f == '\0' && (uVar2 == 0))) {
    uVar2 = FUN_005065cc(*DAT_00508a70,0,auStack_1c);
  }
  uVar1 = FUN_00508e5c(*DAT_00508a70,0xa218,1,local_20);
  uVar2 = uVar2 | uVar1;
  if ((local_20[0] & 0x3d) != 0) {
    uVar2 = 0xffffffff;
  }
  return uVar2;
}

