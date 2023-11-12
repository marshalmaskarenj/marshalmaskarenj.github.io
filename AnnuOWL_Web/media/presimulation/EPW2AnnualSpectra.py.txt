import math
import csv 
import operator
import numpy as np
#from time import process_time as ptm
import tkinter as tk
from tkinter import filedialog
import os
# import System

def openEPW_loc():
    rows = []
    with open(epwFile, 'r') as csvfile:
        csvreader = csv.reader(csvfile)
        for row in csvreader:
            rows.append(row)
    for row in rows[0:1]:
        name = row[1]
        latitude = row[6]
        longitude=row[7]
        timeZone=row[8]
        elevation=row[9]
    return name, latitude, longitude, timeZone, elevation

def SunPos(latitude,longitude,timeZone,hour,DOY):
    phi=float(latitude)
    longitude=float(longitude)
    UTC=float(timeZone)
    HOD=float(hour)
    DOY=float(DOY)
    delta=(-23.45)*math.cos(math.radians((360/365)*(DOY+10)))
    delta_rad=math.radians(delta)
    phi_rad=math.radians(phi)
    B_val=math.radians((DOY-81)*(360/365))
    EoT=(9.87*math.sin(2*B_val))-(7.53*math.cos(B_val))-(1.5*math.sin(B_val))
    LSTM=15*(UTC)
    TC_factor=4*(longitude-LSTM)+EoT
    LST=float(HOD)+(TC_factor/60)
    HRA=15*(LST-12)
    HRA_rad=math.radians(HRA)
    alpha=math.asin((math.sin(delta_rad)*math.sin(phi_rad))+(math.cos(delta_rad)*math.cos(phi_rad)*math.cos(HRA_rad)))
    sunAltitude=math.degrees(alpha)
    azimuth=math.acos(((math.sin(delta_rad)*math.cos(phi_rad))-(math.cos(delta_rad)*math.sin(phi_rad)*math.cos(HRA_rad)))/(math.cos(alpha)))
    az_deg=math.degrees(azimuth)
    if HRA<0:
        sunAzimuth=az_deg
    else:
        sunAzimuth=360-az_deg
    sunAltitude=round(sunAltitude,2)
    sunAzimuth=round(sunAzimuth,2)
    return sunAltitude, sunAzimuth

def openEPW(HOY,output_index):
    rows = []
    output_index= int(output_index)-1
    hour_of_year= int(HOY)+7
    with open(epwFile, 'r') as csvfile:
        csvreader = csv.reader(csvfile)
        for row in csvreader:
            rows.append(row)
    for row in rows[hour_of_year:hour_of_year+1]:
        data = row[output_index]
    return data

def fn_eps(Dh,I,Z): #sky clearness function, Dh (or E_ed) is Horizontal Diffuse Radiation, I (or E_es) is Direct Normal Radiation, Z is solar zenith angle (degrees)
    k=1.041
    if Dh==0:
        Dh=Dh+0.0000001
    clr=(((Dh+I)/Dh)+(k*Z*Z*Z))/(1+(k*Z*Z*Z))
    return clr

def fn_del(m,E_ed,E_es0): # Perez sky brightness, m is optical air mass, E_ed (or Dh) is Horizontal Difuse Radiation, and E_es0 is normal incident extraterrestrial irradiance
    if E_es0==0:
        E_es0=0.1
    delta=m*E_ed/E_es0
    return delta

def fn_a1(eps):
    if eps<1.065:
        a1=1.3525
    elif 1.065<eps<1.230:
        a1=-1.2219
    elif 1.230<eps<1.5:
        a1=-1.1
    elif 1.5<eps<1.95:
        a1=-0.5484
    elif 1.95<eps<2.8:
        a1=-0.6
    elif 2.8<eps<4.5:
        a1=-1.0156
    elif 4.5<eps<6.2:
        a1=-1
    else:
        a1=-1.05
    return a1

def fn_a2(eps):
    if eps<1.065:
        a2= -0.2576
    elif 1.065<eps<1.230:
        a2= -0.7730
    elif 1.230<eps<1.5:
        a2= -0.2515
    elif 1.5<eps<1.95:
        a2= -0.6654
    elif 1.95<eps<2.8:
        a2= -0.3566
    elif 2.8<eps<4.5:
        a2= -0.3670
    elif 4.5<eps<6.2:
        a2= 0.0211
    else:
        a2= 0.0289
    return a2

def fn_a3(eps):
    if eps<1.065:
        a3= -0.2690
    elif 1.065<eps<1.230:
        a3= 1.4148
    elif 1.230<eps<1.5:
        a3= 0.8952
    elif 1.5<eps<1.95:
        a3= -0.2672
    elif 1.95<eps<2.8:
        a3= -2.5000
    elif 2.8<eps<4.5:
        a3= 1.0078
    elif 4.5<eps<6.2:
        a3= 0.5025
    else:
        a3= 0.4260
    return a3

def fn_a4(eps):
    if eps<1.065:
        a4= -1.4366
    elif 1.065<eps<1.230:
        a4= 1.1016
    elif 1.230<eps<1.5:
        a4= 0.0156
    elif 1.5<eps<1.95:
        a4= 0.7117
    elif 1.95<eps<2.8:
        a4= 2.3250
    elif 2.8<eps<4.5:
        a4= 1.4051
    elif 4.5<eps<6.2:
        a4= -0.5119
    else:
        a4= 0.3590
    return a4

def fn_b1(eps):
    if eps<1.065:
        b1= -0.7670
    elif 1.065<eps<1.230:
        b1= -0.2054
    elif 1.230<eps<1.5:
        b1= 0.2782
    elif 1.5<eps<1.95:
        b1= 0.7234
    elif 1.95<eps<2.8:
        b1= 0.2937
    elif 2.8<eps<4.5:
        b1= 0.2875
    elif 4.5<eps<6.2:
        b1= -0.3000
    else:
        b1= -0.3250
    return b1

