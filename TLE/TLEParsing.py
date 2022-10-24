import math

#Convert degrees in radians
def rad(nb):
    return nb * math.pi / 180

def extractTLElines(TLE):
    splitLines = TLE.split('\n')
    return splitLines[0], splitLines[1]

def extractTLEFirstLineData(line):
    #satNb, classification, cos(radPARyear, cos(radPARyearNb, cos(radPARID, EpochYear, epoch, FDMeanMotion, SDMeanMotion, BSTAR, ephType, TLENb
    return float(line[2:7]), line[7], float(line[9:11]), float(line[11:14]), line[14:17], float(line[18:20]), float(line[20:32]), float(line[33:43]), float(line[44:50] + 'e' + line[50:52]) / 1e5, float(line[53:59] + 'e' + line[59:61]) / 1e5, float(line[62]), float(line[64:68])

def extractTLESecondLineData(line):
    #satNb, inclinaison, RAAN, eccentricity, ArgPe, meanAnomaly, meanMotion, revNb
    return float(line[2:7]), float(line[8:16]), float(line[17:25]), float('.' + line[26:33]), float(line[34:42]), float(line[43:51]), float(line[52:63]), float(line[63:68])

#Does the convertion from inclinaison, RAAN, eccentricity, Argument of periapsis, mean anomaly and mean motion to x, y, z data in which the x axis pointing towards the first point of Aries and (x,y) being earth's equatorial plane
def TLEOrbitalElementsToXYZ(inc, RAAN, e, ArgPe, M, n):
    
    #Earth standard orbital parameter
    mu = 398600.436e9
    
    #Converting mean motion from rev/day to rad/sec
    n = n*2*math.pi/86400
    
    #semi-major axis
    a = (mu/n**2)**(1/3)
    
    #Calculating the true anomaly and the radius to get the circular coordinates. For now we assume ArgPe = 0, inclinaison = 0 and RAAN = 0
    nu = M + (2*e-1/4*e**3)*math.sin(rad(M)) + 5/4*e**2*math.sin(rad(2*M)) + 13/12*e**3*math.sin(rad(3*M))
    r = a * (1-e**2) / (1+e*math.cos(rad(nu)))
    
    #Converting in x, y, z coordinates assuming inclinaison = 0 and RAAN = 0
    x = r * math.cos(rad(nu + ArgPe))
    y = r * math.sin(rad(nu + ArgPe))
    z = 0
    
    #base change from the inclinaison assuming RAAN = 0 (rotation around x and projection on y and z)
    yinc = y
    y = yinc * math.cos(rad(inc))
    z = yinc * math.sin(rad(inc))
    
    #Base change (rotation around z) from the RAAN
    xRAAN = x
    yRAAN = y
    x = xRAAN * math.cos(rad(RAAN)) - yRAAN * math.sin(rad(RAAN))
    y = xRAAN * math.sin(rad(RAAN)) + yRAAN * math.cos(rad(RAAN))
    
    return x, y, z

#Will convert a TLE string into x, y, z in order to display the measured position of an object
def transformTLEinXYZ(TLE):

    #Reading the TLE and extracting the usefull orbital elements
    line1, line2 = extractTLElines(TLE)
    _, inc, RAAN, e, ArgPe, M, n, _ = extractTLESecondLineData(line2)
    
    return TLEOrbitalElementsToXYZ(inc, RAAN, e, ArgPe, M, n)

#Predicts the position of an object on it's orbit at a moment T0 + t from a Tle for moment T0 by increasin(radg the mean anomaly usin(radg the mean motion. t is in seconds
def propagTLEinXYZ(TLE, t):
    
    #Reading the TLE and extracting the usefull orbital elements
    line1, line2 = extractTLElines(TLE)
    _, inc, RAAN, e, ArgPe, M, n, _ = extractTLESecondLineData(line2)
    
    #Converting mean motion from rev/day to deg/sec
    angleIncrease = n*360/86400
    
    #Increasin(radg the mean angle to get it's new value after t seconds assuming the orbits 
    M += t * angleIncrease
    
    return TLEOrbitalElementsToXYZ(inc, RAAN, e, ArgPe, M, n)