
int touch_packet_2248_build_entry(int param_1,uint param_2,uint *param_3,int param_4)

{
  char cVar1;
  byte bVar2;
  ushort *puVar3;
  int iVar4;
  int iVar5;
  uint uVar6;
  int iVar7;
  
  iVar5 = *(int *)(param_4 + 8);
  if (param_1 == 0) {
    puVar3 = (ushort *)(*(int *)(param_4 + 0x30) + param_2 * 4);
  }
  else {
    puVar3 = (ushort *)(*(int *)(param_4 + 0x34) + param_2 * 4);
  }
  iVar4 = *(int *)(param_4 + 0xc) + (uint)*puVar3 * 0x90;
  iVar7 = *(int *)(param_4 + 0x10) + (uint)*puVar3 * 0x3c;
  cVar1 = *(char *)(iVar4 + 0x7a);
  if (param_1 == 1) {
    *param_3 = (*(byte *)(iVar5 + 0x5d) & 0xf) << 4 | *(byte *)(iVar5 + 0x60) & 0xf |
               (*(byte *)(iVar5 + 0x5e) & 0xf) << 8 | (*(ushort *)(iVar7 + 0xc) & 0x3f) << 0x10 |
               (uint)*(byte *)(iVar5 + 0x5f) << 0x18;
    param_3[1] = *(uint *)(iVar7 + 0x1a);
    if (cVar1 == '\x01') {
      uVar6 = 0;
    }
    else {
      uVar6 = 0x1000000;
    }
    param_3[2] = (uint)*(ushort *)(iVar7 + 8) | (*(byte *)(iVar7 + 0x20) & 7) << 0x10 | uVar6;
    param_3[3] = 0;
    param_3[4] = 0;
    param_3 = param_3 + 5;
  }
  else {
    param_3[6] = (uint)*(byte *)(iVar4 + 0x8c) << 0x18;
  }
  uVar6 = (*(byte *)(iVar4 + 0x84) - 1) * 0x4000 & 0x4000 | *(ushort *)(iVar7 + 0x2c) - 1 & 0x3fff;
  param_3[3] = uVar6;
  if ((*(char *)(iVar7 + 0x34) == '\x01') && (*(ushort *)(iVar4 + 0x80) != param_2)) {
    param_3[3] = uVar6 | 0x8000;
  }
  iVar5 = touch_state_1ebc_pack(puVar3,param_3);
  if (iVar5 == 0) {
    if (cVar1 == '\x01') {
      bVar2 = *(byte *)(iVar7 + 0x21);
      iVar4 = touch_leaf_2228_mode_scale(1,(uint)bVar2,*(undefined2 *)(iVar7 + 0xe));
      param_3[5] = (iVar4 + -1) * 0x10000 & DAT_000056a0 | (bVar2 & 3) << 0x1c |
                   (uint)*(byte *)(iVar7 + 0x38) << 0x1e | 3;
    }
    else {
      iVar5 = 1;
    }
  }
  return iVar5;
}

