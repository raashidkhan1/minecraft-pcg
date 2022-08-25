import interfaceUtils
import random
from materials import (destruct, lantern, pots, doors, walls, wallTorch, windows, roof, 
        cornerColumn, beds, fenceTop, fenceTopMC, peakRoof, unfeasible_bases)

# Do we send blocks in batches to speed up the generation process?
USE_BATCHING = True

def heightAt(x, z, heightmap, area):
    """Access height using local coordinates."""
    # Warning:
    # Heightmap coordinates are not equal to world coordinates!
    return heightmap[(x - area[0], z - area[1])]

def setBlock(x, y, z, block):
    """Place blocks or add them to batch."""
    if USE_BATCHING:
        # add block to buffer, send once buffer has 100 items in it
        interfaceUtils.placeBlockBatched(x, y, z, block, 100)
    else:
        interfaceUtils.setBlock(x, y, z, block)

# Utility function to check feasible build area
def checkBuildArea(heightmap, area, sizeX, sizeZ):
    start1 = area[0]
    start2 = area[1]
    end1 = start1+area[2]
    end2 = start2+area[3]
    centerX = start1 + int(area[2]/2)
    centerZ = start2 + int(area[3]/2)
    nobase = False
    randDistParam = random.randrange(2,8,2)
    checkCoordinates = [(start1+randDistParam, start2+randDistParam, start1+randDistParam+sizeX, start2+randDistParam+sizeZ), # 1st quadrant
                        (start1+randDistParam, end2-randDistParam-sizeZ, start1+randDistParam+sizeX, end2-randDistParam), #2nd
                        (end1-randDistParam-sizeX, end2-randDistParam-sizeZ, end1-randDistParam, end2-randDistParam-sizeZ), #3rd
                        (end1-randDistParam-sizeX, start2+randDistParam, end1-randDistParam, start2+randDistParam+sizeZ), # 4th
                        (centerX-int(sizeX/2), centerZ-int(sizeZ/2), centerX+int(sizeX/2), centerZ+int(sizeZ/2))] # center
    print(checkCoordinates)
    feasibleCoordinates = []

    while len(checkCoordinates)>0:
        randomCoordinate = random.choice(checkCoordinates)
        x1=randomCoordinate[0]
        z1=randomCoordinate[1]
        x2=randomCoordinate[2]
        z2=randomCoordinate[3]
        print((x1, z1, x2, z2))
        for x in range(x1, x2):
            for z in range(z1, z2):
                y = heightAt(x, z, heightmap, area)
                currBlock = interfaceUtils.getBlock(x, y-1, z)
                if currBlock in unfeasible_bases:
                    nobase = True
                    checkCoordinates.remove((x1, z1, x2, z2))
                    break
                else:
                    nobase= False
            else:
                continue
            break
        else:
            if nobase == False:
                feasibleCoordinates.append((x1, z1, x2, z2))
                print("feasible ", feasibleCoordinates)
                break
        
                       
    if len(feasibleCoordinates) == 0:
        print("No feasible area found for building house with current allocations, try again once.")
        quit()

    chosenArea = feasibleCoordinates.pop(random.randrange(len(feasibleCoordinates)))
    print("Chosen area for building house ", chosenArea)

    houseX = chosenArea[0]
    houseZ = chosenArea[1]

    houseY = max(
                heightAt(houseX, houseZ, heightmap, area),
                heightAt(houseX + sizeX - 1, houseZ, heightmap, area),
                heightAt(houseX, houseZ + sizeZ - 1, heightmap, area),
                heightAt(houseX + sizeX - 1, houseZ + sizeZ - 1, heightmap, area)
        )
    return (houseX, houseY, houseZ)

def recursiveFoundation(x1, y1, z1, x2, z2):
    currBlock = interfaceUtils.getBlock(x1, y1, z1)
    if currBlock not in destruct:
        return
    else:
        for x in range(x1, x2):
            for z in range(z1, z2):
                thisBlock = interfaceUtils.getBlock(x, y1, z)
                if thisBlock in destruct:
                    setBlock(x, y1, z, "diorite")
                recursiveFoundation(x, y1-1, z, x2, z2)


