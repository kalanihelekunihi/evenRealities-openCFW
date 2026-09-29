
void Ins_SPVFS(int param_1,undefined4 *param_2)

{
  Normalize((int)(short)*param_2,(int)(short)param_2[1],param_1 + 0x12a);
  *(undefined4 *)(param_1 + 0x126) = *(undefined4 *)(param_1 + 0x12a);
  Compute_Funcs(param_1);
  return;
}

