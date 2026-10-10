typedef unsigned U;
extern U probe_pneg(U);
static void text(char*s){while(*s)*(volatile U*)0x10003000=(unsigned char)*s++;}
static void hex(U x){int i;for(i=28;i>=0;i-=4)*(volatile U*)0x10003000="0123456789abcdef"[(x>>i)&15];}
int main(void){U product=32767u*16384u;U lane=probe_pneg(product);U scalar=0u-product;U cross=32767u*16384u;text("product=");hex(product);text(" packed-neg=");hex(lane);text(" scalar-neg=");hex(scalar);text("\n");text("packed final-sum=");hex(lane+cross);text(" scalar final-sum=");hex(scalar+cross);text("\n");return lane==0xe0014000&&scalar==0xe0004000?0:7;}
