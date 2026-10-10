typedef unsigned U;
extern U probe_mulaca(U,U,U),probe_mulacax(U,U,U);
static void text(char*s){while(*s)*(volatile U*)0x10003000=(unsigned char)*s++;}
static void hex(U x){int i;for(i=28;i>=0;i-=4)*(volatile U*)0x10003000="0123456789abcdef"[(x>>i)&15];}
int main(void){U z[]={0,0xffffffff,0x80000000},want[]={0x7fffffff,0x7fffffff,0};unsigned i;for(i=0;i<3;i++){text("z=");hex(z[i]);text(" manual=");hex(want[i]);text(" mulaca=");hex(probe_mulaca(0x80008000,0x80008000,z[i]));text(" mulacax=");hex(probe_mulacax(0x80008000,0x80008000,z[i]));text("\n");}text("EXPECTED MODEL DISCREPANCY; not hardware validation\n");return 0;}
