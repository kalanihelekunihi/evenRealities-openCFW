
void msclp_register_config_write(int param_1,int param_2,undefined4 *param_3)

{
  int iVar1;
  
  if (param_2 == 5) {
    *(undefined4 *)(param_1 + DAT_000091f0) = 0;
    iVar1 = 0;
  }
  else if (param_2 == 0xb) {
    *(undefined4 *)(param_1 + 0x3000) = *param_3;
    *(undefined4 *)(param_1 + DAT_00009208) = param_3[1];
    *(undefined4 *)(param_1 + DAT_0000920c) = param_3[2];
    *(undefined4 *)(param_1 + DAT_00009210) = param_3[3];
    *(undefined4 *)(param_1 + DAT_00009214) = param_3[4];
    *(undefined4 *)(param_1 + DAT_000091f0) = param_3[5];
    iVar1 = 6;
  }
  else {
    *(undefined4 *)(param_1 + DAT_000091f0) = *param_3;
    iVar1 = 1;
  }
  *(undefined4 *)(param_1 + DAT_000091f4) = param_3[iVar1];
  *(undefined4 *)(param_1 + DAT_000091f8) = param_3[iVar1 + 1];
  *(undefined4 *)(param_1 + DAT_000091fc) = param_3[iVar1 + 2];
  *(undefined4 *)(param_1 + DAT_00009200) = param_3[iVar1 + 3];
  *(undefined4 *)(param_1 + DAT_00009204) = param_3[iVar1 + 4];
  return;
}

