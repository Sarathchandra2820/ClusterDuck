# import stuff ... 
from clusterduck import *
from clusterduck.jobs import args

args = args.ArgParses()

XYZ = args.xyz()
BASIS = args.basis(default = "aug-cc-pvdz")
METHOD = args.method(default = "mp2")


print(args.list_arguments())