import sys

if __name__ == '__main__':
    import matplotlib.pyplot as plt
    import matplotlib.image as mpimg
    if not sys.argv[7] == True:
        plt.rcParams['toolbar'] = 'None'
    plt.rcParams['figure.figsize'] = (float(sys.argv[3]), float(sys.argv[4]))
    plt.axis("off")
    if sys.argv[6] == False:
        pass
    plt.gcf().canvas.set_window_title(sys.argv[2])
    path = sys.argv[1]
    imgplot = plt.imshow(mpimg.imread(path), interpolation = sys.argv[5])
    plt.show()



