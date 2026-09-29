
void FUN_00514f60(int param_1,undefined4 *param_2)

{
  undefined4 *puVar1;
  undefined4 *puVar2;
  
  if (param_1 != 0) {
    if (param_2 != (undefined4 *)0x0) {
      puVar2 = (undefined4 *)(param_1 + 0x60);
      do {
        *puVar2 = *param_2;
        puVar2[1] = param_2[1];
        puVar1 = param_2 + 2;
        param_2 = param_2 + 3;
        puVar2[2] = *puVar1;
        puVar2 = puVar2 + 3;
        loopEnd();
      } while( true );
    }
    *(uint *)(param_1 + 0x84) = *(uint *)(param_1 + 0x84) & 0xfffffffe;
  }
  FUN_0051565c(1);
  return;
}

