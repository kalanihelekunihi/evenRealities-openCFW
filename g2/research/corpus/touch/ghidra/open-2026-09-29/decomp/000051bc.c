
undefined4 touch_state_1ebc_pack(ushort *param_1,int param_2,int param_3)

{
  char cVar1;
  byte bVar2;
  byte bVar3;
  uint uVar4;
  ushort uVar5;
  int iVar6;
  uint uVar7;
  int *piVar8;
  
  uVar4 = (uint)param_1[1];
  piVar8 = (int *)(*(int *)(param_3 + 0xc) + (uint)*param_1 * 0x90);
  cVar1 = *(char *)((int)piVar8 + 0x7a);
  iVar6 = *(int *)(param_3 + 8);
  uVar5 = *(ushort *)(*(int *)(param_3 + 0x10) + (uint)*param_1 * 0x3c + 0x36);
  if (uVar5 != 0) {
    uVar5 = uVar5 - 1;
  }
  *(uint *)(param_2 + 0xc) = (uint)uVar5 << 0x10 & DAT_000052b8 | *(uint *)(param_2 + 0xc);
  if (((cVar1 != '\x01') || (*(char *)(iVar6 + 0x5a) != '\x01')) &&
     ((cVar1 != '\x02' || (*(char *)(iVar6 + 0x5b) != '\x01')))) {
    if (cVar1 != '\n') {
      uVar7 = 0x400000;
      goto LAB_00005206;
    }
    if (*(char *)(iVar6 + 0x5c) != '\x01') {
      uVar7 = 0x400000;
      goto LAB_00005206;
    }
  }
  uVar7 = (*(byte *)(*piVar8 + 0x33) & 7) << 0x1c | 0xc00000;
LAB_00005206:
  if (-1 < *(int *)(*(int *)(param_3 + 4) + 8) << 0x13) {
    if ((cVar1 == '\x01') && (*(byte *)((int)piVar8 + 0x3a) <= uVar4)) {
      bVar2 = *(byte *)(*piVar8 + 0x2f);
    }
    else {
      bVar2 = *(byte *)(*piVar8 + 0x2e);
    }
    if ((cVar1 == '\x01') && (*(byte *)((int)piVar8 + 0x3a) <= uVar4)) {
      bVar3 = *(byte *)(*piVar8 + 0x31);
    }
    else {
      bVar3 = *(byte *)(*piVar8 + 0x30);
    }
    uVar7 = (bVar3 & 0x1f) << 0x10 | bVar2 | uVar7;
    if (cVar1 == '\x01') {
      uVar7 = uVar7 | (uint)*(byte *)(piVar8[1] + uVar4 * 10 + 9) << 8;
    }
  }
  *(uint *)(param_2 + 0x10) = uVar7;
  return 0;
}

