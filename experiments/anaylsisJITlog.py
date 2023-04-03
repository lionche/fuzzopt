for name in ['jitfunfuzz','montage','comfort', 'die', 'fuzzilli', 'codealchemist']:
# for name in ['montage', 'die', 'fuzzilli', 'codealchemist']:
    jitcount = 0
    endcount = 0

    with open(f'{name}.log', 'r') as f:
        for line in f:
            if 'completed compiling' in line:
                jitcount += 1
            if '<|end|>' in line:
                endcount += 1

    print(f'{name} jit count {jitcount} ')
    print(f'{name} pass count {endcount}')
