
uint crc32_table_42e1ec(int param_1,uint param_2,uint *param_3)

{
  uint uVar1;
  uint uVar2;
  
  if (param_3 == (uint *)0x0) {
    uVar1 = 0xffffffff;
  }
  else {
    uVar1 = ~*param_3;
  }
  for (uVar2 = 0; uVar2 < param_2; uVar2 = uVar2 + 1) {
    uVar1 = *(uint *)(DAT_0042e220 + ((*(byte *)(param_1 + uVar2) ^ uVar1) & 0xff) * 4) ^ uVar1 >> 8
    ;
  }
  return ~uVar1;
}

