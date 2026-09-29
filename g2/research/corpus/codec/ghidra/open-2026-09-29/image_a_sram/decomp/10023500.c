
void gx8002_reset_entry(undefined4 param_1,uint param_2)

{
  gx8002_system_initialize(uRam10023520,param_2 & 0xfffffff7);
  gx8002_main();
  do {
                    /* WARNING: Do nothing block with infinite loop */
  } while( true );
}

