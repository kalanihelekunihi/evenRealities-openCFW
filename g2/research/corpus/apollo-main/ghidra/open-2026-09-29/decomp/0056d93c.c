
undefined8
attsFindUuidInRange(ushort param_1,ushort param_2,undefined1 param_3,undefined4 param_4,int *param_5
                   ,undefined4 *param_6)

{
  int iVar1;
  uint uVar2;
  undefined4 *puVar3;
  
  puVar3 = *(undefined4 **)(DAT_0056e4e4 + 600);
  do {
    if (puVar3 == (undefined4 *)0x0) {
      uVar2 = 0;
LAB_0056d9e8:
      return CONCAT44(param_4,uVar2);
    }
    if ((param_1 < *(ushort *)(puVar3 + 4)) && (*(ushort *)(puVar3 + 4) <= param_2)) {
      param_1 = *(ushort *)(puVar3 + 4);
    }
    if ((*(ushort *)(puVar3 + 4) <= param_1) && (param_1 <= *(ushort *)((int)puVar3 + 0x12))) {
      *param_5 = puVar3[1] + ((uint)param_1 - (uint)*(ushort *)(puVar3 + 4)) * 0x10;
      for (; (param_1 <= *(ushort *)((int)puVar3 + 0x12) && (param_1 <= param_2));
          param_1 = param_1 + 1) {
        iVar1 = attsUuidCmp(*param_5,param_3,param_4);
        if (iVar1 != 0) {
          *param_6 = puVar3;
          uVar2 = (uint)param_1;
          goto LAB_0056d9e8;
        }
        if (param_1 == 0xffff) break;
        *param_5 = *param_5 + 0x10;
      }
    }
    puVar3 = (undefined4 *)*puVar3;
  } while( true );
}

