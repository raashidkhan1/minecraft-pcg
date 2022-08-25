import interfaceUtils
import mapUtils
from worldLoader import WorldSlice
from buildUtils import buildFence, buildHouse, addInterior, USE_BATCHING, checkBuildArea

# x position, z position, x size, z size
# area = (0, 0, 50, 50)  # default build area example

area = ()

# see if a build area has been specified
# you can set a build area in minecraft using the /setbuildarea command
buildArea = interfaceUtils.requestBuildArea()
if buildArea != -1:
    x1 = buildArea["xFrom"]
    z1 = buildArea["zFrom"]
    x2 = buildArea["xTo"]
    z2 = buildArea["zTo"]
    # print(buildArea)
    area = (x1, z1, x2 - x1, z2 - z1)
else:
    print("Please re-run the script after setting build area :(")
    quit()

if __name__ == '__main__':
    """Generate a village within the target area."""
    print(f"Build area is at position {area[0]}, {area[1]} with size {area[2]}, {area[3]}")

    # load the world data
    # this uses the /chunks endpoint in the background
    worldSlice = WorldSlice(area)

    # calculate a heightmap suitable for building:
    heightmap = mapUtils.calcGoodHeightmap(worldSlice)

    # build a fence around the perimeter
    buildFence(area, heightmap)

    houseSizeX = 11
    houseSizeZ = 15
    
    # print(area)
    houseSizeY = 10

    # check feasibility
    feasibleArea = checkBuildArea(heightmap, area, houseSizeX, houseSizeZ)

    # build house
    buildHouse(
                feasibleArea[0], 
                feasibleArea[1], 
                feasibleArea[2], 
                feasibleArea[0]+houseSizeX, 
                feasibleArea[1]+houseSizeY, 
                feasibleArea[2]+houseSizeZ
            )

    # add interior
    addInterior(
                feasibleArea[0], 
                feasibleArea[1], 
                feasibleArea[2], 
                feasibleArea[0]+houseSizeX, 
                feasibleArea[1]+houseSizeY, 
                feasibleArea[2]+houseSizeZ
            )

    if USE_BATCHING:
        # we need to send any blocks remaining in the buffer
        interfaceUtils.sendBlocks()