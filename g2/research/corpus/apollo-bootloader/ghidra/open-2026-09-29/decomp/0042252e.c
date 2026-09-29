
undefined8 FUN_0042252e(void)

{
  bool bVar1;
  char *pcVar2;
  uint uVar3;
  undefined4 in_r3;
  undefined4 uVar4;
  
  uVar3 = critical_save(0);
  pcVar2 = DAT_00422588;
  if (*DAT_00422588 != '\0') {
    *DAT_00422588 = *DAT_00422588 + -1;
  }
  if (*pcVar2 == '\0') {
    *DAT_0042258c = *DAT_0042258c & 0xfeffffff;
    uVar4 = delay_status_change(10,DAT_0042258c,0x1000000,0,uVar3,in_r3);
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

