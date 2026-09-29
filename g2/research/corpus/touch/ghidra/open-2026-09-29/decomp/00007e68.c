
void CalcChecksum(int param_1,uint param_2)

{
  byte bVar1;
  uint uVar2;
  byte bVar3;
  
  bVar1 = 0xff;
  for (uVar2 = 0; uVar2 != param_2; uVar2 = uVar2 + 1 & 0xffff) {
    bVar1 = bVar1 ^ *(byte *)(param_1 + uVar2);
    for (bVar3 = 0; bVar3 < 8; bVar3 = bVar3 + 1) {
      if ((char)bVar1 < '\0') {
        bVar1 = bVar1 << 1 ^ 0x31;
      }
      else {
        bVar1 = bVar1 << 1;
      }
    }
  }
  return;
}

