
undefined8 FUN_004d403e(void)

{
  bool bVar1;
  char *pcVar2;
  uint uVar3;
  undefined4 in_r3;
  undefined4 uVar4;
  
  uVar3 = FUN_00473940(0);
  pcVar2 = DAT_004d4098;
  if (*DAT_004d4098 != '\0') {
    *DAT_004d4098 = *DAT_004d4098 + -1;
  }
  if (*pcVar2 == '\0') {
    *DAT_004d409c = *DAT_004d409c & 0xfeffffff;
    uVar4 = FUN_004807fc(10,DAT_004d409c,0x1000000,0,uVar3,in_r3);
  }
  else {
    uVar4 = 3;
  }
  bVar1 = (bool)isCurrentModePrivileged();
  if (bVar1) {
    enableIRQinterrupts((uVar3 & 1) == 1);
  }
  return CONCAT44(uVar3,uVar4);
}

