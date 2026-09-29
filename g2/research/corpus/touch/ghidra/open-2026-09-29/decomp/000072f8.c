
int touch_sub_3ff8(int param_1,int param_2,int *param_3)

{
  byte bVar1;
  ushort uVar2;
  undefined4 uVar3;
  int iVar4;
  int iVar5;
  uint *puVar6;
  undefined2 *puVar7;
  int iVar8;
  uint uVar9;
  int iVar10;
  
  iVar5 = param_3[2];
  puVar6 = (uint *)**(int **)(*param_3 + 8);
  if (param_1 == 1) {
    iVar10 = param_3[0xb] + param_2 * 0x2c + 0x14;
    iVar4 = param_3[0xd];
  }
  else {
    iVar10 = param_3[10] + param_2 * 0x1c;
    iVar4 = param_3[0xc];
  }
  uVar9 = (uint)*(ushort *)(iVar4 + param_2 * 4);
  uVar2 = *(ushort *)(iVar4 + param_2 * 4 + 2);
  iVar8 = uVar9 * 0x90;
  iVar4 = param_3[3] + iVar8;
  if (*(char *)(iVar4 + 0x7a) == '\x01') {
    if (4 < *(byte *)(iVar4 + 0x85)) {
      iVar4 = event_dispatcher(4,param_3);
      goto LAB_00007356;
    }
  }
  iVar4 = event_dispatcher(2,param_3);
LAB_00007356:
  touch_sub_355c(param_3);
  *(short *)(iVar5 + 0x34) = (short)param_2;
  *(short *)(iVar5 + 0x36) = (short)param_2;
  msclp_scan_register_prepare(iVar10,param_3);
  uVar3 = touch_sub_3f88(uVar9,param_2,param_3);
  iVar5 = msclp_scan_start_wait(uVar3,param_3);
  if (iVar5 == 0) {
    iVar4 = 0x100;
  }
  else if (iVar4 == 0) {
    uVar9 = puVar6[0xc80];
    puVar7 = (undefined2 *)(*(int *)(param_3[3] + iVar8 + 4) + (uint)uVar2 * 10);
    bVar1 = *(byte *)(puVar7 + 3);
    *(byte *)(puVar7 + 3) = bVar1 & 0xfb;
    if ((int)(uVar9 << 0xf) < 0) {
      *(byte *)(puVar7 + 3) = bVar1 | 4;
    }
    *puVar7 = (short)uVar9;
  }
  *puVar6 = *puVar6 & 0x7fffffff;
  return iVar4;
}

