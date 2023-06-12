import sys

sys.path.append("../build")

import pyshell
import pyshell.impl


def test():
    pyshell.start()

    print(f"# Simple Function {pyshell.add(3, 5) = }")

    pyshell.impl.hey()

    #######################################################################
    # Simple Class
    #######################################################################
    person = pyshell.Person()
    person.hey()
    person.say()
    person.name = "John"
    person.age = 36
    person.say()

    john = pyshell.John()
    john.hey()
    john.say()


if __name__ == "__main__":
    test()
