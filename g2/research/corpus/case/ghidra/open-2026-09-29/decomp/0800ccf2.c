
int FUN_0800ccf2(undefined4 param_1)

{
  int in_stack_00000004;
  
  if (in_stack_00000004 != 0) {
    *(undefined1 *)(in_stack_00000004 + 0x28) = 2;
    FUN_0800af30(param_1);
    return in_stack_00000004;
  }
  disableIRQinterrupts();
  do {
                    /* WARNING: Do nothing block with infinite loop */
  } while( true );
}

