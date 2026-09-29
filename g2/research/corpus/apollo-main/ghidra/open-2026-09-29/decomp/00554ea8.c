
undefined8 FUN_00554ea8(void)

{
  int iVar1;
  char cVar2;
  char cVar3;
  undefined4 uVar4;
  undefined4 in_r3;
  
  FUN_00555710();
  cVar2 = FUN_005897e0();
  iVar1 = DAT_00555754;
  cVar3 = FUN_0058a83e(*(undefined4 *)(DAT_00555754 + 4));
  if (((cVar2 == '\0') && (cVar3 == '\0')) && (*(int *)(iVar1 + 0xc) < 1)) {
    uVar4 = 0xaa;
  }
  else if (cVar2 == '\0') {
    uVar4 = 1;
  }
  else {
    uVar4 = 0;
  }
  return CONCAT44(in_r3,uVar4);
}

