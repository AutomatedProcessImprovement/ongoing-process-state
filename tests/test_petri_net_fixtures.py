from ongoing_process_state.petri_net import PetriNet


def _petri_net_with_AND_and_XOR() -> PetriNet:
    petri_net = PetriNet()
    petri_net._cached_search = False
    petri_net.add_place("0", "p0")
    petri_net.add_place("2", "p2")
    petri_net.add_place("3", "p3")
    petri_net.add_place("6", "p6")
    petri_net.add_place("7", "p7")
    petri_net.add_place("9", "p9")
    petri_net.add_place("12", "p12")
    petri_net.add_place("14", "p14")
    petri_net.add_transition("1", "A")
    petri_net.add_transition("4", "B")
    petri_net.add_transition("5", "C")
    petri_net.add_transition("10", "D")
    petri_net.add_transition("11", "E")
    petri_net.add_transition("13", "F")
    petri_net.add_transition("8", "silent_8", invisible=True)
    petri_net.add_edge("0", "1")
    petri_net.add_edge("1", "2")
    petri_net.add_edge("1", "3")
    petri_net.add_edge("2", "4")
    petri_net.add_edge("3", "5")
    petri_net.add_edge("4", "6")
    petri_net.add_edge("5", "7")
    petri_net.add_edge("6", "8")
    petri_net.add_edge("7", "8")
    petri_net.add_edge("8", "9")
    petri_net.add_edge("9", "10")
    petri_net.add_edge("9", "11")
    petri_net.add_edge("10", "12")
    petri_net.add_edge("11", "12")
    petri_net.add_edge("12", "13")
    petri_net.add_edge("13", "14")
    petri_net.initial_marking = {"0"}
    petri_net.final_markings = [{"14"}]
    return petri_net


def _petri_net_with_XOR_within_AND() -> PetriNet:
    petri_net = PetriNet()
    petri_net._cached_search = False
    petri_net.add_place("0", "p0")
    petri_net.add_place("2", "p2")
    petri_net.add_place("4", "p4")
    petri_net.add_place("5", "p5")
    petri_net.add_place("6", "p6")
    petri_net.add_place("13", "p1")
    petri_net.add_place("14", "p1")
    petri_net.add_place("15", "p1")
    petri_net.add_place("16", "p1")
    petri_net.add_place("17", "p1")
    petri_net.add_place("18", "p1")
    petri_net.add_place("25", "p2")
    petri_net.add_place("26", "p2")
    petri_net.add_place("27", "p2")
    petri_net.add_place("28", "p2")
    petri_net.add_place("29", "p2")
    petri_net.add_place("30", "p3")
    petri_net.add_place("37", "p3")
    petri_net.add_place("38", "p3")
    petri_net.add_place("39", "p3")
    petri_net.add_place("41", "p4")
    petri_net.add_place("43", "p4")
    petri_net.add_transition("1", "A")
    petri_net.add_transition("19", "B")
    petri_net.add_transition("20", "C")
    petri_net.add_transition("21", "D")
    petri_net.add_transition("22", "E")
    petri_net.add_transition("23", "F")
    petri_net.add_transition("24", "G")
    petri_net.add_transition("42", "H")
    petri_net.add_transition("3", "silent_3", invisible=True)
    petri_net.add_transition("7", "silent_7", invisible=True)
    petri_net.add_transition("8", "silent_8", invisible=True)
    petri_net.add_transition("9", "silent_9", invisible=True)
    petri_net.add_transition("10", "silent_10", invisible=True)
    petri_net.add_transition("11", "silent_11", invisible=True)
    petri_net.add_transition("12", "silent_12", invisible=True)
    petri_net.add_transition("31", "silent_31", invisible=True)
    petri_net.add_transition("32", "silent_32", invisible=True)
    petri_net.add_transition("33", "silent_33", invisible=True)
    petri_net.add_transition("34", "silent_34", invisible=True)
    petri_net.add_transition("35", "silent_35", invisible=True)
    petri_net.add_transition("36", "silent_36", invisible=True)
    petri_net.add_transition("40", "silent_40", invisible=True)
    petri_net.add_edge("0", "1")
    petri_net.add_edge("1", "2")
    petri_net.add_edge("2", "3")
    petri_net.add_edge("3", "4")
    petri_net.add_edge("3", "5")
    petri_net.add_edge("3", "6")
    petri_net.add_edge("4", "7")
    petri_net.add_edge("4", "8")
    petri_net.add_edge("5", "9")
    petri_net.add_edge("5", "10")
    petri_net.add_edge("6", "11")
    petri_net.add_edge("6", "12")
    petri_net.add_edge("7", "13")
    petri_net.add_edge("8", "14")
    petri_net.add_edge("9", "15")
    petri_net.add_edge("10", "16")
    petri_net.add_edge("11", "17")
    petri_net.add_edge("12", "18")
    petri_net.add_edge("13", "19")
    petri_net.add_edge("14", "20")
    petri_net.add_edge("15", "21")
    petri_net.add_edge("16", "22")
    petri_net.add_edge("17", "23")
    petri_net.add_edge("18", "24")
    petri_net.add_edge("19", "25")
    petri_net.add_edge("20", "26")
    petri_net.add_edge("21", "27")
    petri_net.add_edge("22", "28")
    petri_net.add_edge("23", "29")
    petri_net.add_edge("24", "30")
    petri_net.add_edge("25", "31")
    petri_net.add_edge("26", "32")
    petri_net.add_edge("27", "33")
    petri_net.add_edge("28", "34")
    petri_net.add_edge("29", "35")
    petri_net.add_edge("30", "36")
    petri_net.add_edge("31", "37")
    petri_net.add_edge("32", "37")
    petri_net.add_edge("33", "38")
    petri_net.add_edge("34", "38")
    petri_net.add_edge("35", "39")
    petri_net.add_edge("36", "39")
    petri_net.add_edge("37", "40")
    petri_net.add_edge("38", "40")
    petri_net.add_edge("39", "40")
    petri_net.add_edge("40", "41")
    petri_net.add_edge("41", "42")
    petri_net.add_edge("42", "43")
    petri_net.initial_marking = {"0"}
    petri_net.final_markings = [{"43"}]
    return petri_net


