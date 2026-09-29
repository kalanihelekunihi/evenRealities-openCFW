
undefined8
attsFindServiceGroupEnd(ushort param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  ushort uVar1;
  uint uVar2;
  int iVar3;
  undefined4 *puVar4;
  ushort uVar5;
  int iVar6;
  undefined4 local_20;
  undefined4 uStack_1c;
  
  local_20 = CONCAT22(*DAT_0056e4e8,*DAT_0056e4ec);
  if (param_1 == 0xffff) {
    uVar2 = 0xffff;
  }
  else {
    uVar5 = param_1 + 1;
    uStack_1c = param_4;
    for (puVar4 = *(undefined4 **)(DAT_0056e4e4 + 600); puVar4 != (undefined4 *)0x0;
        puVar4 = (undefined4 *)*puVar4) {
      if (uVar5 < *(ushort *)(puVar4 + 4)) {
        uVar5 = *(ushort *)(puVar4 + 4);
      }
      if (uVar5 <= *(ushort *)((int)puVar4 + 0x12)) {
        iVar6 = puVar4[1] + ((uint)uVar5 - (uint)*(ushort *)(puVar4 + 4)) * 0x10;
        uVar1 = uVar5;
        while (uVar5 = uVar1, uVar5 <= *(ushort *)((int)puVar4 + 0x12)) {
          iVar3 = attsUuidCmp(iVar6,2,(int)&local_20 + 2);
          if ((iVar3 != 0) || (iVar3 = attsUuidCmp(iVar6,2,&local_20), iVar3 != 0)) {
            uVar2 = (uint)param_1;
            goto LAB_0056da9a;
          }
          if (uVar5 == 0xffff) {
            uVar2 = 0xffff;
            goto LAB_0056da9a;
          }
          iVar6 = iVar6 + 0x10;
          param_1 = uVar5;
          uVar1 = uVar5 + 1;
        }
      }
    }
    uVar2 = 0xffff;
  }
LAB_0056da9a:
  return CONCAT44(local_20,uVar2);
}

