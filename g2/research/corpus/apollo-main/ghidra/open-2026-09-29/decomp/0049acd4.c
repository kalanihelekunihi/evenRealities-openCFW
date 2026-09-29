
ushort FUN_0049acd4(int param_1,uint param_2,ushort *param_3)

{
  ushort uVar1;
  uint uVar2;
  
  if (param_3 == (ushort *)0x0) {
    uVar1 = 0xffff;
  }
  else {
    uVar1 = *param_3;
  }
  for (uVar2 = 0; uVar2 < param_2; uVar2 = uVar2 + 1) {
    uVar1 = *(ushort *)
             (DAT_0049ad08 + ((uint)*(byte *)(param_1 + uVar2) ^ (int)(uint)uVar1 >> 8) * 2) ^
            uVar1 << 8;
  }
  return uVar1;
}

