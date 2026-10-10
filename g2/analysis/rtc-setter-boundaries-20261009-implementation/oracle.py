FIELDS=['read_error','weekday','century','year','month','day','hour','minute','second','hundredths']
def oracle(t,control):
    valid=(t['hundredths']<=99 and t['second']<60 and t['minute']<60 and t['hour']<24 and 1<=t['day']<=31 and 1<=t['month']<=12 and t['year']<=100 and t['weekday']<=6)
    if not valid:return {'status':1,'writes':[]}
    bcd=lambda v:((v//10)<<4)|(v%10)
    low=((bcd(t['hour'])&63)<<24)|((bcd(t['minute'])&127)<<16)|((bcd(t['second'])&127)<<8)|(bcd(t['hundredths'])&255)
    upper=((t['century']&1)<<28)|((t['weekday']&7)<<24)|((bcd(t['year'])&255)<<16)|((bcd(t['month'])&31)<<8)|(bcd(t['day'])&63)
    return {'status':0,'writes':[[0x40004800,control|1],[0x40004820,low],[0x40004824,upper],[0x40004800,control&0xfffffffe]]}
seed=dict(zip(FIELDS,[0,1,0,24,1,1,12,34,56,78]))
fixtures=[]
for field,values in [('hundredths',[99,100]),('second',[59,60]),('minute',[59,60]),('hour',[23,24]),('day',[0,31,32]),('month',[0,12,13]),('year',[99,100,101]),('century',[1,2,0xffffffff]),('read_error',[0xffffffff])]:
    for value in values:
        t=dict(seed);t[field]=value
        fixtures.append({'name':field+'_'+str(value),'time':t,'control':0xa5a50010,'expected':oracle(t,0xa5a50010),'novelty':'boundary not present in inspected weekday-focused prior producer tests'})
t=dict(seed,month=2,day=31);fixtures.append({'name':'february31_software_acceptance','time':t,'control':0xa5a50011,'expected':oracle(t,0xa5a50011),'novelty':'calendar consistency absent from validator; WRTC initially set'})

if __name__ == "__main__":
    import json
    print(json.dumps(fixtures,indent=2))