# double walls with torch on non-fluid surface and wood on fluid
def buildFence(area, heightmap):
    #check if fence alreay present
    x = area[0]
    z = area[1]
    y = heightAt(x, z, heightmap, area)

    if interfaceUtils.getBlock(x, y-1, z) in fenceTopMC:
        print("Fence present in current build area")
        return None
    else:
        print("Generating fence in the set build area")
        randomFenceTop = random.choice(fenceTop)

        for x in range(area[0], area[0] + area[2]):
            z = area[1]
            y = heightAt(x, z, heightmap, area)
            currBlock  = interfaceUtils.getBlock(x, y-1, z)
            if currBlock == "minecraft:water":
                setBlock(x, y, z, "acacia_wood")
                setBlock(x, y+1, z, randomFenceTop)
            elif currBlock == "minecraft:lava":
                continue
            else: 
                setBlock(x, y, z, "stone_bricks")
                setBlock(x, y+1, z, "stone_bricks")
                setBlock(x, y+2, z, randomFenceTop)
        for z in range(area[1], area[1] + area[3]):
            x = area[0]
            y = heightAt(x, z, heightmap, area)
            currBlock  = interfaceUtils.getBlock(x, y-1, z)
            if currBlock == "minecraft:water":
                setBlock(x, y, z, "acacia_wood")
                setBlock(x, y+1, z, randomFenceTop)
            elif currBlock == "minecraft:lava":
                continue
            else:         
                setBlock(x, y, z, "stone_bricks")
                setBlock(x, y+1, z, "stone_bricks")
                setBlock(x, y+2, z, randomFenceTop)
        for x in range(area[0], area[0] + area[2]):
            z = area[1] + area[3] - 1
            y = heightAt(x, z, heightmap, area)
            currBlock  = interfaceUtils.getBlock(x, y-1, z)
            if currBlock == "minecraft:water":
                setBlock(x, y, z, "acacia_wood")
                setBlock(x, y+1, z, randomFenceTop)
            elif currBlock == "minecraft:lava":
                continue
            else:         
                setBlock(x, y, z, "stone_bricks")
                setBlock(x, y+1, z, "stone_bricks")
                setBlock(x, y+2, z, randomFenceTop)
        for z in range(area[1], area[1] + area[3]):
            x = area[0] + area[2] - 1
            y = heightAt(x, z, heightmap, area)
            currBlock  = interfaceUtils.getBlock(x, y-1, z)
            if currBlock == "minecraft:water":
                setBlock(x, y, z, "acacia_wood")
                setBlock(x, y+1, z, randomFenceTop)
            elif currBlock == "minecraft:lava":
                continue
            else:         
                setBlock(x, y, z, "stone_bricks")
                setBlock(x, y+1, z, "stone_bricks")
                setBlock(x, y+2, z, randomFenceTop)

def buildHouse(x1, y1, z1, x2, y2, z2):
    # choose random build materials
    randomDoor = random.choice(doors)
    randomWall = random.choice(walls)
    randomWindow = random.choice(windows)
    randomColumn = random.choice(cornerColumn)
    randomroof = random.choice(roof)
    randomPeakRoof = random.choice(peakRoof)
    doorType = random.choice(("single", "double"))

    print("Construction started...")

    # clean the y direction and 1 block outside
    for y in range(y1+1, y2):
        for x in range(x1, x2):
            for z in range(z1, z2):
                setBlock(x, y, z, "air")
        # clean 1 block front area upwards
        for x in range(x1, x2):
            setBlock(x, y, z1-1, "air")
            setBlock(x, y, z2+1, "air")
        for z in range(z1, z2):
            setBlock(x1-1, y, z, "air")
            setBlock(x2+1, y, z, "air")
    
    # make an elevated flat foundation
    recursiveFoundation(x1, y1, z1, x2, z2)       

    # floor
    for x in range(x1, x2):
        for z in range(z1, z2):
            setBlock(x, y1, z, "diorite")
    # walls
    for y in range(y1 + 1, y2):
        for x in range(x1 + 1, x2 - 1):
            setBlock(x, y, z1, randomWall)
            setBlock(x, y, z2 - 1, randomWall)
        for z in range(z1 + 1, z2 - 1):
            setBlock(x1, y, z, randomWall)
            setBlock(x2 - 1, y, z, randomWall)
        for x in range(x1+1, x2):
            setBlock(x, y, z1+7, randomWall)


    # single door
    setBlock(x1+4, y1+1, z1, randomDoor+"[half=lower, facing=south, hinge=right]")
    setBlock(x1+4, y1+2, z1, randomDoor+"[half=upper, facing=south, hinge=right]")
    # double door
    if doorType == "double":
        setBlock(x1+5, y1+1, z1, randomDoor+"[half=lower, facing=south, hinge=left]")
        setBlock(x1+5, y1+2, z1, randomDoor+"[half=upper, facing=south, hinge=left]")

    # Add stairs if ground available else add ladders
    frontBlock = interfaceUtils.getBlock(x1+4, y1-1, z1-1)
    if frontBlock not in destruct:
        if doorType == "double":
            for x in range(x1+4, x1+6):
                setBlock(x, y1, z1-1, "polished_diorite_stairs[facing=south]")
        else:
            setBlock(x1+4, y1, z1-1, "polished_diorite_stairs[facing=south]")
    else:
    # ladder if needed
        currentHeight = y1
        while frontBlock in destruct:
            setBlock(x1+4, currentHeight, z1-1, "ladder")
            currentHeight -= 1
            frontBlock = interfaceUtils.getBlock(x1+4, currentHeight, z1-1)

    # windows
    for i in range(2, 4):
        # front window
        setBlock(x1+3, y2-i, z1, randomWindow)
        setBlock(x1+4, y2-i, z1, randomWindow)
        # right side window
        setBlock(x1, y2-i, z2-3, randomWindow)
        setBlock(x1, y2-i, z2-4, randomWindow)
        # left side window
        setBlock(x2-1, y2-i, z1+3, randomWindow)
        setBlock(x2-1, y2-i, z1+4, randomWindow)
        # iron bars at the back
        setBlock(x2-3, y2-i, z2-1, "iron_bars")
        setBlock(x2-4, y2-i, z2-1, "iron_bars")

    # roof
    if randomroof == "peak":
        if x2 - x1 < z2 - z1:
            for i in range(0, x2 - x1, 2):
                halfI = int(i / 2)
                for x in range(x1 + halfI, x2 - halfI):
                    for z in range(z1, z2):
                        setBlock(x, y2 + halfI, z, randomPeakRoof)
        else:
            # same as above but with x and z swapped
            for i in range(0, z2 - z1, 2):
                halfI = int(i / 2)
                for z in range(z1 + halfI, z2 - halfI):
                    for x in range(x1, x2):
                        setBlock(x, y2 + halfI, z, randomPeakRoof)
    else:
        # add roof slab
        for y in range(y2-1, y2+2):
            for x in range(x1, x2):
                for z in range(z1, z2):
                    setBlock(x, y, z, randomWall)

        # add crenellations on roof
        for y in range(y2+2, y2+4):
            for x in range(x1, x2):
                for z in range(z1, z2):
                    if x % 2 == 0 and z % 2 == 0:
                        setBlock(x, y, z, randomWall)

        for y in range (y2+2, y2+4):
            for x in range(x1+1, x2-1):
                for z in range(z1+1, z2-1):
                    setBlock(x, y, z, "air")

        for x in range(x1+2, x2-2):
            for z in range(z1+2, z2-2):
                setBlock(x, y2+1, z, "air")

    #corners
    for dx in range(2):
        for dz in range(2):
            x = x1 + dx * (x2 - x1 - 1)
            z = z1 + dz * (z2 - z1 - 1)
            for y in range(y1, y2):
                setBlock(x, y, z, randomColumn)
    print("House erected")
    
