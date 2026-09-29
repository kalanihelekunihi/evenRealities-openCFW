
/* WARNING: Control flow encountered bad instruction data */

void gx8002_padmux_defaults(void)

{
  uint unaff_r4;
  uint unaff_r8;
  
  stub();
  if (unaff_r8 < (unaff_r4 & unaff_r8)) {
                    /* WARNING: Bad instruction - Truncating control flow here */
    halt_baddata();
  }
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}

