
undefined8 FUN_004d3f78(void)

{
  bool bVar1;
  char *pcVar2;
  uint uVar3;
  uint *puVar4;
  undefined4 uVar5;
  
  uVar3 = FUN_00473940(0);
  pcVar2 = DAT_004d4088;
  if (*DAT_004d4088 != '\0') {
    *DAT_004d4088 = *DAT_004d4088 + -1;
  }
  puVar4 = DAT_004d408c;
  if (*pcVar2 == '\0') {
    *DAT_004d408c = *DAT_004d408c & 0xfffffffe;
    *puVar4 = *puVar4 & 0xfffffff1;
  }
  else {
    puVar4 = (uint *)0x3;
  }
  FUN_004d403e(puVar4);
  uVar5 = FUN_004d3fc2(0);
  bVar1 = (bool)isCurrentModePrivileged();
  if (bVar1) {
    enableIRQinterrupts((uVar3 & 1) == 1);
  }
  return CONCAT44(uVar3,uVar5);
}

