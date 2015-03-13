from input import loop, select_device

__author__ = 'zh'


def main():
    device = select_device()
    loop(device)


if __name__ == '__main__':
    main()
