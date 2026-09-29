
ushort FUN_005b3ef8(int param_1,ushort param_2)

{
  bool bVar1;
  ushort uVar2;
  ushort uVar3;
  byte bVar4;
  
  uVar2 = 0;
  do {
    if (param_2 <= uVar2) {
      return uVar2;
    }
    bVar4 = *(byte *)(param_1 + (uint)uVar2);
    if ((int)((uint)bVar4 << 0x18) < 0) {
      if ((bVar4 & 0xe0) == 0xc0) {
        uVar3 = 2;
      }
      else if ((bVar4 & 0xf0) == 0xe0) {
        uVar3 = 3;
      }
      else if ((bVar4 & 0xf8) == 0xf0) {
        uVar3 = 4;
      }
      else {
        uVar3 = 1;
      }
    }
    else {
      uVar3 = 1;
    }
    if (param_2 < (ushort)(uVar2 + uVar3)) {
      return uVar2;
    }
    bVar1 = true;
    for (bVar4 = 1; bVar4 < uVar3; bVar4 = bVar4 + 1) {
      if ((*(byte *)(param_1 + (uint)bVar4 + (uint)uVar2) & 0xc0) != 0x80) {
        bVar1 = false;
        break;
      }
    }
    if (!bVar1) {
      return uVar2;
    }
    uVar2 = uVar2 + uVar3;
  } while( true );
}

