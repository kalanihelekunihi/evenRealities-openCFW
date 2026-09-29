
undefined4 FUN_0800ca06(undefined4 param_1)

{
  int in_stack_00000004;
  int in_stack_00000008;
  undefined4 local_18;
  
  if (in_stack_00000004 == 0) {
    disableIRQinterrupts();
    do {
                    /* WARNING: Do nothing block with infinite loop */
    } while( true );
  }
  if (in_stack_00000008 != 0) {
    *(int *)(in_stack_00000008 + 0x30) = in_stack_00000004;
    *(undefined1 *)(in_stack_00000008 + 0x59) = 2;
    FUN_0800ae96(param_1);
    FUN_0800ac08(in_stack_00000008);
    return local_18;
  }
  disableIRQinterrupts();
  do {
                    /* WARNING: Do nothing block with infinite loop */
  } while( true );
}