def addInterior(x1, y1, z1, x2, y2, z2):
    randomTorch = random.choice(wallTorch)
    randomBed = random.choice(beds)
    randomWall = random.choice(walls)
    randomLantern = random.choice(lantern)
    print("Furnishing the house")
    # clear interior
    for y in range(y1 + 1, y2):
        for x in range(x1 + 1, x2 - 1):
            for z in range(z1 + 1, z2 - 1):
                setBlock(x, y, z, "air")

    # center partition wall
    for y in range(y1 + 1, y2):
        for x in range(x1+1, x2-1):
            setBlock(x, y, z1+7, randomWall)

    # open walkthrough
    for y in range(y1+1, y1+3):
        for x in range(x1+4, x1+7):
            setBlock(x, y, z1+7, "air")
    
    # set seating area and kitchen
    i = 1
    for z in range(z1+i, z1+7):
        if i%2 == 0:
            setBlock(x2-2, y1+1, z, "nether_brick_slab[type=bottom]")
            setBlock(x1+1, y1+1, z, "furnace[lit=true,facing=east]")
        else:
            setBlock(x2-2, y1+1, z, "nether_brick_slab[type=double]")
            setBlock(x1+1, y1+1, z, "acacia_log")
        i += 1

    # torch
    setBlock(x1+1, y1+3, z1+1, randomTorch+"[facing=south]")
    setBlock(x2-2, y1+3, z1+1, randomTorch+"[facing=south]")
    setBlock(x2-2, y1+3, z2-2, randomTorch+"[facing=north]")
    setBlock(x1+1, y1+3, z2-2, randomTorch+"[facing=north]")

    # pots
    pot1 = random.choice(pots)
    setBlock(x2-2, y1+1, z2-2, pot1)
    setBlock(x1+1, y1+1, z2-2, pot1)

    # bed
    setBlock(x1+5, y1+1, z2-2, randomBed+"[part=head, facing=south]")
    setBlock(x1+5, y1+1, z2-3, randomBed+"[part=foot, facing=south]")

    # chest
    setBlock(x1+7, y1+1, z2-2, "chest")

    # lanterns
    setBlock(x1+5, y1+3, z2-2, randomLantern+"[hanging=true]")
    # side
    setBlock(x1+1, y1+4, z2-6, randomLantern+"[hanging=true]")
    setBlock(x2-2, y1+4, z2-6, randomLantern+"[hanging=true]")
    setBlock(x1+1, y1+4, z1+5, randomLantern+"[hanging=true]")
    setBlock(x2-2, y1+4, z1+5, randomLantern+"[hanging=true]")

    #dragon heads
    setBlock(int((x1+x2)/2), y2+1, z1-1, "dragon_wall_head")

    # furnace
    setBlock(x2-2, y1+1, z2-6, "blast_furnace"+"[facing=west,lit=true]")

    # 3x5 carpet
    for x in range(x1+4, x1+7):
        for z in range(z1+3, z1+8):
            setBlock(x, y1+1, z, "red_carpet")
            if x==x1+5 and z==z1+5:
                setBlock(x, y1+1, z, random.choice(pots))

    
