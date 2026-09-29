
void FUN_10009c2c(uint param_1)

{
  uint *puVar1;
  uint uVar2;
  short *psVar3;
  
  puVar1 = DAT_10009c94;
  if (param_1 != 0) {
    uVar2 = *DAT_10009c94;
    if ((param_1 < uVar2) || (DAT_10009c94[1] <= param_1)) {
      FUN_10009934(PTR_s_illegal_memory_10009ca0);
      return;
    }
    psVar3 = (short *)(param_1 - 0xc);
    if ((*(short *)(param_1 - 10) == 0) || (*psVar3 != 0x1ea0)) {
      FUN_10009934(PTR_s_to_free_a_bad_data_block__10009c98);
      FUN_10009934(PTR_s_mem__0x_08x__used_flag___d__magi_10009c9c,psVar3,
                   *(undefined2 *)(param_1 - 10),*psVar3);
      uVar2 = *puVar1;
    }
    *(undefined2 *)(param_1 - 10) = 0;
    *psVar3 = 0x1ea0;
    if (psVar3 < (short *)puVar1[2]) {
      puVar1[2] = (uint)psVar3;
    }
    puVar1[4] = (int)psVar3 + ((puVar1[4] - *(int *)(param_1 - 8)) - uVar2);
    FUN_100099d4(psVar3);
  }
  return;
}

