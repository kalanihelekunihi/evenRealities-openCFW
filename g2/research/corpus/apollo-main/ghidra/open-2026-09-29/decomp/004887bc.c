
short FUN_004887bc(uint param_1,uint param_2)

{
  short sVar1;
  ushort uVar2;
  uint uVar3;
  bool bVar4;
  
  bVar4 = (int)param_1 < 0;
  if (bVar4) {
    param_1 = -param_1;
  }
  uVar3 = (uint)bVar4;
  if ((int)param_2 < 0) {
    uVar3 = uVar3 + 2;
    param_2 = -param_2;
  }
  if (param_2 < param_1) {
    param_1 = (param_2 * 0x2d) / param_1;
    uVar3 = uVar3 + 0x10;
  }
  else {
    param_1 = (param_1 * 0x2d) / param_2;
  }
  if ((param_1 & 0xff) < 0x17) {
    uVar2 = (ushort)(1 < (param_1 & 0xff));
    if (5 < (param_1 & 0xff)) {
      uVar2 = uVar2 + 1;
    }
    if (9 < (param_1 & 0xff)) {
      uVar2 = uVar2 + 1;
    }
    if (0xe < (param_1 & 0xff)) {
      uVar2 = uVar2 + 1;
    }
  }
  else {
    uVar2 = (ushort)((param_1 & 0xff) < 0x2d);
    if ((param_1 & 0xff) < 0x2a) {
      uVar2 = uVar2 + 1;
    }
    if ((param_1 & 0xff) < 0x26) {
      uVar2 = uVar2 + 1;
    }
    if ((param_1 & 0xff) < 0x21) {
      uVar2 = uVar2 + 1;
    }
  }
  sVar1 = (short)param_1 + uVar2;
  if ((int)(uVar3 << 0x1b) < 0) {
    sVar1 = 0x5a - sVar1;
  }
  if ((int)(uVar3 << 0x1e) < 0) {
    if ((int)(uVar3 << 0x1f) < 0) {
      sVar1 = sVar1 + 0xb4;
    }
    else {
      sVar1 = 0xb4 - sVar1;
    }
  }
  else if ((int)(uVar3 << 0x1f) < 0) {
    sVar1 = 0x168 - sVar1;
  }
  return sVar1;
}

