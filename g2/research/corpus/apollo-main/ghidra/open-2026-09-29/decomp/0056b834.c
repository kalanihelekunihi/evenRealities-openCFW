
undefined4 attcDiscVerify(undefined4 *param_1)

{
  int *piVar1;
  byte bVar2;
  
  bVar2 = 0;
  piVar1 = (int *)*param_1;
  while( true ) {
    if (*(byte *)(param_1 + 3) <= bVar2) {
      return 0;
    }
    if (((int)((uint)*(byte *)(*piVar1 + 4) << 0x1e) < 0) &&
       (*(short *)(param_1[1] + (uint)bVar2 * 2) == 0)) break;
    bVar2 = bVar2 + 1;
    piVar1 = piVar1 + 1;
  }
  return 0x76;
}

