
undefined4 cmdq_post_loop_block_427c12(uint *param_1,char param_2)

{
  undefined4 uVar1;
  undefined4 *puVar2;
  
  if ((param_1 == (uint *)0x0) || ((*param_1 & 0x1ffffff) != DAT_00427c88)) {
    uVar1 = 2;
  }
  else if (param_1[4] == param_1[5]) {
    uVar1 = 7;
  }
  else {
    puVar2 = (undefined4 *)param_1[5];
    *puVar2 = *(undefined4 *)(param_1[9] + 8);
    puVar2[1] = 0;
    puVar2[2] = (uint)(param_2 != '\0') | *(uint *)(param_1[9] + 4);
    puVar2[3] = param_1[1];
    param_1[5] = (uint)(puVar2 + 4);
    param_1[4] = param_1[5];
    if (DAT_00427c8c <= param_1[2]) {
      DataMemoryBarrier(0x1f);
    }
    **(uint **)(param_1[9] + 0xc) = (uint)(byte)param_1[8];
    uVar1 = 0;
  }
  return uVar1;
}

