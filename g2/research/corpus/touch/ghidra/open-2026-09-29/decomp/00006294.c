
uint touch_sub_2f94(int *param_1,int param_2)

{
  byte bVar1;
  undefined1 uVar2;
  undefined1 uVar3;
  int iVar4;
  undefined4 uVar5;
  undefined4 uVar6;
  undefined4 uVar7;
  int iVar8;
  int iVar9;
  uint uVar10;
  
  iVar8 = *param_1;
  iVar9 = *(int *)(param_2 + 8);
  uVar10 = (uint)*(byte *)(iVar9 + 0x4d) + (uint)*(ushort *)(iVar8 + 0x2c);
  if (0xffff < uVar10) {
    uVar10 = DAT_0000632c;
  }
  bVar1 = *(byte *)(iVar8 + 0x38);
  uVar2 = *(undefined1 *)(iVar9 + 0x4e);
  iVar4 = param_1[0x22];
  uVar3 = *(undefined1 *)((int)param_1 + 0x87);
  uVar5 = touch_sub_2f20(*(undefined2 *)(iVar9 + 0x3c));
  uVar6 = touch_sub_2f62(bVar1 & 0x7f,uVar2);
  if (*(char *)((int)param_1 + 0x7a) == '\x01') {
    uVar7 = 8;
  }
  else if (*(char *)((int)param_1 + 0x7a) == '\n') {
    uVar7 = 8;
  }
  else {
    uVar7 = 4;
  }
  uVar7 = touch_sub_2f70(*(undefined2 *)(iVar8 + 0xe),uVar7,uVar3,uVar2);
  uVar10 = touch_sub_2ef0((char)iVar4,uVar6,uVar7,uVar5,uVar10);
  return uVar10 | 4;
}

