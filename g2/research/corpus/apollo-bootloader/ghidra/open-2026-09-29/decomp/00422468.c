
undefined8 debug_disable(void)

{
  bool bVar1;
  char *pcVar2;
  uint uVar3;
  uint *puVar4;
  undefined4 uVar5;
  
  uVar3 = critical_save(0);
  pcVar2 = DAT_00422578;
  if (*DAT_00422578 != '\0') {
    *DAT_00422578 = *DAT_00422578 + -1;
  }
  puVar4 = DAT_0042257c;
  if (*pcVar2 == '\0') {
    *DAT_0042257c = *DAT_0042257c & 0xfffffffe;
    *puVar4 = *puVar4 & 0xfffffff1;
  }
  else {
    puVar4 = (uint *)0x3;
  }
  FUN_0042252e(puVar4);
  uVar5 = FUN_004224b2(0);
  bVar1 = (bool)isCurrentModePrivileged();
  if (bVar1) {
    enableIRQinterrupts((uVar3 & 1) == 1);
  }
  return CONCAT44(uVar3,uVar5);
}

