typedef unsigned U;
extern U probe_paddh(U,U),probe_paddsat(U,U),probe_pabs(U),probe_pmax(U,U),probe_mulca(U,U),probe_mulcax(U,U),probe_mulaca(U,U,U),probe_mulacax(U,U,U);
static void out(char c){*(volatile U*)0x10003000=(unsigned char)c;}
static void text(char*s){while(*s)out(*s++);}
static void hex(U x){int i;for(i=28;i>=0;i-=4)out("0123456789abcdef"[(x>>i)&15]);}
static int test(char*n,U x,U want){text(n);out(' ');hex(x);text(" expected ");hex(want);out('\n');return x!=want;}
int main(void){int errors=0;U ca,cax,aca,acax;
text("ISA START\n");errors+=test("paddh-negative-odd",probe_paddh(0xfffd0007,0x00020004),0xffff0005);
errors+=test("paddsat",probe_paddsat(0x7fff8000,0x0001ffff),0x7fff8000);
errors+=test("pabs-min",probe_pabs(0x80000001),0x7fff0001);
errors+=test("pmax-unsigned-lanes",probe_pmax(0xffff0001,0x00027fff),0xffff7fff);
errors+=test("mulca-unequal-lanes",probe_mulca(0x00020003,0x00040005),23);
errors+=test("mulcax-unequal-lanes",probe_mulcax(0x00020003,0x00040005),22);
errors+=test("mulaca-saturate",probe_mulaca(0x00010001,0x00010001,0x7fffffff),0x7fffffff);
ca=probe_mulca(0x80008000,0x80008000);cax=probe_mulcax(0x80008000,0x80008000);aca=probe_mulaca(0x80008000,0x80008000,0);acax=probe_mulacax(0x80008000,0x80008000,0);
text("CORNER mulca=");hex(ca);text(" mulcax=");hex(cax);text(" mulaca=");hex(aca);text(" mulacax=");hex(acax);out('\n');
text(errors?"ISA baseline FAIL\n":"ISA baseline PASS; corner remains ISA-unverified\n");return errors?4:0;}
