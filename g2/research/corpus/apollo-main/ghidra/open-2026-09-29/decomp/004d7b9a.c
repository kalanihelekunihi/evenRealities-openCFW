
undefined1 utf16_literal_to_utf8(int param_1,int param_2,int *param_3)

{
  byte bVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  undefined1 uVar5;
  byte bVar6;
  
  bVar6 = 0;
  if ((param_2 - param_1 < 6) || (uVar2 = parse_hex4(param_1 + 2), uVar2 - 0xdc00 < 0x400)) {
LAB_004d7bb6:
    uVar5 = 0;
  }
  else {
    if (uVar2 - 0xd800 < 0x400) {
      uVar5 = 0xc;
      if ((((param_2 - (param_1 + 6) < 6) || (*(char *)(param_1 + 6) != '\\')) ||
          (*(char *)(param_1 + 7) != 'u')) ||
         (uVar3 = parse_hex4(param_1 + 8), 0x3ff < uVar3 - 0xdc00)) goto LAB_004d7bb6;
      uVar2 = (uVar3 & 0x3ff | DAT_004d80d4 & uVar2 << 10) + 0x10000;
    }
    else {
      uVar5 = 6;
    }
    if (uVar2 < 0x80) {
      uVar3 = 1;
      uVar4 = uVar3;
    }
    else if (uVar2 < 0x800) {
      uVar3 = 2;
      bVar6 = 0xc0;
      uVar4 = uVar3;
    }
    else if (uVar2 < 0x10000) {
      uVar3 = 3;
      bVar6 = 0xe0;
      uVar4 = uVar3;
    }
    else {
      if (0x10ffff < uVar2) goto LAB_004d7bb6;
      uVar3 = 4;
      bVar6 = 0xf0;
      uVar4 = uVar3;
    }
    while( true ) {
      uVar3 = uVar3 - 1;
      bVar1 = (byte)uVar2;
      if ((uVar3 & 0xff) == 0) break;
      *(byte *)(*param_3 + (uVar3 & 0xff)) = bVar1 & 0xbf | 0x80;
      uVar2 = uVar2 >> 6;
    }
    if (uVar4 < 2) {
      *(byte *)*param_3 = bVar1 & 0x7f;
    }
    else {
      *(byte *)*param_3 = bVar1 | bVar6;
    }
    *param_3 = *param_3 + uVar4;
  }
  return uVar5;
}

