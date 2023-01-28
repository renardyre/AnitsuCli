import ueberzug.lib.v0 as ueberzug
import shutil
import os

def main():
    P = 0.42
    SCRIPT_PATH = os.path.dirname(__file__)
    UB_FIFO = os.path.join(SCRIPT_PATH, '.img_list')
    COL = shutil.get_terminal_size().columns * P
    
    with ueberzug.Canvas() as canvas:
        pv = canvas.create_placement(
            'pv', x=COL, y=1, height=19,
            scaler=ueberzug.ScalerOption.DISTORT.value
        )
        while True:
            with open(UB_FIFO, 'r') as fifo:
                img = fifo.read().strip()
    
            COL = shutil.get_terminal_size().columns * P
            
            if "jpg" not in img:
                break
    
            pv.x = COL
            pv.path = img
            pv.visibility = ueberzug.Visibility.VISIBLE

if __name__ == "__main__":
    main()