def _petri_net_with_AND_and_nested_XOR() -> PetriNet:
    petri_net = PetriNet()
    petri_net._cached_search = False
    petri_net.add_place("0", "p0")
    petri_net.add_place("2", "p2")
    petri_net.add_place("4", "p4")
    petri_net.add_place("5", "p5")
    petri_net.add_place("8", "p8")
    petri_net.add_place("9", "p9")
    petri_net.add_place("13", "p13")
    petri_net.add_place("14", "p14")
    petri_net.add_place("17", "p17")
    petri_net.add_place("18", "p18")
    petri_net.add_place("19", "p19")
    petri_net.add_place("00", "p00")
    petri_net.add_place("23", "p23")
    petri_net.add_place("25", "p25")
    petri_net.add_place("27", "p27")
    petri_net.add_place("29", "p29")
    petri_net.add_transition("1", "A")
    petri_net.add_transition("10", "B")
    petri_net.add_transition("15", "C")
    petri_net.add_transition("16", "D")
    petri_net.add_transition("24", "E")
    petri_net.add_transition("28", "F")
    petri_net.add_transition("3", "silent_3", invisible=True)
    petri_net.add_transition("6", "silent_6", invisible=True)
    petri_net.add_transition("7", "silent_7", invisible=True)
    petri_net.add_transition("11", "silent_11", invisible=True)
    petri_net.add_transition("12", "silent_12", invisible=True)
    petri_net.add_transition("20", "silent_20", invisible=True)
    petri_net.add_transition("21", "silent_21", invisible=True)
    petri_net.add_transition("22", "silent_22", invisible=True)
    petri_net.add_transition("26", "silent_26", invisible=True)
    petri_net.add_edge("0", "1")
    petri_net.add_edge("1", "2")
    petri_net.add_edge("2", "3")
    petri_net.add_edge("3", "4")
    petri_net.add_edge("3", "5")
    petri_net.add_edge("4", "6")
    petri_net.add_edge("4", "7")
    petri_net.add_edge("6", "8")
    petri_net.add_edge("7", "9")
    petri_net.add_edge("8", "10")
    petri_net.add_edge("9", "11")
    petri_net.add_edge("9", "12")
    petri_net.add_edge("11", "13")
    petri_net.add_edge("12", "14")
    petri_net.add_edge("13", "15")
    petri_net.add_edge("14", "16")
    petri_net.add_edge("10", "17")
    petri_net.add_edge("15", "18")
    petri_net.add_edge("16", "19")
    petri_net.add_edge("17", "20")
    petri_net.add_edge("18", "21")
    petri_net.add_edge("19", "22")
    petri_net.add_edge("20", "23")
    petri_net.add_edge("21", "23")
    petri_net.add_edge("22", "23")
    petri_net.add_edge("5", "24")
    petri_net.add_edge("24", "25")
    petri_net.add_edge("23", "26")
    petri_net.add_edge("25", "26")
    petri_net.add_edge("26", "27")
    petri_net.add_edge("27", "28")
    petri_net.add_edge("28", "29")
    petri_net.initial_marking = {"0"}
    petri_net.final_markings = [{"29"}]
    return petri_net


