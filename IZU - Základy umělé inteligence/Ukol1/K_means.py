

# -*- coding: utf-8 -*-
"""
Created on Sat Feb 15 12:19:23 2020

@author: pat4444
"""
import math



souradnice=[ [0,1,4], [-1,1,3], [-1,-1,3], [1,0,4], [4,0,0], [5,1,1], [5,-1,-1], [6,0,0], [1,4,0], [2,3,1], [0,4,2], [-1,5,1] ]

stredobody = [ [-3,-1,-3], [1,2,-4], [1,0,-3] ]

#stredobody = [[-3,-1,-3], [-1,-1,1], [-1,1,-4]]
#stredobody = [ [0,-1,-2], [1,0,-3], [-3,4,1] ]

prumery = []
i = 0
while True:
    shluk1 = []
    shluk2 = []
    shluk3 = []
    print("ITERATION:",i)
    if prumery:
        print("MEANS:",prumery)
    
    for bod in souradnice:
        vzdalenosti = []
        a = math.sqrt((bod[0]-stredobody[0][0])**2 + (bod[1]-stredobody[0][1])**2 + (bod[2]-stredobody[0][2])**2)
        b = math.sqrt((bod[0]-stredobody[1][0])**2 + (bod[1]-stredobody[1][1])**2 + (bod[2]-stredobody[1][2])**2)
        c = math.sqrt((bod[0]-stredobody[2][0])**2 + (bod[1]-stredobody[2][1])**2 + (bod[2]-stredobody[2][2])**2)
        
        vzdalenosti.append(a)
        vzdalenosti.append(b)
        vzdalenosti.append(c)
        vzdalenosti.sort()
        
        if a == b or a == c or b == c:
            if a == b:
                if len(shluk1) > len(shluk2):
                    shluk1.append(bod)
                else:
                    shluk2.append(bod)
            elif a == c:
                if len(shluk1) > len(shluk3):
                    shluk1.append(bod)
                else:
                    shluk3.append(bod)
            else:
                if len(shluk2) > len(shluk3):
                    shluk2.append(bod)
                else:
                    shluk3.append(bod)
        
        
        if vzdalenosti[0] == a:
            shluk1.append(bod)
        elif vzdalenosti[0] == b:
            shluk2.append(bod)
        else:
            shluk3.append(bod)
             
    
    print("CLUSTER1:",shluk1)
    print("CLUSTER2:",shluk2)
    print("CLUSTER3:",shluk3)
    print("--------------------------------------------------------")
    
    x = 0
    y = 0
    z = 0
    
    shl1_prum = []
    shl2_prum = []
    shl3_prum = []
    
    for bod in shluk1:    
        x = bod[0] + x
        y = bod[1] + y
        z = bod[2] + z
    if len(shluk1) == 0:
        shl1_prum = stredobody[0]
    else:
        shl1_prum = [x/len(shluk1), y/len(shluk1), z/len(shluk1)]
    
    x = 0
    y = 0
    z = 0
    
    for bod in shluk2:    
        x = bod[0] + x
        y = bod[1] + y
        z = bod[2] + z
             
    shl2_prum = [x/len(shluk2), y/len(shluk2), z/len(shluk2)]
    
    x = 0
    y = 0
    z = 0
    
    for bod in shluk3:    
        x = bod[0] + x
        y = bod[1] + y
        z = bod[2] + z
             
    shl3_prum = [x/len(shluk3), y/len(shluk3), z/len(shluk3)]
        
    prumery = [shl1_prum, shl2_prum, shl3_prum]
    if shl1_prum == stredobody[0] and shl2_prum == stredobody[1] and shl3_prum == stredobody[2] or i == 30:
        break
    
    stredobody = prumery
    i = i +1
    
    
    
    

    