
void FUN_0047cbc4(int param_1,uint param_2,uint *param_3)

{
  uint uVar1;
  uint uVar2;
  
  uVar2 = *param_3;
  for (uVar1 = 0; uVar1 < param_2; uVar1 = uVar1 + 1) {
    uVar2 = *(uint *)(DAT_0047cc14 + ((uint)*(byte *)(param_1 + uVar1) ^ uVar2 >> 0x18) * 4) ^
            uVar2 << 8;
  }
  *param_3 = uVar2;
  return;
}

