
int FUN_00507c94(int param_1,byte *param_2,byte *param_3,short *param_4)

{
  int iVar1;
  uint uVar2;
  byte *pbVar3;
  byte *pbVar4;
  byte *pbVar5;
  byte *local_2c;
  short *psStack_28;
  
  pbVar3 = param_3 + 5;
  pbVar4 = param_3 + 5;
  pbVar5 = param_3 + 3;
  local_2c = param_3;
  psStack_28 = param_4;
  iVar1 = FUN_00507c10(param_1,param_3,&local_2c);
  if (iVar1 == 0) {
    uVar2 = (uint)local_2c & 0xff;
    if (uVar2 == 0) {
      *param_4 = (ushort)param_2[1] * 0x100 + (ushort)*param_2;
      param_4[1] = (ushort)param_2[3] * 0x100 + (ushort)param_2[2];
      param_4[2] = (ushort)param_2[5] * 0x100 + (ushort)param_2[4];
      param_4[3] = (ushort)param_2[7] * 0x100 + (ushort)param_2[6];
      *(undefined1 *)(param_4 + 4) = 1;
      param_4[0x13] = (ushort)*param_3 * 0x100 + (ushort)param_2[8];
      param_4[0x14] = (ushort)param_3[2] * 0x100 + (ushort)param_3[1];
      param_4[0x15] = (ushort)param_3[4] * 0x100 + (ushort)param_3[3];
      *(undefined1 *)(param_4 + 0x16) = 1;
      *(byte *)((int)param_4 + 0x2d) = (byte)(((uint)*pbVar3 << 0x1d) >> 0x1e);
      *(byte *)(param_4 + 0x17) = (byte)(((uint)*pbVar3 << 0x1a) >> 0x1d) - 1;
      *(undefined1 *)((int)param_4 + 0x2f) = 1;
      *(undefined1 *)((int)param_4 + 0x4d) = 1;
    }
    else if (uVar2 == 2) {
      param_4[0xc] = (ushort)param_2[1] * 0x100 + (ushort)*param_2;
      param_4[0xd] = (ushort)param_2[3] * 0x100 + (ushort)param_2[2];
      param_4[0xe] = (ushort)param_2[5] * 0x100 + (ushort)param_2[4];
      param_4[0xf] = (ushort)param_2[7] * 0x100 + (ushort)param_2[6];
      *(undefined1 *)(param_4 + 0x10) = 1;
      param_4[0x18] = (ushort)*param_3 * 0x100 + (ushort)param_2[8];
      param_4[0x19] = (ushort)param_3[2] * 0x100 + (ushort)param_3[1];
      param_4[0x1a] = (ushort)param_3[4] * 0x100 + (ushort)param_3[3];
      *(byte *)(param_4 + 0x1b) = (byte)(((uint)*pbVar3 << 0x19) >> 0x1f);
      *(byte *)((int)param_4 + 0x2d) = (byte)(((uint)*pbVar3 << 0x1d) >> 0x1e);
      *(byte *)(param_4 + 0x17) = (byte)(((uint)*pbVar3 << 0x1a) >> 0x1d) - 1;
      *(undefined1 *)((int)param_4 + 0x2f) = 1;
      *(undefined1 *)((int)param_4 + 0x4d) = 1;
    }
    else if (uVar2 < 2) {
      param_4[5] = (ushort)param_2[1] * 0x100 + (ushort)*param_2;
      param_4[6] = (ushort)param_2[3] * 0x100 + (ushort)param_2[2];
      param_4[7] = (ushort)param_2[5] * 0x100 + (ushort)param_2[4];
      param_4[8] = (ushort)param_2[7] * 0x100 + (ushort)param_2[6];
      *(undefined1 *)(param_4 + 9) = 1;
      param_4[0x18] = (ushort)*param_3 * 0x100 + (ushort)param_2[8];
      param_4[0x19] = (ushort)param_3[2] * 0x100 + (ushort)param_3[1];
      param_4[0x1a] = (ushort)param_3[4] * 0x100 + (ushort)param_3[3];
      *(byte *)(param_4 + 0x1b) = (byte)(((uint)*pbVar3 << 0x19) >> 0x1f);
      *(undefined1 *)((int)param_4 + 0x4d) = 1;
    }
    else if (uVar2 == 4) {
      param_4[0x18] = (ushort)param_2[7] * 0x100 + (ushort)param_2[6];
      param_4[0x19] = (ushort)*param_3 * 0x100 + (ushort)param_2[8];
      param_4[0x1a] = (ushort)param_3[2] * 0x100 + (ushort)param_3[1];
      *(byte *)(param_4 + 0x1b) = (byte)(((uint)*pbVar3 << 0x19) >> 0x1f);
      param_4[0x13] = (ushort)param_2[1] * 0x100 + (ushort)*param_2;
      param_4[0x14] = (ushort)param_2[3] * 0x100 + (ushort)param_2[2];
      param_4[0x15] = (ushort)param_2[5] * 0x100 + (ushort)param_2[4];
      *(undefined1 *)(param_4 + 0x16) = 1;
      *(byte *)((int)param_4 + 0x2d) = (byte)(((uint)*pbVar3 << 0x1d) >> 0x1e);
      *(byte *)(param_4 + 0x17) = (byte)(((uint)*pbVar3 << 0x1a) >> 0x1d) - 1;
      *(undefined1 *)((int)param_4 + 0x2f) = 1;
      *(byte *)((int)param_4 + 0x47) = *pbVar5 & 0xf;
      *(byte *)(param_4 + 0x24) = *pbVar5 >> 4;
      *(byte *)((int)param_4 + 0x49) = param_3[4] >> 4;
      *(undefined1 *)(param_4 + 0x25) = 1;
      *(undefined1 *)((int)param_4 + 0x4d) = 1;
    }
    else if (uVar2 < 4) {
      if ((int)((uint)*(byte *)(param_1 + 0x12) << 0x1e) < 0) {
        param_4[0x11] = (ushort)param_3[4] * 0x100 + (ushort)param_3[3];
        *(undefined1 *)(param_4 + 0x12) = 1;
      }
      else {
        param_4[10] = (ushort)param_3[4] * 0x100 + (ushort)param_3[3];
        *(undefined1 *)(param_4 + 0xb) = 1;
      }
      *(byte *)((int)param_4 + 0x4b) = (byte)(((uint)*pbVar4 << 0x19) >> 0x1e);
      *(undefined1 *)(param_4 + 0x26) = 1;
      *(uint *)(param_4 + 0x1c) =
           (uint)param_2[1] * 0x100 + (uint)*param_2 + (uint)param_2[2] * 0x10000 +
           (uint)param_2[3] * 0x1000000;
      *(uint *)(param_4 + 0x1e) =
           (uint)param_2[5] * 0x100 + (uint)param_2[4] + (uint)param_2[6] * 0x10000 +
           (uint)param_2[7] * 0x1000000;
      *(uint *)(param_4 + 0x20) =
           (uint)*param_3 * 0x100 + (uint)param_2[8] + (uint)param_3[1] * 0x10000 +
           (uint)param_3[2] * 0x1000000;
      *(byte *)(param_4 + 0x22) = (byte)(((uint)*pbVar4 << 0x1d) >> 0x1e);
      *(byte *)((int)param_4 + 0x45) = (byte)(((uint)*pbVar4 << 0x1b) >> 0x1e);
      *(undefined1 *)(param_4 + 0x23) = 1;
      *(undefined1 *)((int)param_4 + 0x4d) = 0;
    }
    else if (uVar2 == 6) {
      param_4[0x18] = (ushort)param_2[7] * 0x100 + (ushort)param_2[6];
      param_4[0x19] = (ushort)*param_3 * 0x100 + (ushort)param_2[8];
      param_4[0x1a] = (ushort)param_3[2] * 0x100 + (ushort)param_3[1];
      *(byte *)(param_4 + 0x1b) = (byte)(((uint)*pbVar3 << 0x19) >> 0x1f);
      *(undefined1 *)((int)param_4 + 0x4d) = 1;
    }
    else if (uVar2 < 6) {
      param_4[0x13] = (ushort)param_2[1] * 0x100 + (ushort)*param_2;
      param_4[0x14] = (ushort)param_2[3] * 0x100 + (ushort)param_2[2];
      param_4[0x15] = (ushort)param_2[5] * 0x100 + (ushort)param_2[4];
      *(undefined1 *)(param_4 + 0x16) = 1;
      *(byte *)((int)param_4 + 0x2d) = (byte)(((uint)*pbVar3 << 0x1d) >> 0x1e);
      *(byte *)(param_4 + 0x17) = (byte)(((uint)*pbVar3 << 0x1a) >> 0x1d) - 1;
      *(undefined1 *)((int)param_4 + 0x2f) = 1;
      *(byte *)((int)param_4 + 0x47) = *pbVar5 & 0xf;
      *(byte *)(param_4 + 0x24) = *pbVar5 >> 4;
      *(byte *)((int)param_4 + 0x49) = param_3[4] >> 4;
      *(undefined1 *)(param_4 + 0x25) = 1;
      *(undefined1 *)((int)param_4 + 0x4d) = 1;
    }
    else if (uVar2 == 7) {
      *(uint *)(param_4 + 0x1c) =
           (uint)param_2[1] * 0x100 + (uint)*param_2 + (uint)param_2[2] * 0x10000 +
           (uint)param_2[3] * 0x1000000;
      *(uint *)(param_4 + 0x1e) =
           (uint)param_2[5] * 0x100 + (uint)param_2[4] + (uint)param_2[6] * 0x10000 +
           (uint)param_2[7] * 0x1000000;
      *(uint *)(param_4 + 0x20) =
           (uint)*param_3 * 0x100 + (uint)param_2[8] + (uint)param_3[1] * 0x10000 +
           (uint)param_3[2] * 0x1000000;
      *(byte *)(param_4 + 0x22) = (byte)(((uint)*pbVar4 << 0x1d) >> 0x1e);
      *(byte *)((int)param_4 + 0x45) = (byte)(((uint)*pbVar4 << 0x1b) >> 0x1e);
      *(undefined1 *)(param_4 + 0x23) = 1;
      *(byte *)((int)param_4 + 0x4b) = (byte)(((uint)*pbVar4 << 0x19) >> 0x1e);
      *(undefined1 *)(param_4 + 0x26) = 1;
      *(undefined1 *)((int)param_4 + 0x4d) = 0;
    }
    else {
      iVar1 = -1;
    }
  }
  return iVar1;
}

