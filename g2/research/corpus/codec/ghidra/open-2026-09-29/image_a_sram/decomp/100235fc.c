
void trap(void)

{
  undefined4 *puVar1;
  int iVar2;
  int iVar3;
  undefined4 *puVar4;
  undefined4 in_r13;
  int iVar5;
  undefined4 unaff_retaddr;
  
  do {
    *(undefined4 *)((int)register0x00000038 + -4) = in_r13;
    *piRam10023644 = (int)register0x00000038;
    iVar2 = iRam10023648;
    register0x00000038 = (BADSPACEBASE *)(iRam10023648 + -0x48);
    puVar4 = (undefined4 *)(iRam10023648 + -0x48);
    iVar5 = iRam10023648 + -0x48;
    for (puVar1 = (undefined4 *)0x0; puVar1 < (undefined4 *)0x31; puVar1 = puVar1 + 1) {
      *puVar4 = *puVar1;
      puVar4 = puVar4 + 1;
    }
    iVar3 = *piRam10023644;
    *(int *)(iVar2 + -0x10) = iVar3;
    puVar4 = (undefined4 *)(iVar3 + -4);
    in_r13 = *puVar4;
    *(undefined4 *)(iVar2 + -0x14) = in_r13;
    *(undefined4 *)(iVar2 + -0xc) = unaff_retaddr;
    *(undefined4 **)(iVar2 + -8) = puVar4;
    *(undefined4 **)(iVar2 + -4) = puVar4;
    unaff_retaddr = 0x10023640;
    trap_c(iVar5);
  } while( true );
}

