import math
import xml.etree.ElementTree as etree

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

NP = 100

XCC = []
XU = []
YU = []
XL = []
YL = []
YT = []
YC = []

YLED = []

DYC = []
XQ = [0.0, 0.0]
YQ = [0.0, 0.0]
ALP = [0.0] * 14


def calc_theta(SVAL) -> float:
    if SVAL == 0:
        return 0
    if SVAL == 1:
        return math.pi / 2
    if SVAL == -1:
        return -math.pi / 2
    return math.atan(SVAL / math.sqrt(1 - math.pow(SVAL, 2)))


def num_points():
    global NP
    global XCC, XU, YU, XL, YL, YT, YC, DYC
    global YLED

    NP = int(input("How Many Points Do You Want Generated : [100] ") or 100)

    XCC = [0.0] * NP
    XU = [0.0] * NP
    YU = [0.0] * NP
    XL = [0.0] * NP
    YL = [0.0] * NP
    YT = [0.0] * NP
    YC = [0.0] * NP
    DYC = [0.0] * NP

    YLED = [0.0] * NP


def coord_spacing():
    while (True):
        print("You Have The Following Options For Coordinate Spacing:")
        print("     1 - Equal Spacing")
        print("     2 - Half Cosine With Smaller Increments Near 0")
        print("     3 - Half Cosine With Smaller Increments Near 1")
        print("     4 - Full Cosine")
        SPAC = int(input(" Your Choice : [4] ") or 4)

        if SPAC < 0 or SPAC > 4: continue

        break

    match SPAC:
        case 1:
            DELTH = 1 / (NP - 1)
            for I in range(NP):
                XCC[I] = DELTH * (I)
        case 2:
            DELTH = math.pi / 2 / (NP - 1)
            for I in range(NP):
                XCC[I] = 1 - math.cos(DELTH * (I))
        case 3:
            DELTH = math.pi / 2 / (NP - 1)
            for I in range(NP):
                XCC[I] = math.cos(math.pi / 2 - DELTH * (I))
        case _:
            # default to Full Cosine
            DELTH = math.pi / (NP - 1)
            for I in range(NP):
                XCC[I] = .5 - .5 * math.cos(DELTH * (I))

    """
    DELTH = math.pi / (NP -1)
    for I in range(NP):
        XCC[I] = .5 - .5 * math.cos(DELTH * I)
    """

