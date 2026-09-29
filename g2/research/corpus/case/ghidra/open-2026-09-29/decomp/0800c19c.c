
void FUN_0800c19c(int param_1,undefined4 param_2,int param_3)

{
  if (param_1 != 0) {
    FUN_0800bfe2(param_1,*DAT_0800c1c8 + 0x18);
    if (param_3 != 0) {
      param_2 = 0xffffffff;
    }
    FUN_0800abb0(param_2,param_3);
    return;
  }
  disableIRQinterrupts();
  do {
                    /* WARNING: Do nothing block with infinite loop */
  } while( true );
}

