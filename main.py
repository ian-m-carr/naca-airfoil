import math
import xml.etree.ElementTree as etree
from collections.abc import Iterable


# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

class Airfoil:
    NP = 0

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

    def __init__(self, num_points: int = 100):
        self.NP = num_points
        self.XCC = [0.0] * self.NP
        self.XU = [0.0] * self.NP
        self.YU = [0.0] * self.NP
        self.XL = [0.0] * self.NP
        self.YL = [0.0] * self.NP
        self.YT = [0.0] * self.NP
        self.YC = [0.0] * self.NP
        self.DYC = [0.0] * self.NP

        self.YLED = [0.0] * self.NP

    def calc_theta(self, SVAL) -> float:
        if SVAL == 0:
            return 0
        if SVAL == 1:
            return math.pi / 2
        if SVAL == -1:
            return -math.pi / 2
        return math.atan(SVAL / math.sqrt(1 - math.pow(SVAL, 2)))

    def set_coord_spacing(self, spacing: int):
        match spacing:
            case 1:
                DELTH = 1 / (self.NP - 1)
                for I in range(self.NP):
                    self.XCC[I] = DELTH * (I)
            case 2:
                DELTH = math.pi / 2 / (self.NP - 1)
                for I in range(self.NP):
                    self.XCC[I] = 1 - math.cos(DELTH * (I))
            case 3:
                DELTH = math.pi / 2 / (self.NP - 1)
                for I in range(self.NP):
                    self.XCC[I] = math.cos(math.pi / 2 - DELTH * (I))
            case _:
                # default to Full Cosine
                DELTH = math.pi / (self.NP - 1)
                for I in range(self.NP):
                    self.XCC[I] = .5 - .5 * math.cos(DELTH * (I))

    def naca_four_modified(self, MM: int, PP: int, TOC: int, IP: int, TT: int, LED: float, LEDD: int):
        MC = MM / 100
        PC = PP / 10
        TC = TOC / 100
        TP = TT / 10
        D1 = (2.24 - 5.42 * TP + 12.3 * math.pow(TP, 2)) / 10 / (1 - .878 * TP)
        D2 = (.294 - 2 * (1 - TP) * D1) / math.pow(1 - TP, 2)
        D3 = (-.196 + (1 - TP) * D1) / math.pow(1 - TP, 3)
        A0 = .296904 * IP / 6
        R1 = math.pow(1 - TP, 2) / 5 / (.588 - 2 * D1 * (1 - TP))
        AA1 = .3 / TP - 15 * A0 / 8 / math.sqrt(TP) - TP / 10 / R1
        A2 = -.3 / math.pow(TP, 2) + 5 * A0 / 4 / math.pow(TP, 1.5) + 1 / 5 / R1
        A3 = .1 / math.pow(TP, 3) - .375 * A0 / math.pow(TP, 2.5) - 1 / 10 / R1 / TP

        for I in range(self.NP):
            if self.XCC[I] > TP:
                self.YT[I] = 5 * TC * (.002 + D1 * (1 - self.XCC[I]) + D2 * math.pow(1 - self.XCC[I], 2) + D3 * math.pow(1 - self.XCC[I], 3))
            else:
                self.YT[I] = 5 * TC * (A0 * math.sqrt(self.XCC[I]) + AA1 * self.XCC[I] + A2 * math.pow(self.XCC[I], 2) + A3 * math.pow(self.XCC[I], 3))

            if MM == 0: continue

            if self.XCC[I] > PC:
                self.YC[I] = MC / math.pow(1 - PC, 2) * (1 - 2 * PC + 2 * PC * self.XCC[I] - math.pow(self.XCC[I], 2))
                self.DYC[I] = 2 * MC / math.pow(1 - PC, 2) * (PC - self.XCC[I])
            else:
                self.YC[I] = MC / PC ^ 2 * (2 * PC * self.XCC[I] - math.pow(self.XCC[I], 2))
                self.DYC[I] = 2 * MC / PC ^ 2 * (PC - self.XCC[I])

        if LED > 0 and LEDD > 0:
            for I in range(self.NP):
                # do we have any droop to add to camber
                if self.XCC[I] < LEDD / 10:
                    self.YLED[I] = LED * math.pow(1 - (self.XCC[I] / (LEDD / 10)), 2)

        self.LER = 1.1019 * math.pow(IP / 6 * TC, 2)
        if IP >= 9:
            LER = 3 * 1.1019 * math.pow(TC, 2)

        self.TEANG = 2 * math.atan(1.16925 * TC)

        DESIG = MM * 1000 + PP * 1000 + TOC
        SESIG = IP * 10 + TT
        self.DESIG_str = "{:04d}".format(DESIG) + "-" + "{:02d}".format(SESIG)

        # now derive the surfaces
        for I in range(self.NP):
            THET = 0  # math.atan(DYC[I])
            self.XU[I] = self.XCC[I] - self.YT[I] * math.sin(THET)
            self.YU[I] = self.YC[I] + self.YT[I] * math.cos(THET) - self.YLED[I]
            self.XL[I] = self.XCC[I] + self.YT[I] * math.sin(THET)
            self.YL[I] = self.YC[I] - self.YT[I] * math.cos(THET) - self.YLED[I]

    def naca_five_modified(self, LL: int, PP: int, QQ: int, TOC: int, IP: int, TT: int, LED: float, LEDD: int):
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

        THETA = self.calc_theta(SVAL)

        QC = (3 * MC - 7 * math.pow(MC, 2) + 8 * math.pow(MC, 3) - 4 * math.pow(MC, 4)) / math.sqrt(MC * (1 - MC)) - 1.5 * (1 - 2 * MC) * (math.pi / 2 - THETA)
        K1 = 9 * LC / QC
        K2K1 = (3 * math.pow((MC - PC), 2) - math.pow(MC, 3)) / math.pow((1 - MC), 3)

        for I in range(self.NP):
            # thickness distribution (before/after max thickness position)
            if self.XCC[I] > TP:
                self.YT[I] = 5 * TC * (.002 + D1 * (1 - self.XCC[I]) + D2 * math.pow((1 - self.XCC[I]), 2) + D3 * math.pow((1 - self.XCC[I]), 3))
            else:
                self.YT[I] = 5 * TC * (A0 * math.sqrt(self.XCC[I]) + AA1 * self.XCC[I] + A2 * math.pow(self.XCC[I], 2) + A3 * math.pow(self.XCC[I], 3))

            if LL == 0: continue  # LL is lift, 0 implies no lift, eg tail fin or strake

            # camber distribution
            if QQ == 0:  # normal camber curve
                if self.XCC[I] > MC:  # Back
                    self.YC[I] = (K1 / 6) * math.pow(MC, 3) * (1 - self.XCC[I])
                    self.DYC[I] = (-K1 / 6) * math.pow(MC, 3)
                else:  # Front
                    self.YC[I] = (K1 / 6) * (math.pow(self.XCC[I], 3) - 3 * MC * math.pow(self.XCC[I], 2) + math.pow(MC, 2) * (3 - MC) * self.XCC[I])
                    self.DYC[I] = (K1 / 6) * (3 * math.pow(self.XCC[I], 2) - 6 * MC * self.XCC[I] + math.pow(MC, 2) * (3 - MC))
            else:  # reflex camber curve
                if self.XCC[I] > MC:  # Back
                    self.YC[I] = (K1 / 6) * (
                            K2K1 * math.pow((self.XCC[I] - MC), 3) - K2K1 * math.pow((1 - MC), 3) * self.XCC[I] - math.pow(MC, 3) * self.XCC[I] + math.pow(
                        MC, 3))
                    self.DYC[I] = (K1 / 6) * (3 * K2K1 * math.pow((self.XCC[I] - MC), 2) - K2K1 * math.pow((1 - MC), 3) - math.pow(MC, 3))
                else:  # Front
                    self.YC[I] = (K1 / 6) * (
                            math.pow((self.XCC[I] - MC), 3) - K2K1 * math.pow((1 - MC), 3) * self.XCC[I] - math.pow(MC, 3) * self.XCC[I] + math.pow(MC, 3))
                    self.DYC[I] = (K1 / 6) * (3 * math.pow((self.XCC[I] - MC), 2) - K2K1 * math.pow((1 - MC), 3) - math.pow(MC, 3))

        if LED > 0 and LEDD > 0:
            for I in range(self.NP):
                # do we have any droop to add to camber
                if self.XCC[I] < LEDD / 10:
                    self.YLED[I] = LED * math.pow(1 - (self.XCC[I] / (LEDD / 10)), 2)

        # leading edge radius
        self.LER = 1.1019 * math.pow((IP / 6 * TC), 2)

        if IP >= 9:
            self.LER = 3 * 1.1019 * math.pow((TC), 2)

        # trailing edge angle
        self.TEANG = 2 * math.atan(1.16925 * TC)

        # designation
        DESIG = LL * 10000 + PP * 1000 + QQ * 100 + TOC
        self.DESIG_str = str(DESIG)

        # modification designation
        SESIG = IP * 10 + TT
        self.DESIG_str = "{:05d}".format(self.DESIG_str) + "-" + "{:02d}".format(SESIG)

        # now derive the surfaces
        for I in range(self.NP):
            THET = 0  # math.atan(DYC[I])
            self.XU[I] = self.XCC[I] - self.YT[I] * math.sin(THET)
            self.YU[I] = self.YC[I] + self.YT[I] * math.cos(THET) - self.YLED[I]
            self.XL[I] = self.XCC[I] + self.YT[I] * math.sin(THET)
            self.YL[I] = self.YC[I] - self.YT[I] * math.cos(THET) - self.YLED[I]

    def plot_svg(self, container: etree.Element, vert_offset: float) -> float:
        all_x = self.XU + self.XL
        minx = math.floor(min(all_x) * 100) - 1
        maxx = math.ceil(max(all_x) * 100) + 1
        all_y = self.YL + self.YU
        miny = math.floor(min(all_y) * 100) - 1
        maxy = math.ceil(max(all_y) * 100) + 1

        el_tx1 = etree.SubElement(container, "g", transform="translate(5,{})".format(vert_offset + maxy))
        el_tx2 = etree.SubElement(el_tx1, "g", transform="scale(.9,-.9)")  # scale so that 0-100 x fills 90 percent of the width

        # vertical divisions every 10
        for x in range(1, 101):
            if x % 10 == 0:
                x_pos = str(x)
                el_line = etree.SubElement(el_tx2, "line", fill='none', x1=x_pos, x2=x_pos, y1=str(miny), y2=str(maxy))
                el_line.set('stroke-width', '0.1')
                el_line.set('stroke', 'darkgreen')
            elif x % 5 == 0:
                x_pos = str(x)
                el_line = etree.SubElement(el_tx2, "line", fill='none', x1=x_pos, x2=x_pos, y1=str(miny), y2=str(maxy))
                el_line.set('stroke-width', '0.05')
                el_line.set('stroke', 'green')

        # horizontal divisions every 1
        for y in range(1, maxy + 1):
            y_pos = str(y)
            el_line = etree.SubElement(el_tx2, "line", fill="none", x1=str(minx), x2=str(maxx), y1=y_pos, y2=y_pos)
            if y % 5 == 0:
                el_line.set('stroke-width', '0.1')
                el_line.set('stroke', 'darkgreen')
            else:
                el_line.set('stroke-width', '0.05')
                el_line.set('stroke', 'green')

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
        el_line = etree.SubElement(el_tx2, "line", fill="none", stroke="black", x1=str(minx - 1), x2=str(maxx + 1), y1="0", y2="0")
        el_line.set('stroke-width', '0.1')

        # y axis
        el_line = etree.SubElement(el_tx2, "line", fill="none", stroke="black", x1="0", x2="0", y1=str(miny - 1), y2=str(maxy + 1))
        el_line.set('stroke-width', '0.1')

        # the airfoil curve
        el_path = etree.SubElement(el_tx2, "path", fill="none", stroke="red",
                                   d=self.profile_to_svg_path())
        el_path.set('stroke-width', '0.2')

        # text block
        """
        <g transform="translate(0,18.1424)">
		<g transform="scale(1,1)">
			<text fill="rgb(48,48,144)" font-size="1.8" style="font-family:Arial,Helvetica,sans-serif;" x="1" y="2">Name = NACA 24012 Airfoil cl=0.30 T=12.0% P=20.0%</text>
			<text fill="rgb(48,48,144)" font-size="1.8" style="font-family:Arial,Helvetica,sans-serif;" x="1" y="4">Chord = 100mm  Radius = 0mm  Thickness = 100%  Origin = 0%  Pitch = 0&#176; </text>
		</g>
        </g>
        """
        el_tx1 = etree.SubElement(container, "g", transform="translate(5,{})".format(vert_offset + (maxy - miny)))
        el_tx2 = etree.SubElement(el_tx1, "g", transform="scale(.9,.9)")  # scale so that 0-100 x fills 90 percent of the width

        el_txt = etree.SubElement(el_tx2, "text", fill="rgb(48,48,144)", style="font-family:Arial,Helvetica,sans-serif;", x="1", y="2")
        el_txt.set("font-size", "1.8")
        el_txt.text = "Name: " + self.DESIG_str

        # additional info
        # el_txt = etree.SubElement(el_tx2, "text", fill="rgb(48,48,144)", style="font-family:Arial,Helvetica,sans-serif;", x="1", y="4")
        # el_txt.set("font-size","1.8")
        # el_txt.text = ""

        # return the height of the profile maximum + minimum (-ve)
        return maxy - miny + 5

    def profile_to_svg_path(self) -> str:
        path = ""
        step_type = "M "  # begin with a move

        fmt = "{:.2f} {:.2f}"
        # backward along the upper surface
        for I in range(self.NP - 1, -1, -1):
            path += step_type + fmt.format(self.XU[I] * 100, self.YU[I] * 100)
            step_type = " L "  # after first we want line to

        # then forward along the lower
        for I in range(self.NP):
            path += step_type + fmt.format(self.XL[I] * 100, self.YL[I] * 100)

        # finally close the path at the trailing edge
        if self.YU[self.NP - 1] != self.YL[self.NP - 1]:
            path += step_type + fmt.format(self.XU[self.NP - 1] * 100, self.YU[self.NP - 1] * 100)

        return path


