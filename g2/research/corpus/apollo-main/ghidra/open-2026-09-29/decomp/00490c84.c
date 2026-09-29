
void FUN_00490c84(undefined4 param_1,uint param_2,uint param_3,undefined4 param_4)

{
  uint uVar1;
  byte bVar2;
  uint local_18 [3];
  uint uVar3;
  
  uVar1 = 0;
  local_18[0] = param_2;
  local_18[1] = param_3;
  local_18[2] = param_4;
  while( true ) {
    uVar3 = param_2 & 0x7f;
    bVar2 = (byte)uVar3;
    param_2 = param_2 >> 7;
    if ((3 < uVar1) || (param_3 == 0 && param_2 == 0)) break;
    *(byte *)((int)local_18 + uVar1) = bVar2 | 0x80;
    uVar1 = uVar1 + 1;
  }
  if (param_3 != 0) {
    uVar3 = uVar3 | (param_3 & 7) << 4;
    for (param_3 = param_3 >> 3; bVar2 = (byte)uVar3, param_3 != 0; param_3 = param_3 >> 7) {
      *(byte *)((int)local_18 + uVar1) = bVar2 | 0x80;
      uVar1 = uVar1 + 1;
      uVar3 = param_3 & 0x7f;
    }
  }
  *(byte *)((int)local_18 + uVar1) = bVar2;
  FUN_00490616(param_1,local_18,uVar1 + 1);
  return;
}