def naca_five_modified():
    global NP
    global XCC, YT, DYC, YLED

    print("You Have Chosen To Create A NACA Modified 5 Digit Airfoil\n")
    LL = int(input(" Enter The First Digit Of The 5 (Cl * 20/3) 2 -> Cl = 0.3: [2]") or 2)
    PP = int(input(" Enter The Second Digit Of The 5 (position of max camber * 20) 3 = 0.15 or 15% of chord : [3]") or 3)
    QQ = int(input(" Enter The Third Digit Of The 5 (0 normal camber, 1 reflex camber): [0]") or 0)
    TOC = int(input(" Enter The Last Two Digits Of The 5 (max thickness percentage) : [18]") or 18)
    IP = int(input(" Enter The First Digit of the modification (6 = original LE curvature) : [6]") or 6)
    TT = int(input(" Enter The Second Digit Of modification (position in 1/10 chord of max thickness default 0.3) : [3]") or 3)

    LED = float(input(" Enter The leading edge droop distance (at LE) : [0]") or 0)
    LEDD = int(input(" Enter The chord length over which droop is introduced (position in 1/10 chord from LE) : [0]") or 0)

    if QQ < 0 or QQ > 1:
        raise Exception("third digit should be 0 (normal) or 1 (reflex) for camber line")

    LC = LL / 10
    PC = PP / 20
    TC = TOC / 100
    MC = PC / 2
    TP = TT / 10
    D1 = (2.24 - 5.42 * TP + 12.3 * math.pow(TP, 2)) / 10 / (1 - .878 * TP)
    D2 = (.294 - 2 * (1 - TP) * D1) / math.pow((1 - TP), 2)
    D3 = (-.196 + (1 - TP) * D1) / math.pow((1 - TP), 3)
    A0 = .296904 * IP / 6
    R1 = math.pow((1 - TP), 2) / 5 / (.588 - 2 * D1 * (1 - TP))
    AA1 = .3 / TP - 15 * A0 / 8 / math.sqrt(TP) - TP / 10 / R1
    A2 = -.3 / math.pow(TP, 2) + 5 * A0 / 4 / math.pow(TP, (1.5)) + 1 / 5 / R1
    A3 = .1 / math.pow(TP, 3) - .375 * A0 / math.pow(TP, (2.5)) - 1 / 10 / R1 / TP

    while (True):
        PCT = math.sqrt(math.pow(MC, 2) * (MC / 3 - 2 * math.sqrt(MC / 3) + 1))
        if abs(PC - PCT) <= .0001:
            break

        MC = MC * PC / PCT

    SVAL = 1 - 2 * MC

    THETA = calc_theta(SVAL)

    QC = (3 * MC - 7 * math.pow(MC, 2) + 8 * math.pow(MC, 3) - 4 * math.pow(MC, 4)) / math.sqrt(MC * (1 - MC)) - 1.5 * (1 - 2 * MC) * (math.pi / 2 - THETA)
    K1 = 9 * LC / QC
    K2K1 = (3 * math.pow((MC - PC), 2) - math.pow(MC, 3)) / math.pow((1 - MC), 3)

    for I in range(NP):
        # thickness distribution (before/after max thickness position)
        if XCC[I] > TP:
            YT[I] = 5 * TC * (.002 + D1 * (1 - XCC[I]) + D2 * math.pow((1 - XCC[I]), 2) + D3 * math.pow((1 - XCC[I]), 3))
        else:
            YT[I] = 5 * TC * (A0 * math.sqrt(XCC[I]) + AA1 * XCC[I] + A2 * math.pow(XCC[I], 2) + A3 * math.pow(XCC[I], 3))

        if LL == 0: continue  # LL is lift, 0 implies no lift, eg tail fin or strake

        # camber distribution
        if QQ == 0:  # normal camber curve
            if XCC[I] > MC:  # Back
                YC[I] = (K1 / 6) * math.pow(MC, 3) * (1 - XCC[I])
                DYC[I] = (-K1 / 6) * math.pow(MC, 3)
            else:  # Front
                YC[I] = (K1 / 6) * (math.pow(XCC[I], 3) - 3 * MC * math.pow(XCC[I], 2) + math.pow(MC, 2) * (3 - MC) * XCC[I])
                DYC[I] = (K1 / 6) * (3 * math.pow(XCC[I], 2) - 6 * MC * XCC[I] + math.pow(MC, 2) * (3 - MC))
        else:  # reflex camber curve
            if XCC[I] > MC:  # Back
                YC[I] = (K1 / 6) * (K2K1 * math.pow((XCC[I] - MC), 3) - K2K1 * math.pow((1 - MC), 3) * XCC[I] - math.pow(MC, 3) * XCC[I] + math.pow(MC, 3))
                DYC[I] = (K1 / 6) * (3 * K2K1 * math.pow((XCC[I] - MC), 2) - K2K1 * math.pow((1 - MC), 3) - math.pow(MC, 3))
            else:  # Front
                YC[I] = (K1 / 6) * (math.pow((XCC[I] - MC), 3) - K2K1 * math.pow((1 - MC), 3) * XCC[I] - math.pow(MC, 3) * XCC[I] + math.pow(MC, 3))
                DYC[I] = (K1 / 6) * (3 * math.pow((XCC[I] - MC), 2) - K2K1 * math.pow((1 - MC), 3) - math.pow(MC, 3))

    if LED > 0 and LEDD > 0:
        for I in range(NP):
            # do we have any droop to add to camber
            if XCC[I] < LEDD / 10:
                YLED[I] = LED * math.pow(1 - (XCC[I] / (LEDD / 10)), 2)

    # leading edge radius
    LER = 1.1019 * math.pow((IP / 6 * TC), 2)

    if IP >= 9:
        LER = 3 * 1.1019 * math.pow((TC), 2)

    # trailing edge angle
    TEANG = 2 * math.atan(1.16925 * TC)

    # designation
    DESIG = LL * 10000 + PP * 1000 + QQ * 100 + TOC
    DESIG_str = str(DESIG)

    # modification designation
    SESIG = IP * 10 + TT
    DESIG_str = DESIG_str + "-" + str(SESIG)

    print("Leading edge radius : " + str(LER))
    print("Trailing edge angle : " + str(TEANG))

    print(DESIG_str)


