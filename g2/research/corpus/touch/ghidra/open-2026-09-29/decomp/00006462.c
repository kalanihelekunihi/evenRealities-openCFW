
void touch_sub_3162(uint param_1,int param_2,int *param_3)

{
  ushort uVar1;
  int iVar2;
  int iVar3;
  uint uVar4;
  ushort *puVar5;
  int iVar6;
  int local_2c;
  
  iVar3 = **(int **)(*param_3 + 8);
  iVar6 = param_3[10] + param_1 * 0x1c;
  local_2c = iVar3 + 0x2000;
  param_2 = param_1 + param_2;
  for (; param_1 <= param_2 - 1U; param_1 = param_1 + 1) {
    uVar4 = (uint)*(ushort *)(param_3[0xc] + param_1 * 4);
    iVar2 = touch_sub_4ade(uVar4,param_3);
    if (iVar2 != 0) {
      iVar2 = *(int *)(iVar3 + 0x3200);
      puVar5 = (ushort *)
               (*(int *)(param_3[3] + uVar4 * 0x90 + 4) +
               (uint)*(ushort *)(param_3[0xc] + param_1 * 4 + 2) * 10);
      uVar1 = puVar5[3];
      *(byte *)(puVar5 + 3) = (byte)uVar1 & 0xfb;
      if (iVar2 << 0xf < 0) {
        *(byte *)(puVar5 + 3) = (byte)uVar1 | 4;
      }
      *puVar5 = (ushort)iVar2;
      if (*(char *)(param_3[2] + 0x76) == '\0') {
        uVar4 = (uint)*(byte *)(iVar6 + 0x1b) << 0x18;
        *(uint *)(iVar6 + 0x18) = uVar4;
        *(uint *)(iVar6 + 0x18) = uVar4 | (uint)*puVar5 << 8;
      }
      else {
        uVar4 = (uint)*(byte *)(iVar6 + 0x1b) << 0x18;
        *(uint *)(iVar6 + 0x18) = uVar4;
        *(uint *)(iVar6 + 0x18) = uVar4 | *(uint *)(local_2c + 0xc) & 0xffffff;
      }
    }
    iVar6 = iVar6 + 0x1c;
    local_2c = local_2c + 0x2c;
  }
  return;
}

