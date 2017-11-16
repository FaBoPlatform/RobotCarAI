# coding: utf-8

import time
import sys
from kerberos import Kerberos

print("start")

kerberos = Kerberos()

try:
    for i in range(0,300):
        distance1,distance2,distance3 = kerberos.get_distance()
        sys.stdout.write("Distance to target = "+str(distance1)+", "+str(distance2)+", "+str(distance3)+"         \r")
        sys.stdout.flush()
        time.sleep(0.022)
    print("")
    sys.stdout.flush()

except:
    import traceback
    traceback.print_exc()
finally:
    pass

print("end")
