def camel(st):
    st = list(st)
    is_upper = True
    for i in range(len(st)):
        if st[i].lower() == st[i].upper():
            continue
        if is_upper:
            st[i] = st[i].upper()
        else:
            st[i] = st[i].lower()
        is_upper = not is_upper
    return "".join(st)

print(camel("wadwad"))