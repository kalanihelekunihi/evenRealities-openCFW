
undefined8 FUN_0055eaae(int param_1,undefined4 param_2,uint param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  byte bVar4;
  byte bVar5;
  code *pcVar6;
  uint local_18;
  undefined4 uStack_14;
  
  local_18 = param_3;
  uStack_14 = param_4;
  for (bVar5 = 0; iVar3 = DAT_0055ee50, bVar5 < 8; bVar5 = bVar5 + 1) {
    if (*(char *)((uint)bVar5 + param_1 + 0xc4) != '\0') {
      iVar3 = FUN_0055ea78(param_1,bVar5,&local_18);
      iVar1 = DAT_0055ee50;
      if (iVar3 != DAT_0055ee50) break;
      bVar4 = (byte)local_18 & *(byte *)((uint)bVar5 + param_1 + 0xc4);
      local_18 = CONCAT31(local_18._1_3_,bVar4);
      if (bVar4 != 0) {
        iVar3 = FUN_0055ea94(param_1,bVar5,bVar4);
        if (iVar3 != iVar1) break;
        iVar3 = FUN_0055ea40(bVar5);
        pcVar6 = *(code **)(param_1 + iVar3 * 4 + 0x98);
        if (pcVar6 != (code *)0x0) {
          uVar2 = FUN_0055ea40(bVar5);
          (*pcVar6)(param_1,uVar2,local_18 & 0xff);
        }
      }
    }
  }
  return CONCAT44(local_18,iVar3);
}