def fn_b2(eps):
    if eps<1.065:
        b2= 0.0007
    elif 1.065<eps<1.230:
        b2= 0.0367
    elif 1.230<eps<1.5:
        b2= -0.1812
    elif 1.5<eps<1.95:
        b2= -0.6219
    elif 1.95<eps<2.8:
        b2= 0.0496
    elif 2.8<eps<4.5:
        b2= -0.5328
    elif 4.5<eps<6.2:
        b2= 0.1922
    else:
        b2= 0.1156
    return b2

def fn_b3(eps):
    if eps<1.065:
        b3= 1.2734
    elif 1.065<eps<1.230:
        b3= -3.9128
    elif 1.230<eps<1.5:
        b3= -4.5000
    elif 1.5<eps<1.95:
        b3= -5.6812
    elif 1.95<eps<2.8:
        b3= -5.6812
    elif 2.8<eps<4.5:
        b3= -3.8500
    elif 4.5<eps<6.2:
        b3= 0.7023
    else:
        b3= 0.7781
    return b3

def fn_b4(eps):
    if eps<1.065:
        b4= -0.1233
    elif 1.065<eps<1.230:
        b4= 0.9156
    elif 1.230<eps<1.5:
        b4= 1.1766
    elif 1.5<eps<1.95:
        b4= 2.6297
    elif 1.95<eps<2.8:
        b4= 1.8415
    elif 2.8<eps<4.5:
        b4= 3.3750
    elif 4.5<eps<6.2:
        b4= -1.6317
    else:
        b4= 0.0025
    return b4

def fn_c1(eps):
    if eps<1.065:
        c1= 2.8000
    elif 1.065<eps<1.230:
        c1= 6.9750
    elif 1.230<eps<1.5:
        c1= 24.7219
    elif 1.5<eps<1.95:
        c1= 33.3389
    elif 1.95<eps<2.8:
        c1= 21.0000
    elif 2.8<eps<4.5:
        c1= 14.0000
    elif 4.5<eps<6.2:
        c1= 19.0000
    else:
        c1= 31.0625
    return c1

def fn_c2(eps):
    if eps<1.065:
        c2= 0.6004
    elif 1.065<eps<1.230:
        c2= 0.1774
    elif 1.230<eps<1.5:
        c2= -13.0812
    elif 1.5<eps<1.95:
        c2= -18.3000
    elif 1.95<eps<2.8:
        c2= -4.7656
    elif 2.8<eps<4.5:
        c2= -0.9999
    elif 4.5<eps<6.2:
        c2= -5.0000
    else:
        c2= -14.5000
    return c2

def fn_c3(eps):
    if eps<1.065:
        c3= 1.2375
    elif 1.065<eps<1.230:
        c3= 6.4477
    elif 1.230<eps<1.5:
        c3= -37.7000
    elif 1.5<eps<1.95:
        c3= -62.2500
    elif 1.95<eps<2.8:
        c3= -21.5906
    elif 2.8<eps<4.5:
        c3= -7.1406
    elif 4.5<eps<6.2:
        c3= 1.2438
    else:
        c3= -46.1148
    return c3

def fn_c4(eps):
    if eps<1.065:
        c4= 1.0000
    elif 1.065<eps<1.230:
        c4= -0.1239
    elif 1.230<eps<1.5:
        c4= 34.8438
    elif 1.5<eps<1.95:
        c4= 52.0781
    elif 1.95<eps<2.8:
        c4= 7.2492
    elif 2.8<eps<4.5:
        c4= 7.5469
    elif 4.5<eps<6.2:
        c4= -1.9094
    else:
        c4= 55.3750
    return c4

def fn_d1(eps):
    if eps<1.065:
        d1= 1.8734
    elif 1.065<eps<1.230:
        d1= -1.5798
    elif 1.230<eps<1.5:
        d1= -5.0000
    elif 1.5<eps<1.95:
        d1= -3.5000
    elif 1.95<eps<2.8:
        d1= -3.5000
    elif 2.8<eps<4.5:
        d1= -3.4000
    elif 4.5<eps<6.2:
        d1= -4.0000
    else:
        d1= -7.2312
    return d1

def fn_d2(eps):
    if eps<1.065:
        d2= 0.6297
    elif 1.065<eps<1.230:
        d2= -0.5081
    elif 1.230<eps<1.5:
        d2= 1.5218
    elif 1.5<eps<1.95:
        d2= 0.0016
    elif 1.95<eps<2.8:
        d2= -0.1554
    elif 2.8<eps<4.5:
        d2= -0.1078
    elif 4.5<eps<6.2:
        d2= 0.0250
    else:
        d2= 0.4050
    return d2

def fn_d3(eps):
    if eps<1.065:
        d3= 0.9738
    elif 1.065<eps<1.230:
        d3= -1.7812
    elif 1.230<eps<1.5:
        d3= 3.9229
    elif 1.5<eps<1.95:
        d3= 1.1477
    elif 1.95<eps<2.8:
        d3= 1.4062
    elif 2.8<eps<4.5:
        d3= -1.0750
    elif 4.5<eps<6.2:
        d3= 0.3844
    else:
        d3= 13.3500
    return d3

def fn_d4(eps):
    if eps<1.065:
        d4= 0.2809
    elif 1.065<eps<1.230:
        d4= 0.1080
    elif 1.230<eps<1.5:
        d4= -2.6204
    elif 1.5<eps<1.95:
        d4= 0.1062
    elif 1.95<eps<2.8:
        d4= 0.3988
    elif 2.8<eps<4.5:
        d4= 1.5702
    elif 4.5<eps<6.2:
        d4= 0.2656
    else:
        d4= 0.6234
    return d4

