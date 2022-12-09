def shortener(st):
    st = list(st)
    skobki = 0
    for ii in range(len(st)):
        i = st[ii]
        if i == '(':
            skobki += 1
        elif i == ')':
            skobki -= 1
            st[ii] = ''
        
        if skobki>0:
            st[ii] = ''
    return ''.join(st)

print(shortener("dwawdwad(wwwwwwwwwwwwwwwwwwwwda(awd)ad) wadwad (wad) wad"))