def _petri_net_with_AND_and_nested_XOR_simple() -> PetriNet:
    petri_net = PetriNet()
    petri_net._cached_search = False
    petri_net.add_place("0", "p0")
    petri_net.add_place("2", "p2")
    petri_net.add_place("3", "p3")
    petri_net.add_place("8", "p8")
    petri_net.add_place("9", "p9")
    petri_net.add_place("11", "p11")
    petri_net.add_transition("1", "A")
    petri_net.add_transition("4", "B")
    petri_net.add_transition("5", "C")
    petri_net.add_transition("6", "D")
    petri_net.add_transition("7", "E")
    petri_net.add_transition("10", "F")
    petri_net.add_edge("0", "1")
    petri_net.add_edge("1", "2")
    petri_net.add_edge("1", "3")
    petri_net.add_edge("2", "4")
    petri_net.add_edge("2", "5")
    petri_net.add_edge("2", "6")
    petri_net.add_edge("3", "7")
    petri_net.add_edge("4", "8")
    petri_net.add_edge("5", "8")
    petri_net.add_edge("6", "8")
    petri_net.add_edge("7", "9")
    petri_net.add_edge("8", "10")
    petri_net.add_edge("9", "10")
    petri_net.add_edge("10", "11")
    petri_net.initial_marking = {"0"}
    petri_net.final_markings = [{"11"}]
    return petri_net


def _petri_net_with_loop_inside_AND() -> PetriNet:
    petri_net = PetriNet()
    petri_net._cached_search = False
    petri_net.add_place("0", "p0")
    petri_net.add_place("2", "p2")
    petri_net.add_place("4", "p4")
    petri_net.add_place("5", "p5")
    petri_net.add_place("8", "p8")
    petri_net.add_place("9", "p9")
    petri_net.add_place("12", "p12")
    petri_net.add_place("14", "p14")
    petri_net.add_transition("1", "A")
    petri_net.add_transition("6", "B")
    petri_net.add_transition("7", "C")
    petri_net.add_transition("13", "D")
    petri_net.add_transition("3", "silent_3", invisible=True)
    petri_net.add_transition("10", "silent_10", invisible=True)
    petri_net.add_transition("11", "silent_11", invisible=True)
    petri_net.add_edge("0", "1")
    petri_net.add_edge("1", "2")
    petri_net.add_edge("2", "3")
    petri_net.add_edge("3", "4")
    petri_net.add_edge("3", "5")
    petri_net.add_edge("4", "6")
    petri_net.add_edge("5", "7")
    petri_net.add_edge("6", "8")
    petri_net.add_edge("7", "9")
    petri_net.add_edge("8", "10")
    petri_net.add_edge("10", "4")
    petri_net.add_edge("8", "11")
    petri_net.add_edge("9", "11")
    petri_net.add_edge("11", "12")
    petri_net.add_edge("12", "13")
    petri_net.add_edge("13", "14")
    petri_net.initial_marking = {"0"}
    petri_net.final_markings = [{"14"}]
    return petri_net