def fn_e1(eps):
    if eps<1.065:
        e1= 0.0356
    elif 1.065<eps<1.230:
        e1= 0.2624
    elif 1.230<eps<1.5:
        e1= -0.0156
    elif 1.5<eps<1.95:
        e1= 0.4659
    elif 1.95<eps<2.8:
        e1= 0.0032
    elif 2.8<eps<4.5:
        e1= -0.0672
    elif 4.5<eps<6.2:
        e1= 1.0468
    else:
        e1= 1.5000
    return e1

def fn_e2(eps):
    if eps<1.065:
        e2= -0.1246
    elif 1.065<eps<1.230:
        e2= 0.0672
    elif 1.230<eps<1.5:
        e2= 0.1597
    elif 1.5<eps<1.95:
        e2= -0.3296
    elif 1.95<eps<2.8:
        e2= 0.0766
    elif 2.8<eps<4.5:
        e2= 0.4016
    elif 4.5<eps<6.2:
        e2= -0.3788
    else:
        e2= -0.6426
    return e2

def fn_e3(eps):
    if eps<1.065:
        e3= -0.5718
    elif 1.065<eps<1.230:
        e3= -0.2190
    elif 1.230<eps<1.5:
        e3= 0.4199
    elif 1.5<eps<1.95:
        e3= -0.0876
    elif 1.95<eps<2.8:
        e3= -0.0656
    elif 2.8<eps<4.5:
        e3= 0.3017
    elif 4.5<eps<6.2:
        e3= -2.4517
    else:
        e3= 1.8564
    return e3

def fn_e4(eps):
    if eps<1.065:
        e4= 0.9938
    elif 1.065<eps<1.230:
        e4= -0.4285
    elif 1.230<eps<1.5:
        e4= -0.5562
    elif 1.5<eps<1.95:
        e4= -0.0329
    elif 1.95<eps<2.8:
        e4= -0.1294
    elif 2.8<eps<4.5:
        e4= -0.4844
    elif 4.5<eps<6.2:
        e4= 1.4656
    else:
        e4= 0.5636
    return e4

def variableselect(E_ed,E_Es,Z,m,E_es0):
    Z=math.radians(Z)
    eps=fn_eps(E_ed,E_es,Z)
    delta=fn_del(m,E_ed,E_es0)
    a=(fn_a1(eps)+(fn_a2(eps)*Z)+delta*(fn_a3(eps)+(fn_a4(eps)*Z)))
    b=(fn_b1(eps)+(fn_b2(eps)*Z)+delta*(fn_b3(eps)+(fn_b4(eps)*Z)))
    if eps<1.065:
        c=math.exp((delta*(2.8+(0.6004*Z)))**(1.2375))-1
        d=(-1*math.exp(delta*(1.8734+(0.6297*Z))))+0.9738+(delta*0.2809)
    else:
        c=(fn_c1(eps)+(fn_c2(eps)*Z)+delta*(fn_c3(eps)+(fn_c4(eps)*Z)))
        d=(fn_d1(eps)+(fn_d2(eps)*Z)+delta*(fn_d3(eps)+(fn_d4(eps)*Z)))
    e=(fn_e1(eps)+(fn_e2(eps)*Z)+delta*(fn_e3(eps)+(fn_e4(eps)*Z)))
    return a,b,c,d,e

def PerezSky(alt_deg,az_deg,Lz,a,b,c,d,e): #alt_deg = Solar Altitude | az1_deg = Solar Azimuth
    # patchpos[n][0] shows the altitude of the patch, patchpos[n][1] shows the azimuth of the patch. First 30 patches are at 6 degree alt (30P @ 6deg -- near horizon) followed by 30P @ 18deg, 24P @ 30deg, 24P @ 42deg, 18P @ 54deg, 12P @ 66 deg, 6P @ 78deg, and the final zenith patch
    patchpos=[[6,0],[6,12],[6,24],[6,36],[6,48],[6,60],[6,72],[6,84],[6,96],[6,108],[6,120],[6,132],[6,144],[6,156],[6,168],[6,180],[6,192],[6,204],[6,216],[6,228],[6,240],[6,252],[6,264],[6,276],[6,288],[6,300],[6,312],[6,324],[6,336],[6,348],[18,0],[18,12],[18,24],[18,36],[18,48],[18,60],[18,72],[18,84],[18,96],[18,108],[18,120],[18,132],[18,144],[18,156],[18,168],[18,180],[18,192],[18,204],[18,216],[18,228],[18,240],[18,252],[18,264],[18,276],[18,288],[18,300],[18,312],[18,324],[18,336],[18,348],[30,0],[30,15],[30,30],[30,45],[30,60],[30,75],[30,90],[30,105],[30,120],[30,135],[30,150],[30,165],[30,180],[30,195],[30,210],[30,225],[30,240],[30,255],[30,270],[30,285],[30,300],[30,315],[30,330],[30,345],[42,0],[42,15],[42,30],[42,45],[42,60],[42,75],[42,90],[42,105],[42,120],[42,135],[42,150],[42,165],[42,180],[42,195],[42,210],[42,225],[42,240],[42,255],[42,270],[42,285],[42,300],[42,315],[42,330],[42,345],[54,0],[54,20],[54,40],[54,60],[54,80],[54,100],[54,120],[54,140],[54,160],[54,180],[54,200],[54,220],[54,240],[54,260],[54,280],[54,300],[54,320],[54,340],[66,0],[66,30],[66,60],[66,90],[66,120],[66,150],[66,180],[66,210],[66,240],[66,270],[66,300],[66,330],[78,0],[78,60],[78,120],[78,180],[78,240],[78,300],[90,0]]
    patch_lum=[[0 for col in range(1)] for row in range(145)]
    az_s = math.radians(az_deg)
    Zsdeg=90-alt_deg
    Zs = math.radians(Zsdeg)
    for i in range (0,145,1):
        Z=math.radians(90-patchpos[i][0])
        az=math.radians(patchpos[i][1])
        Az_net = abs(az-az_s)
        kappa = math.acos((math.cos(Zs)*math.cos(Z))+(math.sin(Zs)*math.sin(Z)*math.cos(Az_net)))  # Skypatch Sun Distance
        phyZ = 1+a*math.exp(b/math.cos(math.radians(Z)))
        phy0 = 1+a*math.exp(b)
        fkappa = 1+(c*(math.exp(d*kappa)))+(e*(math.cos(kappa))**2)
        fZs = 1+(c*(math.exp(d*Zs)))+(e*(math.cos(Zs))**2)
        r_gradation = phyZ/phy0
        r_indicatrix = fkappa/fZs
        ratio = r_indicatrix*r_gradation
        Lz=float(Lz)
        Ldes = Lz * ratio
        patch_lum[i]=Ldes
    return patch_lum

