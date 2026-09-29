
undefined8 FUN_00539304(void)

{
  bool bVar1;
  char *pcVar2;
  uint uVar3;
  int iVar4;
  
  uVar3 = FUN_00473940();
  pcVar2 = DAT_00539344;
  if (*DAT_00539344 != '\0') {
    *DAT_00539344 = *DAT_00539344 + -1;
  }
  if (*pcVar2 == '\0') {
    *DAT_00539340 = 0;
    iVar4 = FUN_004d3f78();
    if (iVar4 == 3) {
      iVar4 = 0;
    }
  }
  else {
    iVar4 = 3;
  }
  bVar1 = (bool)isCurrentModePrivileged();
  if (bVar1) {
    enableIRQinterrupts((uVar3 & 1) == 1);
  }
  return CONCAT44(uVar3,iVar4);
}

