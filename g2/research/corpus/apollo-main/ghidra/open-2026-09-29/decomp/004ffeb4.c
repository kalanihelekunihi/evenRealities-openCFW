
undefined4 FUN_004ffeb4(uint param_1)

{
  byte bVar1;
  int iVar2;
  undefined4 uVar3;
  
  iVar2 = FUN_00558142();
  if ((iVar2 == 0) || (*(byte *)(iVar2 + 1) <= param_1)) {
    uVar3 = 1;
  }
  else {
    bVar1 = *(byte *)(iVar2 + param_1 + 2);
    if (bVar1 == 0) {
      uVar3 = 1;
    }
    else if (bVar1 == 2) {
      uVar3 = 3;
    }
    else if (bVar1 < 2) {
      uVar3 = 2;
    }
    else if (bVar1 == 4) {
      uVar3 = 4;
    }
    else if (bVar1 < 4) {
      uVar3 = 5;
    }
    else {
      uVar3 = 1;
    }
  }
  return uVar3;
}