def mtakagi(lum):
    CCT=6500+((1.1985*10**8)/(lum**1.2))
    return CCT

def mchain99(lum):
    CCT=(10**6)/(-132.1+59.77*math.log10(lum))
    return CCT

def mchain04(lum):
    LCF=120
    CCT=(10**6)/(181.35233+LCF*(-4.22630+math.log10(lum)))
    return CCT

def mrusnak(lum):
    p=10.2
    q=0.26
    CCT=(10**6)/(p*(lum**q))
    return CCT

def SpectralSkydome(matrix_out):
    matrix_out=[float(i) for i in matrix_out]
    matrix_out=[int(i) for i in matrix_out]
    m_out=[(0*1) for i in range(145)]
    matCCT=[(0*1) for i in range(145)]
    selectmodel=[(0*1) for i in range(145)]
    for i in range (0,145,1):
        if float(matrix_out[i])<250:
            mval=250
            CCT=mchain99(mval)
            mdl=1
        elif 250<float(matrix_out[i])<3172:
            mval=float(matrix_out[i])
            CCT=mchain99(float(matrix_out[i]))
            mdl=1
        elif 3172<float(matrix_out[i])<5200:
            mval=float(matrix_out[i])
            CCT=mrusnak(float(matrix_out[i]))
            mdl=2
        elif float(matrix_out[i])>5200:
            mval=float(matrix_out[i])
            CCT=mchain04(float(matrix_out[i]))
            mdl=3
        else:
            mval=float(matrix_out[i])
            CCT=5000
            mdl=0
        m_out[i]=int(mval)
        matCCT[i]= int(CCT)
        selectmodel[i]=int(mdl)
    return matCCT

def xDcalc(CCT):
    if CCT<=7000:
        xD=(-4.607*1000000000/(CCT*CCT*CCT))+(2.9678*1000000/(CCT*CCT))+(0.09911*1000/CCT)+0.244063
    else:
        xD=(-2.0064*1000000000/(CCT*CCT*CCT))+(1.9018*1000000/(CCT*CCT))+(0.24748*1000/CCT)+0.237040
    xD=round(xD,3)
    if xD>0.380:
        xD=0.380
    return xD

def yDcalc(xD):
    yD=(-3.000*xD*xD)+(2.870*xD)-0.275
    yD=round(yD,3)
    return yD

def factorcalc(xD,yD):
    M1=((-1.3515)+(-1.7703*xD)+(5.9114*yD))/((0.0241)+(0.2562*xD)+(-0.7341*yD))
    M2=((0.0300)+(-31.4424*xD)+(30.0717*yD))/((0.0241)+(0.2562*xD)+(-0.7341*yD))
    M1=round(M1,5)
    M2=round(M2,5)
    return M1,M2

def dotproduct(vec1, vec2, vec3):
    return sum(map(operator.mul, vec1, vec2, vec3))

