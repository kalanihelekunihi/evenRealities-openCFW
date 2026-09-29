
void msclp_scan_start_wait(undefined4 param_1,undefined4 *param_2)

{
  undefined4 uVar1;
  int iVar2;
  int iVar3;
  
  iVar3 = *(int *)((undefined4 *)*param_2)[2];
  uVar1 = __aeabi_uidiv(*(undefined4 *)*param_2,DAT_000069bc);
  for (iVar2 = pdl_timeout_count_scale(param_1,uVar1,5);
      ((*(uint *)(iVar3 + 0x100) & 0x100) == 0 && (iVar2 != 0)); iVar2 = iVar2 + -1) {
  }
  *(undefined4 *)(iVar3 + 0x100) = DAT_000069c0;
  return;
}

