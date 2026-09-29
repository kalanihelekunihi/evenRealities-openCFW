
uint FUN_00581e6a(int param_1,int param_2,uint param_3)

{
  uint uVar1;
  char cVar2;
  uint uVar3;
  
  if ((param_2 == 0) || (param_3 == 0)) {
    uVar1 = 0;
  }
  else {
    if (param_1 == 0) {
      uVar1 = 4000;
      cVar2 = 'A';
    }
    else {
      if (param_1 != 1) {
        return 0;
      }
      uVar1 = 200;
      cVar2 = 'a';
    }
    if (param_3 < uVar1) {
      uVar1 = param_3;
    }
    for (uVar3 = 0; uVar3 < uVar1; uVar3 = uVar3 + 1) {
      if ((uVar3 + 1) % 0x50 == 0) {
        *(undefined1 *)(param_2 + uVar3) = 10;
      }
      else {
        *(char *)(param_2 + uVar3) = (char)uVar3 + cVar2 + (char)(uVar3 / 0x1a) * -0x1a;
      }
    }
  }
  return uVar1;
}