def interpolate(inp, fi):
    i, f = int(fi // 1), fi % 1  # Split floating-point index into whole & fractional parts.
    j = i+1 if f > 0 else i  # Avoid index error.
    return (1-f) * inp[i] + f * inp[j]

def matrixmult (A, B):
    rows_A = len(A)
    cols_A = len(A[0])
    cols_B = len(B[0])
    C = [[0 for row in range(cols_B)] for col in range(rows_A)]
    for i in range(rows_A):
        for j in range(cols_B):
            for k in range(cols_A):
                C[i][j] += A[i][k] * B[k][j]
    return C

def SPD2CIEXYZ(spd_selectx): #converts 176 values relative combined SPD to 107 values (176 to 71 then pre and post) and then evaluates X,Y,Z and CCT
    inp = spd_selectx
    new_len = 71
    delta = (len(inp)-1) / (new_len-1)
    outp = [interpolate(inp, i*delta) for i in range(new_len)]
    prelist=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    postlist=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    fulllist=prelist+outp+postlist
    spd_select=fulllist    
    capX=[[]for i in range (107)]
    capY=[[]for i in range (107)]
    capZ=[[]for i in range (107)]
    for i in range (0,107,1):
        capX[i]=5*float(xbar[i])*float(spd_select[i])
        capY[i]=5*float(ybar[i])*float(spd_select[i])
        capZ[i]=5*float(zbar[i])*float(spd_select[i])
    sum_capX=sum(capX)
    sum_capY=sum(capY)
    sum_capZ=sum(capZ)
    small_x=sum_capX/(sum_capX+sum_capY+sum_capZ)
    small_y=sum_capY/(sum_capX+sum_capY+sum_capZ)
    small_z=1-(small_x+small_y)
    small_arrxyz=[small_x,small_y,small_z]
    CIExyzarr=(str(round(small_arrxyz[0],4))+","+str(round(small_arrxyz[1],4))+","+str(round(small_arrxyz[2],4)))
    CIEx=(str(round(small_arrxyz[0],4)))
    CIEy=(str(round(small_arrxyz[1],4)))
    CIEz=(str(round(small_arrxyz[2],4)))
    xnvall=(round(small_arrxyz[0],4))
    ynvall=(round(small_arrxyz[1],4))
    nnvall=(xnvall-0.3320)/(0.1858-ynvall)
    CCTv=int((449*nnvall*nnvall*nnvall)+(3525*nnvall*nnvall)+(6823.3*nnvall)+(5520.33)) #https://doi.org/10.1016/j.solener.2018.02.021
    return CIEx,CIEy,CIEz,CCTv

def RelativeCombinedSPD(DOY,HOD,Zen_Lum_Lz,HorzDiffRad,DirNormRad,sunAltitude,sunAzimuth,SPD_5,luminance):
    SPD=SPD_5
    num_streams=int(len(SPD)/107)
    num_streams=145
    lum_d=luminance
    strdn= 0.0433 #0.0433 steradians per division (cone with 13.5° apex angle): https://escholarship.org/content/qt7079393t/qt7079393t.pdf
    sine_array=[0.104528463,0.104528463,0.104528463,0.104528463,0.104528463,0.104528463,0.104528463,0.104528463,0.104528463,0.104528463,0.104528463,0.104528463,0.104528463,0.104528463,0.104528463,0.104528463,0.104528463,0.104528463,0.104528463,0.104528463,0.104528463,0.104528463,0.104528463,0.104528463,0.104528463,0.104528463,0.104528463,0.104528463,0.104528463,0.104528463,0.309016994,0.309016994,0.309016994,0.309016994,0.309016994,0.309016994,0.309016994,0.309016994,0.309016994,0.309016994,0.309016994,0.309016994,0.309016994,0.309016994,0.309016994,0.309016994,0.309016994,0.309016994,0.309016994,0.309016994,0.309016994,0.309016994,0.309016994,0.309016994,0.309016994,0.309016994,0.309016994,0.309016994,0.309016994,0.309016994,0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.669130606,0.669130606,0.669130606,0.669130606,0.669130606,0.669130606,0.669130606,0.669130606,0.669130606,0.669130606,0.669130606,0.669130606,0.669130606,0.669130606,0.669130606,0.669130606,0.669130606,0.669130606,0.669130606,0.669130606,0.669130606,0.669130606,0.669130606,0.669130606,0.809016994,0.809016994,0.809016994,0.809016994,0.809016994,0.809016994,0.809016994,0.809016994,0.809016994,0.809016994,0.809016994,0.809016994,0.809016994,0.809016994,0.809016994,0.809016994,0.809016994,0.809016994,0.913545458,0.913545458,0.913545458,0.913545458,0.913545458,0.913545458,0.913545458,0.913545458,0.913545458,0.913545458,0.913545458,0.913545458,0.978147601,0.978147601,0.978147601,0.978147601,0.978147601,0.978147601,1]
    illumin_d=[(0) for i in range(num_streams)]
    for i in range (0,num_streams,1):
        illumin_d[i]=lum_d[i]*sine_array[i]*strdn
    patch_illum=illumin_d
    total_illum=sum(illumin_d)
    net_illum=total_illum   
    SPD_5b = [([0]*num_streams) for i in range(71)]
    for i in range (0,71,1):
        for j in range (0, num_streams,1):
            SPD_5b[i][j]=SPD_5[i+16+(107*j)] # truncated between 380-730 from 300-830, thus reduced to 70+1 from 106+1 values.
    inp = [[float(y) for y in x] for x in SPD_5b]
    new_len=176
    delta = (len(inp)-1) / (new_len-1)
    outpt=[([0]*176) for i in range(num_streams)]
    inpt=[([0]*71) for i in range(num_streams)]
    for nn in range (0,71,1):
        for ni in range (0,num_streams,1):
            inpt[ni][nn]=inp[nn][ni]
    for mm in range (0,num_streams,1):
        outpt[mm] = [interpolate(inpt[:][mm], i*delta) for i in range(new_len)]
    SPD_2=outpt  # interpolated data between 380-730nm; from 5nm (70+1 values) to 2nm (175+1 values)
    photopic_obs_arr=[0.000039,0.000046915,0.000057176,0.000072344,0.000093508,0.00012,0.00015149,0.00019182,0.00024691,0.00031852,0.000396,0.00047302,0.00057222,0.00072456,0.00094116,0.00121,0.0015308,0.0019353,0.0024548,0.0031178,0.004,0.0051593,0.0065462,0.0080865,0.0097677,0.0116,0.013583,0.015715,0.018007,0.020454,0.023,0.02561,0.028351,0.031311,0.034521,0.038,0.041768,0.045843,0.050244,0.054981,0.06,0.065278,0.070911,0.077016,0.083667,0.09098,0.099046,0.10788,0.11753,0.12799,0.13902,0.15047,0.16272,0.17624,0.19127,0.20802,0.22673,0.24748,0.27018,0.29505,0.323,0.35469,0.38929,0.42563,0.46339,0.503,0.54451,0.58697,0.62935,0.67088,0.71,0.74546,0.77784,0.80811,0.83631,0.862,0.88496,0.90544,0.92373,0.93992,0.954,0.96601,0.97602,0.98409,0.99031,0.99495,0.9981,0.99975,0.99986,0.99833,0.995,0.98974,0.98272,0.97408,0.96386,0.952,0.9385,0.92346,0.90701,0.8892,0.87,0.84939,0.82758,0.80479,0.78119,0.757,0.73242,0.7075,0.68222,0.65667,0.631,0.60531,0.57964,0.55396,0.52835,0.503,0.47803,0.4534,0.42908,0.40503,0.381,0.35683,0.33282,0.30934,0.28659,0.265,0.24489,0.22605,0.20816,0.19116,0.175,0.15965,0.14513,0.1315,0.11878,0.107,0.096189,0.086265,0.077121,0.06871,0.061,0.053955,0.04755,0.041759,0.036564,0.032,0.028077,0.024708,0.021801,0.019281,0.017,0.014837,0.012835,0.011068,0.0095333,0.00821,0.0070854,0.0061385,0.0053431,0.0046764,0.004102,0.0035891,0.0031341,0.0027381,0.0023932,0.002091,0.0018246,0.0015902,0.0013845,0.0012041,0.001047,0.00091111,0.00079324,0.00069008,0.0005995,0.00052]
    delta_wavelength=[1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,1]
    SPD_2x=[[float(y) for y in x] for x in SPD_2]
    array_product=[([0]*176) for i in range(num_streams)]
    outpt=[([0]*176) for i in range(num_streams)]
    for ij in range(0,num_streams,1):
        for ii in range(0,len(SPD_2x[0]),1):
            array_product[ij][ii]=SPD_2x[ij][ii]*photopic_obs_arr[ii]*delta_wavelength[ii]
    sumproduct=[([0]*1) for i in range(num_streams)]
    for i in range(0,num_streams,1):
        sumproduct[i]=sum(array_product[i])
    avdata=[([0]*176) for i in range(num_streams)]
    for nn in range (0, num_streams,1):
        avdata[nn]=[i * ((illumin_d[nn])/(683*(sumproduct[nn]+0.000000001))) for i in SPD_2x[nn]] # factor of 0.0000...1 added to avoid 'divide by zero' exception
    sum_avdata=[sum(x) for x in zip(*avdata)]
    maxval=max(sum_avdata)
    norm_avdata = [x / maxval for x in sum_avdata]
    Rel_comb_SPD=[round(a, 4) for a in norm_avdata]
    CIEx,CIEy,CIEz,CCTv=SPD2CIEXYZ(Rel_comb_SPD)
    prelim_arr=[DOY,HOD,float(Zen_Lum_Lz),float(HorzDiffRad),float(DirNormRad),sunAltitude,sunAzimuth,CIEx,CIEy,CIEz,CCTv]
    RCSPD=prelim_arr+Rel_comb_SPD
    return RCSPD


if True:
    import sys
    print(sys.executable)
    xbar=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0.0014,0.0022,0.0042,0.0076,0.0143,0.0232,0.0435,0.0776,0.1344,0.2148,0.2839,0.3285,0.3483,0.3481,0.3362,0.3187,0.2908,0.2511,0.1954,0.1421,0.0956,0.058,0.032,0.0147,0.0049,0.0024,0.0093,0.0291,0.0633,0.1096,0.1655,0.2257,0.2904,0.3597,0.4334,0.5121,0.5945,0.6784,0.7621,0.8425,0.9163,0.9786,1.0263,1.0567,1.0622,1.0456,1.0026,0.9384,0.8544,0.7514,0.6424,0.5419,0.4479,0.3608,0.2835,0.2187,0.1649,0.1212,0.0874,0.0636,0.0468,0.0329,0.0227,0.0158,0.0114,0.0081,0.0058,0.0041,0.0029,0.002,0.0014,0.001,0.0007,0.0005,0.0003,0.0002,0.0002,0.0001,0.0001,0.0001,0,0,0,0,0,0,0,0,0,0,0]
    ybar=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0.0001,0.0001,0.0002,0.0004,0.0006,0.0012,0.0022,0.004,0.0073,0.0116,0.0168,0.023,0.0298,0.038,0.048,0.06,0.0739,0.091,0.1126,0.139,0.1693,0.208,0.2586,0.323,0.4073,0.503,0.6082,0.71,0.7932,0.862,0.9149,0.954,0.9803,0.995,1,0.995,0.9786,0.952,0.9154,0.87,0.8163,0.757,0.6949,0.631,0.5668,0.503,0.4412,0.381,0.321,0.265,0.217,0.175,0.1382,0.107,0.0816,0.061,0.0446,0.032,0.0232,0.017,0.0119,0.0082,0.0057,0.0041,0.0029,0.0021,0.0015,0.001,0.0007,0.0005,0.0004,0.0002,0.0002,0.0001,0.0001,0.0001,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    zbar=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0.0065,0.0105,0.0201,0.0362,0.0679,0.1102,0.2074,0.3713,0.6456,1.0391,1.3856,1.623,1.7471,1.7826,1.7721,1.7441,1.6692,1.5281,1.2876,1.0419,0.813,0.6162,0.4652,0.3533,0.272,0.2123,0.1582,0.1117,0.0782,0.0573,0.0422,0.0298,0.0203,0.0134,0.0087,0.0057,0.0039,0.0027,0.0021,0.0018,0.0017,0.0014,0.0011,0.001,0.0008,0.0006,0.0003,0.0002,0.0002,0.0001,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    root=tk.Tk()
    root.withdraw()
    file_pathTK=filedialog.askopenfilename(filetypes=[('.epwfiles', '.epw')], title='Select your Weather file for desired location (.epw filetype)')
    filenameTK=os.path.splitext(os.path.basename(file_pathTK))[0]
    foldernameTK=os.path.dirname(file_pathTK)+'/'
