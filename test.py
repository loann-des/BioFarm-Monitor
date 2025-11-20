def facto(n : int, acc : int) -> int:
    return facto(n-1,n*acc) if n else acc

print(facto(5,1))

class Pfacto :
    def __init__(self):
        self.x = 1
    def print_facto(self,n) -> None :
        if n :
            self.x*=n
            self.print_facto(n-1)
        else : 
            print(self.x)
    
fact = Pfacto()
print (fact.print_facto(5))