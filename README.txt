This program uses Kraken API and Moving average convergence/divergence to determine which cryptos to sell and buy


For Running in Jupyter Notebook: Create a cell above containing

!pip install krakenex

------------------------------------------------------------------------------

For running as an exe (windows):
do not add !pip install krakenex
create a folder, install python into it
save code as .py in the folder you just created

Win+R
cmd
cd path\to\your\project\folder
python -m venv myenv
myenv\Scripts\activate
pip install krakenex pandas
pip install pyinstaller
pyinstaller --onefile your_script_name.py

go to folder\dist where youll find the .exe

.exe can run without supporting files
------------------------------------------------------------------------------

If you want to change which currency pairs are used, in jupyter notebook, run the following code. It will output all valid currency pairs, and the minimum amount of each pair that can be traded in one transaction. You can use this to alter the code to trade only the currency pairs you want to trade

Cell 1
!pip install krakenex
Cell 2
import krakenex

def fetch_minimum_order_sizes():
    api = krakenex.API()
    response = api.query_public('AssetPairs')
    
    if response.get('error'):
        print("Error fetching asset pair information:", response['error'])
        return

    min_order_sizes = {}
    for pair_name, pair_info in response['result'].items():
        # Extracting the pair's minimum order size
        min_order_sizes[pair_name] = pair_info['ordermin']

    return min_order_sizes

min_order_sizes = fetch_minimum_order_sizes()
if min_order_sizes:
    for pair, min_size in min_order_sizes.items():
        print(f"{pair}: Minimum order size = {min_size}")


