
class MyClass:
    name1 = "Max"
    
    def __init__(self, name=MyClass.name1):
        self.name = name
        print(f"{self.name}")