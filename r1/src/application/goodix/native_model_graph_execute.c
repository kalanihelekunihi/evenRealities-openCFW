/* Native model graph dispatch: stock 0x2907c,0x37890,0x34194,0x6f838,
 * 0x2f7dc. REA identifies the descriptor and operator layouts; executable
 * stock/C comparisons cover the complete 1476 instruction bytes.
 * Workspace and descriptors are caller backed. Callback return statuses are
 * ignored by stock, and recurrent state resets only for reset == 1.
 * See r1/docs/reference/goodix-model-graph-execute-c-review.md.
 */
#include "native_model_graph_execute.h"
#include <stdint.h>
#include <stddef.h>
#include "native_spo2_infer_support.h"
extern void *memmove(void *,const void *,size_t);
extern void *memset(void *,int,size_t);
static uint32_t W(uintptr_t p,uint32_t o){return *(const volatile uint32_t *)(p+o);}
static void S(uintptr_t p,uint32_t o,uint32_t v){*(volatile uint32_t *)(p+o)=v;}
static uint32_t byte(uintptr_t p,uint32_t o){return *(const volatile uint8_t *)(p+o);}
static uint32_t address(void *p){return (uint32_t)(uintptr_t)p;}
typedef uint32_t (*operator_fn)(const void *,const void *,const void *);
static void run(uintptr_t model,uint32_t field,uint32_t offset,void *in,void *out)
{
 operator_fn fn=(operator_fn)(uintptr_t)W(model,field);(void)fn((void *)(model+offset),in,out);
}
static void descriptor(uintptr_t p,uint32_t rows,uint32_t columns,uint32_t element,uintptr_t data)
{
 (void)r1_goodix_native_tensor_descriptor_initialize((void *)p,1,rows,columns,element,(void *)data);
}
uint32_t r1_goodix_native_model_u8_pipeline(const void *model,const void *inputs,void *outputs,const void *configuration)
{
 uintptr_t op=(uintptr_t)model,ins=(uintptr_t)inputs,outs=(uintptr_t)outputs,cfg=(uintptr_t)configuration;uint32_t first[5],second[5];uintptr_t base=W(W(outs,0),16);
 memset(first,0,sizeof(first));memset(second,0,sizeof(second));uint32_t incoming[2]={0,W(ins,4)},outgoing[2]={0,W(outs,4)};
 descriptor((uintptr_t)first,byte(cfg,0),byte(cfg,1),1,base);incoming[0]=W(ins,0);outgoing[0]=address(first);run(op,20,0,incoming,outgoing);
 descriptor((uintptr_t)second,byte(cfg,2),byte(cfg,3),1,base+0x3e0u);incoming[1]=outgoing[1];outgoing[0]=address(second);incoming[0]=address(first);run(op,44,24,incoming,outgoing);
 descriptor((uintptr_t)first,byte(cfg,4),byte(cfg,5),1,base);incoming[1]=outgoing[1];outgoing[0]=address(first);incoming[0]=address(second);run(op,68,48,incoming,outgoing);
 uintptr_t target=W(outs,0);memmove((void *)target,first,20);return (uint32_t)target;
}
uint32_t r1_goodix_native_model_float_projection(const void *model,void *input_descriptor,void *outputs,const void *configuration)
{
 uintptr_t op=(uintptr_t)model,outs=(uintptr_t)outputs,cfg=(uintptr_t)configuration;uint32_t first[5],second[5];uintptr_t base=W(W(outs,0),16);memset(first,0,sizeof(first));memset(second,0,sizeof(second));uint32_t pointers[2]={address(first),address(second)};uint32_t incoming[3]={address(input_descriptor),(uint32_t)outs,(uint32_t)cfg};
 descriptor(pointers[0],byte(cfg,0),byte(cfg,1),4,base);run(op,20,0,incoming,&pointers[0]);
 descriptor(pointers[1],byte(cfg,2),byte(cfg,3),4,base+0x1f0u);run(op,44,24,&pointers[0],&pointers[1]);
 descriptor(pointers[0],byte(cfg,4),byte(cfg,5),4,base);run(op,68,48,&pointers[1],&pointers[0]);
 uintptr_t target=W(outs,0);memmove((void *)target,(void *)(uintptr_t)pointers[0],20);return (uint32_t)target;
}
uint32_t r1_goodix_native_model_subgraph_execute(const void *model,void *workspace,void *destination)
{
 uintptr_t op=(uintptr_t)model,work=(uintptr_t)workspace;uint32_t d0[5],cc[5],aux[5],ra[5],rb[5],bounds_a[2]={0,0},bounds_b[2]={0,0};memset(d0,0,20);memset(cc,0,20);memset(aux,0,20);memset(ra,0,20);ra[4]=address(bounds_a);
 uint32_t p0=address(d0),pc=address(cc),pa=address(aux);uint32_t in[3]={0,0,0},out[2]={0,0};
 descriptor(p0,1,125,4,work);out[0]=p0;out[1]=address(ra);run(op,8,0,&p0,out);
 descriptor(p0,1,125,1,work);bounds_a[0]=W(op,0);bounds_a[1]=W(op,4);descriptor(pc,16,125,1,work);uint32_t scalar[2]={2000,0};descriptor(pa,1,1,4,(uintptr_t)scalar);
 in[0]=p0;in[1]=address(ra);in[2]=pa;out[0]=pc;out[1]=address(ra);run(op,32,12,in,out);
 descriptor(p0,16,62,1,work);run(op,40,36,&pc,&p0);
 uint32_t config1[2]={0x3e043e04u,0x00003e10u};bounds_b[0]=0;bounds_b[1]=0;memset(rb,0,20);rb[4]=address(bounds_b);S(pc,16,(uint32_t)(work+0x3e0u));in[0]=p0;in[1]=address(ra);out[0]=pc;out[1]=address(rb);r1_goodix_native_model_u8_pipeline((void *)(op+44),in,out,config1);
 in[0]=pc;in[1]=address(rb);in[2]=p0;/* Fourth native word belongs to the second residual range. */
 uint32_t residual[4]={in[0],in[1],in[2],address(ra)};out[0]=pc;out[1]=address(ra);run(op,128,116,residual,out);
 descriptor(p0,16,31,1,work);run(op,136,132,&pc,&p0);
 uint32_t config2[2]={0x1f041f04u,0x00001f10u};in[0]=p0;in[1]=address(ra);out[0]=pc;out[1]=address(rb);r1_goodix_native_model_u8_pipeline((void *)(op+140),in,out,config2);
 residual[0]=pc;residual[1]=address(rb);residual[2]=p0;residual[3]=address(ra);out[0]=pc;out[1]=address(ra);run(op,224,212,residual,out);
 descriptor(p0,16,15,1,work);run(op,232,228,&pc,&p0);descriptor(pc,16,15,4,work+0x3e0u);in[0]=p0;in[1]=address(ra);run(op,236,236,in,&pc);
 descriptor(p0,8,15,4,work);uint32_t config3[2]={0x0f010f01u,0x00000f08u};r1_goodix_native_model_float_projection((void *)(op+264),(void *)(uintptr_t)pc,&p0,config3);
 descriptor(pa,8,15,4,work+0x1e0u);run(op,260,240,&pc,&pa);in[0]=p0;in[1]=pa;run(op,348,336,in,&p0);
 uint32_t count=W(p0,0)*W(p0,12)*W(p0,8)*W(p0,4);memmove(destination,(void *)(uintptr_t)W(p0,16),count);return 0;
}
uint32_t r1_goodix_native_model_graph_execute(const void *model,const void *unused,const void *input_buffers,const void *unused2,void *output_buffers,uint32_t unused3,uint32_t reset)
{
 (void)unused;(void)unused2;(void)unused3;uintptr_t op=(uintptr_t)model,ins=(uintptr_t)input_buffers,outs=(uintptr_t)output_buffers,work=W(ins,4),other=work+0x3e0u;
 r1_goodix_native_model_subgraph_execute((void *)(op+356),(void *)work,(void *)work);
 uint32_t a[5],b[5],c[5];memset(a,0,20);memset(b,0,20);memset(c,0,20);uint32_t pa=address(a),pb=address(b),pc=address(c);
 descriptor(pa,120,1,4,work);descriptor(pb,W(op,708),1,4,other);run(op,728,708,&pa,&pb);
 descriptor(pa,W(op,732),1,4,work);run(op,752,732,&pb,&pa);descriptor(pb,W(op,732),1,4,other);run(op,756,756,&pa,&pb);
 memmove((void *)(uintptr_t)(W(ins,4)+0x8b8u),(void *)(uintptr_t)W(pb,16),W(pb,0)*W(pb,12)*W(pb,8)*W(pb,4));memmove((void *)(uintptr_t)W(ins,4),(void *)(uintptr_t)W(ins,0),500);
 uintptr_t current=W(ins,4);r1_goodix_native_model_subgraph_execute((void *)(op+4),(void *)current,(void *)current);
 descriptor(pa,120,1,4,current);descriptor(pb,3,1,4,W(ins,4)+0x8b8u);descriptor(pc,123,1,4,other);uint32_t concat[2]={pa,pb};run(op,760,760,concat,&pc);
 if(reset==1)memset((void *)(uintptr_t)W(op,768),0,W(op,764)*4u);
 memmove((void *)work,(void *)other,492);descriptor(pa,123,1,4,work);descriptor(pb,W(op,764),1,4,work+0x7c0u);run(op,784,764,&pa,&pb);
 descriptor(pa,W(op,788),1,4,work);run(op,808,788,&pb,&pa);descriptor(pb,W(op,812),1,4,other);run(op,832,812,&pa,&pb);
 memmove((void *)(uintptr_t)W(outs,0),(void *)(uintptr_t)W(pb,16),W(pb,0)*W(pb,12)*W(pb,8)*W(pb,4));return 0;
}
uint32_t r1_goodix_native_model_graph_execute_veneer(const void *model,const void *unused,const void *input_buffers,const void *unused2,void *output_buffers,uint32_t unused3,uint32_t reset)
{
 return r1_goodix_native_model_graph_execute(model,unused,input_buffers,unused2,output_buffers,unused3,reset);
}
