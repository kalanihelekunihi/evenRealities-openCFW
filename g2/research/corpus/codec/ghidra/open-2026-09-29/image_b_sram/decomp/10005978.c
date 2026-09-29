
void FUN_10005978(int param_1,uint param_2,int param_3,int param_4)

{
  uint *puVar1;
  uint *puVar2;
  
  puVar1 = DAT_10005a58;
  puVar2 = DAT_10005a54;
  if (param_1 == 1) {
    puVar2 = (uint *)&DAT_a0a00010;
    uRam00000100 = uRam00000100 & 0xfffbffff | (param_2 & 1) << 0x12;
  }
  else if (param_1 == 2) {
    *DAT_10005a54 = *DAT_10005a54 & 0xefffffff;
    uRam00000100 = uRam00000100 & 0xfff7ffff | (param_2 & 1) << 0x13;
  }
  else if (param_1 == 4) {
    *DAT_10005a58 = *DAT_10005a58 & 0xefffffff;
    uRam00000100 = uRam00000100 & 0xffefffff | (param_2 & 1) << 0x14;
    puVar2 = puVar1;
  }
  else {
    puVar2 = (uint *)0x0;
  }
  *puVar2 = *puVar2 & 0xfbffffff | 0x4000000;
  do {
  } while (puVar2[5] != 0);
  *puVar2 = *puVar2 & 0xfbffffff;
  *puVar2 = *puVar2 & 0xf7ffffff | ((byte)~(param_2 != 0) & 1) << 0x1b;
  *puVar2 = *puVar2 & 0xfdffffff | ((byte)~(param_3 != 0) & 1) << 0x19;
  *puVar2 = *puVar2 & 0xfeffffff | 0x1000000;
  *puVar2 = *puVar2 & 0xffff0000 | 0x6000;
  *puVar2 = *puVar2 & 0x7fffffff | param_4 << 0x1f;
  puVar2[1] = puVar2[1] & 0xff00ffff;
  puVar2[1] = puVar2[1] & 0xffff0000 | 0x10;
  return;
}

