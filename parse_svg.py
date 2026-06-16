import re, numpy as np
def load_paths(svgfile='_t.svg'):
    body=open(svgfile).read().split("</defs>")[-1]
    tags=re.findall(r'<path\b[^>]*>',body)
    def ptf(s):
        m=re.search(r'transform="([^"]+)"',s)
        if not m: return np.eye(3)
        T=np.eye(3)
        for fn,args in re.findall(r'(\w+)\(([^)]*)\)',m.group(1)):
            v=[float(x) for x in re.split(r'[ ,]+',args.strip())]; M=np.eye(3)
            if fn=='matrix': M=np.array([[v[0],v[2],v[4]],[v[1],v[3],v[5]],[0,0,1]])
            elif fn=='translate': M[0,2]=v[0]; M[1,2]=v[1] if len(v)>1 else 0
            elif fn=='scale': M[0,0]=v[0]; M[1,1]=v[1] if len(v)>1 else v[0]
            T=T@M
        return T
    def pd(d):
        toks=re.findall(r'[MLCZmlczHVhv]|-?\d*\.?\d+(?:e-?\d+)?',d)
        pts=[];subs=[];i=0;cur=None;cmd=None
        while i<len(toks):
            t=toks[i]
            if t in 'MLCZHVmlczhv': cmd=t;i+=1
            if cmd in('M','L'):
                x,y=float(toks[i]),float(toks[i+1]);i+=2;cur=(x,y);pts.append(cur)
                if cmd=='M':
                    if pts[:-1]: subs.append(pts[:-1])
                    pts=[cur]
            elif cmd=='C':
                p0=cur;c1=(float(toks[i]),float(toks[i+1]));c2=(float(toks[i+2]),float(toks[i+3]));p1=(float(toks[i+4]),float(toks[i+5]));i+=6
                for tt in np.linspace(0,1,9)[1:]:
                    x=(1-tt)**3*p0[0]+3*(1-tt)**2*tt*c1[0]+3*(1-tt)*tt**2*c2[0]+tt**3*p1[0]
                    y=(1-tt)**3*p0[1]+3*(1-tt)**2*tt*c1[1]+3*(1-tt)*tt**2*c2[1]+tt**3*p1[1]
                    pts.append((x,y))
                cur=p1
            else: i+=1
        if pts: subs.append(pts)
        return subs
    out=[]
    for tg in tags:
        if 'stroke=' not in tg or 'stroke="none"' in tg: continue
        dm=re.search(r'\bd="([^"]+)"',tg)
        if not dm: continue
        cm=re.search(r'stroke="rgb\(([^)]+)\)"',tg); col=cm.group(1) if cm else "?"
        T=ptf(tg)
        for sub in pd(dm.group(1)):
            if len(sub)<2: continue
            P=np.array(sub); Ph=np.c_[P,np.ones(len(P))]@T.T
            out.append((col,Ph[:,:2]))
    return out
def fit_circle(P):
    xs,ys=P[:,0],P[:,1]; A=np.c_[2*xs,2*ys,np.ones(len(xs))]; b=xs**2+ys**2
    c,*_=np.linalg.lstsq(A,b,rcond=None); cx,cy=c[0],c[1]
    return cx,cy,np.sqrt(c[2]+cx**2+cy**2)
