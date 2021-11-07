# UniPD-MeS-2022
Personal repository for unipd course "Modelli e software per l'ottimizzazione discreta" 

## Use user defined functions w/o having a copy in every subfolder
Use this piece of code to use functions defined in myFunctions.py file from each subfolder without having a copy in everyone of it.
```python
import sys
from os.path import dirname, abspath
sys.path.append(dirname(dirname(abspath(__file__))))
import myFunctions
```