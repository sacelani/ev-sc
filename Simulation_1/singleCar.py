def main():    
    car1 = make_car()
    calc_rate_options(car1)

class  Car(object):
    # inputs
    timeParked = 0
    stateOfCharge = 0
    batCapacity = 0
    maxChargeRate = 0
    
    # outputs
    chargeRate = 0
    priceRate = 0
    balance = 0
    
def make_car():
    car = Car()
    car.timeParked = float(input('Enter amount of time vehicle will be parked (hrs): '))
    car.stateOfCharge = float(input('Enter current state of charge of battery (%): '))
    car.batCapacity = float(input('Enter max capacity of battery (kWh): '))
    car.maxChargeRate = float(input('Enter max rate of charge battery can handle (kW): '))
    return car
    
def calc_rate_options(car):
    # INPUT car object
    PRICE = 0.15 # Price per kWh
    
    car.stateOfCharge = car.stateOfCharge / 100. # convert stateOfCharge percentage into number 0-1
    maxPercentOutcome = ((car.maxChargeRate * car.timeParked) / car.batCapacity) + car.stateOfCharge
    
    if maxPercentOutcome > 1:   # Get High Percentage
        highPercentOutcome = 1
    else:
        highPercentOutcome = maxPercentOutcome
    
    midPercentOutcome = ((2.0/3) * (highPercentOutcome - car.stateOfCharge)) + car.stateOfCharge   # Get Mid Percentage
    lowPercentOutcome = ((1.0/3) * (highPercentOutcome - car.stateOfCharge)) + car.stateOfCharge   # Get Low Percentage
    
    rateHigh = ((highPercentOutcome - car.stateOfCharge) * car.batCapacity) / car.timeParked    # Rate to charge to high (kW)
    rateMid  = ((midPercentOutcome - car.stateOfCharge) * car.batCapacity) / car.timeParked      # Rate to charge to mid
    rateLow  = ((lowPercentOutcome - car.stateOfCharge) * car.batCapacity) / car.timeParked      # Rate to charge to mid

    # Assume customer is paying $1/kW

    priceHigh = rateHigh * car.timeParked * PRICE        # Price for high rate of charge
    priceMid = rateMid * car.timeParked * PRICE          # Price for mid rate of charge
    priceLow = rateLow * car.timeParked * PRICE          # Price for low rate of charge
    
    print('High - Final Percentage: ',  highPercentOutcome*100,'%', sep="")      # Print High Button
    print('Cost: $', "%.2f" % priceHigh)
    print()
    print('Mid - Final Percentage: ', midPercentOutcome*100,'%', sep="")        # Print Mid Button
    print('Cost: $', "%.2f" % priceMid)
    print()
    print('Low - Final Percentage: ', lowPercentOutcome*100,'%', sep="")        # Print Low Button
    print('Cost: $', "%.2f" % priceLow)
    
    chosen = input('Choose "high" "med" or "low" rate: ')
    
    if chosen == "high":
        car.chargeRate = rateHigh
        car.priceRate = priceHigh
    elif chosen == "med":
        car.chargeRate = rateMid
        car.priceRate = priceMid
    elif chosen == "low":
        car.chargeRate = rateLow
        car.priceRate = priceLow
    else:
        print('Invalid Input')
        
    
    
if __name__ == '__main__':
    main()