def plot_svg(filename: str, airfoils: Iterable[Airfoil]):
    # A4 = 210mmx297mm 297/210 = 1.4143
    root = etree.Element('svg',
                         width="210mm", height="297mm",  # A4 paper size
                         viewBox="0 0 100 141.3",  # scale viewport for a "square" coordinate grid
                         version='1.1', xmlns='http://www.w3.org/2000/svg')

    el = etree.SubElement(root, "title")
    el.text = "Airfoil plot"

    y_offset = 5
    for airfoil in airfoils:
        y_offset += airfoil.plot_svg(root, y_offset)

    tree = etree.ElementTree(root)
    with open(filename, "wb") as files:
        tree.write(files)


def do_naca_four() -> Airfoil:
    print("Create A NACA 4 Digit (Modified) Airfoil\n")
    MM = int(input(" Enter The First Digit Of The 4 (the maximum camber divided by 100): [0]") or 0)
    PP = int(input(" Enter The Second Digit Of The 5 (the position of the maximum camber divided by 10) : [0]") or 0)
    TOC = int(input(" Enter The Last Two Digits Of The 5 (max thickness percentage) : [18]") or 18)

    IP = int(input(" Enter The First Digit of the modification (6 = original LE curvature) : [6]") or 6)
    TT = int(input(" Enter The Second Digit Of modification (position in 1/10 chord of max thickness default 0.3) : [3]") or 3)

    # optionally add a leading edge droop
    LED = float(input(" Enter The leading edge droop distance (at LE) : [0]") or 0)
    if LED != 0.0:
        LEDD = int(input(" Enter The chord length over which droop is introduced (position in 1/10 chord from LE) : [0]") or 0)
    else:
        LEDD = 0.0

    # construct the airfoil
    af = Airfoil(np)

    # and set it's spacing
    af.set_coord_spacing(spacing)

    # calculate the profile
    af.naca_four_modified(MM, PP, TOC, IP, TT, LED, LEDD)

    return af


