
void case_control_word0_replace_field22(uint *param_1,uint param_2)

{
  *param_1 = *param_1 & 0xfe3fffff | param_2;
  return;
}