#    start_time = ptm()
    input_file=file_pathTK
    epwFile=input_file
    name, latitude, longitude, timeZone, elevation=openEPW_loc()
    SPDhour_arr=[]
    header_arr=['DOY','HOD','ZenLum','HrzDfRad','DrNrmRad','SunAlt','SunAz','CIE_x','CIE_y','CIE_z','CCT',380,382,384,386,388,390,392,394,396,398,400,402,404,406,408,410,412,414,416,418,420,422,424,426,428,430,432,434,436,438,440,442,444,446,448,450,452,454,456,458,460,462,464,466,468,470,472,474,476,478,480,482,484,486,488,490,492,494,496,498,500,502,504,506,508,510,512,514,516,518,520,522,524,526,528,530,532,534,536,538,540,542,544,546,548,550,552,554,556,558,560,562,564,566,568,570,572,574,576,578,580,582,584,586,588,590,592,594,596,598,600,602,604,606,608,610,612,614,616,618,620,622,624,626,628,630,632,634,636,638,640,642,644,646,648,650,652,654,656,658,660,662,664,666,668,670,672,674,676,678,680,682,684,686,688,690,692,694,696,698,700,702,704,706,708,710,712,714,716,718,720,722,724,726,728,730]
    SPDhour_arr.append(header_arr)
    credit_string=" This python-based utility converts the EPW file weather data for any defined location to Annual Spectral data for unobstructed sky hemisphere for that location. \n Developed by Marshal Maskarenj at UCLouvain, this utility follows the approach recommended by Maskarenj, Deroisy and Altomonte (doi.org/10.1016/j.enbuild.2022.112012).\n For each annual daylit hour, the Perez all weather sky model is used to convert hourly zenith luminance to patch-luminance for 145 Tregenza patches. \n Each patch luminance is converted to daylight correlated color temperature (CCT) using Diakite-Kortlever and Knoop spectral sky models (doi.org/10.1177/1477153520982265). \n Hourly patch CCT is then converted to patch spectral power distribution (SPD) following the approach recommended in the CIE015 standard.\n SPDs of all patches are merged with appropriate cosine correction, to generate relative combined SPD of sky hemisphere.\n The tristimulus X,Y,Z values are then evaluated from the SPD, and chromaticity coordinates x, and y (and complementary z) are derived by factoring.\n McCamy's equation is used to derive CCT from chromaticity coordinates x and y, whereas the chromaticity coordinate z is also tablulated to be further used for deriving Circadian Stimulus using Truong's approximation (doi.org/10.1177/1477153519887423) \n The generated text based .aowl file tabulates, for each hour, the  [Date of Year], [Hour of Day], [Zenith luminance], [Horizonal Diffuse Radiation], [Direct Normal Radiation], [Sun Altitude], [Sun Azimuth], [CIE chromaticity coordinate x], [CIE chromaticity coordinate y], [CIE chromaticity coordinate complement z], [Correlated Color Temperature], and relative SPD from 380-730nm for each 2nm separation. \n \n The development of this tool was funded by FNRS under the postdoctoral project SCALE (40000322) awarded to Marshal Maskarenj (2020-23) at Architecture et Climat, LAB, UCLouvain, Belgium."
    print(credit_string)
    print("\n Kindly note: This utility could take upto 30 minutes to calculate the Annual Spectral data from each EPW file.\n The percentage completion will appear below.\n")
    for HOY in range (0,8760,1):
        DOY = int(HOY/24)+1
        HOD=HOY-(24*(DOY-1))
        sunAltitude, sunAzimuth=SunPos(latitude,longitude,timeZone,HOD+1,DOY)
        Zen_Lum_Lz=openEPW(HOY+1,20)
        HorzDiffRad=openEPW(HOY+1,16)
        DirNormRad=openEPW(HOY+1,15)
        sAlt=sunAltitude
        OptAirMass=round(1/(math.cos(math.radians(sAlt))+0.50572*((96.07995-sAlt)**(-1.6364))),3)
        NormExIrrad=openEPW(HOY+1,12)