def _petri_net_with_two_loops_inside_AND_followed_by_XOR_within_AND() -> PetriNet:
    petri_net = PetriNet()
    petri_net._cached_search = False
    petri_net.add_place("0", "p0")
    petri_net.add_place("2", "p2")
    petri_net.add_place("4", "p4")
    petri_net.add_place("5", "p5")
    petri_net.add_place("8", "p8")
    petri_net.add_place("9", "p9")
    petri_net.add_place("13", "p13")
    petri_net.add_place("15", "p15")
    petri_net.add_place("16", "p16")
    petri_net.add_place("21", "p21")
    petri_net.add_place("22", "p22")
    petri_net.add_place("23", "p23")
    petri_net.add_place("24", "p24")
    petri_net.add_place("29", "p29")
    petri_net.add_place("30", "p30")
    petri_net.add_place("31", "p31")
    petri_net.add_place("32", "p32")
    petri_net.add_place("37", "p37")
    petri_net.add_place("38", "p38")
    petri_net.add_place("40", "p40")
    petri_net.add_place("42", "p42")
    petri_net.add_transition("1", "A")
    petri_net.add_transition("6", "B")
    petri_net.add_transition("7", "C")
    petri_net.add_transition("25", "D")
    petri_net.add_transition("26", "E")
    petri_net.add_transition("27", "F")
    petri_net.add_transition("28", "G")
    petri_net.add_transition("41", "H")
    petri_net.add_transition("3", "silent_3", invisible=True)
    petri_net.add_transition("10", "silent_10", invisible=True)
    petri_net.add_transition("11", "silent_11", invisible=True)
    petri_net.add_transition("12", "silent_12", invisible=True)
    petri_net.add_transition("14", "silent_14", invisible=True)
    petri_net.add_transition("17", "silent_17", invisible=True)
    petri_net.add_transition("18", "silent_18", invisible=True)
    petri_net.add_transition("19", "silent_19", invisible=True)
    petri_net.add_transition("20", "silent_20", invisible=True)
    petri_net.add_transition("33", "silent_33", invisible=True)
    petri_net.add_transition("34", "silent_34", invisible=True)
    petri_net.add_transition("35", "silent_35", invisible=True)
    petri_net.add_transition("36", "silent_36", invisible=True)
    petri_net.add_transition("39", "silent_39", invisible=True)
    petri_net.add_edge("0", "1")
    petri_net.add_edge("1", "2")
    petri_net.add_edge("2", "3")
    petri_net.add_edge("3", "4")
    petri_net.add_edge("3", "5")
    petri_net.add_edge("4", "6")
    petri_net.add_edge("5", "7")
    petri_net.add_edge("6", "8")
    petri_net.add_edge("7", "9")
    petri_net.add_edge("8", "10")
    petri_net.add_edge("8", "12")
    petri_net.add_edge("9", "11")
    petri_net.add_edge("9", "12")
    petri_net.add_edge("10", "4")
    petri_net.add_edge("11", "5")
    petri_net.add_edge("12", "13")
    petri_net.add_edge("13", "14")
    petri_net.add_edge("14", "15")
    petri_net.add_edge("14", "16")
    petri_net.add_edge("15", "17")
    petri_net.add_edge("15", "18")
    petri_net.add_edge("16", "19")
    petri_net.add_edge("16", "20")
    petri_net.add_edge("17", "21")
    petri_net.add_edge("18", "22")
    petri_net.add_edge("19", "23")
    petri_net.add_edge("20", "24")
    petri_net.add_edge("21", "25")
    petri_net.add_edge("22", "26")
    petri_net.add_edge("23", "27")
    petri_net.add_edge("24", "28")
    petri_net.add_edge("25", "29")
    petri_net.add_edge("26", "30")
    petri_net.add_edge("27", "31")
    petri_net.add_edge("28", "32")
    petri_net.add_edge("29", "33")
    petri_net.add_edge("30", "34")
    petri_net.add_edge("31", "35")
    petri_net.add_edge("32", "36")
    petri_net.add_edge("33", "37")
    petri_net.add_edge("34", "37")
    petri_net.add_edge("35", "38")
    petri_net.add_edge("36", "38")
    petri_net.add_edge("37", "39")
    petri_net.add_edge("38", "39")
    petri_net.add_edge("39", "40")
    petri_net.add_edge("40", "41")
    petri_net.add_edge("41", "42")
    petri_net.initial_marking = {"0"}
    petri_net.final_markings = [{"42"}]
    return petri_net


