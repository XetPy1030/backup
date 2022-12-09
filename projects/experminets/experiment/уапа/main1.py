def top3(st):
    symbs = {}
    for i in st:
        symbs[i] = symbs.get(i, 0) + 1
    
    symbs = sorted(symbs.items(), key=lambda x: x[1], reverse=True)
    
    return symbs[:3]

print(top3("elsjfhkeushfuisefhiefys"))