#        if HOY==87:
#            tmpct=ptm() - start_time
#        if HOY==870:
#            tmpct=(ptm() - start_time)/10
#        if HOY==1740:
#            tmpct=(ptm() - start_time)/20
        for i in range(1,100,1):
            if HOY==87*i:
#                tmtc=int((100-i)*tmpct)
                print(str(i)+" percent complete")#", estimated time for completion: "+str(tmtc)+" seconds")
        if sunAltitude>0.1:
            #Dh (or E_ed) is HorzDiffRad, I (or E_es) is DirNormRad, Z is zenith angle (deg), m is OptAirMass, and E_es0 is NormExIrrad
            if float(Zen_Lum_Lz) < 1:
                Zen_Lum_Lz=1
            if float(HorzDiffRad) < 1:
                HorzDiffRad=1
            E_ed=float(HorzDiffRad)
            E_es=float(DirNormRad)
            Z=math.radians(90-sunAltitude)
            m=float(OptAirMass)
            E_es0=float(NormExIrrad)
            a,b,c,d,e=variableselect(E_ed,E_es,Z,m,E_es0)
            matrix_out=PerezSky(sunAltitude,sunAzimuth,Zen_Lum_Lz,a,b,c,d,e)    
            m_CCT=SpectralSkydome(matrix_out)
            wav_arr=[300,305,310,315,320,325,330,335,340,345,350,355,360,365,370,375,380,385,390,395,400,405,410,415,420,425,430,435,440,445,450,455,460,465,470,475,480,485,490,495,500,505,510,515,520,525,530,535,540,545,550,555,560,565,570,575,580,585,590,595,600,605,610,615,620,625,630,635,640,645,650,655,660,665,670,675,680,685,690,695,700,705,710,715,720,725,730,735,740,745,750,755,760,765,770,775,780,785,790,795,800,805,810,815,820,825,830]
            s0_arr=[0.04,3.02,6.00,17.80,29.60,42.45,55.30,56.30,57.30,59.55,61.80,61.65,61.50,65.15,68.80,66.10,63.40,64.60,65.80,80.30,94.80,99.80,104.80,105.35,105.90,101.35,96.80,105.35,113.90,119.75,125.60,125.55,125.50,123.40,121.30,121.30,121.30,117.40,113.50,113.30,113.10,111.95,110.80,108.65,106.50,107.65,108.80,107.05,105.30,104.85,104.40,102.20,100.00,98.00,96.00,95.55,95.10,92.10,89.10,89.80,90.50,90.40,90.30,89.35,88.40,86.20,84.00,84.55,85.10,83.50,81.90,82.25,82.60,83.75,84.90,83.10,81.30,76.60,71.90,73.10,74.30,75.35,76.40,69.85,63.30,67.50,71.70,74.35,77.00,71.10,65.20,56.45,47.70,58.15,68.60,66.80,65.00,65.50,66.00,63.50,61.00,57.15,53.30,56.10,58.90,60.40,61.90]
            s1_arr=[0.02,2.26,4.50,13.45,22.40,32.20,42.00,41.30,40.60,41.10,41.60,39.80,38.00,40.20,42.40,40.45,38.50,36.75,35.00,39.20,43.40,44.85,46.30,45.10,43.90,40.50,37.10,36.90,36.70,36.30,35.90,34.25,32.60,30.25,27.90,26.10,24.30,22.20,20.10,18.15,16.20,14.70,13.20,10.90,8.60,7.35,6.10,5.15,4.20,3.05,1.90,0.95,0.00,-0.80,-1.60,-2.55,-3.50,-3.50,-3.50,-4.65,-5.80,-6.50,-7.20,-7.90,-8.60,-9.05,-9.50,-10.20,-10.90,-10.80,-10.70,-11.35,-12.00,-13.00,-14.00,-13.80,-13.60,-12.80,-12.00,-12.65,-13.30,-13.10,-12.90,-11.75,-10.60,-11.10,-11.60,-11.90,-12.20,-11.20,-10.20,-9.00,-7.80,-9.50,-11.20,-10.80,-10.40,-10.50,-10.60,-10.15,-9.70,-9.00,-8.30,-8.80,-9.30,-9.55,-9.80]
            s2_arr=[0.00,1.00,2.00,3.00,4.00,6.25,8.50,8.15,7.80,7.25,6.70,6.00,5.30,5.70,6.10,4.55,3.00,2.10,1.20,0.05,-1.10,-0.80,-0.50,-0.60,-0.70,-0.95,-1.20,-1.90,-2.60,-2.75,-2.90,-2.85,-2.80,-2.70,-2.60,-2.60,-2.60,-2.20,-1.80,-1.65,-1.50,-1.40,-1.30,-1.25,-1.20,-1.10,-1.00,-0.75,-0.50,-0.40,-0.30,-0.15,0.00,0.10,0.20,0.35,0.50,1.30,2.10,2.65,3.20,3.65,4.10,4.40,4.70,4.90,5.10,5.90,6.70,7.00,7.30,7.95,8.60,9.20,9.80,10.00,10.20,9.25,8.30,8.95,9.60,9.05,8.50,7.75,7.00,7.30,7.60,7.80,8.00,7.35,6.70,5.95,5.20,6.30,7.40,7.10,6.80,6.90,7.00,6.70,6.40,5.95,5.50,5.80,6.10,6.30,6.50]
            SPDarr=[]
            for CCT in m_CCT:
                if CCT<4000:
                    CCT=4000
                if CCT>25000:
                    CCT=25000
                CCT=float(CCT)
                xD=xDcalc(CCT)
                yD=yDcalc(xD)
                M1,M2=factorcalc(xD,yD)            
                for i in range(0,len(wav_arr),1):
                    SPDval=s0_arr[i]+M1*s1_arr[i]+M2*s2_arr[i]
                    SPDarr.append(SPDval)
            Rel_comb_SPD=RelativeCombinedSPD(DOY,HOD,Zen_Lum_Lz,HorzDiffRad,DirNormRad,sunAltitude,sunAzimuth,SPDarr,matrix_out)  
            SPDhour_arr.append(Rel_comb_SPD)
        else:
            SPDhour_arr.append([DOY,HOD,float(Zen_Lum_Lz),float(HorzDiffRad),float(DirNormRad),'-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-'])