def _petri_net_with_two_loops_inside_AND_followed_by_XOR_within_AND_simple() -> PetriNet:
    petri_net = PetriNet()
    petri_net._cached_search = False
    petri_net.add_place("0", "p0")
    petri_net.add_place("2", "p2")
    petri_net.add_place("3", "p3")
    petri_net.add_place("6", "p6")
    petri_net.add_place("7", "p7")
    petri_net.add_place("11", "p11")
    petri_net.add_place("12", "p12")
    petri_net.add_place("17", "p17")
    petri_net.add_place("18", "p18")
    petri_net.add_place("20", "p20")
    petri_net.add_transition("1", "A")
    petri_net.add_transition("4", "B")
    petri_net.add_transition("5", "C")
    petri_net.add_transition("13", "D")
    petri_net.add_transition("14", "E")
    petri_net.add_transition("15", "F")
    petri_net.add_transition("16", "G")
    petri_net.add_transition("19", "H")
    petri_net.add_transition("8", "silent_8", invisible=True)
    petri_net.add_transition("9", "silent_9", invisible=True)
    petri_net.add_transition("10", "silent_10", invisible=True)
    petri_net.add_edge("0", "1")
    petri_net.add_edge("1", "2")
    petri_net.add_edge("1", "3")
    petri_net.add_edge("2", "4")
    petri_net.add_edge("3", "5")
    petri_net.add_edge("4", "6")
    petri_net.add_edge("5", "7")
    petri_net.add_edge("6", "8")
    petri_net.add_edge("6", "10")
    petri_net.add_edge("7", "9")
    petri_net.add_edge("7", "10")
    petri_net.add_edge("8", "2")
    petri_net.add_edge("9", "3")
    petri_net.add_edge("10", "11")
    petri_net.add_edge("10", "12")
    petri_net.add_edge("11", "13")
    petri_net.add_edge("11", "14")
    petri_net.add_edge("12", "15")
    petri_net.add_edge("12", "16")
    petri_net.add_edge("13", "17")
    petri_net.add_edge("14", "17")
    petri_net.add_edge("15", "18")
    petri_net.add_edge("16", "18")
    petri_net.add_edge("17", "19")
    petri_net.add_edge("18", "19")
    petri_net.add_edge("19", "20")
    petri_net.initial_marking = {"0"}
    petri_net.final_markings = [{"20"}]
    return petri_net


def _petri_net_with_three_loops_inside_AND_two_of_them_inside_sub_AND() -> PetriNet:
    petri_net = PetriNet()
    petri_net._cached_search = False
    petri_net.add_place("0", "p0")
    petri_net.add_place("2", "p2")
    petri_net.add_place("4", "p4")
    petri_net.add_place("6", "p6")
    petri_net.add_place("7", "p7")
    petri_net.add_place("10", "p10")
    petri_net.add_place("11", "p11")
    petri_net.add_place("15", "p15")
    petri_net.add_place("17", "p17")
    petri_net.add_place("18", "p18")
    petri_net.add_place("20", "p20")
    petri_net.add_place("23", "p23")
    petri_net.add_place("25", "p25")
    petri_net.add_transition("3", "A")
    petri_net.add_transition("8", "B")
    petri_net.add_transition("9", "C")
    petri_net.add_transition("19", "D")
    petri_net.add_transition("16", "E")
    petri_net.add_transition("24", "F")
    petri_net.add_transition("1", "silent_1", invisible=True)
    petri_net.add_transition("5", "silent_5", invisible=True)
    petri_net.add_transition("12", "silent_12", invisible=True)
    petri_net.add_transition("13", "silent_13", invisible=True)
    petri_net.add_transition("14", "silent_14", invisible=True)
    petri_net.add_transition("21", "silent_21", invisible=True)
    petri_net.add_transition("22", "silent_22", invisible=True)
    petri_net.add_edge("0", "1")
    petri_net.add_edge("1", "2")
    petri_net.add_edge("1", "18")
    petri_net.add_edge("2", "3")
    petri_net.add_edge("3", "4")
    petri_net.add_edge("4", "5")
    petri_net.add_edge("5", "6")
    petri_net.add_edge("5", "7")
    petri_net.add_edge("6", "8")
    petri_net.add_edge("7", "9")
    petri_net.add_edge("8", "10")
    petri_net.add_edge("9", "11")
    petri_net.add_edge("10", "12")
    petri_net.add_edge("10", "14")
    petri_net.add_edge("11", "13")
    petri_net.add_edge("11", "14")
    petri_net.add_edge("12", "6")
    petri_net.add_edge("13", "7")
    petri_net.add_edge("14", "15")
    petri_net.add_edge("15", "16")
    petri_net.add_edge("16", "17")
    petri_net.add_edge("17", "22")
    petri_net.add_edge("18", "19")
    petri_net.add_edge("19", "20")
    petri_net.add_edge("20", "21")
    petri_net.add_edge("20", "22")
    petri_net.add_edge("21", "18")
    petri_net.add_edge("22", "23")
    petri_net.add_edge("23", "24")
    petri_net.add_edge("24", "25")
    petri_net.initial_marking = {"0"}
    petri_net.final_markings = [{"25"}]
    return petri_net


