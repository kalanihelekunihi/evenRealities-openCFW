
undefined8 FUN_00503498(undefined1 param_1,uint param_2,int *param_3,undefined4 param_4)

{
  int *piVar1;
  undefined1 uVar2;
  undefined4 uVar3;
  int iVar4;
  uint uVar5;
  int *piVar6;
  byte bVar7;
  undefined8 uVar8;
  uint local_20;
  int *local_1c;
  undefined4 uStack_18;
  
  uVar5 = param_2;
  piVar6 = param_3;
  local_1c = param_3;
  uStack_18 = param_4;
  local_20 = param_2;
  if ((*param_3 == 0) ||
     (uVar8 = FUN_0047ae78(*param_3,2,&local_1c), uVar5 = (uint)((ulonglong)uVar8 >> 0x20),
     piVar6 = (int *)0x0, (int)uVar8 == 0)) {
    piVar1 = DAT_00503ff4;
    if ((param_2 & 0xff) != 0) {
      *(byte *)((int)param_3 + 7) = *(byte *)*DAT_00503ff4 & 1;
      if ((*(char *)((int)param_3 + 7) != '\0') && (*param_3 == 0)) {
        uVar3 = DmConnPeerAddr(param_1,uVar5,piVar6);
        uVar2 = DmConnPeerAddrType(param_1);
        iVar4 = FUN_0047a71c(uVar2,uVar3,1);
        *param_3 = iVar4;
      }
      *(undefined1 *)((int)param_3 + 0xb) = 0;
      bVar7 = *(byte *)(*piVar1 + 2);
      iVar4 = DmConnPeerAddrType(param_1);
      if (iVar4 == 1) {
        bVar7 = bVar7 | 2;
      }
      *(undefined1 *)(param_3 + 2) = 1;
      local_20 = (uint)bVar7;
      DmSecPairReq(param_1,*(undefined1 *)(*piVar1 + 3),*(undefined1 *)*piVar1,
                   *(undefined1 *)(*piVar1 + 1));
    }
  }
  else {
    *(undefined1 *)((int)param_3 + 6) = 1;
    *(undefined1 *)(param_3 + 2) = 1;
    DmSecEncryptReq(param_1,(uint)local_1c & 0xff);
  }
  return CONCAT44(local_1c,local_20);
}

