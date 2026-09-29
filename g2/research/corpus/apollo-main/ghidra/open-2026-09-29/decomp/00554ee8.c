
undefined4 FUN_00554ee8(void)

{
  int iVar1;
  char cVar2;
  char cVar3;
  int iVar4;
  undefined4 uVar5;
  
  iVar4 = FUN_00555710();
  cVar2 = FUN_005897e0();
  iVar1 = DAT_00555754;
  cVar3 = FUN_0058a83e(*(undefined4 *)(DAT_00555754 + 4));
  if (((cVar2 == '\0') && (cVar3 == '\0')) && (iVar4 - 1U <= *(uint *)(iVar1 + 0xc))) {
    uVar5 = 0xaa;
  }
  else if (cVar2 == '\0') {
    uVar5 = 1;
  }
  else {
    uVar5 = 0;
  }
  return uVar5;
}

