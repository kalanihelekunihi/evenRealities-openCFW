
undefined8 FUN_00597cae(void)

{
  undefined4 *puVar1;
  undefined4 *puVar2;
  char *pcVar3;
  undefined4 uVar4;
  int iVar5;
  undefined4 in_r3;
  
  pcVar3 = DAT_00597d2c;
  puVar2 = DAT_00597d24;
  if (*DAT_00597d2c == '\0') {
    *DAT_00597d24 = DAT_00597d30;
    puVar1 = DAT_00597d20;
    *DAT_00597d20 = 2;
    iVar5 = FUN_00597c6c(*puVar2,*puVar1);
    if (iVar5 == 0) {
      *pcVar3 = '\x01';
    }
    uVar4 = *puVar1;
  }
  else {
    uVar4 = *DAT_00597d20;
  }
  return CONCAT44(in_r3,uVar4);
}

