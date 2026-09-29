
uint vector_entry_4674(void)

{
  ushort uVar1;
  ushort uVar2;
  uint uVar3;
  int unaff_r4;
  uint unaff_r5;
  ushort *unaff_r6;
  uint uVar4;
  int unaff_r8;
  int unaff_r10;
  int unaff_r11;
  uint in_stack_00000000;
  int in_stack_00000004;
  
  do {
    uVar4 = (uint)*(byte *)(unaff_r4 + 0x3a);
    if (uVar4 <= unaff_r5) {
LAB_00007910:
      uVar2 = *(ushort *)(in_stack_00000004 + 6);
      while( true ) {
        if (*(ushort *)(unaff_r4 + 0x38) <= uVar4) {
          return in_stack_00000000;
        }
        uVar1 = *unaff_r6;
        uVar3 = __aeabi_uidiv(unaff_r10 * (uint)uVar2,100);
        if ((uVar1 < uVar3) || (uVar3 = __aeabi_uidiv(unaff_r8 * (uint)uVar2,100), uVar3 < uVar1))
        break;
        unaff_r6 = unaff_r6 + 5;
        uVar4 = uVar4 + 1;
      }
      return in_stack_00000000 | 0x400;
    }
    uVar2 = *unaff_r6;
    uVar3 = __aeabi_uidiv(unaff_r10 * unaff_r11,100);
    if ((uVar2 < uVar3) || (uVar3 = __aeabi_uidiv(unaff_r8 * unaff_r11,100), uVar3 < uVar2)) {
      in_stack_00000000 = in_stack_00000000 | 0x400;
      goto LAB_00007910;
    }
    unaff_r6 = unaff_r6 + 5;
    unaff_r5 = unaff_r5 + 1;
  } while( true );
}