def do_naca_five() -> Airfoil:
    print("Create A NACA 5 Digit (Modified) Airfoil\n")
    LL = int(input(" Enter The First Digit Of The 5 (Cl * 20/3) 2 -> Cl = 0.3: [2]") or 2)
    PP = int(input(" Enter The Second Digit Of The 5 (position of max camber * 20) 3 = 0.15 or 15% of chord : [3]") or 3)
    QQ = int(input(" Enter The Third Digit Of The 5 (0 normal camber, 1 reflex camber): [0]") or 0)
    TOC = int(input(" Enter The Last Two Digits Of The 5 (max thickness percentage) : [18]") or 18)

    IP = int(input(" Enter The First Digit of the modification (6 = original LE curvature) : [6]") or 6)
    TT = int(input(" Enter The Second Digit Of modification (position in 1/10 chord of max thickness default 0.3) : [3]") or 3)

    # optionally add a leading edge droop
    LED = float(input(" Enter The leading edge droop distance (at LE) : [0]") or 0)
    if LED != 0.0:
        LEDD = int(input(" Enter The chord length over which droop is introduced (position in 1/10 chord from LE) : [0]") or 0)
    else:
        LEDD = 0.0

    # construct the airfoil
    af = Airfoil(np)

    # and set it's spacing
    af.set_coord_spacing(spacing)

    # calculate the profile
    af.naca_five_modified(LL, PP, QQ, TOC, IP, TT, LED, LEDD)

    return af


