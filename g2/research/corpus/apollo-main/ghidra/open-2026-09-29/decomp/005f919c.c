
uint tt_face_get_location(int param_1,uint param_2,int *param_3)

{
  uint uVar1;
  byte *pbVar2;
  undefined1 *puVar3;
  uint uVar4;
  
  uVar1 = 0;
  uVar4 = 0;
  if (param_2 < *(uint *)(param_1 + 0x2d4)) {
    if (*(short *)(param_1 + 0xd2) == 0) {
      puVar3 = (undefined1 *)(*(int *)(param_1 + 0x2d8) + param_2 * 2);
      uVar4 = (uint)CONCAT11(*puVar3,puVar3[1]);
      if (puVar3 + 4 <= (undefined1 *)(*(int *)(param_1 + 0x2d8) + *(int *)(param_1 + 0x2d4) * 2)) {
        uVar4 = (uint)CONCAT11(puVar3[2],puVar3[3]);
      }
      uVar1 = (uint)CONCAT11(*puVar3,puVar3[1]) << 1;
      uVar4 = uVar4 << 1;
    }
    else {
      pbVar2 = (byte *)(*(int *)(param_1 + 0x2d8) + param_2 * 4);
      uVar1 = (uint)pbVar2[3] |
              (uint)pbVar2[1] << 0x10 | (uint)*pbVar2 << 0x18 | (uint)pbVar2[2] << 8;
      uVar4 = uVar1;
      if (pbVar2 + 8 <= (byte *)(*(int *)(param_1 + 0x2d8) + *(int *)(param_1 + 0x2d4) * 4)) {
        uVar4 = (uint)pbVar2[7] |
                (uint)pbVar2[5] << 0x10 | (uint)pbVar2[4] << 0x18 | (uint)pbVar2[6] << 8;
      }
    }
  }
  if (*(uint *)(param_1 + 0x2b0) < uVar1) {
    *param_3 = 0;
    uVar1 = 0;
  }
  else {
    if (*(uint *)(param_1 + 0x2b0) < uVar4) {
      if (param_2 != *(int *)(param_1 + 0x2d4) - 2U) {
        *param_3 = 0;
        return 0;
      }
      uVar4 = *(uint *)(param_1 + 0x2b0);
    }
    if (uVar4 < uVar1) {
      *param_3 = *(int *)(param_1 + 0x2b0) - uVar1;
    }
    else {
      *param_3 = uVar4 - uVar1;
    }
  }
  return uVar1;
}

