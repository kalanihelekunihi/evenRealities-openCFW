
void case_finalize_length_checksum(int param_1,int param_2)

{
  uint uVar1;
  int iVar2;
  
  iVar2 = param_1 + param_2;
  *(char *)(iVar2 + -1) = (char)param_2 + '}';
  for (uVar1 = 0; (int)uVar1 < param_2 + -1; uVar1 = uVar1 + 1 & 0xff) {
    *(char *)(iVar2 + -1) = *(char *)(iVar2 + -1) + *(char *)(param_1 + uVar1);
  }
  return;
}