# the number of points per airfoil surface (* 2 for upper and lower surfaces!)
np = int(input("How Many Points Do You Want Generated : [100] ") or 100)

airfoils = []

# how to distribute the coordinates along the x axis
while (True):
    print("You Have The Following Options For Coordinate Spacing:")
    print("     1 - Equal Spacing")
    print("     2 - Half Cosine With Smaller Increments Near 0")
    print("     3 - Half Cosine With Smaller Increments Near 1")
    print("     4 - Full Cosine")
    spacing = int(input(" Your Choice : [4] ") or 4)

    if spacing < 0 or spacing > 4: continue
    break

# enter the NACA profile and modification digits NNNNN-MM
while True:
    print("choose the specification type:")
    print("     1 - NACA 4 modified")
    print("     2 - NACA 5 modified")
    profile_spec = int(input(" Your Choice : [2] ") or 2)

    if profile_spec == 1:
        airfoils.append(do_naca_four())
    elif profile_spec == 2:
        airfoils.append(do_naca_five())
    else:
        print("unrecognised profile specification!")

    if int(input(" 0 to finish, 1 to continue : [0]") or 0) == 0:
        break

# plot the set of airfoils to an svg file
plot_svg("airfoil.svg", airfoils)

# for i in range(NP):
#    print(i, XU[i], YU[i], XL[i], YL[i])
