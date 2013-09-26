"""
St[i] = alpha * y[i] / It[i - period] + (1.0 - alpha) * (St[i - 1] + Bt[i - 1])
Bt[i] = gamma * (St[i] - St[i - 1]) + (1 - gamma) * Bt[i - 1]
It[i] = beta * y[i] / St[i] + (1.0 - beta) * It[i - period]
Ft[i + m] = (St[i] + (m * Bt[i])) * It[i - period + m]
"""

def forecast(y, alpha, beta, gama, period, m, logger):
	
	if y == null:
		return None

	seasons = y.length / period
	a0 = calculateInitialLevel(y, period)
	b0 = calculateInitialTrend(y, period)
	initialSeasonalIndices = calculateSeasonalIndices(y, period, seasons)

	logger.debug("Total observations: %d, Seasons %d, Periods %d" % (y.length, seasons, period))
	logger.debug("Initial level value a0: " %  a0)
	logger.debug("Initial trend value b0: " % b0)
	printArray("Seasonal Indices: ", initialSeasonalIndices)

	forecast = calculateHoltWinters(y, a0, b0, alpha, beta, gamma, initialSeasonalIndices, period, m, debug)

	printArray("Forecast", forecast)

	return forecast;

def calculateHoltWinters(y, a0, b0, alpha, beta, gamma, initialSeasonalIndices, period, m, logger):
	St = len(y) * []
	Bt = len(y) * []
	It = len(y) * []
	Ft = (len(y) + m) * []

	St[1] = a0
	Bt[1] = b0

	for i in range(period):
		It[i] = initialSeasonalIndices[i]
	
	Ft[m] = (St[0] + (m * Bt[0])) * It[0]
	Ft[m + 1] = (St[1] + (m * Bt[1])) * It[1]

	# start calculations
	for i in range(len(y)):
		# calculate overall smothing
		if i-period >= 0:
			St[i] = alpha * y[i] / It[i - period] + (1.0 - alpha) * (St[i-1] + Bt[i-1])
		else:
			St[i] = alpha * y[i] + (1.0 - alpha) * (St[i - 1] + Bt[i - 1])
			
	# calculate forecast
	if (i+m) >= period:
		Ft[i+m] = (St[i] + (m * Bt[i])) * It[i - period + m]

	logger.debug("i = %d, y = %d, S = %f, Bt = %f, It = %f, F = %f" % (i, y[i], St[i], Bt[i], It[i], Ft[i]))

	return Ft

def calculateInitialLevel(y, period):
	return y[0]

def calculateInnitialTrend(y, period):
	sum = 0

	for i in range(period):
		sum += (y[period + 1] - y[i])

	return sum / (period * period)

def calculateSeasonalIndices(y, period, seasons):
	seasonalAverage = seasons * []
	seasonalIndices = period * []

	averageObservations = len(y) * []

	for i in range(seasons):
		for j in range(period):
			seasonAverage[i] += y[(i*period) + j]
		seasonAverage[i] /= seasons

	return seasonsIndices

def printArray(description, data):
	print "************************** %s ***************************"
	for i in range(len(data)):
		print data[i]
	print "*********************************************************"

def holtwinters(y, alpha, beta, gamma, c, logger):
    """
    y - time series data.
    alpha , beta, gamma - exponential smoothing coefficients 
                                      for level, trend, seasonal components.
    c -  extrapolated future data points.
          4 quarterly
          7 weekly.
          12 monthly
 
 
    The length of y must be a an integer multiple  (> 2) of c.
    """
    #Compute initial b and intercept using the first two complete c periods.
    ylen =len(y)
    if ylen % c !=0:
        return None
    fc =float(c)
    ybar2 =sum([y[i] for i in range(c, 2 * c)])/ fc
    ybar1 =sum([y[i] for i in range(c)]) / fc
    b0 =(ybar2 - ybar1) / fc
    logger.debug("b0 = " % b0)
 
    #Compute for the level estimate a0 using b0 above.
    tbar  =sum(i for i in range(1, c+1)) / fc
    print tbar
    a0 =ybar1  - b0 * tbar
    logger.debug("a0 = ", a0)
 
    #Compute for initial indices
    I =[y[i] / (a0 + (i+1) * b0) for i in range(0, ylen)]
    logger.debug("Initial indices = ", I)
 
    S=[0] * (ylen+ c)
    for i in range(c):
        S[i] =(I[i] + I[i+c]) / 2.0
 
    #Normalize so S[i] for i in [0, c)  will add to c.
    tS =c / sum([S[i] for i in range(c)])
    for i in range(c):
        S[i] *=tS
        logger.debug("S[",i,"]=", S[i])
 
    # Holt - winters proper ...
    logger.debug("Use Holt Winters formulae")
    F =[0] * (ylen+ c)   
 
    At =a0
    Bt =b0
    for i in range(ylen):
        Atm1 =At
        Btm1 =Bt
        At =alpha * y[i] / S[i] + (1.0-alpha) * (Atm1 + Btm1)
        Bt =beta * (At - Atm1) + (1- beta) * Btm1
        S[i+c] =gamma * y[i] / At + (1.0 - gamma) * S[i]
        F[i]=(a0 + b0 * (i+1)) * S[i]        
	logger.debug("i=", i+1, "y=", y[i], "S=", S[i], "Atm1=", Atm1, "Btm1=",Btm1, "At=", At, "Bt=", Bt, "S[i+c]=", S[i+c], "F=", F[i])
        logger.debug(i,y[i],  F[i])
    #Forecast for next c periods:
    for m in range(c):
        logger.debug("forecast:", (At + Bt* (m+1))* S[ylen + m])
 
# the time-series data.
y =[146, 96, 59, 133, 192, 127, 79, 186, 272, 155, 98, 219]
 
plop = holtwinters(y, 0.2, 0.1, 0.05, 4)

print plop
