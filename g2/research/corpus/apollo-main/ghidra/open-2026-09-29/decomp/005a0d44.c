
void FUN_005a0d44(char param_1,char param_2)

{
  uint *puVar1;
  
  if (((param_2 == '\x01') && (param_1 == '\x02')) && (*DAT_005a16f8 == '\0')) {
    *DAT_005a1718 = 1;
  }
  puVar1 = DAT_005a1700;
  if ((param_2 == '\x01') && (param_1 == '\0')) {
    *DAT_005a1700 = *DAT_005a1700 & 0xfffeffff;
    *puVar1 = *puVar1 & 0xfffffff7;
    *puVar1 = *puVar1 & 0xffffffbf;
    *DAT_005a16f8 = '\0';
  }
  return;
}

