
uint vector_entry_465c(uint param_1)

{
  ushort uVar1;
  ushort uVar2;
  uint uVar3;
  int unaff_r4;
  uint unaff_r5;
  ushort *unaff_r6;
  uint unaff_r7;
  int unaff_r8;
  uint unaff_r9;
  int unaff_r10;
  int unaff_r11;
  uint in_stack_00000000;
  int in_stack_00000004;
  
  while ((param_1 <= unaff_r9 &&
         (uVar3 = __aeabi_uidiv(unaff_r8 * unaff_r11,100), unaff_r9 <= uVar3))) {
    unaff_r6 = unaff_r6 + 5;
    unaff_r5 = unaff_r5 + 1;
    unaff_r7 = (uint)*(byte *)(unaff_r4 + 0x3a);
    if (unaff_r7 <= unaff_r5) goto LAB_00007910;
    uVar2 = *unaff_r6;
    param_1 = __aeabi_uidiv(unaff_r10 * unaff_r11,100);
    unaff_r9 = (uint)uVar2;
  }
  in_stack_00000000 = in_stack_00000000 | 0x400;
LAB_00007910:
  uVar2 = *(ushort *)(in_stack_00000004 + 6);
  while( true ) {
    if (*(ushort *)(unaff_r4 + 0x38) <= unaff_r7) {
      return in_stack_00000000;
    }
    uVar1 = *unaff_r6;
    uVar3 = __aeabi_uidiv(unaff_r10 * (uint)uVar2,100);
    if ((uVar1 < uVar3) || (uVar3 = __aeabi_uidiv(unaff_r8 * (uint)uVar2,100), uVar3 < uVar1))
    break;
    unaff_r6 = unaff_r6 + 5;
    unaff_r7 = unaff_r7 + 1;
  }
  return in_stack_00000000 | 0x400;
}

