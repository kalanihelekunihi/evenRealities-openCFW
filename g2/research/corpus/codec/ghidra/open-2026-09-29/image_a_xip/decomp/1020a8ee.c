
/* WARNING: Control flow encountered bad instruction data */

void gx8002_pga_corrections(int param_1,int param_2,undefined4 param_3,uint param_4)

{
  uint unaff_r4;
  uint in_r12;
  uint in_r13;
  byte in_psr;
  int iStack00000008;
  int iStack0000000c;
  uint uStack00000010;
  
  if (!(bool)(in_psr & 1)) {
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
  uStack00000010 = param_4 >> (in_r13 & 0x3f);
  if (!(bool)(in_psr & 1)) {
    uStack00000010 = unaff_r4;
  }
  iStack0000000c = param_1 << (in_r12 & 0x3f);
  if (!(bool)(in_psr & 1)) {
    iStack0000000c = param_2;
  }
  iStack00000008 = 0x3c - in_r12;
  gx8002_pack_double();
  return;
}

