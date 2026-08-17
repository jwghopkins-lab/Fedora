import math, itertools

# Approximate coordinates. ALL NEED FIELD/SOURCE VERIFICATION.
P = {
 "GREENWICH  (Observatory gate standards)": (51.47790, -0.00140),
 "TRAFALGAR  (north terrace standards)":    (51.50850, -0.12810),
 "GUILDHALL  (Great Hall standards)":       (51.51550, -0.09220),
 "WESTMINSTER(Parliamentary Copy in wall)": (51.49950, -0.12470),
}

lat0 = sum(v[0] for v in P.values())/len(P)
mPerDegLat = 111132.0
mPerDegLon = 111320.0*math.cos(math.radians(lat0))

def xy(p):  return ((p[1])*mPerDegLon, (p[0])*mPerDegLat)
def ll(x,y): return (y/mPerDegLat, x/mPerDegLon)

def inter(a,b,c,d):
    (x1,y1),(x2,y2),(x3,y3),(x4,y4) = xy(a),xy(b),xy(c),xy(d)
    den = (x1-x2)*(y3-y4)-(y1-y2)*(x3-x4)
    if abs(den) < 1e-9: return None,None,None
    t = ((x1-x3)*(y3-y4)-(y1-y3)*(x3-x4))/den
    u = ((x1-x3)*(y1-y2)-(y1-y3)*(x1-x2))/den
    px,py = x1+t*(x2-x1), y1+t*(y2-y1)
    return ll(px,py), t, u

names = list(P)
print("=== the four sites ===")
for n in names: print(f"  {n:44s} {P[n][0]:.5f}, {P[n][1]:.5f}")

print("\n=== all 3 pairs of non-adjacent lines (each uses all four points once) ===")
for (a,b) in itertools.combinations(range(4),2):
    c,d = [i for i in range(4) if i not in (a,b)]
    pt,t,u = inter(P[names[a]],P[names[b]],P[names[c]],P[names[d]])
    inside = (0 <= t <= 1) and (0 <= u <= 1)
    print(f"\n  {names[a].split('(')[0].strip()} -- {names[b].split('(')[0].strip()}")
    print(f"  x {names[c].split('(')[0].strip()} -- {names[d].split('(')[0].strip()}")
    print(f"     crossing  {pt[0]:.5f}, {pt[1]:.5f}     "
          f"{'BETWEEN both pairs' if inside else 'outside the segments (extended lines only)'}")
