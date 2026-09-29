
undefined4 Ins_WCVTP(int param_1,uint *param_2)

{
  undefined4 unaff_r7;
  
  if (*param_2 < *(uint *)(param_1 + 0x180)) {
    (**(code **)(param_1 + 0x25c))(param_1,*param_2,param_2[1]);
  }
  else if (*(char *)(param_1 + 0x235) != '\0') {
    *(undefined4 *)(param_1 + 0xc) = 0x86;
  }
  return unaff_r7;
}

