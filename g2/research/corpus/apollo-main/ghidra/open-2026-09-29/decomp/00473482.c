
undefined8 FUN_00473482(void)

{
  undefined4 *puVar1;
  undefined4 uVar2;
  undefined4 unaff_r7;
  
  puVar1 = DAT_004734bc;
  if (DAT_004734bc[2] == 0) {
    do {
      *(undefined1 *)(puVar1 + 1) = 1;
      uVar2 = *puVar1;
    } while (*(char *)(puVar1 + 1) == '\0');
  }
  else {
    uVar2 = (*(code *)DAT_004734bc[2])();
  }
  return CONCAT44(unaff_r7,uVar2);
}

