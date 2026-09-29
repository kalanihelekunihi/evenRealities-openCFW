
/* WARNING: Control flow encountered bad instruction data */

void FUN_1000f824(int param_1,undefined4 param_2,ushort *param_3)

{
  undefined4 *puVar1;
  undefined4 uVar2;
  undefined4 *puVar3;
  
  puVar1 = (undefined4 *)((uint)(param_3[1] >> 1) + param_1);
  puVar3 = (undefined4 *)((uint)(*param_3 >> 1) + param_1);
  uVar2 = *puVar3;
  *puVar3 = *puVar1;
  *puVar1 = uVar2;
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}