def _petri_net_with_loop_inside_parallel_and_loop_all_back() -> PetriNet:
    petri_net = PetriNet()
    petri_net._cached_search = False
    petri_net.add_place("0", "p0")
    petri_net.add_place("2", "p2")
    petri_net.add_place("4", "p4")
    petri_net.add_place("8", "p8")
    petri_net.add_place("6", "p6")
    petri_net.add_place("10", "p10")
    petri_net.add_place("12", "p12")
    petri_net.add_place("15", "p15")
    petri_net.add_transition("1", "A")
    petri_net.add_transition("5", "B")
    petri_net.add_transition("9", "C")
    petri_net.add_transition("14", "D")
    petri_net.add_transition("3", "silent_3", invisible=True)
    petri_net.add_transition("7", "silent_7", invisible=True)
    petri_net.add_transition("11", "silent_11", invisible=True)
    petri_net.add_transition("13", "silent_13", invisible=True)
    petri_net.add_edge("0", "1")
    petri_net.add_edge("1", "2")
    petri_net.add_edge("2", "3")
    petri_net.add_edge("3", "4")
    petri_net.add_edge("3", "8")
    petri_net.add_edge("4", "5")
    petri_net.add_edge("5", "6")
    petri_net.add_edge("6", "7")
    petri_net.add_edge("6", "11")
    petri_net.add_edge("7", "4")
    petri_net.add_edge("8", "9")
    petri_net.add_edge("9", "10")
    petri_net.add_edge("10", "11")
    petri_net.add_edge("11", "12")
    petri_net.add_edge("12", "13")
    petri_net.add_edge("12", "14")
    petri_net.add_edge("13", "2")
    petri_net.add_edge("14", "15")
    petri_net.initial_marking = {"0"}
    petri_net.final_markings = [{"15"}]
    return petri_net


def _petri_net_with_infinite_loop() -> PetriNet:
    petri_net = PetriNet()
    petri_net._cached_search = False
    petri_net.add_place("0", "p0")
    petri_net.add_place("2", "p2")
    petri_net.add_place("4", "p4")
    petri_net.add_place("6", "p6")
    petri_net.add_place("9", "p9")
    petri_net.add_place("11", "p11")
    petri_net.add_place("14", "p14")
    petri_net.add_place("16", "p16")
    petri_net.add_transition("1", "A")
    petri_net.add_transition("7", "B")
    petri_net.add_transition("15", "C")
    petri_net.add_transition("3", "silent_3", invisible=True)
    petri_net.add_transition("5", "silent_5", invisible=True)
    petri_net.add_transition("8", "silent_8", invisible=True)
    petri_net.add_transition("10", "silent_10", invisible=True)
    petri_net.add_transition("12", "silent_12", invisible=True)
    petri_net.add_transition("13", "silent_13", invisible=True)
    petri_net.add_edge("0", "1")
    petri_net.add_edge("1", "2")
    petri_net.add_edge("2", "3")
    petri_net.add_edge("3", "4")
    petri_net.add_edge("4", "5")
    petri_net.add_edge("4", "8")
    petri_net.add_edge("5", "6")
    petri_net.add_edge("6", "7")
    petri_net.add_edge("7", "9")
    petri_net.add_edge("8", "9")
    petri_net.add_edge("9", "10")
    petri_net.add_edge("10", "11")
    petri_net.add_edge("11", "12")
    petri_net.add_edge("11", "13")
    petri_net.add_edge("12", "2")
    petri_net.add_edge("13", "14")
    petri_net.add_edge("14", "15")
    petri_net.add_edge("15", "16")
    petri_net.initial_marking = {"0"}
    petri_net.final_markings = [{"16"}]
    return petri_net


