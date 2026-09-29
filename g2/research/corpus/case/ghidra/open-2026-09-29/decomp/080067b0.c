
void case_control_word5_replace_slot(int param_1,uint param_2,int param_3)

{
  *(uint *)(param_1 + 0x14) =
       *(uint *)(param_1 + 0x14) & ~(7 << (param_2 & 4)) | param_3 << (param_2 & 4);
  return;
}

