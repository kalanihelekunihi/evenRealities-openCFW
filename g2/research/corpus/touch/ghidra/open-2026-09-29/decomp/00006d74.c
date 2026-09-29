
uint touch_sub_3a74(uint param_1,uint param_2,int *param_3)

{
  int iVar1;
  uint uVar2;
  undefined4 *puVar3;
  uint *puVar4;
  uint uVar5;
  uint local_24;
  
  uVar5 = (param_1 + param_2) - 1;
  if (param_3 == (int *)0x0) {
    return 1;
  }
  if (param_2 == 0) {
    return 1;
  }
  if (8 < param_2) {
    return 1;
  }
  if (3 < uVar5) {
    return 1;
  }
  *(uint *)(param_3[1] + 8) = *(uint *)(param_3[1] + 8) & DAT_0000702c;
  iVar1 = touch_state_298e_status80(param_3);
  if (iVar1 == 0x80) {
    return 0x40;
  }
  uVar2 = event_dispatcher(2,param_3);
  if (uVar2 != 0) {
    return uVar2;
  }
  touch_sub_2e40(param_3);
  puVar3 = (undefined4 *)param_3[2];
  puVar4 = (uint *)**(undefined4 **)(*param_3 + 8);
  *(undefined1 *)((int)puVar3 + 0x73) = 1;
  if (((*(ushort *)(puVar3 + 0xd) == param_1) && (*(ushort *)((int)puVar3 + 0x36) == uVar5)) &&
     (*(int *)(param_3[1] + 8) << 0x1a < 0)) {
    local_24 = puVar4[0x60] & 1;
    if ((puVar4[0x60] & 1) != 0) {
      *puVar4 = *puVar4 & 0x7fffffff;
      puVar4[0x51] = 0x100;
      touch_sub_3308(0x7e,1,param_3);
      local_24 = 0;
    }
  }
  else {
    *(short *)(puVar3 + 0xd) = (short)param_1;
    *(short *)((int)puVar3 + 0x36) = (short)uVar5;
    *(short *)((int)puVar3 + 0x46) = (short)param_2;
    *(undefined1 *)((int)puVar3 + 0x71) = 3;
    *puVar4 = *puVar4 | 0x30000;
    *puVar4 = *puVar4 & DAT_00007030;
    puVar4[0x1d] = DAT_00007034;
    *puVar4 = *puVar4 & 0x7fffffff;
    if ((int)(puVar4[0x60] << 7) < 0) {
      puVar4[0x51] = 0x10000;
      local_24 = 0;
    }
    else {
      puVar4[0x51] = 1;
      local_24 = touch_sub_3308(0x13b,2,param_3);
      if (local_24 != 0) goto LAB_00006f90;
    }
    iVar1 = param_3[0xb];
    for (uVar5 = 0; uVar5 < param_2 * 0xb; uVar5 = uVar5 + 1) {
      puVar4[uVar5 + 0x800] = *(uint *)(iVar1 + param_1 * 0x2c + uVar5 * 4);
    }
    iVar1 = param_2 * 0xb + DAT_00007038;
    puVar4[iVar1] = puVar4[iVar1] | 4;
    puVar4[0xf00] = puVar4[0xf00] | 1;
    if ((*(uint *)((int)puVar4 + DAT_0000703c) & 1) == 0) {
      local_24 = 4;
    }
    if ((int)(puVar4[0x60] << 7) < 0) {
      puVar4[0x51] = 0x100;
    }
    if (local_24 == 0) {
      puVar4[3] = puVar4[3] & DAT_00007040;
      *puVar4 = *puVar4 & DAT_00007030;
      puVar4[0x1c] = puVar4[0x1c] & DAT_00007044;
      if (0x3fff < *(ushort *)(param_3[2] + 0x4a)) {
        *(short *)(param_3[2] + 0x4a) = (short)DAT_00007048;
      }
      puVar4[0x1c] = puVar4[0x1c] | (uint)*(ushort *)(param_3[2] + 0x4a) << 0x10;
      puVar4[0x1c] = puVar4[0x1c] | 0x80000000;
      *(uint *)(**(int **)(*param_3 + 8) + 0x70) =
           *(uint *)(**(int **)(*param_3 + 8) + 0x70) & 0xffff0000;
      *(uint *)(**(int **)(*param_3 + 8) + 0x70) =
           *(uint *)(**(int **)(*param_3 + 8) + 0x70) | *(uint *)(param_3[2] + 0x28);
      uVar5 = puVar4[2] & DAT_00007040;
      iVar1 = __aeabi_uidiv(0x100,param_2);
      puVar4[2] = uVar5 | (0x100 - (iVar1 + -0xb) * param_2) * 0x10000 & DAT_0000704c;
    }
  }
LAB_00006f90:
  *(uint *)(param_3[1] + 8) = *(uint *)(param_3[1] + 8) & 0xffffffcf;
  *(uint *)(param_3[1] + 8) = *(uint *)(param_3[1] + 8) | 0x20;
  if (local_24 == 0) {
    if ((code *)*puVar3 != (code *)0x0) {
      (*(code *)*puVar3)(param_3[7]);
    }
    *puVar4 = *puVar4 & 0x7fffffff;
    *puVar4 = *puVar4 | 0x80000000;
    puVar4[0x4a] = 0x10;
    puVar4[0x50] = puVar4[0x50] | 1;
  }
  return local_24;
}