def _petri_net_with_infinite_loop_and_AND() -> PetriNet:
    petri_net = PetriNet()
    petri_net._cached_search = False
    petri_net.add_place("0", "p0")
    petri_net.add_place("2", "p2")
    petri_net.add_place("4", "p4")
    petri_net.add_place("6", "p6")
    petri_net.add_place("8", "p8")
    petri_net.add_place("11", "p11")
    petri_net.add_place("12", "p12")
    petri_net.add_place("14", "p14")
    petri_net.add_place("17", "p17")
    petri_net.add_place("20", "p20")
    petri_net.add_place("22", "p22")
    petri_net.add_place("25", "p25")
    petri_net.add_place("27", "p27")
    petri_net.add_transition("1", "A")
    petri_net.add_transition("9", "B")
    petri_net.add_transition("15", "C")
    petri_net.add_transition("26", "D")
    petri_net.add_transition("3", "silent_3", invisible=True)
    petri_net.add_transition("5", "silent_5", invisible=True)
    petri_net.add_transition("7", "silent_7", invisible=True)
    petri_net.add_transition("10", "silent_10", invisible=True)
    petri_net.add_transition("13", "silent_13", invisible=True)
    petri_net.add_transition("16", "silent_16", invisible=True)
    petri_net.add_transition("18", "silent_18", invisible=True)
    petri_net.add_transition("19", "silent_19", invisible=True)
    petri_net.add_transition("21", "silent_21", invisible=True)
    petri_net.add_transition("23", "silent_23", invisible=True)
    petri_net.add_transition("24", "silent_24", invisible=True)
    petri_net.add_edge("0", "1")
    petri_net.add_edge("1", "2")
    petri_net.add_edge("2", "3")
    petri_net.add_edge("3", "4")
    petri_net.add_edge("4", "5")
    petri_net.add_edge("4", "19")
    petri_net.add_edge("5", "6")
    petri_net.add_edge("5", "12")
    petri_net.add_edge("6", "7")
    petri_net.add_edge("6", "10")
    petri_net.add_edge("7", "8")
    petri_net.add_edge("8", "9")
    petri_net.add_edge("9", "11")
    petri_net.add_edge("10", "11")
    petri_net.add_edge("11", "18")
    petri_net.add_edge("12", "13")
    petri_net.add_edge("12", "16")
    petri_net.add_edge("13", "14")
    petri_net.add_edge("14", "15")
    petri_net.add_edge("15", "17")
    petri_net.add_edge("16", "17")
    petri_net.add_edge("17", "18")
    petri_net.add_edge("18", "20")
    petri_net.add_edge("19", "20")
    petri_net.add_edge("20", "21")
    petri_net.add_edge("21", "22")
    petri_net.add_edge("22", "23")
    petri_net.add_edge("22", "24")
    petri_net.add_edge("23", "2")
    petri_net.add_edge("24", "25")
    petri_net.add_edge("25", "26")
    petri_net.add_edge("26", "27")
    petri_net.initial_marking = {"0"}
    petri_net.final_markings = [{"27"}]
    return petri_net


def _petri_net_with_optional_AND_with_skipping_and_loop_branches() -> PetriNet:
    petri_net = PetriNet()
    petri_net._cached_search = False
    petri_net.add_place("0", "p0")
    petri_net.add_place("2", "p2")
    petri_net.add_place("4", "p4")
    petri_net.add_place("5", "p5")
    petri_net.add_place("8", "p8")
    petri_net.add_place("9", "p9")
    petri_net.add_place("12", "p12")
    petri_net.add_place("16", "p16")
    petri_net.add_place("18", "p18")
    petri_net.add_transition("1", "A")
    petri_net.add_transition("10", "B")
    petri_net.add_transition("7", "C")
    petri_net.add_transition("17", "D")
    petri_net.add_transition("3", "silent_3", invisible=True)
    petri_net.add_transition("6", "silent_6", invisible=True)
    petri_net.add_transition("11", "silent_11", invisible=True)
    petri_net.add_transition("13", "silent_13", invisible=True)
    petri_net.add_transition("14", "silent_14", invisible=True)
    petri_net.add_transition("15", "silent_15", invisible=True)
    petri_net.add_edge("0", "1")
    petri_net.add_edge("1", "2")
    petri_net.add_edge("2", "3")
    petri_net.add_edge("2", "15")
    petri_net.add_edge("3", "4")
    petri_net.add_edge("3", "5")
    petri_net.add_edge("4", "6")
    petri_net.add_edge("4", "11")
    petri_net.add_edge("5", "7")
    petri_net.add_edge("6", "8")
    petri_net.add_edge("7", "9")
    petri_net.add_edge("8", "10")
    petri_net.add_edge("9", "13")
    petri_net.add_edge("9", "14")
    petri_net.add_edge("10", "12")
    petri_net.add_edge("11", "12")
    petri_net.add_edge("12", "14")
    petri_net.add_edge("13", "5")
    petri_net.add_edge("14", "16")
    petri_net.add_edge("15", "16")
    petri_net.add_edge("16", "17")
    petri_net.add_edge("17", "18")
    petri_net.initial_marking = {"0"}
    petri_net.final_markings = [{"18"}]
    return petri_net