def derive_surfaces():
    global XU, YU, XL, YL
    for I in range(NP):
        THET = 0  # math.atan(DYC[I])
        XU[I] = XCC[I] - YT[I] * math.sin(THET)
        YU[I] = YC[I] + YT[I] * math.cos(THET) - YLED[I]
        XL[I] = XCC[I] + YT[I] * math.sin(THET)
        YL[I] = YC[I] - YT[I] * math.cos(THET) - YLED[I]


def plot_svg(fileName: str):
    all_x = XU + XL
    minx = math.floor(min(all_x) * 100) - 1
    maxx = math.ceil(max(all_x) * 100) + 1
    all_y = YL + YU
    miny = math.floor(min(all_y) * 100) - 1
    maxy = math.ceil(max(all_y) * 100) + 1

    root = etree.Element('svg', width="1024", height="768", viewBox="0 0 102 76", version='1.1', xmlns='http://www.w3.org/2000/svg')
    el = etree.SubElement(root, "title")
    el.text = "Airfoil plot"

    el_tx1 = etree.SubElement(root, "g", transform="translate(3,20)")
    el_tx2 = etree.SubElement(el_tx1, "g", transform="scale(.9,-.9)")

    # vertical divisions every 10
    for x in range(1, 101):
        if x % 10 == 0:
            x_pos = str(x)
            el_line = etree.SubElement(el_tx2, "line", fill='none', x1=x_pos, x2=x_pos, y1=str(miny), y2=str(maxy))
            el_line.set('stroke-width', '0.1')
            el_line.set('stroke','darkgreen')
        elif x % 5 == 0:
            x_pos = str(x)
            el_line = etree.SubElement(el_tx2, "line", fill='none', x1=x_pos, x2=x_pos, y1=str(miny), y2=str(maxy))
            el_line.set('stroke-width', '0.05')
            el_line.set('stroke','green')

    # horizontal divisions every 1
    for y in range(1, maxy + 1):
        y_pos = str(y)
        el_line = etree.SubElement(el_tx2, "line", fill="none", x1=str(minx), x2=str(maxx), y1=y_pos, y2=y_pos)
        if y % 5 == 0:
            el_line.set('stroke-width', '0.1')
            el_line.set('stroke','darkgreen')
        else:
            el_line.set('stroke-width', '0.05')
            el_line.set('stroke','green')

    for y in range(-1, miny - 1, -1):
        y_pos = str(y)
        el_line = etree.SubElement(el_tx2, "line", fill="none", x1=str(minx), x2=str(maxx), y1=y_pos, y2=y_pos)
        if y % 5 == 0:
            el_line.set('stroke-width', '0.1')
            el_line.set('stroke', 'darkgreen')
        else:
            el_line.set('stroke-width', '0.05')
            el_line.set('stroke', 'green')

    # x axis
    el_line = etree.SubElement(el_tx2, "line", fill="none", stroke="black", x1=str(minx -1), x2=str(maxx + 1), y1="0", y2="0")
    el_line.set('stroke-width', '0.1')

    # y axis
    el_line = etree.SubElement(el_tx2, "line", fill="none", stroke="black", x1="0", x2="0", y1=str(miny-1), y2=str(maxy+1))
    el_line.set('stroke-width', '0.1')

    # the airfoil curve
    el_path = etree.SubElement(el_tx2, "path", fill="none", stroke="red",
                               d=profile_to_svg_path())
    el_path.set('stroke-width', '0.2')

    tree = etree.ElementTree(root)
    with open(fileName, "wb") as files:
        tree.write(files)


def profile_to_svg_path() -> str:
    path = ""
    step_type = "M "  # begin with a move

    fmt = "{:.2f} {:.2f}"
    # backward along the upper surface
    for I in range(NP - 1, -1, -1):
        path += step_type + fmt.format(XU[I] * 100, YU[I] * 100)
        step_type = " L "  # after first we want line to

    # then forward along the lower
    for I in range(NP):
        path += step_type + fmt.format(XL[I] * 100, YL[I] * 100)

    return path


num_points()
coord_spacing()
naca_five_modified()
derive_surfaces()
plot_svg("airfoil.svg")

# for i in range(NP):
#    print(i, XU[i], YU[i], XL[i], YL[i])