#    print("this simulation took ", ptm() - start_time, "seconds")
#    newcredit_string="This python-based utility converts the EPW file weather data for any defined location to Annual Spectal data for unobstructed sky hemisphere for that location. \n Developed by Marshal Maskarenj at UCLouvain -- this utility follows the approach recommended by Maskarenj; Deroisy and Altomonte (doi.org/10.1016/j.enbuild.2022.112012).\n For each annual daylit hour -- the Perez all weather sky model is used to convert hourly zenith luminance to patch-luminance for 145 Tregenza patches. \n Each patch luminance is converted to daylight correlated color temperature (CCT) using Diakite-Kortlever and Knoop spectral sky models (doi.org/10.1177/1477153520982265). \n Hourly patch CCT is then converted to patch spectral power distribution (SPD) following the approach recommended in the CIE015 standard.\n SPDs of all patches are merged with appropriate cosine correction to generate relative combined SPD of sky hemisphere.\n The tristimulus X Y Z values are then evaluated from the SPD -- and chromaticity coordinates x and y (and complementary z) are derived by factoring.\n McCamy's equation is used to derive CCT from chromaticity coordinates x and y -- whereas the chromaticity coordinate z is also tablulated to be further used for deriving Circadian Stimulus using Truong's approximation (doi.org/10.1177/1477153519887423) \n The generated text based .aowl file tabulates for each hour -- the  (Date of Year) | (Hour of Day) | (Zenith luminance) | (Horizonal Diffuse Radiation) | (Direct Normal Radiation) | (Sun Altitude) | (Sun Azimuth) | (CIE chromaticity coordinate x) | (CIE chromaticity coordinate y) | (CIE chromaticity coordinate complement z) | (Correlated Color Temperature) and relative SPD from 380-730nm for each 2nm separation. \n \n The development of this tool was funded by FNRS under the postdoctoral project SCALE (40000322) awarded to Marshal Maskarenj (2020-23) at Architecture et Climat | LAB | UCLouvain | Belgium."
#    SPDhour_arr.append([newcredit_string])
    np.savetxt(foldernameTK+filenameTK+"4.aowl",SPDhour_arr, delimiter =",",  fmt ='% s') 
    input('Press Enter to Exit this Utility')        