#Example input BC:7-CS:3-.....
#BC - Charge Capacity
#CS - Charge Speed
#CU - Charge Update
#CR - Charge Request
#PR - Port Request
def appToSim(inputString):
	#inputString = "-BC:7.235-CS:5.322-"
	commandList = inputString.split("-")  #Split input string into commands
	commandList = commandList[1:]	
	commandList = commandList[:-1]  #Remove empty command resulting in last "-"
	
	command = "" #storage for individual command from Command List
	
	# identifier="" #Identifier from a given command ex: "BC"
	
	commIDPair = {}
	
	value = 0     #Float value of the command
	
	
	for cmd in commandList:
		command = cmd.split(";")
		commIDPair.update({ command[0] : float(command[1]) })
		#print(commIDPair[command[0]])
		
	for cmd in commIDPair:
		if (cmd == "BC"):
			ChargeCapcity = commIDPair["BC"]
		if (cmd == "CS"):
			ChargeSpeed = commIDPair["CS"]
		if (cmd == "CU"):
			ChargeUpdage = commIDPair["CU"]
		if (cmd == "CR"):
			ChargeRequest = commIDPair["CR"]
		if (cmd == "PR"):
			PortRequest = commIDPair["PR"]



appToSim("-BC:7.235-CS:5.322-")