def _petri_net_based_on_sepsis() -> PetriNet:
    petri_net = PetriNet()
    petri_net._cached_search = False
    petri_net.add_place("0", "p0")
    petri_net.add_place("2", "p2")
    petri_net.add_place("4", "p4")
    petri_net.add_place("5", "p5")
    petri_net.add_place("7", "p7")
    petri_net.add_place("10", "p10")
    petri_net.add_place("12", "p12")
    petri_net.add_place("14", "p14")
    petri_net.add_place("17", "p17")
    petri_net.add_place("18", "p18")
    petri_net.add_place("20", "p20")
    petri_net.add_place("22", "p22")
    petri_net.add_place("23", "p23")
    petri_net.add_place("25", "p25")
    petri_net.add_place("28", "p28")
    petri_net.add_place("30", "p30")
    petri_net.add_place("32", "p32")
    petri_net.add_transition("1", "A")
    petri_net.add_transition("3", "B")
    petri_net.add_transition("8", "C")
    petri_net.add_transition("26", "D")
    petri_net.add_transition("15", "E")
    petri_net.add_transition("19", "F")
    petri_net.add_transition("31", "G")
    petri_net.add_transition("6", "silent_6", invisible=True)
    petri_net.add_transition("9", "silent_9", invisible=True)
    petri_net.add_transition("11", "silent_11", invisible=True)
    petri_net.add_transition("24", "silent_24", invisible=True)
    petri_net.add_transition("27", "silent_27", invisible=True)
    petri_net.add_transition("13", "silent_13", invisible=True)
    petri_net.add_transition("16", "silent_16", invisible=True)
    petri_net.add_transition("21", "silent_21", invisible=True)
    petri_net.add_transition("29", "silent_29", invisible=True)
    petri_net.add_edge("0", "1")
    petri_net.add_edge("1", "2")
    petri_net.add_edge("1", "5")
    petri_net.add_edge("1", "23")
    petri_net.add_edge("2", "3")
    petri_net.add_edge("3", "4")
    petri_net.add_edge("4", "11")
    petri_net.add_edge("5", "6")
    petri_net.add_edge("5", "9")
    petri_net.add_edge("6", "7")
    petri_net.add_edge("7", "8")
    petri_net.add_edge("8", "10")
    petri_net.add_edge("9", "10")
    petri_net.add_edge("10", "11")
    petri_net.add_edge("11", "12")
    petri_net.add_edge("11", "18")
    petri_net.add_edge("12", "13")
    petri_net.add_edge("12", "16")
    petri_net.add_edge("13", "14")
    petri_net.add_edge("14", "15")
    petri_net.add_edge("15", "17")
    petri_net.add_edge("16", "17")
    petri_net.add_edge("17", "21")
    petri_net.add_edge("18", "19")
    petri_net.add_edge("19", "20")
    petri_net.add_edge("20", "21")
    petri_net.add_edge("21", "22")
    petri_net.add_edge("22", "29")
    petri_net.add_edge("23", "24")
    petri_net.add_edge("23", "27")
    petri_net.add_edge("24", "25")
    petri_net.add_edge("25", "26")
    petri_net.add_edge("26", "28")
    petri_net.add_edge("27", "28")
    petri_net.add_edge("28", "29")
    petri_net.add_edge("29", "30")
    petri_net.add_edge("30", "31")
    petri_net.add_edge("31", "32")
    petri_net.initial_marking = {"0"}
    petri_net.final_markings = [{"32"}]
    return petri_net
