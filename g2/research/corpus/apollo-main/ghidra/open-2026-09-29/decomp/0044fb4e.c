
int FUN_0044fb4e(int param_1)

{
  byte bVar1;
  int iVar2;
  
  if (param_1 == 0) {
    param_1 = FUN_0044fa1a();
  }
  if (param_1 == 0) {
    iVar2 = 0;
  }
  else {
    bVar1 = *(byte *)(param_1 + 0x2fc) & 7;
    if (bVar1 == 1) {
      iVar2 = *(int *)(param_1 + 0x14);
    }
    else {
      if ((*(byte *)(param_1 + 0x2fc) & 7) != 0) {
        if (bVar1 == 3) {
          iVar2 = FUN_0044fad2(param_1);
          return iVar2 - *(int *)(param_1 + 0x14);
        }
        if (bVar1 < 3) {
          iVar2 = FUN_0044fad2(param_1);
          return iVar2 - *(int *)(param_1 + 0x10);
        }
      }
      iVar2 = *(int *)(param_1 + 0x10);
    }
  }
  return iVar2;
}

