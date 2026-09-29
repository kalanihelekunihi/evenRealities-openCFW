
uint FUN_0044c47a(int param_1,int param_2)

{
  byte bVar1;
  uint uVar2;
  
  bVar1 = FUN_0044b8b8(param_1,param_2);
  if (bVar1 < 3) {
    uVar2 = 0;
  }
  else {
    uVar2 = 0xff;
    if (bVar1 < 0xfd) {
      uVar2 = (int)((uint)bVar1 * 0xff) >> 8;
    }
    if (param_2 == 0) {
      param_1 = FUN_0044dca2(param_1);
    }
    for (; param_1 != 0; param_1 = FUN_0044dca2(param_1)) {
      bVar1 = FUN_0044b8b8(param_1,0);
      if (bVar1 < 3) {
        return 0;
      }
      if (bVar1 < 0xfd) {
        uVar2 = (int)(bVar1 * uVar2) >> 8;
      }
    }
    if (uVar2 < 3) {
      uVar2 = 0;
    }
    else if (0xfc < uVar2) {
      uVar2 = 0xff;
    }
  }
  return uVar2;
}

