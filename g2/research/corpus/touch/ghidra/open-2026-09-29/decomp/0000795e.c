
uint vector_entry_465e(void)

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
  char in_CY;
  uint in_stack_00000000;
  int in_stack_00000004;
  
  while ((in_CY != '\0' && (uVar3 = __aeabi_uidiv(unaff_r8 * unaff_r11,100), unaff_r9 <= uVar3))) {
    unaff_r6 = unaff_r6 + 5;
    unaff_r5 = unaff_r5 + 1;
    unaff_r7 = (uint)*(byte *)(unaff_r4 + 0x3a);
    if (unaff_r7 <= unaff_r5) goto LAB_00007910;
    unaff_r9 = (uint)*unaff_r6;
    uVar3 = __aeabi_uidiv(unaff_r10 * unaff_r11,100);
    in_CY = uVar3 <= unaff_r9;
  }
  in_stack_00000000 = in_stack_00000000 | 0x400;
LAB_00007910:
  uVar1 = *(ushort *)(in_stack_00000004 + 6);
  while( true ) {
    if (*(ushort *)(unaff_r4 + 0x38) <= unaff_r7) {
      return in_stack_00000000;
    }
    uVar2 = *unaff_r6;
    uVar3 = __aeabi_uidiv(unaff_r10 * (uint)uVar1,100);
    if ((uVar2 < uVar3) || (uVar3 = __aeabi_uidiv(unaff_r8 * (uint)uVar1,100), uVar3 < uVar2))
    break;
    unaff_r6 = unaff_r6 + 5;
    unaff_r7 = unaff_r7 + 1;
  }
  return in_stack_00000000 | 0x400;
}

