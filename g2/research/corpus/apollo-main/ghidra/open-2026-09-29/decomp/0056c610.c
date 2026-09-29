
ushort attsFindInRange(ushort param_1,ushort param_2,int *param_3)

{
  undefined4 *puVar1;
  
  puVar1 = *(undefined4 **)(DAT_0056cd98 + 600);
  while( true ) {
    if (puVar1 == (undefined4 *)0x0) {
      return 0;
    }
    if ((param_1 < *(ushort *)(puVar1 + 4)) && (*(ushort *)(puVar1 + 4) <= param_2)) {
      param_1 = *(ushort *)(puVar1 + 4);
    }
    if ((*(ushort *)(puVar1 + 4) <= param_1) && (param_1 <= *(ushort *)((int)puVar1 + 0x12))) break;
    puVar1 = (undefined4 *)*puVar1;
  }
  *param_3 = puVar1[1] + ((uint)param_1 - (uint)*(ushort *)(puVar1 + 4)) * 0x10;
  return param_1;
}

