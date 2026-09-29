
/* WARNING: Control flow encountered bad instruction data */
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void gx8002_app_core_ops(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4
                        )

{
  int iVar1;
  int unaff_r6;
  
  *(undefined4 *)(unaff_r6 + 0x24) = param_3;
  iVar1 = *(int *)(iRam10026d44 + 0x70);
  *(uint *)(unaff_r6 + 0x50) = (uint)*(ushort *)(unaff_r6 + 0x18);
  *(undefined4 *)(*(ushort *)(iVar1 + 0x18) + 0x14) = param_4;
  stub();
  stub();
  stub();
  stub();
  stub();
  stub();
  stub();
  stub();
  stub();
  stub();
  stub();
  stub();
  stub();
  stub();
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}

