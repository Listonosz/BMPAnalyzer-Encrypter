import time
import os
import math
from random import randint

PRIME_8BIT = 100001449
E_DEFAULT = pow(2,16)+1

def testPrime(n) : 
#Odcinamy przypadki:
#i*i <= n Bo liczby wieksze od sqrt(n) musza byc iloczynem mniejszych juz sprawdzonych
#Dla kazdej wiekszej znalezionej liczby przypadek mod 2 i 3 sprawdzamy oddzielnie

    if (n <= 1) : 
        return False
    if (n <= 3) : 
        return True

    if (n % 2 == 0 or n % 3 == 0) : 
        return False
  
    i = 5
    while(i * i <= n) : 
        if (n % i == 0 or n % (i + 2) == 0) :
            return False
        i = i + 6
    return True

def findLowerPrime(n):
    while n >= 2:
        n -= 1
        if testPrime(n):
            return n

def findHigherPrime(n):
    while n < math.inf:
        n += 1
        if testPrime(n):
            return n

def NWW(a,b):
    if a > b:
        G = a
    else:
        G = b
    while(True):
        if((G % a == 0) and (G % b == 0)):
            res = G
            break
        G += 1
    return res

def NWD(a,b):
    return math.gcd(a,b)

def NWW(a,b):
    return a*b // NWD(a,b)

def ModularInverse(a, n):
    t = 0
    r = n
    newT = 1
    newR = a
    while newR != 0:
        quotient = int(r/newR)
        tmp = newR
        newR = r - int(quotient*newR)
        r = tmp
        tmp = newT
        newT = t - int(quotient*newT)
        t = tmp
    if r > 1:
        return "-1"
    if t < 0:
        t = t + n
    return t

def ModularPow(base,exp,mod):
    if mod == 1:
        return 0
    c = 1
    for ePrim in range(0,exp):
        c = (c * base) % mod
    return c

def encryptM(m, publicKey):
    n = publicKey[0]
    e = publicKey[1]
    # c = ModularPow(m,e,n)
    c = pow(m,e,n)
    return c

def decryptC(c, privateKey):
    n = int(privateKey[0])
    d = int(privateKey[1])
    # m = ModularPow(c,d,n)
    m = pow(c,d,n)
    return m

def randomPQ(maxPbitslen):
    maxBound = int(''.join(["1" for i in range(maxPbitslen)]),2)
    lowBound = int(maxBound/100)
    pRand = randint(lowBound,maxBound)
    p =findLowerPrime(pRand)
    qRand = randint(int(lowBound/100),int(maxBound/10))
    q = findLowerPrime(qRand)
    return p,q

def generatePrivateKey(p,q,e_=E_DEFAULT):
    n = p*q
    lam = NWW(p-1,q-1)
    e = e_
    d = ModularInverse(e, lam)
    return [n,d]


def generatePublicKey(p,q,e=E_DEFAULT):
    n = p*q
    return [n,e]

p,q = randomPQ(24)
public = generatePublicKey(p,q)
private = generatePrivateKey(p,q)

mIn = 2987987

start = time.clock()

c = encryptM(mIn, public)
mOut = decryptC(c, private)

end = time.clock()
time = end-start
print("P:",p, "Q:",q,"PUB:",public,"PRIV:",private)
print("INPUT: ", mIn)
print("CRYPTED: ", c)
print("OUTPUT: ", mOut, "Computed in time:",time)

