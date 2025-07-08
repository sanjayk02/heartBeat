cmd = [
    r"W:/user/maya/python/LCToolSet/standalone/openImageio_1.7.3dev/bin/oiiotool.exe",
    "-v", "--debug", "--runstats",
    "-d", "half",
    "--compression", "pxr24",
    "--tile", "64",
    "-i", r"W:/assets/character/peter/peterCasualA/MDL/AH/r0018/TEX/backpackGenericA_LIT.0000.tif",
    "--iscolorspace", "sRGB",
    "--tocolorspace", "linear",
    "-otex", r"E:/Sanjay/tools/maya2022/AssetDelivery/backpackGenericA_LIT.0000.exr"
]
subprocess.call(cmd)
